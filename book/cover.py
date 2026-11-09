"""KDP paperback full-wrap cover geometry and deterministic PDF renderer."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLEED_IN = 0.125
SPINE_FACTORS = {
    "premium_color": 0.002347,
    "standard_color": 0.002252,
    "black_white_white": 0.002252,
    "black_white_cream": 0.0025,
}


def calculate_cover_geometry(profile: dict, page_count: int) -> dict:
    if page_count < 24 or page_count % 2:
        raise ValueError("KDP paperback page count must be even and at least 24")
    trim_w = float(profile["trim_width_in"])
    trim_h = float(profile["trim_height_in"])
    bleed = float(profile.get("bleed_outside_in", BLEED_IN))
    if abs(bleed - BLEED_IN) > 1e-6:
        raise ValueError("This paperback template requires KDP's 0.125-inch bleed")
    color_mode = profile["color_mode"]
    if color_mode not in SPINE_FACTORS:
        raise ValueError(f"Unsupported KDP paper profile: {color_mode}")
    factor = SPINE_FACTORS[color_mode]
    spine = page_count * factor
    width = bleed + trim_w + spine + trim_w + bleed
    height = bleed + trim_h + bleed
    dpi = int(profile.get("dpi", 300))
    return {
        "binding": "paperback",
        "page_count": page_count,
        "paper_profile": color_mode,
        "spine_factor_in_per_page": factor,
        "spine_width_in": round(spine, 6),
        "trim_width_in": trim_w,
        "trim_height_in": trim_h,
        "bleed_in": bleed,
        "cover_width_in": round(width, 6),
        "cover_height_in": round(height, 6),
        "cover_width_px_at_dpi": round(width * dpi),
        "cover_height_px_at_dpi": round(height * dpi),
        "spine_text_allowed": page_count > 79,
        "dpi": dpi,
        "source": "Amazon KDP Create a Paperback Cover published paperback formula",
    }


def _cover_html(manifest: dict, geometry: dict, hero_uri: str) -> str:
    w = geometry["cover_width_in"]
    h = geometry["cover_height_in"]
    bleed = geometry["bleed_in"]
    trim_w = geometry["trim_width_in"]
    trim_h = geometry["trim_height_in"]
    spine = geometry["spine_width_in"]
    back_x = bleed
    spine_x = bleed + trim_w
    front_x = spine_x + spine
    title_en = html.escape(manifest["title"]["en"])
    title_ar = html.escape(manifest["title"]["ar"])
    hero = html.escape(hero_uri, quote=True)
    # The barcode reservation is intentionally blank for KDP to place its barcode.
    back_text = (
        "A joyful little journey about colors, friendship, and discovery. "
        "Read together, notice the world, and share a new moment on every page."
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<style>
@page {{ size: {w}in {h}in; margin: 0 }}
* {{ box-sizing: border-box }}
html, body {{ margin:0; padding:0; width:{w}in; height:{h}in; overflow:hidden }}
.sheet {{ position:relative; width:{w}in; height:{h}in; background:#fffaf0; overflow:hidden }}
.panel {{ position:absolute; top:0; height:{h}in; overflow:hidden }}
.back {{ left:0; width:{trim_w+bleed}in; background:#f3ead7 }}
.front {{ left:{front_x}in; width:{trim_w+bleed}in; background:#fff4d9 }}
.back-copy {{ position:absolute; left:{back_x+0.375}in; top:0.75in; width:{trim_w-0.75}in;
 font:14pt/1.45 sans-serif; color:#355064 }}
.back-copy .ar {{ direction:rtl; text-align:right; font-size:15pt }}
.barcode {{ position:absolute; left:{back_x+trim_w-2.375}in; bottom:0.375in;
 width:2in; height:1.2in; background:#fff; }}
.front img {{ position:absolute; left:0.25in; top:1.35in; width:{trim_w-0.5}in;
 height:4.2in; object-fit:contain }}
.front-title {{ position:absolute; left:0.375in; right:0.375in; top:0.42in;
 text-align:center; color:#244e68; font:bold 25pt/1.15 sans-serif }}
.front-ar {{ display:block; direction:rtl; font-size:23pt; margin-top:0.12in }}
.front-sub {{ position:absolute; left:0.4in; right:0.4in; bottom:0.52in;
 text-align:center; color:#355064; font:12pt/1.3 sans-serif }}
.spine {{ position:absolute; left:{spine_x}in; top:0; width:{spine}in; height:{h}in;
 background:#e5b95f }}
</style></head><body><main class="sheet">
<section class="panel back"><div class="back-copy">
<p>{back_text}</p><p class="ar" lang="ar">رحلة مرحة بين الألوان والصداقة والاكتشاف، في حكاية تُقرأ معاً وتفتح باب الحديث والخيال.</p>
</div><div class="barcode"></div></section>
<div class="spine"></div>
<section class="panel front"><div class="front-title">{title_en}
<span class="front-ar" lang="ar">{title_ar}</span></div>
<img src="{hero}" alt="The Happy Little Train illustration"/>
<div class="front-sub">A bilingual story for little readers · Ages 3–6</div></section>
</main></body></html>"""


def build_cover(manifest_path: Path, profile_path: Path, artwork_dir: Path,
                output_path: Path, page_count: int = 24) -> dict:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject
    from weasyprint import HTML

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = json.loads(profile_path.read_text(encoding="utf-8"))
    profile = profiles["profiles"][manifest["kdp_profile"]]
    geometry = calculate_cover_geometry(profile, page_count)
    hero = artwork_dir / "page-01.svg"
    if not hero.is_file():
        raise FileNotFoundError(f"Missing cover hero artwork: {hero}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=_cover_html(manifest, geometry, hero.resolve().as_uri()),
         base_url=str(ROOT)).write_pdf(str(output_path))
    reader = PdfReader(str(output_path))
    if len(reader.pages) != 1:
        raise RuntimeError(f"Cover PDF must contain exactly one page; got {len(reader.pages)}")
    page = reader.pages[0]
    width_pt = geometry["cover_width_in"] * 72
    height_pt = geometry["cover_height_in"] * 72
    page.mediabox = RectangleObject([0, 0, width_pt, height_pt])
    page.bleedbox = RectangleObject([0, 0, width_pt, height_pt])
    page.trimbox = RectangleObject([
        BLEED_IN * 72, BLEED_IN * 72,
        (BLEED_IN + 2 * geometry["trim_width_in"] + geometry["spine_width_in"]) * 72,
        (BLEED_IN + geometry["trim_height_in"]) * 72,
    ])
    writer = PdfWriter()
    writer.add_page(page)
    writer.add_metadata({
        "/Title": f"{manifest['title']['en']} — Paperback Full-Wrap Cover",
        "/Subject": "KDP paperback cover geometry; verify against the final KDP cover template",
    })
    with output_path.with_suffix(".tmp.pdf").open("wb") as stream:
        writer.write(stream)
    output_path.with_suffix(".tmp.pdf").replace(output_path)
    report = {**geometry, "status": "PASS", "pdf": str(output_path),
              "page_count_pdf": len(reader.pages),
              "barcode_reserved": True,
              "spine_text_rendered": False,
              "kdp_status": "STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED"}
    report_path = output_path.parent / "cover-preflight.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="config/books/happy-little-train.json")
    parser.add_argument("--profiles", default="config/kdp_profiles.json")
    parser.add_argument("--artwork", default="assets/artwork")
    parser.add_argument("--output", default="dist/the-happy-little-train-cover.pdf")
    parser.add_argument("--pages", type=int, default=24)
    args = parser.parse_args()
    report = build_cover(ROOT / args.manifest, ROOT / args.profiles,
                         ROOT / args.artwork, ROOT / args.output, args.pages)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
