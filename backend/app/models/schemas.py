import re
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime

VALID_TAG_TYPES = {"person", "event", "anniversary", "birthday", "custom"}


class ImageBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str


class ImageCreate(ImageBase):
    pass


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    tag_type: Optional[str] = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tag name cannot be blank")
        return v

    @field_validator("tag_type")
    @classmethod
    def validate_tag_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TAG_TYPES:
            raise ValueError(f"tag_type must be one of {VALID_TAG_TYPES}")
        return v


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category name cannot be blank")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^#[0-9a-fA-F]{6}$", v):
            raise ValueError("Color must be a valid hex code (e.g. #ff0000)")
        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ImageResponse(ImageBase):
    model_config = ConfigDict(from_attributes=True)

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


class ImageUploadResponse(BaseModel):
    id: Optional[int] = None
    filename: str
    status: str
    message: Optional[str] = None
    exif_data: Optional[dict] = None


class BatchUploadResponse(BaseModel):
    total: int
    successful: int
    failed: int
    images: List[ImageUploadResponse]


class NotesUpdate(BaseModel):
    notes: str = Field(..., max_length=10000)


class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=500)
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class OCRResult(BaseModel):
    text: str
    confidence: float
    suggested_tags: List[str] = []
    suggested_category: Optional[str] = None
