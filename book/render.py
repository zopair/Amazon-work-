#!/usr/bin/env python3
"""Render the approved bilingual book with WeasyPrint/Pango and original artwork."""
from __future__ import annotations
import argparse, html
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from weasyprint import HTML, CSS
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from .content import PAGES

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "assets" / "artwork"
OUT = ROOT / "dist" / "the-happy-little-train-print.pdf"
PAGE_W, PAGE_H = 8.625, 8.75
ART_H = 5.72
DPI = 300


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def artwork_for(index: int) -> Path:
    for suffix in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
        candidate = ART_DIR / f"page-{index:02d}{suffix}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Missing original artwork for page {index:02d}; expected page-{index:02d}.svg/.png/.jpg/.webp")


def validate_artwork() -> list[Path]:
    if len(PAGES) != 24:
        raise RuntimeError(f"Expected 24 approved pages, got {len(PAGES)}")
    paths = [artwork_for(i) for i in range(1, 25)]
    min_w, min_h = round(PAGE_W * DPI), round(ART_H * DPI)
    for i, path in enumerate(paths, 1):
        if path.suffix.lower() == ".svg":
            root = ET.parse(path).getroot()
            if not root.tag.endswith("svg"):
                raise ValueError(f"Page {i:02d}: invalid SVG root")
            w = int(float(root.attrib["width"].removesuffix("px")))
            h = int(float(root.attrib["height"].removesuffix("px")))
            if w < min_w or h < min_h:
                raise ValueError(f"Page {i:02d} SVG canvas is {w}x{h}; needs at least {min_w}x{min_h}")
        else:
            with Image.open(path) as im:
                w, h = im.size
                if w < min_w or h < min_h:
                    raise ValueError(f"Page {i:02d} artwork is {w}x{h}px; needs at least {min_w}x{min_h}px for 300 DPI at placed size")
                if im.mode not in ("RGB", "RGBA"):
                    raise ValueError(f"Page {i:02d} artwork must be RGB/RGBA, got {im.mode}")
    return paths


def make_html(paths: list[Path]) -> str:
    pages = []
    for n, (row, art) in enumerate(zip(PAGES, paths), 1):
        et, eb, at, ab, me, ma, kind = row
        art_uri = art.resolve().as_uri()
        pages.append(f"""
        <section class="page" id="page-{n:02d}">
          <div class="art"><img src="{art_uri}" alt="Original illustration for page {n}"></div>
          <div class="copy">
            <div class="english"><h1>{esc(et)}</h1><p>{esc(eb)}</p></div>
            <div class="arabic" lang="ar" dir="rtl"><h2>{esc(at)}</h2><p>{esc(ab)}</p></div>
            <div class="mom">
              <div class="mom-en"><b>Mom's Turn:</b> {esc(me)}</div>
              <div class="mom-ar" lang="ar" dir="rtl"><b>دور الأم:</b> {esc(ma)}</div>
            </div>
          </div>
        </section>""")
    return "<!doctype html><html lang='en'><head><meta charset='utf-8'></head><body>" + "".join(pages) + "</body></html>"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(OUT))
    args = parser.parse_args()
    artwork = validate_artwork()
    css = ROOT / "book" / "templates" / "book.css"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=make_html(artwork), base_url=str(ROOT)).write_pdf(
        str(output), stylesheets=[CSS(filename=str(css))],
        presentational_hints=True, optimize_images=True,
    )
    reader = PdfReader(str(output))
    writer = PdfWriter()
    trim_w = trim_h = 8.5 * 72
    media_w, media_h = PAGE_W * 72, PAGE_H * 72
    for page_no, page in enumerate(reader.pages, 1):
        x0 = 0 if page_no % 2 else 0.125 * 72
        page.mediabox = RectangleObject([0, 0, media_w, media_h])
        page.bleedbox = RectangleObject([0, 0, media_w, media_h])
        page.trimbox = RectangleObject([x0, 0.125 * 72, x0 + trim_w, 0.125 * 72 + trim_h])
        writer.add_page(page)
    writer.add_metadata({
        "/Title": "The Happy Little Train | قطار الألوان السعيد",
        "/Subject": "24-page bilingual children's book; 8.5 x 8.5 in trim",
    })
    temp = output.with_suffix(".boxed.pdf")
    with temp.open("wb") as stream:
        writer.write(stream)
    temp.replace(output)
    print(f"Rendered {output} with {len(reader.pages)} pages and original artwork.")


if __name__ == "__main__":
    main()
