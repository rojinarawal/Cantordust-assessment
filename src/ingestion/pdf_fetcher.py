import io
import requests
import pdfplumber
from langchain_core.tools import tool

@tool
def fetch_pdf_text(url: str) -> str:
    """Download a PDF from a URL and return its extracted text content,
    including any tables found, so it can be analyzed for product specs."""
    headers = {
        "User-Agent": (
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.deyeinverter.com/",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    text_chunks = []
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            text_chunks.append(f"--- Page {page_num} ---\n{page_text}")
            for table in page.extract_tables():
                text_chunks.append(f"[Table on page {page_num}]: {table}")
    return "\n".join(text_chunks)