# The Happy Little Train — bilingual book production pipeline

A modular, deterministic, no-secret production pipeline for the approved 24-page Arabic/English children's book.

## Swarm planning and artwork

The feature branch `feature/deterministic-swarm-phase-3` adds:
- A versioned book manifest and KDP interior profile.
- A Character Bible that centralizes the locomotive and supporting characters.
- Story and character agents that emit stable JSON.
- A Pillow-based procedural illustrator (original vector-like raster art; not an LLM or diffusion model).
- A fail-fast orchestrator and standard-library regression tests.

Run planning and scene validation:

```bash
python -m book.agents.orchestrator
python -m unittest discover -s tests -v
```

Generate the 24 illustrations (requires the pinned Pillow dependency):

```bash
python -m book.agents.orchestrator --generate-art
python -m book.inputs
```

Generated files are written to `assets/artwork/page-01.jpg` … `page-24.jpg`. Review all images before using them in a print book. Do not treat successful image generation as artistic approval.

## Existing print pipeline

1. `book/content.py`: approved bilingual manuscript and parent prompts.
2. `assets/artwork/`: 24 original illustrations, required by the artwork gate.
3. `book/render.py`: HTML/CSS pagination via WeasyPrint + Pango/HarfBuzz.
4. `book/preflight.py`: PDF page count, MediaBox/TrimBox/BleedBox, bilingual text and embedded fonts.
5. `.github/workflows/build.yml`: current print build, qpdf validation, page proofs and Actions artifact.

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

The deterministic agents require no API keys, paid model endpoints, cloud servers or downloaded model weights. The new quality workflow uses the Python standard library. The complete existing print dependency chain is not yet proven to be GitHub-only: pip and Ubuntu apt sources remain an explicit provenance-audit item. Do not claim full GitHub-only dependency sourcing until that audit is complete.
