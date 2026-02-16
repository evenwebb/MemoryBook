import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.cache import cache
from ...models import schemas
from ...models.database import Tag

logger = logging.getLogger("memorybook")

router = APIRouter(prefix="/tags", tags=["tags"])

TAG_CACHE_PREFIX = "tags:all:"


def _invalidate_tag_cache():
    """Clear all tag-related cache entries."""
    cache.clear()


@router.get("/", response_model=List[schemas.TagResponse])
async def get_tags(
    tag_type: Optional[str] = Query(None, description="Filter by tag type"),
    db: Session = Depends(get_db)
):
    """Get all tags, optionally filtered by type (cached)"""
    cache_key = f"{TAG_CACHE_PREFIX}{tag_type or 'none'}"

    cached_tags = cache.get(cache_key)
    if cached_tags:
        return cached_tags

    query = db.query(Tag)

    if tag_type:
        query = query.filter(Tag.tag_type == tag_type)

    tags = query.order_by(Tag.name).all()

    cache.set(cache_key, tags, ttl_seconds=600)
    return tags


@router.post("/", response_model=schemas.TagResponse)
async def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db)
):
    """Create a new tag, or return existing if name matches"""
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        return existing

    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    # Invalidate cache after successful commit
    _invalidate_tag_cache()

    return db_tag


@router.get("/{tag_id}", response_model=schemas.TagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a tag by ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=schemas.TagResponse)
async def update_tag(
    tag_id: int,
    tag: schemas.TagCreate,
    db: Session = Depends(get_db)
):
    """Update a tag"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)

    db.commit()
    db.refresh(db_tag)

    # Invalidate cache after successful commit
    _invalidate_tag_cache()

    return db_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()

    # Invalidate cache after successful commit
    _invalidate_tag_cache()

    return {"message": "Tag deleted successfully"}
