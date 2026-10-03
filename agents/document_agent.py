import os
import json
from utils.pdf_reader import read_pdf
from utils.docx_reader import read_docx
from utils.ocr_fallback import is_pdf_scanned, extract_image_text_llm
from schemas import ExtractedDocument

def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def process_single_file(file_path: str, llm_client) -> ExtractedDocument:
    """Reads, classifies, and extracts key fields from a single file."""
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""

    # 1. Read Raw Text
    if ext == ".pdf":
        if is_pdf_scanned(file_path):
            raw_text = extract_image_text_llm(llm_client, file_path)
        else:
            raw_text = read_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        raw_text = read_docx(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        raw_text = extract_image_text_llm(llm_client, file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # 2. Classify Document Type
    classify_prompt_template = load_prompt("prompts/classify_prompt.txt")
    classify_prompt = classify_prompt_template.format(extracted_text=raw_text[:2000])
    
    classify_res = llm_client.generate_json(classify_prompt)
    doc_type = classify_res.get("doc_type", "Unknown")

    # 3. Extract Key Fields
    extract_prompt_template = load_prompt("prompts/extract_prompt.txt")
    extract_prompt = extract_prompt_template.format(doc_type=doc_type, extracted_text=raw_text)
    
    key_fields = llm_client.generate_json(extract_prompt)

    # 4. Return standard Pydantic schema
    return ExtractedDocument(
        file_name=os.path.basename(file_path),
        doc_type=doc_type,
        extracted_text=raw_text,
        key_fields=key_fields
    )

def process_documents(file_paths: list[str], llm_client) -> list[ExtractedDocument]:
    """Deliverable function: Batch process list of uploaded documents."""
    results = []
    for file_path in file_paths:
        doc_record = process_single_file(file_path, llm_client)
        results.append(doc_record)
    return results
