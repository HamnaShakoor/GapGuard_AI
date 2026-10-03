import fitz  # PyMuPDF

def read_pdf(file_path: str) -> str:
    """Extract text from a PDF file page by page."""
    doc = fitz.open(file_path)
    extracted_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            extracted_text.append(f"--- Page {page_num + 1} ---\n{text}")
            
    doc.close()
    return "\n\n".join(extracted_text)
