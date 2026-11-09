"""Adapter from the approved manuscript to a stable machine-readable story contract."""
from __future__ import annotations

from .contracts import validate_page_records
from ..content import PAGES


def build_story() -> dict:
    records = []
    for number, row in enumerate(PAGES, start=1):
        en_title, en_body, ar_title, ar_body, parent_en, parent_ar, art_key = row
        records.append({
            "page": number,
            "title": {"en": en_title, "ar": ar_title},
            "body": {"en": en_body, "ar": ar_body},
            "parent_prompt": {"en": parent_en, "ar": parent_ar},
            "scene_key": art_key,
        })
    validate_page_records(records, expected_pages=24)
    return {
        "schema_version": "1.0",
        "source": "book.content.PAGES",
        "page_count": len(records),
        "locales": ["en", "ar"],
        "pages": records,
    }
