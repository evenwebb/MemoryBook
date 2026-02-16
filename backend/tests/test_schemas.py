"""Tests for Pydantic schema validation."""
import pytest
from pydantic import ValidationError
from app.models.schemas import (
    TagCreate, CategoryCreate, NotesUpdate, SearchRequest
)


class TestTagCreate:
    def test_valid_tag(self):
        tag = TagCreate(name="birthday", tag_type="event")
        assert tag.name == "birthday"
        assert tag.tag_type == "event"

    def test_name_stripped(self):
        tag = TagCreate(name="  birthday  ")
        assert tag.name == "birthday"

    def test_blank_name_rejected(self):
        with pytest.raises(ValidationError):
            TagCreate(name="   ")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            TagCreate(name="")

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            TagCreate(name="x" * 101)

    def test_valid_tag_types(self):
        for tag_type in ["person", "event", "anniversary", "birthday", "custom"]:
            tag = TagCreate(name="test", tag_type=tag_type)
            assert tag.tag_type == tag_type

    def test_invalid_tag_type(self):
        with pytest.raises(ValidationError):
            TagCreate(name="test", tag_type="invalid")

    def test_none_tag_type_allowed(self):
        tag = TagCreate(name="test", tag_type=None)
        assert tag.tag_type is None


class TestCategoryCreate:
    def test_valid_category(self):
        cat = CategoryCreate(name="Photos", description="My photos", color="#ff0000")
        assert cat.name == "Photos"

    def test_name_stripped(self):
        cat = CategoryCreate(name="  Photos  ")
        assert cat.name == "Photos"

    def test_blank_name_rejected(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="   ")

    def test_valid_hex_color(self):
        cat = CategoryCreate(name="Test", color="#abcdef")
        assert cat.color == "#abcdef"

    def test_invalid_hex_color(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="Test", color="red")

    def test_invalid_hex_short(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="Test", color="#fff")

    def test_none_color_allowed(self):
        cat = CategoryCreate(name="Test", color=None)
        assert cat.color is None

    def test_description_max_length(self):
        with pytest.raises(ValidationError):
            CategoryCreate(name="Test", description="x" * 501)


class TestNotesUpdate:
    def test_valid_notes(self):
        notes = NotesUpdate(notes="Some notes about this image")
        assert notes.notes == "Some notes about this image"

    def test_notes_max_length(self):
        with pytest.raises(ValidationError):
            NotesUpdate(notes="x" * 10001)

    def test_notes_at_max(self):
        notes = NotesUpdate(notes="x" * 10000)
        assert len(notes.notes) == 10000


class TestSearchRequest:
    def test_defaults(self):
        req = SearchRequest()
        assert req.limit == 50
        assert req.offset == 0
        assert req.query is None

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            SearchRequest(limit=0)
        with pytest.raises(ValidationError):
            SearchRequest(limit=101)

    def test_offset_non_negative(self):
        with pytest.raises(ValidationError):
            SearchRequest(offset=-1)

    def test_query_max_length(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="x" * 501)
