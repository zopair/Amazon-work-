#!/usr/bin/env python3
"""Strict KDP-oriented structural preflight. Does not replace KDP Previewer."""
from pathlib import Path
import sys
from pypdf import PdfReader

PDF = Path(sys.argv[1] if len(sys.argv) > 1 else "dist/the-happy-little-train-print.pdf")
EXPECTED = (8.625 * 72, 8.75 * 72)
TRIM = (8.5 * 72, 8.5 * 72)
ARABIC_RANGES = ((0x0600,0x06FF),(0x0750,0x077F),(0x08A0,0x08FF),(0xFB50,0xFDFF),(0xFE70,0xFEFF))

def has_arabic(text: str) -> bool:
    return any(any(a <= ord(ch) <= b for a,b in ARABIC_RANGES) for ch in text)

def page_has_artwork(page) -> bool:
    resources = page.get("/Resources")
    if not resources:
        return False
    xobjects = resources.get_object().get("/XObject")
    if not xobjects:
        return False
    return any(obj.get_object().get("/Subtype") == "/Image" for obj in xobjects.get_object().values())

def embedded_font(font) -> bool:
    font = font.get_object()
    descriptor = font.get("/FontDescriptor")
    if descriptor:
        d = descriptor.get_object()
        return any(d.get(k) for k in ("/FontFile", "/FontFile2", "/FontFile3"))
    descendants = font.get("/DescendantFonts")
    if descendants:
        return any(embedded_font(item) for item in descendants.get_object())
    return False

def main():
    if not PDF.is_file() or PDF.stat().st_size < 20_000:
        raise SystemExit(f"FAIL: missing or implausibly small PDF: {PDF}")
    reader = PdfReader(str(PDF))
    if len(reader.pages) != 24:
        raise SystemExit(f"FAIL: expected 24 pages, got {len(reader.pages)}")
    for i, page in enumerate(reader.pages, 1):
        m, t, b = page.mediabox, page.trimbox, page.bleedbox
        if abs(float(m.width)-EXPECTED[0]) > .25 or abs(float(m.height)-EXPECTED[1]) > .25:
            raise SystemExit(f"FAIL page {i}: media box {float(m.width):.2f}x{float(m.height):.2f}pt")
        if abs(float(t.width)-TRIM[0]) > .25 or abs(float(t.height)-TRIM[1]) > .25:
            raise SystemExit(f"FAIL page {i}: trim box is not 612x612pt")
        if abs(float(b.width)-EXPECTED[0]) > .25 or abs(float(b.height)-EXPECTED[1]) > .25:
            raise SystemExit(f"FAIL page {i}: bleed box mismatch")
        text = page.extract_text() or ""
        if "Mom's Turn:" not in text:
            raise SystemExit(f"FAIL page {i}: missing Mom's Turn prompt")
        if not has_arabic(text):
            raise SystemExit(f"FAIL page {i}: Arabic text missing from text layer")
        if not text.strip():
            raise SystemExit(f"FAIL page {i}: empty text layer")
        if not page_has_artwork(page):
            raise SystemExit(f"FAIL page {i}: original artwork image not embedded")
        resources = page.get("/Resources")
        fonts = resources.get_object().get("/Font") if resources else None
        if not fonts or not fonts.get_object():
            raise SystemExit(f"FAIL page {i}: no font resources")
        if not any(embedded_font(ref) for ref in fonts.get_object().values()):
            raise SystemExit(f"FAIL page {i}: no embedded font program found")
    print("PASS: 24 pages; KDP media/trim/bleed geometry; Arabic + English text; Mom's Turn; embedded artwork and fonts.")
    print("NOTE: visual proofing and KDP Print Previewer approval are still required.")

if __name__ == "__main__":
    main()
