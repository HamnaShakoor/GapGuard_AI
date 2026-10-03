from pydantic import BaseModel
from llm.json_utils import parse_and_validate


class T(BaseModel):
    doc_type: str


print(parse_and_validate('```json\n{"doc_type": "cv"}\n```', T))
print(parse_and_validate('Here you go: {"doc_type": "cnic"} hope it helps', T))