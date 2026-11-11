# The Happy Little Train — bilingual book production pipeline

A modular, deterministic, no-secret production pipeline for the approved 24-page Arabic/English children's book.

## Swarm planning and artwork

The feature branch `feature/deterministic-swarm-phase-3` adds:
- A versioned book manifest and KDP interior profile.
- A Character Bible that centralizes the locomotive and supporting characters.
- A localization QA agent that checks bilingual completeness, script and text direction; it does not perform automatic translation.
- Story and character agents that emit stable JSON.
- A pure-standard-library SVG illustrator that produces original, resolution-independent vector scenes.
- A fail-fast orchestrator and regression tests.
- An EPUB 3 exporter and a zero-JavaScript static website exporter, both using the same 24 SVG assets.

Run planning and scene validation:

```bash
python -m book.agents.orchestrator
python -m unittest discover -s tests -v
```

Generate the 24 vector illustrations:

```bash
python -m book.agents.orchestrator --generate-art
python -m book.inputs
```

Generated files are written to `assets/artwork/page-01.svg` … `page-24.svg`. Build all digital outputs with `python -m book.agents.orchestrator --generate-art --build-epub --build-site`. The EPUB is written to `dist/publish/` and the static website to `dist/site/`. Review all images before using them in a print book; successful generation is not artistic approval.

## Existing print pipeline

1. `book/content.py`: approved bilingual manuscript and parent prompts.
2. `assets/artwork/`: 24 original illustrations, required by the artwork gate.
3. `book/render.py`: HTML/CSS pagination via WeasyPrint + Pango/HarfBuzz.
4. `book/preflight.py`: PDF page count, MediaBox/TrimBox/BleedBox, bilingual text and embedded fonts.
5. `book/cover.py`: calculate paperback full-wrap geometry and render the cover PDF from the selected book/KDP profile.
6. `.github/workflows/build.yml`: generate SVG artwork, render the print PDF and full-wrap cover, run structural checks and upload artifacts.
7. `.github/workflows/swarm-artwork.yml`: lightweight artwork-only generation and 14-day artifact workflow.

Run the print pipeline locally after installing the system libraries/fonts listed in the existing workflow:

```bash
python -m pip install -r requirements.txt
python -m book.inputs
python -m book.render
python -m book.preflight
qpdf --check dist/the-happy-little-train-print.pdf
```

## KDP production notes

Interior trim: 8.5 × 8.5 in. With bleed, PDF media size: 8.625 × 8.75 in. The feature branch now generates a full-wrap cover PDF through `book/cover.py`. Its geometry still requires comparison against the final KDP Cover Calculator template for the selected marketplace, paper and page count.

A 24-page, 8.5 × 8.5 in color paperback requires Premium Color under current KDP page-count tables; Standard Color starts at 72 pages. KDP's Arabic paperback availability restriction means a bilingual Arabic/English print edition is not guaranteed to be accepted. KDP Print Previewer and the selected marketplace/metadata remain the final authority.

## Resource and dependency policy

The story, character and illustration agents use only the Python standard library; no API keys, paid model endpoints, cloud servers or model weights are required. GitHub Actions run 42718252743 on `feature/multi-book-pipeline-phase-4` passed artwork generation, EPUBCheck 5.4.0, print PDF rendering/preflight, full-wrap cover generation and proof packaging. Human review of the downloaded artifacts and KDP Print Previewer acceptance remain mandatory. The existing PDF renderer still depends on WeasyPrint, pypdf and native Ubuntu rendering libraries. Pillow is optional and loaded only for raster artwork; the SVG-first build does not require it. Its complete dependency chain is not yet proven to be GitHub-only; pip and Ubuntu apt sources remain an explicit provenance-audit item.
