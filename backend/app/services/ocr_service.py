import logging
import re
from typing import Dict, List

import pytesseract
from ..core.config import settings

logger = logging.getLogger("memorybook")


class OCRService:
    """Handle OCR processing using Tesseract"""

    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def extract_text(self, image_path: str) -> Dict[str, any]:
        """Extract text from image using OCR"""
        try:
            # Run OCR
            text = pytesseract.image_to_string(image_path, lang=settings.OCR_LANGUAGES)

            # Get confidence data
            data = pytesseract.image_to_data(image_path, lang=settings.OCR_LANGUAGES, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100.0  # Normalize to 0-1
            }
        except Exception as e:
            logger.error("OCR processing failed for %s: %s", image_path, e)
            return {
                'text': '',
                'confidence': 0.0
            }

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from OCR text"""
        dates = []
        # Common date patterns
        patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return dates

    def extract_names(self, text: str) -> List[str]:
        """Extract potential names from text (simple heuristic)"""
        lines = text.split('\n')
        names = []

        # Look for lines that might be names (capitalized words, 2-3 words)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            words = line.split()
            if 2 <= len(words) <= 3:
                # Check if all words start with capital letters and contain only letters
                if all(word[0].isupper() and word.isalpha() for word in words):
                    names.append(line)

        return names[:5]  # Return top 5 potential names
