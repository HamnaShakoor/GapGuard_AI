import docx

def read_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    full_text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
    return "\n".join(full_text)
