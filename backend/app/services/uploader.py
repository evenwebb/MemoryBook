import os
import shutil
from pathlib import Path
from typing import List, Dict, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile
from ..core.config import settings
from ..services.image_processor import ImageProcessor
from ..services.ocr_service import OCRService
from ..services.tag_suggester import TagSuggester
from sqlalchemy.orm import Session
from ..models.database import Image, Category, Tag
from ..core.database import SessionLocal
from datetime import datetime


class MultiThreadedUploader:
    """Handle multi-threaded batch image uploads"""
    
    def __init__(self, db: Session, max_workers: int = 4):
        self.db = db
        self.db_factory = db.__class__  # Store session factory
        self.max_workers = max_workers
        self.image_processor = ImageProcessor()
        self.ocr_service = OCRService()
        self.tag_suggester = TagSuggester()
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file"""
        # Check extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not allowed"
        
        # Check file size (will be checked again after reading)
        return True, ""
    
    def process_single_image(self, file: UploadFile, upload_dir: str) -> Dict:
        """Process a single image upload - creates its own DB session for thread safety"""
        # Create a new database session for this thread
        thread_db = SessionLocal()
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(file)
            if not is_valid:
                return {
                    'success': False,
                    'filename': file.filename,
                    'error': error_msg
                }
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"{timestamp}_{Path(file.filename).stem}{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            os.makedirs(upload_dir, exist_ok=True)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > settings.MAX_UPLOAD_SIZE:
                os.remove(file_path)
                return {
                    'success': False,
                    'filename': file.filename,
                    'error': f"File size {file_size} exceeds maximum {settings.MAX_UPLOAD_SIZE}"
                }
            
            # Process image
            dimensions = self.image_processor.get_image_dimensions(file_path)
            if dimensions:
                self.image_processor.optimize_image(file_path)
            
            # Generate thumbnail
            thumbnail_filename = f"thumb_{unique_filename}"
            thumbnail_path = os.path.join(settings.THUMBNAIL_DIR, thumbnail_filename)
            thumbnail_generated = self.image_processor.generate_thumbnail(file_path, thumbnail_path)
            
            # Extract metadata
            exif_data = self.image_processor.extract_exif_data(file_path)
            
            # Create database record using thread-local session
            image = Image(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                thumbnail_path=thumbnail_path if thumbnail_generated else None,
                file_size=file_size,
                mime_type=file.content_type or "image/jpeg",
                width=dimensions[0] if dimensions else None,
                height=dimensions[1] if dimensions else None,
                exif_data=exif_data
            )
            
            thread_db.add(image)
            thread_db.flush()  # Get ID without committing
            
            # Process OCR in background (could be moved to background task)
            ocr_result = self.ocr_service.extract_text(file_path)
            if ocr_result['text']:
                image.ocr_text = ocr_result['text']
                image.ocr_processed = datetime.now()
                
                # Suggest tags and category
                extracted_dates = self.ocr_service.extract_dates(ocr_result['text'])
                extracted_names = self.ocr_service.extract_names(ocr_result['text'])
                suggested_tags = self.tag_suggester.suggest_tags(
                    ocr_result['text'],
                    extracted_dates,
                    extracted_names
                )
                suggested_category = self.tag_suggester.suggest_category(ocr_result['text'])
                
                # Store suggestions in image metadata (could be used for UI)
                if not image.exif_data:
                    image.exif_data = {}
                image.exif_data['suggested_tags'] = suggested_tags
                if suggested_category:
                    image.exif_data['suggested_category'] = suggested_category
                    
                    # Auto-apply suggested category
                    from ..models.database import Category
                    category = thread_db.query(Category).filter(
                        Category.name.ilike(f"%{suggested_category}%")
                    ).first()
                    if category and category not in image.categories:
                        image.categories.append(category)
            
            # Get data before commit
            image_id = image.id
            exif_data = image.exif_data
            
            # Commit this thread's changes
            thread_db.commit()
            
            return {
                'success': True,
                'filename': file.filename,
                'image_id': image_id,
                'exif_data': exif_data
            }
            
        except Exception as e:
            thread_db.rollback()
            return {
                'success': False,
                'filename': file.filename,
                'error': str(e)
            }
        finally:
            thread_db.close()
    
    def upload_batch(self, files: List[UploadFile], progress_callback: Callable = None) -> Dict:
        """Upload multiple files using thread pool"""
        upload_dir = settings.UPLOAD_DIR
        results = {
            'total': len(files),
            'successful': 0,
            'failed': 0,
            'images': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_image, file, upload_dir): file
                for file in files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                result = future.result()
                
                if result['success']:
                    results['successful'] += 1
                    # Database commit already handled in process_single_image
                else:
                    results['failed'] += 1
                
                results['images'].append({
                    'id': result.get('image_id'),
                    'filename': result['filename'],
                    'status': 'success' if result['success'] else 'failed',
                    'message': result.get('error'),
                    'exif_data': result.get('exif_data') if result['success'] else None
                })
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(results)
        
        return results

