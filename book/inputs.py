"""Artwork gate and machine-readable report for raster and vector assets."""
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET
from .content import PAGES

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets" / "artwork"
MIN_W, MIN_H = 2588, 1716


def svg_dimensions(path: Path) -> tuple[int, int]:
    root = ET.parse(path).getroot()
    if not root.tag.endswith("svg"):
        raise ValueError("Root element is not SVG")
    def px(value):
        value = str(value).strip().lower().removesuffix("px")
        return int(float(value))
    width, height = px(root.attrib["width"]), px(root.attrib["height"])
    viewbox = root.attrib.get("viewBox", "").replace(",", " ").split()
    if len(viewbox) != 4 or float(viewbox[2]) <= 0 or float(viewbox[3]) <= 0:
        raise ValueError("SVG requires a valid positive viewBox")
    return width, height


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="dist/artwork-preflight.json")
    args = parser.parse_args()
    results = []
    for n in range(1, 25):
        matches = [ART / f"page-{n:02d}{s}" for s in (".svg", ".png", ".jpg", ".jpeg", ".webp")]
        path = next((x for x in matches if x.is_file()), None)
        if path is None:
            results.append({"page": n, "status": "missing", "expected": f"page-{n:02d}.svg/.png/.jpg/.webp"})
            continue
        try:
            if path.suffix.lower() == ".svg":
                w, h = svg_dimensions(path)
                ok = w >= MIN_W and h >= MIN_H
                mode, resolution = "VECTOR", "resolution-independent"
            else:
                try:
                    from PIL import Image
                except ImportError as exc:
                    raise RuntimeError("Pillow is required only when raster artwork is supplied; SVG is dependency-free") from exc
                with Image.open(path) as im:
                    w, h, mode = im.width, im.height, im.mode
                    ok = w >= MIN_W and h >= MIN_H and mode in ("RGB", "RGBA")
                resolution = "raster-300dpi-target"
            results.append({"page": n, "status": "ready" if ok else "invalid",
                             "file": path.name, "width": w, "height": h,
                             "mode": mode, "resolution": resolution,
                             "minimum": [MIN_W, MIN_H]})
        except Exception as exc:
            results.append({"page": n, "status": "invalid", "file": path.name, "error": str(exc)})
    report = {"book_pages": len(PAGES), "artwork_ready": sum(x["status"] == "ready" for x in results),
              "artwork_required": 24, "minimum_raster_dpi": 300, "vector_allowed": True, "pages": results}
    out = ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(PAGES) != 24 or report["artwork_ready"] != 24:
        raise SystemExit("Artwork gate failed: no print-ready PDF will be published.")


if __name__ == "__main__":
    main()
