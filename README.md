# The Happy Little Train — bilingual KDP pipeline

A modular, free-to-run GitHub Actions pipeline for the approved 24-page Arabic/English children's book.

## Pipeline

1. `book/content.py`: approved bilingual copy and Mom's Turn prompts.
2. `assets/artwork/`: original page illustrations (hard-required; no synthetic fallback).
3. `book/render.py`: HTML/CSS pagination via WeasyPrint + Pango/HarfBuzz shaping.
4. `book/preflight.py`: PDF page count, media/trim/bleed boxes, bilingual text layer and embedded fonts.
5. `.github/workflows/build.yml`: cloud build, qpdf validation, 24-page visual proofs, artifact upload, tagged release publishing.

## Required artwork

Add 24 original illustrations named `page-01.png` … `page-24.png` under `assets/artwork/`. JPG/JPEG/WebP are accepted. Minimum placed size is 2588 × 1716 pixels (300 DPI at 8.625 × 5.72 inches), RGB/RGBA. The pipeline intentionally stops if even one original illustration is absent or undersized.

## Run locally

Install the system libraries/fonts listed in the workflow, then:

```bash
python -m pip install -r requirements.txt
python -m book.inputs
python -m book.render
python -m book.preflight
qpdf --check dist/the-happy-little-train-print.pdf
```

Pushes to `main` run CI and publish a 30-day Actions artifact when all gates pass. Push a version tag such as `v1.0.0` to create a GitHub Release with the validated PDF attached.

## KDP production notes

Interior trim: 8.5 × 8.5 in. With bleed, PDF media size: 8.625 × 8.75 in (0.125 in outside bleed, plus 0.125 in top and bottom). Text is inset from the trim edge. The output is a single-page-per-PDF-page interior; the wrap cover is a separate deliverable.

A 24-page, 8.5 × 8.5 in color paperback requires Premium Color under current KDP page-count tables; Standard Color starts at 72 pages. KDP currently limits RTL paperback support to Hebrew, Yiddish and Japanese, not Arabic. A bilingual Arabic/English manuscript must therefore be checked in KDP Print Previewer and may not be accepted in the requested RTL configuration. This pipeline cannot guarantee KDP acceptance.
