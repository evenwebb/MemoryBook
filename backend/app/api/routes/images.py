from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ...core.database import get_db
from ...models import schemas
from ...models.database import Image, Category, Tag
from ...services.uploader import MultiThreadedUploader
from ...services.image_processor import ImageProcessor
from ...services.ocr_service import OCRService
from sqlalchemy import or_, and_
from datetime import datetime

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=schemas.BatchUploadResponse)
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple images with batch processing"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploader = MultiThreadedUploader(db)
    result = uploader.upload_batch(files)
    
    return schemas.BatchUploadResponse(**result)


@router.get("/", response_model=List[schemas.ImageResponse])
async def get_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of images with optional filtering"""
    query = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    )
    
    if category_id:
        query = query.join(Image.categories).filter(Category.id == category_id)
    
    if tag_id:
        query = query.join(Image.tags).filter(Tag.id == tag_id)
    
    images = query.order_by(Image.upload_date.desc()).offset(skip).limit(limit).all()
    return images


@router.get("/{image_id}", response_model=schemas.ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """Get single image by ID"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """Delete an image"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete files
    import os
    if os.path.exists(image.file_path):
        os.remove(image.file_path)
    if image.thumbnail_path and os.path.exists(image.thumbnail_path):
        os.remove(image.thumbnail_path)
    
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.post("/{image_id}/tags", response_model=schemas.ImageResponse)
async def add_tags_to_image(
    image_id: int,
    tag_ids: List[int],
    db: Session = Depends(get_db)
):
    """Add tags to an image"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    # Only add tags that aren't already present
    existing_tag_ids = {tag.id for tag in image.tags}
    new_tags = [tag for tag in tags if tag.id not in existing_tag_ids]
    image.tags.extend(new_tags)
    db.commit()
    db.refresh(image)
    
    return image


@router.delete("/{image_id}/tags/{tag_id}", response_model=schemas.ImageResponse)
async def remove_tag_from_image(
    image_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Remove a tag from an image"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag and tag in image.tags:
        image.tags.remove(tag)
        db.commit()
        db.refresh(image)
    
    return image


@router.post("/{image_id}/categories", response_model=schemas.ImageResponse)
async def add_categories_to_image(
    image_id: int,
    category_ids: List[int],
    db: Session = Depends(get_db)
):
    """Add categories to an image"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    # Only add categories that aren't already present
    existing_category_ids = {cat.id for cat in image.categories}
    new_categories = [cat for cat in categories if cat.id not in existing_category_ids]
    image.categories.extend(new_categories)
    db.commit()
    db.refresh(image)
    
    return image


@router.delete("/{image_id}/categories/{category_id}", response_model=schemas.ImageResponse)
async def remove_category_from_image(
    image_id: int,
    category_id: int,
    db: Session = Depends(get_db)
):
    """Remove a category from an image"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if category and category in image.categories:
        image.categories.remove(category)
        db.commit()
        db.refresh(image)
    
    return image


@router.put("/{image_id}/notes", response_model=schemas.ImageResponse)
async def update_image_notes(
    image_id: int,
    notes: str,
    db: Session = Depends(get_db)
):
    """Update image notes"""
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image.notes = notes
    db.commit()
    db.refresh(image)
    return image


@router.put("/{image_id}/rotate", response_model=schemas.ImageResponse)
async def rotate_image(
    image_id: int,
    degrees: int = Query(..., description="Rotation degrees: 90, 180, 270, or -90"),
    db: Session = Depends(get_db)
):
    """Rotate image by 90, 180, or 270 degrees"""
    if degrees not in [90, 180, 270, -90]:
        raise HTTPException(status_code=400, detail="Degrees must be 90, 180, 270, or -90")
    
    image = db.query(Image).options(
        joinedload(Image.tags),
        joinedload(Image.categories)
    ).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image.rotation = (image.rotation + degrees) % 360
    db.commit()
    db.refresh(image)
    return image


@router.post("/{image_id}/process-ocr", response_model=schemas.ImageResponse)
async def process_ocr(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Manually trigger OCR processing for an image"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    ocr_service = OCRService()
    ocr_result = ocr_service.extract_text(image.file_path)
    
    if ocr_result['text']:
        image.ocr_text = ocr_result['text']
        image.ocr_processed = datetime.now()
        
        # Update suggestions
        extracted_dates = ocr_service.extract_dates(ocr_result['text'])
        extracted_names = ocr_service.extract_names(ocr_result['text'])
        
        from ...services.tag_suggester import TagSuggester
        tag_suggester = TagSuggester()
        suggested_tags = tag_suggester.suggest_tags(
            ocr_result['text'],
            extracted_dates,
            extracted_names
        )
        suggested_category = tag_suggester.suggest_category(ocr_result['text'])
        
        if not image.exif_data:
            image.exif_data = {}
        image.exif_data['suggested_tags'] = suggested_tags
        if suggested_category:
            image.exif_data['suggested_category'] = suggested_category
        
        db.commit()
        db.refresh(image)
    
    return image

