from llm.json_utils import parse_and_validate

import json
import time
from llm.json_utils import parse_and_validate

from groq import Groq, RateLimitError
from pydantic import ValidationError

import config

_client = None


def _get_client():
    global _client
    if _client is None:
        config.check_config()
        _client = Groq(api_key=config.API_KEY)
    return _client


def call_text(prompt, system=None, json_mode=False, temperature=0.2):
    """Send a prompt, get plain text back. Retries on rate limits."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(config.MAX_RETRIES + 1):
        try:
            resp = _get_client().chat.completions.create(**kwargs)
            return resp.choices[0].message.content
        except RateLimitError:
            if attempt == config.MAX_RETRIES:
                raise
            time.sleep(config.RATE_LIMIT_WAIT * (attempt + 1))


def call_json(prompt, schema, system=None):
    """Send a prompt, get a validated Pydantic object back."""
    schema_hint = json.dumps(schema.model_json_schema())
    full_prompt = (
        f"{prompt}\n\nReturn ONLY valid JSON matching this schema:\n{schema_hint}"
    )

    last_error = None
    for _ in range(2):  # first try + one retry
        p = full_prompt
        if last_error:
            p += f"\n\nYour previous answer was invalid: {last_error}\nFix it and return only JSON."
        raw = call_text(p, system=system, json_mode=True)
        try:
            return parse_and_validate(raw, schema)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)

    raise ValueError(f"LLM returned invalid JSON twice: {last_error}")