import os
from typing import List, Dict, Any
from schemas import DocumentRecord, DocType, ClassificationResult, ExtractionResult

# Note: Aapke project ke structure ke hisaab se llm_client ko import karein
# e.g., from utils.llm import llm_client ya setup kiye gaye client ko use karein


def map_to_doctype(raw_type: str) -> DocType:
    """LLM ke raw output string ko safe DocType Enum mein convert karta hai."""
    if not raw_type:
        return DocType.UNKNOWN

    clean_val = str(raw_type).strip().upper()

    # Generic variations aur LLM outputs ke liye mapping
    aliases = {
        "TRANSCRIPT": getattr(DocType, "TRANSCRIPT", DocType.UNKNOWN),
        "PHOTOGRAPH": getattr(DocType, "PHOTO", DocType.UNKNOWN),
        "PHOTOGRAPHY": getattr(DocType, "PHOTO", DocType.UNKNOWN),
        "PICTURE": getattr(DocType, "PHOTO", DocType.UNKNOWN),
        "IMAGE": getattr(DocType, "PHOTO", DocType.UNKNOWN),
        "RESUME": getattr(DocType, "CV", DocType.UNKNOWN),
    }

    if clean_val in aliases:
        return aliases[clean_val]

    try:
        return DocType(clean_val)
    except ValueError:
        return DocType.UNKNOWN


def extract_raw_text(file_path: str) -> str:
    """File se raw text extract karne ka helper function (PyMuPDF / pdfplumber etc.)."""
    # Aapka existing text extraction logic yahan aayega
    # Sample fallback textagar implementation baaqi hai:
    return f"Sample extracted text from {os.path.basename(file_path)}"


def classify_document(raw_text: str) -> ClassificationResult:
    """Document ki classification karta hai using LLM client."""
    prompt = f"""Analyze the following document text and classify its type (e.g., CV, TRANSCRIPT, PASSPORT, PHOTO) and confidence score:

    Text:
    {raw_text[:2000]}
    """
    # System ke llm_client call ke saath structured validation
    # return llm_client.call_json(prompt, schema=ClassificationResult)
    
    # Fallback dummy response agar offline test kar rahe hon:
    return ClassificationResult(doc_type="CV", confidence=0.95)


def extract_key_fields(raw_text: str, doc_type: DocType) -> Dict[str, Any]:
    """Document ke type ke hisaab se key fields extract karta hai."""
    prompt = f"""Extract key metadata fields for document type {doc_type.value}:
    
    Text:
    {raw_text[:3000]}
    """
    # return llm_client.call_json(prompt, schema=ExtractionResult).fields
    return {"status": "extracted", "sample_key": "sample_value"}


def process_single_file(file_path: str) -> DocumentRecord:
    """Ek single file ko process karke validated DocumentRecord return karta hai."""
    # 1. Raw text extract karein
    raw_text = extract_raw_text(file_path)

    # 2. LLM classification
    classify_res = classify_document(raw_text)

    # 3. doc_type ko safe DocType Enum mein convert karein
    enum_doc_type = map_to_doctype(classify_res.doc_type)

    # 4. Key fields extraction
    key_fields = extract_key_fields(raw_text, enum_doc_type)

    # 5. Corrected DocumentRecord return karein (exact schema fields)
    return DocumentRecord(
        filename=os.path.basename(file_path),
        doc_type=enum_doc_type,
        confidence=classify_res.confidence,
        text=raw_text,
        fields=key_fields,
    )


def process_documents(file_paths: List[str]) -> List[DocumentRecord]:
    """Multiple files ki list ko process karke DocumentRecord objects ki list deta hai."""
    processed_records = []
    for path in file_paths:
        if os.path.exists(path):
            record = process_single_file(path)
            processed_records.append(record)
        else:
            print(f"Warning: File path not found: {path}")

    return processed_records
