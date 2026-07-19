import os
import re
import httpx
import logging
from io import BytesIO
import PyPDF2
from sqlalchemy.orm import Session
import sys

# Ensure backend directory is in path when run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import models
from database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF_URL = "https://www.mha.gov.in/sites/default/files/250883_english_01042024.pdf"

def ingest_pdf_to_db():
    logger.info("Initializing database tables...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    logger.info(f"Downloading PDF from {PDF_URL}...")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = httpx.get(PDF_URL, headers=headers, timeout=120.0, follow_redirects=True)
        response.raise_for_status()
        pdf_bytes = response.content
    except Exception as e:
        logger.error(f"Failed to download PDF: {e}")
        db.close()
        return

    logger.info("Parsing PDF content...")
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
    
    full_text = ""
    for i, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    logger.info("Chunking text into Articles...")
    # Rough regex to find "Article X." or "X. " 
    # The Constitution usually formats articles with numbers at the start of paragraphs.
    # For a simple keyword search, we will chunk the text into roughly 1000 character segments 
    # overlapping slightly, OR try to split by 'Article'.
    # We will use a generic paragraph chunker for robust searching since PDF extraction is messy.
    
    chunks = []
    paragraphs = full_text.split('\n')
    current_chunk = ""
    
    for para in paragraphs:
        # Ignore very short lines that might be page numbers
        if len(para.strip()) < 5:
            continue
            
        if len(current_chunk) + len(para) > 800:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += " " + para
            
    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info(f"Generated {len(chunks)} searchable chunks. Inserting into database...")
    
    for i, chunk in enumerate(chunks):
        # Extract potential keywords (e.g., words longer than 5 chars, capitalized)
        words = re.findall(r'\b[A-Z][a-z]{5,}\b', chunk)
        keywords = ", ".join(list(set(words))[:10]) # Take top 10 unique capitalized words as keywords
        
        doc = models.LegalKnowledge(
            document_name="Constitution of India",
            section_title=f"Section {i+1}",
            raw_text=chunk,
            keywords=keywords
        )
        db.add(doc)
        
    db.commit()
    logger.info("Successfully ingested PDF into LegalKnowledge table.")
    db.close()

if __name__ == "__main__":
    ingest_pdf_to_db()
