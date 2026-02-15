import logging
import os
from PIL import Image as PILImage, ImageFile
from pathlib import Path
from typing import Tuple, Optional, Dict
import hashlib
from ..core.config import settings

logger = logging.getLogger("memorybook")

# Allow loading truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Register HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


class ImageProcessor:
    """Handle image processing, thumbnail generation, and optimisation"""

    @staticmethod
    def generate_thumbnail(image_path: str, output_path: str, size: Optional[Tuple[int, int]] = None) -> bool:
        """Generate thumbnail from image with optimised performance"""
        try:
            size = size or settings.THUMBNAIL_SIZE

            # Create output directory once
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with PILImage.open(image_path) as img:
                # Auto-orient based on EXIF
                try:
                    from PIL.ExifTags import TAGS
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            if TAGS.get(tag) == 'Orientation':
                                if value == 3:
                                    img = img.rotate(180, expand=True)
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                except (AttributeError, KeyError, IndexError) as e:
                    logger.debug("Could not read EXIF orientation for %s: %s", image_path, e)

                # Convert to RGB if necessary (optimised)
                if img.mode not in ('RGB', 'L'):
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = PILImage.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    else:
                        img = img.convert('RGB')

                # Use draft mode for faster thumbnail generation on large images
                if hasattr(img, 'draft'):
                    img.draft('RGB', size)

                # Create thumbnail maintaining aspect ratio
                img.thumbnail(size, PILImage.Resampling.LANCZOS)

                # Save with progressive JPEG for better web performance
                img.save(output_path, 'JPEG', quality=85, optimize=True, progressive=True)
                return True
        except Exception as e:
            logger.error("Error generating thumbnail for %s: %s", image_path, e)
            return False

    @staticmethod
    def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int]]:
        """Get image dimensions"""
        try:
            with PILImage.open(image_path) as img:
                return img.size
        except Exception as e:
            logger.warning("Could not read image dimensions for %s: %s", image_path, e)
            return None

    @staticmethod
    def optimise_image(image_path: str, max_size: Optional[Tuple[int, int]] = None) -> bool:
        """Optimise image by resizing if too large"""
        try:
            max_size = max_size or settings.MAX_IMAGE_SIZE
            with PILImage.open(image_path) as img:
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
                    img.save(image_path, optimize=True, quality=90)
                    logger.info("Optimised oversized image: %s", image_path)
                return True
        except Exception as e:
            logger.warning("Could not optimise image %s: %s", image_path, e)
            return False

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate MD5 hash of file for duplicate detection with larger chunks"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # Use larger chunks for better performance
            for chunk in iter(lambda: f.read(65536), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def extract_exif_data(image_path: str) -> Optional[Dict]:
        """Extract EXIF metadata from image"""
        try:
            with PILImage.open(image_path) as img:
                exif_data = img.getexif()
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        tag = PILImage.ExifTags.TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = str(value)
                    return exif_dict
        except Exception as e:
            logger.debug("Could not extract EXIF data from %s: %s", image_path, e)
        return None
