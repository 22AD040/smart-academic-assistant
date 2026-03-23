from pypdf import PdfReader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text(file):
    reader = PdfReader(file)
    text = ""

    for i, page in enumerate(reader.pages):
        try:
            content = page.extract_text()
            if content:
                text += f"\n[Page {i+1}]\n{content}"
        except:
            continue

    return text

def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks