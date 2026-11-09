# The Happy Little Train — bilingual book production pipeline

A modular, deterministic, no-secret production pipeline for the approved 24-page Arabic/English children's book.

## Swarm planning and artwork

The feature branch `feature/deterministic-swarm-phase-3` adds:
- A versioned book manifest and KDP interior profile.
- A Character Bible that centralizes the locomotive and supporting characters.
- Story and character agents that emit stable JSON.
- A pure-standard-library SVG illustrator that produces original, resolution-independent vector scenes.
- A fail-fast orchestrator and regression tests.

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

Generated files are written to `assets/artwork/page-01.svg` … `page-24.svg`. Review all images before using them in a print book. Successful generation is not artistic approval.

## Existing print pipeline

1. `book/content.py`: approved bilingual manuscript and parent prompts.
2. `assets/artwork/`: 24 original illustrations, required by the artwork gate.
3. `book/render.py`: HTML/CSS pagination via WeasyPrint + Pango/HarfBuzz.
4. `book/preflight.py`: PDF page count, MediaBox/TrimBox/BleedBox, bilingual text and embedded fonts.
5. `.github/workflows/build.yml`: generate SVG artwork, render the print PDF, run qpdf checks and upload page proofs.
6. `.github/workflows/swarm-artwork.yml`: lightweight artwork-only generation and 14-day artifact workflow.

Run the print pipeline locally after installing the system libraries/fonts listed in the existing workflow:

```bash
python -m pip install -r requirements.txt
python -m book.inputs
python -m book.render
python -m book.preflight
qpdf --check dist/the-happy-little-train-print.pdf
```

## KDP production notes

Interior trim: 8.5 × 8.5 in. With bleed, PDF media size: 8.625 × 8.75 in. The full-wrap cover is a separate deliverable and must use exact KDP calculator settings; this repository does not yet generate a cover.

A 24-page, 8.5 × 8.5 in color paperback requires Premium Color under current KDP page-count tables; Standard Color starts at 72 pages. KDP's Arabic paperback availability restriction means a bilingual Arabic/English print edition is not guaranteed to be accepted. KDP Print Previewer and the selected marketplace/metadata remain the final authority.

## Resource and dependency policy

The story, character and illustration agents use only the Python standard library; no API keys, paid model endpoints, cloud servers or model weights are required. GitHub Actions has successfully generated all 24 SVG assets; the print PDF integration still needs an end-to-end run and proof inspection. The existing PDF renderer still depends on WeasyPrint, pypdf and native Ubuntu rendering libraries. Pillow is optional and loaded only for raster artwork; the SVG-first build does not require it. Its complete dependency chain is not yet proven to be GitHub-only; pip and Ubuntu apt sources remain an explicit provenance-audit item.
