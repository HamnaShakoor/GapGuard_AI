import fitz

def is_pdf_scanned(file_path: str) -> bool:
    """Checks if a PDF has readable text or is purely image-based."""
    doc = fitz.open(file_path)
    has_text = False
    for page in doc:
        if page.get_text().strip():
            has_text = True
            break
    doc.close()
    return not has_text

def extract_image_text_llm(llm_client, image_path: str) -> str:
    """Fallback OCR using LLM vision capabilities for scanned files/images."""
    prompt = "Extract all readable text from this scanned image/document exactly as it appears."
    response = llm_client.generate_vision(image_path=image_path, prompt=prompt)
    return response
