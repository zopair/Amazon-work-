"""Standard-library validation shared by the deterministic agents."""
from __future__ import annotations


def validate_page_records(records: list[dict], expected_pages: int) -> None:
    if len(records) != expected_pages:
        raise ValueError(f"Expected {expected_pages} pages; found {len(records)}")
    required_locales = ("en", "ar")
    for expected_number, record in enumerate(records, start=1):
        if record.get("page") != expected_number:
            raise ValueError(f"Page sequence error at position {expected_number}")
        for field in ("title", "body", "parent_prompt"):
            value = record.get(field)
            if not isinstance(value, dict):
                raise ValueError(f"Page {expected_number}: {field} must be an object")
            for locale in required_locales:
                text = value.get(locale)
                if not isinstance(text, str) or not text.strip():
                    raise ValueError(f"Page {expected_number}: missing {field}.{locale}")
        if not isinstance(record.get("scene_key"), str) or not record["scene_key"].strip():
            raise ValueError(f"Page {expected_number}: scene_key is required")
