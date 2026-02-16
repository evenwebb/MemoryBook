import logging
import re
from typing import List, Optional
from dateutil import parser as date_parser

logger = logging.getLogger("memorybook")


class TagSuggester:
    """Suggest tags and categories based on OCR text and patterns"""

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        'receipts': ['receipt', 'total', 'subtotal', 'tax', 'payment', 'change', 'cash', 'card', 'invoice', 'purchase'],
        'certificates': ['certificate', 'certified', 'award', 'achievement', 'diploma', 'degree', 'honor', 'recognition'],
        'school photos': ['school', 'class', 'grade', 'student', 'teacher', 'academy', 'education', 'yearbook'],
    }

    # Event keywords
    EVENT_KEYWORDS = {
        'anniversary': ['anniversary', 'wedding', 'married', 'years together'],
        'birthday': ['birthday', 'born', 'turned', 'years old', 'happy birthday'],
    }

    def suggest_tags(self, ocr_text: str, extracted_dates: List[str] = None, extracted_names: List[str] = None) -> List[str]:
        """Suggest tags based on OCR text"""
        suggestions = []
        text_lower = ocr_text.lower()

        # Add extracted names as person tags
        if extracted_names:
            suggestions.extend(extracted_names)

        # Check for event keywords
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                suggestions.append(event_type)

        # Extract years (for anniversaries/birthdays)
        years = re.findall(r'\b(19|20)\d{2}\b', ocr_text)
        if years:
            suggestions.extend([f"year-{year}" for year in set(years)])

        # Extract dates and suggest date-based tags
        if extracted_dates:
            for date_str in extracted_dates[:3]:  # Limit to 3 dates
                try:
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    # Suggest month-based tags
                    month_name = parsed_date.strftime('%B').lower()
                    suggestions.append(f"month-{month_name}")
                except (ValueError, OverflowError) as e:
                    logger.debug("Could not parse date '%s': %s", date_str, e)

        return list(set(suggestions))  # Remove duplicates

    def suggest_category(self, ocr_text: str) -> Optional[str]:
        """Suggest category based on OCR text"""
        text_lower = ocr_text.lower()
        category_scores = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            # Return category with highest score
            return max(category_scores.items(), key=lambda x: x[1])[0]

        return None

    def extract_structured_data(self, ocr_text: str) -> dict:
        """Extract structured data from OCR text"""
        data = {
            'dates': [],
            'names': [],
            'amounts': [],
            'locations': []
        }

        # Extract dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
        ]
        for pattern in date_patterns:
            data['dates'].extend(re.findall(pattern, ocr_text))

        # Extract monetary amounts
        amount_pattern = r'\$?\d+\.?\d{0,2}'
        data['amounts'] = re.findall(amount_pattern, ocr_text)

        return data
