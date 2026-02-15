from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

# Association tables for many-to-many relationships
image_tags = Table(
    'image_tags',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_image_tags_tag_id', 'tag_id'),
)

image_categories = Table(
    'image_categories',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_image_categories_category_id', 'category_id'),
)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    original_filename = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    upload_date = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Metadata
    exif_data = Column(JSON, nullable=True)
    ocr_text = Column(Text, nullable=True)
    ocr_processed = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    rotation = Column(Integer, default=0)  # 0, 90, 180, 270

    # Dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # Relationships
    tags = relationship(
        "Tag", secondary=image_tags, back_populates="images",
        lazy="joined", passive_deletes=True,
    )
    categories = relationship(
        "Category", secondary=image_categories, back_populates="images",
        lazy="joined", passive_deletes=True,
    )

    __table_args__ = (
        Index('ix_images_upload_date', 'upload_date'),
        Index('ix_images_original_filename', 'original_filename'),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    images = relationship("Image", secondary=image_categories, back_populates="categories", passive_deletes=True)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    tag_type = Column(String, nullable=True)  # 'person', 'event', 'anniversary', 'birthday', 'custom'
    created_at = Column(DateTime, server_default=func.now())

    images = relationship("Image", secondary=image_tags, back_populates="tags", passive_deletes=True)
