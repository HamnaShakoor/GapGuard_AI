import os
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Naye updated schemas import karein
from schemas import DocumentRecord
from utils.pdf_reader import read_pdf
from utils.docx_reader import read_docx
from utils.ocr_fallback import is_pdf_scanned, extract_image_text_llm

def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Structured outputs ke liye temporary Pydantic schemas
class ClassificationResult(BaseModel):
    doc_type: str = Field(description="Detected type e.g., CV, Transcript, CNIC, Photograph, Unknown")
    confidence: float = Field(default=1.0)
    reasoning: str = Field(default="")

class ExtractionResult(BaseModel):
    key_fields: Dict[str, Any] = Field(default_factory=dict, description="Parsed metadata fields")

def process_single_file(file_path: str, llm_client) -> DocumentRecord:
    """Reads, classifies, and extracts key fields from a single file using call_json."""
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

    # 2. Classify Document Type using call_json
    classify_prompt_template = load_prompt("prompts/classify_prompt.txt")
    classify_prompt = classify_prompt_template.format(extracted_text=raw_text[:2000])
    
    # Updated: call_json with schema
    classify_res: ClassificationResult = llm_client.call_json(
        prompt=classify_prompt, 
        schema=ClassificationResult
    )
    doc_type = classify_res.doc_type if hasattr(classify_res, 'doc_type') else classify_res.get("doc_type", "Unknown")

    # 3. Extract Key Fields using call_json
    extract_prompt_template = load_prompt("prompts/extract_prompt.txt")
    extract_prompt = extract_prompt_template.format(doc_type=doc_type, extracted_text=raw_text)
    
    # Updated: call_json with schema
    extract_res: ExtractionResult = llm_client.call_json(
        prompt=extract_prompt, 
        schema=ExtractionResult
    )
    key_fields = extract_res.key_fields if hasattr(extract_res, 'key_fields') else extract_res.get("key_fields", {})

    # 4. Return standard DocumentRecord schema
    return DocumentRecord(
        file_name=os.path.basename(file_path),
        doc_type=doc_type,
        extracted_text=raw_text,
        key_fields=key_fields
    )

def process_documents(file_paths: List[str], llm_client) -> List[DocumentRecord]:
    """Deliverable function: Batch process list of uploaded documents."""
    results = []
    for file_path in file_paths:
        doc_record = process_single_file(file_path, llm_client)
        results.append(doc_record)
    return results
