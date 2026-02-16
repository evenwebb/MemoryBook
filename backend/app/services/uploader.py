import logging
import os
import shutil
from pathlib import Path
from typing import List, Dict, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from fastapi import UploadFile
from ..core.config import settings
from ..services.image_processor import ImageProcessor
from ..services.ocr_service import OCRService
from ..services.tag_suggester import TagSuggester
from sqlalchemy.orm import Session
from ..models.database import Image, Category, Tag
from ..core.database import SessionLocal
from datetime import datetime

logger = logging.getLogger("memorybook")


def _run_background_ocr(image_id: int, file_path: str) -> None:
    """Run OCR processing in a background thread after upload completes."""
    db = SessionLocal()
    try:
        ocr_service = OCRService()
        tag_suggester = TagSuggester()

        ocr_result = ocr_service.extract_text(file_path)
        if not ocr_result['text']:
            return

        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            logger.warning("Image %d not found for background OCR", image_id)
            return

        image.ocr_text = ocr_result['text']
        image.ocr_processed = datetime.now()

        # Suggest tags and category
        extracted_dates = ocr_service.extract_dates(ocr_result['text'])
        extracted_names = ocr_service.extract_names(ocr_result['text'])
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

            # Auto-apply suggested category
            category = db.query(Category).filter(
                Category.name.ilike(f"%{suggested_category}%")
            ).first()
            if category and category not in image.categories:
                image.categories.append(category)

        db.commit()
        logger.info("Background OCR completed for image %d", image_id)
    except Exception as e:
        db.rollback()
        logger.error("Background OCR failed for image %d: %s", image_id, e)
    finally:
        db.close()


class MultiThreadedUploader:
    """Handle multi-threaded batch image uploads"""

    def __init__(self, db: Session, max_workers: int = 4):
        self.db = db
        self.max_workers = max_workers
        self.image_processor = ImageProcessor()

    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if not file.filename:
            return False, "No filename provided"

        # Check extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not allowed"

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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_ext = Path(file.filename).suffix.lower()
            safe_stem = Path(file.filename).stem.replace(" ", "_")[:100]
            unique_filename = f"{timestamp}_{safe_stem}{file_ext}"
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
                self.image_processor.optimise_image(file_path)

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
            thread_db.commit()

            image_id = image.id
            result_exif = image.exif_data

            # Schedule OCR as a background task (non-blocking)
            ocr_thread = threading.Thread(
                target=_run_background_ocr,
                args=(image_id, file_path),
                daemon=True,
            )
            ocr_thread.start()

            logger.info("Uploaded image %s (id=%d)", file.filename, image_id)

            return {
                'success': True,
                'filename': file.filename,
                'image_id': image_id,
                'exif_data': result_exif
            }

        except Exception as e:
            thread_db.rollback()
            logger.error("Failed to upload %s: %s", file.filename, e)
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

        logger.info("Starting batch upload of %d files", len(files))

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

        logger.info(
            "Batch upload complete: %d/%d successful",
            results['successful'], results['total']
        )
        return results
