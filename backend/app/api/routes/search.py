from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List
from ...core.database import get_db
from ...models import schemas
from ...models.database import Image, Category, Tag

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=List[schemas.ImageResponse])
async def search_images(
    search_request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """Advanced search for images with optimised queries"""
    query = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    )
    
    # Text search in OCR text
    if search_request.query:
        # Full-text search (works with both PostgreSQL and SQLite)
        search_term = f"%{search_request.query}%"
        filters = [
            Image.original_filename.ilike(search_term),
            Image.filename.ilike(search_term)
        ]
        # Add OCR text filter only if column exists and is not None
        filters.append(Image.ocr_text.ilike(search_term))
        query = query.filter(or_(*filters))
    
    # Filter by categories
    if search_request.category_ids:
        query = query.join(Image.categories).filter(
            Category.id.in_(search_request.category_ids)
        )
    
    # Filter by tags
    if search_request.tag_ids:
        query = query.join(Image.tags).filter(
            Tag.id.in_(search_request.tag_ids)
        )
    
    # Filter by date range
    if search_request.date_from:
        query = query.filter(Image.upload_date >= search_request.date_from)
    
    if search_request.date_to:
        query = query.filter(Image.upload_date <= search_request.date_to)
    
    # Remove duplicates from joins
    query = query.distinct()
    
    # Apply pagination
    images = query.order_by(Image.upload_date.desc()).offset(
        search_request.offset
    ).limit(search_request.limit).all()
    
    return images


@router.get("/suggestions")
async def get_search_suggestions(
    q: str,
    db: Session = Depends(get_db)
):
    """Get search suggestions based on query"""
    suggestions = {
        'tags': [],
        'categories': [],
        'dates': []
    }
    
    if not q or len(q) < 2:
        return suggestions
    
    search_term = f"%{q}%"
    
    # Suggest tags
    tags = db.query(Tag).filter(Tag.name.ilike(search_term)).limit(10).all()
    suggestions['tags'] = [{'id': t.id, 'name': t.name} for t in tags]
    
    # Suggest categories
    categories = db.query(Category).filter(Category.name.ilike(search_term)).limit(10).all()
    suggestions['categories'] = [{'id': c.id, 'name': c.name} for c in categories]
    
    return suggestions

