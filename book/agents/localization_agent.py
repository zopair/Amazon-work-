"""Localization completeness and script-direction QA for approved translations."""
from __future__ import annotations

import unicodedata


ARABIC_RANGES = ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF),
                 (0xFB50, 0xFDFF), (0xFE70, 0xFEFF))


def _has_arabic(text: str) -> bool:
    return any(any(start <= ord(char) <= end for start, end in ARABIC_RANGES) for char in text)


def _has_latin(text: str) -> bool:
    return any(("A" <= char <= "Z") or ("a" <= char <= "z") for char in text)


def audit_locales(story: dict, expected_locales: list[str]) -> dict:
    """Fail closed on missing translations; never fabricate or machine-translate copy."""
    if not story.get("pages"):
        raise ValueError("Localization audit requires story pages")
    required_fields = ("title", "body", "parent_prompt")
    checks = []
    for page in story["pages"]:
        for field in required_fields:
            values = page.get(field)
            if not isinstance(values, dict):
                raise ValueError(f"Page {page['page']}: missing locale map for {field}")
            for locale in expected_locales:
                text = values.get(locale)
                if not isinstance(text, str) or not text.strip():
                    raise ValueError(f"Page {page['page']}: missing {field}.{locale}")
                if locale == "ar" and not _has_arabic(text):
                    raise ValueError(f"Page {page['page']}: {field}.ar has no Arabic-script characters")
                if locale == "en" and not _has_latin(text):
                    raise ValueError(f"Page {page['page']}: {field}.en has no Latin-script characters")
                checks.append({
                    "page": page["page"],
                    "field": field,
                    "locale": locale,
                    "direction": "rtl" if locale in ("ar", "he", "fa", "ur") else "ltr",
                    "unicode_nfc": unicodedata.normalize("NFC", text) == text,
                    "characters": len(text),
                })
    return {
        "status": "PASS",
        "page_count": len(story["pages"]),
        "locales": expected_locales,
        "checked_fields": len(checks),
        "direction": {locale: ("rtl" if locale in ("ar", "he", "fa", "ur") else "ltr")
                      for locale in expected_locales},
        "translation_mode": "approved_source_copy_validation_only",
        "automatic_translation_performed": False,
        "checks": checks,
    }
