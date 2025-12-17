from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ImageBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str


class ImageCreate(ImageBase):
    pass


class TagBase(BaseModel):
    name: str
    tag_type: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImageResponse(ImageBase):
    id: int
    file_path: str
    thumbnail_path: Optional[str]
    upload_date: datetime
    exif_data: Optional[dict] = None
    ocr_text: Optional[str] = None
    ocr_processed: Optional[datetime] = None
    notes: Optional[str] = None
    rotation: Optional[int] = 0
    width: Optional[int] = None
    height: Optional[int] = None
    tags: List[TagResponse] = []
    categories: List[CategoryResponse] = []
    
    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    id: Optional[int] = None
    filename: str
    status: str
    message: Optional[str] = None
    exif_data: Optional[dict] = None  # Include suggestions


class BatchUploadResponse(BaseModel):
    total: int
    successful: int
    failed: int
    images: List[ImageUploadResponse]


class SearchRequest(BaseModel):
    query: Optional[str] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class OCRResult(BaseModel):
    text: str
    confidence: float
    suggested_tags: List[str] = []
    suggested_category: Optional[str] = None

