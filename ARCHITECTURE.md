# AI Swarm Architecture & Research
_Last reviewed: 2026-11-10_

## 1. Current repository baseline

The repository contains an approved bilingual title, **The Happy Little Train / قطار الألوان السعيد**, with 24 page records and an existing print renderer. The current renderer remains unchanged on this feature branch.

- `book/content.py`: approved 24-page English/Arabic copy and parent prompts.
- `book/render.py`: HTML/CSS to print PDF via WeasyPrint/Pango.
- `book/preflight.py`: PDF page count, page boxes, text, fonts and artwork checks.
- `book/inputs.py`: artwork presence, dimensions and color-mode gate.
- `.github/workflows/build.yml`: now generates SVG artwork, validates assets, transfers them between jobs, and supports manual seed/preview-only inputs.
- `book/agents/`: new deterministic agent package on the feature branch.
- `config/`, `schemas/`, `assets/style/`, `tests/`: new manifest, KDP profile, character bible and regression contracts.
- `assets/artwork/`: no approved production illustrations have been committed.

The current production pipeline is fail-closed: no missing or placeholder artwork is silently accepted. The approved manuscript is preserved. The new procedural illustrations are prototypes until PDF proofs receive human review.

## 2. Hard publishing constraint

Amazon KDP's current official help states that Arabic paperback publishing is not currently available. A geometrically correct PDF must not be represented as guaranteed publishable as an Arabic-language paperback. An English-primary edition containing Arabic passages still needs an explicit account, metadata and Previewer check.

For an 8.5 x 8.5 inch paperback interior:
- Trim: 8.5 x 8.5 in.
- With bleed: 8.625 x 8.75 in.
- At 24 pages with bleed: minimum inside/gutter margin 0.375 in; minimum top, bottom and outside margins 0.375 in.
- 24 pages are within the Premium Color minimum; Standard Color starts at 72 pages for this trim.
- Interior and full-wrap cover are separate deliverables.
- KDP Print Previewer and the actual selected marketplace/settings remain the final authority.

Official sources:
- https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
- https://kdp.amazon.com/en_US/help/topic/GUQT4C8J6RR6V8TY

## 3. Selected stack and explicit trade-offs

| Concern | Selected approach | Why / limitation |
|---|---|---|
| Orchestration | Python standard library | Lightweight, no remote queue, no secrets, deterministic |
| Story Agent | Adapter over approved manuscript | Prevents unreviewed copy drift; not an LLM |
| Character Agent | JSON Character Bible + scene-cast mapping | One canonical source for character features and style |
| Illustrator Agent | Python standard-library SVG generation | Original resolution-independent vector art; no image package/model required; still requires visual review |
| Layout | Existing WeasyPrint/Pango renderer | Kept unchanged until integration tests pass |
| PDF QA | Existing pypdf/qpdf/Poppler checks | Structural validation does not guarantee KDP approval |
| Delivery | GitHub Actions artifacts | No paid storage/server required |

No CrewAI or Swarm framework is installed in the runtime. The agents are small Python modules with explicit JSON contracts. This avoids framework overhead and avoids representing deterministic scripts as autonomous LLM agents.

## 4. Feature-branch implementation

The feature branch `feature/deterministic-swarm-phase-3` introduces:

- `schemas/book-manifest.schema.json`: versioned book/job contract.
- `config/books/happy-little-train.json`: explicit bilingual book configuration and deterministic seed.
- `config/kdp_profiles.json`: trim, bleed, margin and color profile; not a KDP cover calculator.
- `assets/style/character-bible.json`: fixed locomotive/animal descriptions, visual palette and per-scene cast.
- `book/agents/contracts.py`: shared page-contract validation.
- `book/agents/story_agent.py`: maps the approved 24-page manuscript into locale-keyed JSON.
- `book/agents/character_agent.py`: validates cast and emits deterministic scene prompts.
- `book/agents/art_agent.py`: renders original procedural SVG artwork with a 2588 x 1716 canvas and a fixed 1294 x 858 viewBox; no Pillow is required for illustration generation.
- `book/agents/orchestrator.py`: fail-fast stage runner, manifest validation and JSON reports.
- `tests/test_swarm.py`: standard-library regression suite.
- `.github/workflows/quality.yml`: Python compile/tests/JSON validation, read-only permissions.

Run the metadata/scene planning locally with:

```bash
python -m book.agents.orchestrator
```

Generate the 24 procedural vector illustrations:

```bash
python -m book.agents.orchestrator --generate-art
python -m book.inputs
```

The art agent uses only Python's standard library and no external image API, remote model, stock asset or secret. SVG is resolution-independent; human visual approval is still required before print production.

## 5. KDP interior profile

The current profile is `square-8.5-premium-color-24p`:
- Trim 8.5 x 8.5 in.
- Media 8.625 x 8.75 in.
- 0.125 in top, bottom and outside bleed.
- 0.375 in minimum margins for the 24-page bleed case.
- Premium Color; 300 DPI art target.

SVG artwork is vector-based and does not require raster DPI upscaling; raster uploads still use the 300-DPI placed-size gate. The profile intentionally marks `cover_requires_calculator: true`. A full-wrap cover cannot be calculated from interior trim alone: spine width depends on final page count, paper type and KDP settings. No guessed cover dimensions will be emitted.

## 6. Workflow and resource controls

- `quality.yml` runs standard-library tests and JSON validation on pushes, pull requests and manual dispatch.
- `swarm-artwork.yml` generates and packages 24 SVGs without installing any Python third-party packages.
- `build.yml` now generates the artwork, audits it, transfers it to the renderer job and offers manual `seed` and `preview_only` inputs.
- The complete print workflow has not yet been run on the feature branch.
- No secrets, paid APIs, external queues or automated KDP account interactions are required by the new agents.
- Generated artwork and PDFs should remain CI artifacts, not Git history.
- All third-party Actions still need reviewed full-SHA pinning before production hardening.

## 7. Strict GitHub-only dependency provenance

The existing print workflow installs Python packages with pip's default package index and native libraries with Ubuntu apt repositories. Therefore the full project does **not yet** meet a literal “all dependencies fetched from GitHub only” requirement. The new quality workflow itself uses only Python's standard library and GitHub-hosted Actions, but the illustration agent depends on Pillow, already present in the existing pinned requirements file. Do not claim strict GitHub-only dependency acquisition until every direct and transitive dependency and the OS runner baseline have been audited.

## 8. Acceptance and release boundary

A future successful production run must provide:
- Exactly 24 interior pages and the required MediaBox/TrimBox/BleedBox geometry.
- 24 approved original vector or raster illustrations meeting the placed-size threshold.
- Embedded fonts, English/Arabic text extraction and no blank pages.
- A separately calculated KDP full-wrap cover.
- qpdf integrity, page proofs/contact sheet and machine-readable QA report.
- Explicit status `STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED` until KDP Previewer and language/metadata eligibility are confirmed.

A free GitHub-hosted CPU runner is suitable for deterministic procedural artwork. It is not a practical free environment for repeated SDXL/FLUX diffusion inference. A true LLM/diffusion mode remains optional and must never silently introduce paid APIs or services.
