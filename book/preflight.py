#!/usr/bin/env python3
"""Strict KDP-oriented structural preflight; not a substitute for KDP Previewer."""
from pathlib import Path
import json
import sys
from pypdf import PdfReader
from pypdf.generic import ContentStream

PDF = Path(sys.argv[1] if len(sys.argv) > 1 else "dist/the-happy-little-train-print.pdf")
EXPECTED = (8.625 * 72, 8.75 * 72)
TRIM = (8.5 * 72, 8.5 * 72)
ARABIC_RANGES = ((0x0600,0x06FF),(0x0750,0x077F),(0x08A0,0x08FF),(0xFB50,0xFDFF),(0xFE70,0xFEFF))


def has_arabic(text: str) -> bool:
    return any(any(a <= ord(ch) <= b for a,b in ARABIC_RANGES) for ch in text)


def page_artwork_diagnostics(page, reader) -> tuple[bool, int, int, list[str]]:
    """Recognize raster XObjects, SVG form XObjects, or inline vector drawings."""
    resources = page.get("/Resources")
    xobject_types = []
    if resources:
        xobjects = resources.get_object().get("/XObject")
        if xobjects:
            xobject_types = [str(obj.get_object().get("/Subtype"))
                             for obj in xobjects.get_object().values()]
            if any(kind in ("/Image", "/Form") for kind in xobject_types):
                return True, 0, 0, xobject_types
    contents = page.get("/Contents")
    if not contents:
        return False, 0, 0, xobject_types
    stream = ContentStream(contents, reader)
    path_ops = {b"m", b"l", b"c", b"v", b"y", b"h", b"re",
                b"S", b"s", b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*"}
    path_count = sum(1 for _, operator in stream.operations if operator in path_ops)
    byte_count = len(stream.get_data())
    return path_count >= 10, path_count, byte_count, xobject_types


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

    page_results = []
    for i, page in enumerate(reader.pages, 1):
        m, t, b = page.mediabox, page.trimbox, page.bleedbox
        media = [round(float(m.width), 3), round(float(m.height), 3)]
        trim = [round(float(t.width), 3), round(float(t.height), 3)]
        bleed = [round(float(b.width), 3), round(float(b.height), 3)]
        if abs(media[0]-EXPECTED[0]) > .25 or abs(media[1]-EXPECTED[1]) > .25:
            raise SystemExit(f"FAIL page {i}: media box {media}")
        if abs(trim[0]-TRIM[0]) > .25 or abs(trim[1]-TRIM[1]) > .25:
            raise SystemExit(f"FAIL page {i}: trim box is not 612x612pt")
        if abs(bleed[0]-EXPECTED[0]) > .25 or abs(bleed[1]-EXPECTED[1]) > .25:
            raise SystemExit(f"FAIL page {i}: bleed box mismatch")

        page_text = page.extract_text() or ""
        parent_prompt = "Mom's Turn:" in page_text
        arabic_present = has_arabic(page_text)
        if not parent_prompt:
            raise SystemExit(f"FAIL page {i}: missing Mom's Turn prompt")
        if not arabic_present:
            raise SystemExit(f"FAIL page {i}: Arabic text missing from text layer")
        if not page_text.strip():
            raise SystemExit(f"FAIL page {i}: empty text layer")

        artwork_ok, path_count, content_bytes, xobject_types = page_artwork_diagnostics(page, reader)
        if not artwork_ok:
            raise SystemExit(
                f"FAIL page {i}: original artwork not embedded "
                f"(XObjects={xobject_types}, vector_path_ops={path_count}, content_bytes={content_bytes})"
            )

        resources = page.get("/Resources")
        fonts = resources.get_object().get("/Font") if resources else None
        if not fonts or not fonts.get_object():
            raise SystemExit(f"FAIL page {i}: no font resources")
        embedded_count = sum(1 for ref in fonts.get_object().values() if embedded_font(ref))
        if embedded_count < 1:
            raise SystemExit(f"FAIL page {i}: no embedded font program found")

        page_results.append({
            "page": i, "media_box_pt": media, "trim_box_pt": trim,
            "bleed_box_pt": bleed, "arabic_text": arabic_present,
            "parent_prompt": parent_prompt, "artwork": "PASS",
            "vector_path_ops": path_count, "artwork_xobjects": xobject_types,
            "embedded_font_resources": embedded_count,
        })

    result = {
        "status": "PASS",
        "pdf": str(PDF),
        "pdf_size_bytes": PDF.stat().st_size,
        "page_count": len(reader.pages),
        "media_box_pt": list(EXPECTED),
        "trim_box_pt": list(TRIM),
        "bleed_box_pt": list(EXPECTED),
        "checks": {
            "page_count": "PASS", "media_trim_bleed": "PASS",
            "arabic_english_text": "PASS", "parent_prompts": "PASS",
            "vector_or_raster_artwork": "PASS", "embedded_fonts": "PASS",
        },
        "kdp_status": "STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED",
        "pages": page_results,
    }
    report_dir = PDF.parent / "swarm"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "pdf-preflight.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    swarm_report_path = report_dir / "swarm-report.json"
    if swarm_report_path.is_file():
        swarm_report = json.loads(swarm_report_path.read_text(encoding="utf-8"))
        swarm_report["structural_status"] = "PASS"
        swarm_report["pdf_preflight_status"] = "PASS"
        swarm_report["kdp_status"] = result["kdp_status"]
        swarm_report["pdf_size_bytes"] = result["pdf_size_bytes"]
        swarm_report_path.write_text(
            json.dumps(swarm_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("PASS: 24 pages; media/trim/bleed geometry; Arabic + English text; Mom's Turn; artwork and embedded fonts.")
    print("Machine-readable report: dist/swarm/pdf-preflight.json")
    print("NOTE: visual proofing and KDP Print Previewer approval are still required.")


if __name__ == "__main__":
    main()
