# AI Swarm Architecture & Research
_Last reviewed: 2026-11-10_

## 1. Current repository baseline

The repository already contains a working foundation for one approved bilingual title, **The Happy Little Train / قطار الألوان السعيد**:

- `book/content.py`: 24 approved English/Arabic page records, including parent prompts.
- `book/content_check.py`: content integrity checks.
- `book/inputs.py`: artwork presence, dimensions and color-mode gate.
- `book/render.py`: HTML/CSS to print-PDF renderer using WeasyPrint and Pango.
- `book/preflight.py`: 24-page, MediaBox/TrimBox/BleedBox, text, embedded-font and artwork checks.
- `book/templates/book.css`: page layout.
- `.github/workflows/build.yml`: separate content/artwork gates, render, PDF validation, proof PNGs and 30-day Actions artifact.
- `assets/artwork/`: currently contains only its README; the 24 production illustrations are absent.

The existing pipeline is intentionally fail-closed: it must not silently substitute blank or placeholder illustrations. Preserve the approved 24-page copy unless a content revision is explicitly approved.

## 2. Hard publishing constraint discovered

Amazon KDP's current official help states that Arabic paperback publishing is not currently available. The existing manuscript is bilingual Arabic/English, so a geometrically correct PDF must **not** be represented as guaranteed publishable as an Arabic-language paperback. An English-primary edition containing Arabic passages still needs an explicit KDP account/metadata/Previewer check; do not assume that changing the metadata language bypasses the restriction.

For an 8.5 x 8.5 inch paperback interior:
- Trim: 8.5 x 8.5 in.
- With bleed: 8.625 x 8.75 in (0.125 in on top, bottom and outside edge).
- At 24 pages with bleed: minimum inside/gutter margin 0.375 in; minimum top, bottom and outside margins 0.375 in.
- 24 pages are within the Premium Color minimum; Standard Color starts at 72 pages for this trim size.
- The interior PDF and full-wrap cover are separate deliverables. The current repository only builds the interior; a cover workflow/module remains to be implemented.
- KDP Print Previewer and the actual selected marketplace/settings remain the final authority.

Sources:
- KDP trim, bleed and margin rules: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
- KDP Arabic language availability: https://kdp.amazon.com/en_US/help/topic/GUQT4C8J6RR6V8TY

## 3. Recommended free/open-source stack

| Concern | Selected approach | Why / limitation |
|---|---|---|
| Orchestration | Python standard library; small deterministic agents exchanging JSON | No paid API, no model download, reproducible on GitHub-hosted runners |
| Story generation | Template/grammar-driven story agent with validation and explicit content inputs | Truly free and lightweight; it is not an LLM and must not be marketed as unconstrained generative AI |
| Bilingual text | Existing approved page data; preserve Arabic and English as separate fields | Avoid accidental translation drift; Arabic shaping remains a rendering QA gate |
| Illustration | Original procedural artwork rendered with Pillow drawing primitives, using a fixed character/style bible and per-scene JSON | Small CPU/memory footprint; no model weights, external image API or network calls. This is designed vector-like raster artwork, not diffusion-generated painting |
| Optional SVG path | Python-generated SVG only if later required; render/validate locally in CI | CairoSVG is LGPL-3.0-or-later and adds native dependencies; do not add unless the output quality justifies it |
| PDF layout | Keep WeasyPrint + Pango/HarfBuzz and the current HTML/CSS renderer | Already integrated; supports print CSS and Arabic shaping through system fonts |
| PDF inspection | pypdf + qpdf + Poppler tools | Structural validation and low-resolution page proofs |
| Fonts | Noto Arabic/Sans fonts installed in the runner; record font package/version | Verify font embedding and glyph coverage |
| Delivery | GitHub Actions artifacts; optional tagged GitHub Release | No external storage or paid server |

Relevant upstream GitHub projects:
- WeasyPrint (BSD-3-Clause): https://github.com/Kozea/WeasyPrint
- Pillow (MIT-CMU): https://github.com/python-pillow/Pillow
- pypdf (BSD-3-Clause): https://github.com/py-pdf/pypdf
- CairoSVG (LGPL-3.0-or-later; optional only): https://github.com/Kozea/CairoSVG
- Picture Book (MIT; useful as a UX/reference project, not a required runtime dependency): https://github.com/agammann/picture-book
- Storybook Generator (Gemini-backed; not selected because it relies on a remote model/API and image generation may incur charges): https://github.com/KalminX/storybook_generator
- Storia (local Ollama + SDXL; not selected for GitHub-hosted CI because model weights/GPU or long CPU execution make it unsuitable for a low-resource free runner): https://github.com/ShevonRuzen/Storia

Repository choice is based on the actual pipeline requirements, not star count. Before copying code from any external repository, re-check its current LICENSE and preserve notices.

## 4. Agent responsibilities and contracts

1. **Orchestrator** — reads a book manifest, validates configuration, runs agents in order, writes a machine-readable run manifest and stops on the first failed gate.
2. **Story Agent** — creates/loads exactly 24 page records, bilingual title/body, age band, moral/learning goal, scene description and parent prompt. It validates word limits, non-empty fields and repeated phrasing.
3. **Art Director + Illustration Agent** — owns a character bible, palette, visual style, scene-to-page mapping and deterministic seeds. Produces 24 original images at the actual placed size (minimum 2588 x 1716 px for the current 8.625 x 5.72 in placement at 300 DPI). It must not download assets or call image APIs.
4. **Layout Agent** — renders one interior page per content record, keeps text inside safe areas, applies bleed and emits a separate full-wrap cover once cover dimensions are calculated from the selected KDP print settings.
5. **KDP QA Agent** — checks page count, page boxes, margins, raster dimensions, RGB/RGBA mode, embedded fonts, Arabic text layer, image presence, PDF integrity and visual proofs. It reports structural readiness, never guarantees KDP acceptance.
6. **Release Agent** — uploads only validated outputs and QA reports as Actions artifacts; publishes a release only for an explicitly pushed version tag.

Agents are Python modules, not separate hosted AI services. The pipeline must be deterministic for a fixed manifest and seed.

## 5. Target repository layout

```text
.
├── .github/
│   └── workflows/
│       ├── build.yml                 # Existing: validation + interior PDF + artifact
│       └── quality.yml               # Planned: lint/tests/security and workflow checks
├── assets/
│   ├── artwork/                      # Generated/approved page-01 ... page-24
│   ├── fonts/                        # Only redistributable fonts + license notices
│   └── style/                        # Palette, character bible, art direction
├── book/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── story_agent.py
│   │   ├── art_agent.py
│   │   ├── layout_agent.py
│   │   ├── qa_agent.py
│   │   └── release_agent.py
│   ├── content.py                    # Existing approved copy
│   ├── content_check.py              # Existing
│   ├── inputs.py                     # Existing artwork gate
│   ├── render.py                     # Existing interior renderer
│   ├── preflight.py                  # Existing PDF preflight
│   ├── cover.py                      # Planned separate cover builder
│   ├── manifest.schema.json          # Planned book/job contract
│   └── templates/
│       └── book.css                  # Existing print stylesheet
├── config/
│   ├── kdp_profiles.json             # Trim, bleed, color, page-count profile
│   └── books/
│       └── happy-little-train.json   # Book-specific metadata and seed
├── tests/
│   ├── test_content.py
│   ├── test_artwork.py
│   ├── test_geometry.py
│   └── test_pipeline.py
├── dist/                             # CI-only output; do not commit generated PDFs
├── ARCHITECTURE.md
├── TASKS.md
├── README.md
├── generate_book.py                  # Existing compatibility entry point
└── requirements.txt                  # Existing pinned Python packages
```

## 6. Workflow design and resource controls

- Triggers: `workflow_dispatch` for manual production; push/PR for code validation; version tags only for release publishing.
- Keep jobs sequential where they share large files; run independent lightweight content checks in parallel.
- Use GitHub-hosted Ubuntu runners; no always-on server, database, external queue or paid API.
- Use `concurrency` to prevent duplicate production runs for the same book.
- Set explicit job timeouts, least-privilege permissions, bounded artifact retention and `pip` caching.
- Pin every third-party GitHub Action to a reviewed full commit SHA before production hardening; do not execute untrusted PR code with write permissions.
- No secrets are required for the deterministic pipeline. Never add API keys, cookies, personal tokens or credential scraping.
- Avoid automated account creation, scraping, repeated external API calls, artificial traffic or any KDP upload bot. The workflow creates files only; publishing remains a human-controlled KDP action.
- Keep generated PDFs/proofs out of Git history; store them as Actions artifacts.

## 7. Source-provenance constraint

The current workflow installs Python packages with `pip` from its default package index and installs native libraries with `apt-get` from Ubuntu repositories. Therefore, despite the application and upstream projects being open source, the current dependency acquisition path does **not** yet satisfy a literal interpretation of “all tools/libraries must be fetched from GitHub only.” This is an explicit Phase 3 blocker: inventory the full transitive dependency graph, prefer GitHub-hosted release/source artifacts with pinned commit/tag and checksums, and document any runner-image/OS baseline exception. Do not claim strict GitHub-only provenance until that audit passes. If no reliable GitHub-only path exists for a dependency, replace it with a suitable lighter implementation rather than silently falling back to another registry.

## 8. Acceptance criteria

A successful CI run must produce:
- Exactly 24 interior PDF pages.
- Correct 8.625 x 8.75 in MediaBox/BleedBox and 8.5 x 8.5 in TrimBox on every page.
- At least 0.375 in inside, top, bottom and outside safe margins for this 24-page bleed profile.
- 24 original, color illustrations meeting the effective 300-DPI placed-size threshold.
- Embedded fonts, Arabic and English text extraction, no missing glyphs, no blank pages.
- A separate cover PDF sized from the official KDP calculator/profile.
- qpdf integrity check, contact sheet/page proofs, machine-readable QA report.
- Explicit status: `STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED` until the file passes the KDP Print Previewer and language/metadata eligibility checks.

## 9. Important boundary

A GitHub-hosted CPU runner can reliably produce deterministic vector-like illustrations and books. It is not a practical free environment for repeated SDXL/FLUX diffusion generation. A real LLM/diffusion mode may be added only as an optional, user-controlled self-hosted runner profile; it must never silently introduce a paid API or external service.
