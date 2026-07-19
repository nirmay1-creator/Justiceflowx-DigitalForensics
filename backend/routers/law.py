from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
from database import get_db

router = APIRouter(
    prefix="/api/law",
    tags=["law"]
)

@router.get("/search")
def search_law(q: str = Query(..., min_length=2, description="Keyword to search"), db: Session = Depends(get_db)):
    """
    Search the LegalKnowledge database for keywords in the raw text or keywords column.
    Returns the top 5 matching sections.
    """
    # Simple ILIKE search for broad compatibility
    search_term = f"%{q}%"
    
    results = db.query(models.LegalKnowledge).filter(
        or_(
            models.LegalKnowledge.raw_text.ilike(search_term),
            models.LegalKnowledge.keywords.ilike(search_term),
            models.LegalKnowledge.section_title.ilike(search_term)
        )
    ).limit(5).all()
    
    if not results:
        # Fallback if no exact match
        return {"results": []}
        
    formatted_results = []
    for r in results:
        formatted_results.append({
            "id": r.id,
            "document": r.document_name,
            "section": r.section_title,
            "text": r.raw_text,
            "keywords": r.keywords
        })
        
    return {"results": formatted_results}
