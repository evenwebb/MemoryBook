"""Tests for the tag suggestion service."""
import pytest
from app.services.tag_suggester import TagSuggester


@pytest.fixture
def suggester():
    return TagSuggester()


class TestSuggestCategory:
    def test_receipt_detection(self, suggester):
        text = "TOTAL: $45.99\nTax: $3.50\nPayment: VISA"
        result = suggester.suggest_category(text)
        assert result == "receipts"

    def test_certificate_detection(self, suggester):
        text = "Certificate of Achievement\nAwarded to John Doe"
        result = suggester.suggest_category(text)
        assert result == "certificates"

    def test_school_detection(self, suggester):
        text = "Class of 2020\nStudent: Jane Smith\nGrade: A"
        result = suggester.suggest_category(text)
        assert result == "school photos"

    def test_no_match_returns_none(self, suggester):
        text = "Random text with no keywords"
        result = suggester.suggest_category(text)
        assert result is None

    def test_highest_score_wins(self, suggester):
        # More receipt keywords than certificate
        text = "Receipt for purchase\nTotal: $100\nTax included\nPayment received"
        result = suggester.suggest_category(text)
        assert result == "receipts"

    def test_empty_text(self, suggester):
        assert suggester.suggest_category("") is None


class TestSuggestTags:
    def test_birthday_keyword(self, suggester):
        result = suggester.suggest_tags("Happy Birthday to you!")
        assert "birthday" in result

    def test_anniversary_keyword(self, suggester):
        result = suggester.suggest_tags("Our wedding anniversary celebration")
        assert "anniversary" in result

    def test_year_extraction(self, suggester):
        result = suggester.suggest_tags("Photo from 2019")
        assert any("year-" in tag for tag in result)

    def test_name_tags(self, suggester):
        result = suggester.suggest_tags("", extracted_names=["John Smith"])
        assert "John Smith" in result

    def test_date_tags(self, suggester):
        result = suggester.suggest_tags("", extracted_dates=["01/15/2020"])
        assert any("month-" in tag for tag in result)

    def test_deduplication(self, suggester):
        result = suggester.suggest_tags(
            "birthday happy birthday",
            extracted_names=["Test Name"]
        )
        assert len(result) == len(set(result))

    def test_empty_text_no_crash(self, suggester):
        result = suggester.suggest_tags("")
        assert isinstance(result, list)


class TestExtractStructuredData:
    def test_date_extraction(self, suggester):
        data = suggester.extract_structured_data("Date: 01/15/2020")
        assert len(data['dates']) > 0

    def test_amount_extraction(self, suggester):
        data = suggester.extract_structured_data("Total: $45.99")
        assert len(data['amounts']) > 0

    def test_empty_text(self, suggester):
        data = suggester.extract_structured_data("")
        assert data['dates'] == []
        assert data['amounts'] == []
