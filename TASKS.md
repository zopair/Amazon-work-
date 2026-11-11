# AI Swarm Production Task List
_Last reviewed: 2026-11-10_

Legend: [x] implemented in repository / [ ] pending / [!] blocker or decision required.

## Phase 1 — Repository and tool research

- [x] Confirm repository access, default branch and write permission.
- [x] Inventory current book pipeline and identify existing 24-page bilingual manuscript.
- [x] Confirm current renderer (WeasyPrint/Pango), PDF validator (pypdf/qpdf), image gate (Pillow) and Actions artifact path.
- [x] Verify KDP trim/bleed/margin rules against official help.
- [x] Verify 24-page 8.5 x 8.5 color paperback requires Premium Color; Standard Color starts at 72 pages.
- [x] Verify current KDP Arabic paperback restriction.
- [x] Compare GitHub-native/open-source storybook references and reject paid API / heavyweight CI dependencies.
- [x] Select deterministic, no-secret, low-resource architecture.
- [x] Pin exact direct/transitive Python package versions and inventory upstream licenses/repos in `DEPENDENCIES.md`.
- [x] Pin third-party GitHub Actions to immutable full commit SHAs.
- [ ] Resolve strict GitHub-only dependency provenance: current pip default-index and apt-get installs are not GitHub-only; audit and replace/pin the complete transitive dependency chain or document a runner-image exception.

## Phase 2 — Project plan and structure

- [x] Document current repository baseline and missing assets.
- [x] Define agent responsibilities and JSON contracts.
- [x] Define target directory structure.
- [x] Record KDP publishing blocker and distinguish structural PDF validation from KDP approval.
- [x] Create this task list and `ARCHITECTURE.md`.
- [x] Add `config/kdp_profiles.json` and `config/books/happy-little-train.json`.
- [x] Add JSON Schema for the book manifest.
- [x] Add agent package skeleton and orchestrator entry point.
- [x] Add tests before changing the production renderer.

## Phase 3 — Build the deterministic production swarm

- [x] Implement fail-fast orchestrator, manifest validation and machine-readable JSON reports.
- [x] Implement story adapter using the approved content; preserve exactly 24 bilingual page records.
- [x] Implement character bible, fixed palette, scene cast map and deterministic scene prompts.
- [x] Implement localization QA for English/Arabic completeness, script presence, Unicode normalization and RTL/LTR direction; it validates approved copy and does not fabricate translations.
- [x] Implement standard-library SVG illustration agent with fixed locomotive geometry and deterministic per-page seeds.
- [x] Add standard-library regression tests for page contracts, character mappings, manifest/profile and orchestrator outputs.
- [x] Add a quality workflow for compile, tests and JSON validation.
- [ ] Add story quality checks: age suitability, readability, repeated phrases, continuity, learning goal and prohibited-content checks.
- [ ] Add optional offline translation engine only after model/package licensing, model size and runner-resource constraints are proven.
- [x] Generate all 24 deterministic SVG illustrations on GitHub Actions and inspect the 24-page contact sheet; art remains a prototype pending print-proof review.
- [x] Validate SVG XML, canvas dimensions, page mapping and deterministic output in regression tests.
- [x] Run generated SVGs through the print renderer and inspect the resulting PDF proofs.
- [x] Integrate deterministic artwork generation into the existing print workflow and add manual seed/preview-only inputs; dependency provenance remains unresolved.
- [x] Run the integrated print workflow: 24-page PDF generated, SVG vectors detected in PDF streams, Arabic/English text and embedded fonts validated, and qpdf passed.
- [x] Render all 24 page proofs; inspect the full contact sheet and sample full-resolution pages for layout and safe-zone issues.
- [x] Implement a separate paperback full-wrap cover builder using KDP's published paper multiplier, trim dimensions and 0.125-inch bleed; suppress spine text below 80 pages.
- [ ] Verify generated cover geometry against a fresh KDP Cover Calculator template for the chosen marketplace before upload.
- [ ] Add font licensing notices and pin tested Arabic font versions.
- [x] Add unit tests for 24-page Premium Color spine width, full-wrap width/height, and invalid page-count/paper profiles.
- [ ] Add integration tests for cover PDF page boxes and visual safe-zone inspection.

## Phase 4 — GitHub Actions automation

- [x] Add PR/push quality workflow with least-privilege read-only permissions and timeout.
- [x] Add manual workflow inputs for deterministic seed and preview-only mode (profile/format selection remains pending).
- [x] Keep content audit, artwork generation/audit, PDF rendering, QA and artifact packaging as explicit jobs.
- [x] Pin all third-party Actions to reviewed full commit SHAs.
- [ ] Resolve strict dependency source provenance before claiming GitHub-only acquisition.
- [x] Add queue discovery and a dynamic `strategy.matrix` workflow; matrix execution is capped at one concurrent book to conserve runner minutes.\n- [x] Add ImageMagick pixel-dimension validation for 300-DPI full-wrap cover raster proofs (±1 px tolerance).\n- [x] Add a blocking W3C EPUBCheck 5.4.0 gate before any gh-pages publication.\n- [x] Add a bounded exponential-backoff utility for transient connection failures; no live model/API client exists in this deterministic release to wire it into.\n- [x] Set 14-day per-book artifact retention and serialized matrix execution.
- [x] Upload generated SVG artwork and JSON QA reports as a separate 14-day artifact; PDF proofs remain pending.
- [x] Restrict gh-pages publishing to pushes on `main` and require all matrix EPUBCheck jobs to pass.
- [ ] Verify fork/PR workflows cannot obtain write permissions or secrets.

## Phase 5 — Trial book and acceptance

- [x] Generate all 24 original vector illustrations.
- [x] Render the 24-page interior PDF (GitHub Actions artifact; 170,499 bytes).
- [x] Generate the full-wrap cover PDF in CI; compare final geometry with the selected KDP Cover Calculator template before release.
- [x] Run content, image, font, geometry and qpdf checks; all structural checks passed.
- [x] Render all 24 page proofs and inspect the contact sheet plus sampled full-resolution pages.
- [ ] Confirm the KDP profile against the selected marketplace and current KDP calculator.
- [ ] Run KDP Print Previewer manually and resolve every warning.
- [ ] Mark the artifact `STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED` until Previewer and language eligibility are confirmed.

## Phase 6 — Hardening and operations

- [ ] Add regression fixtures and deterministic build comparison.
- [ ] Add artifact size/time budgets and fail on unexpected growth.
- [ ] Add dependency/license inventory and scheduled dependency review.
- [ ] Add reproducibility metadata (commit SHA, profile version, seed, tool versions, font versions).
- [ ] Document manual KDP upload and human review; do not automate KDP login/upload.
- [ ] Document recovery, rerun and artifact-retention procedures.

## Current blockers

1. **Procedural artwork is generated but not production-approved.** GitHub Actions generated 24 SVGs and the 24-page contact sheet was visually inspected. Full PDF proof inspection and human approval remain required.
2. **Arabic paperback availability.** KDP's official Arabic help currently says paperback publishing in Arabic is unavailable. A bilingual Arabic/English print edition is therefore not guaranteed to be accepted. Resolve language/metadata eligibility before treating the print PDF as publishable.
3. **Cover template verification.** A separate paperback full-wrap PDF builder now exists; its computed geometry still requires comparison with the final KDP Cover Calculator template. The 24-page spine is too narrow for spine text.
4. **Dependency source provenance is not yet GitHub-only.** Current workflow uses pip's default package index and Ubuntu apt repositories; a full transitive dependency provenance audit and replacement/pinning plan is required.
5. **No true local LLM/diffusion in CI.** The first release uses deterministic story adapters and original SVG illustrations. Heavy model inference is explicitly out of scope for hosted runners.

## Phase 3 implementation checkpoint

The feature branch `feature/deterministic-swarm-phase-3` contains the manifest/schema, KDP profile, book configuration, character bible, story/character/SVG/localization agents, EPUB/static-site publisher, orchestrator, regression tests and integrated Actions workflows. The 24-page PDF, EPUB and static site have passed GitHub Actions. A separate KDP paperback cover builder and KDP geometry unit tests have now been added. Superseded by feature-branch workflow run 42718252743: EPUBCheck 5.4.0, print PDF/preflight and full-wrap cover build all passed.

Next: download and inspect the generated PDF/cover/EPUB artifacts, complete page-by-page editorial/art approval, resolve dependency provenance and KDP language eligibility, and compare the cover against the live KDP template. Keep the PR unmerged until these gates are addressed.


## Phase 4 implementation checkpoint

The branch `feature/multi-book-pipeline-phase-4` adds `books-queue/`, `book.discover_books`, dynamic matrix build/EPUBCheck jobs, an ImageMagick `identify` cover pixel gate, and a gh-pages publisher that depends on every EPUBCheck matrix result. Matrix concurrency is deliberately capped at one and artifacts expire after 14 days.

**Multi-book content limitation:** discovery and matrix orchestration are queue-driven, but the current manuscript adapter and PDF renderer still consume the existing approved 24-page `book.content.PAGES` source and fixed renderer output. A second queue entry does not yet represent an independently authored manuscript. Do not enqueue different story content until the content adapter, renderer and content audit are parameterized per manifest. This is a known Phase 4 follow-up, not a claim of fully generalized book authoring.

**Network resilience limitation:** `book/agents/retry.py` provides bounded exponential backoff for idempotent transient network operations. The current swarm has no model/API transport client, so there is no outbound model request to patch; the helper is ready for any future approved connector.


## Verified feature-branch execution — 2026-11-09

Workflow run [42718252743](https://github.com/zopair/Amazon-work-/actions/runs/42718252743) on commit `2931aa1b903cef0dcf6dd1c7ffef6909f060eb16` completed successfully. Verified jobs:
- 24-page bilingual content integrity audit.
- Deterministic generation and audit of all 24 original SVG illustrations.
- EPUB 3.4 validation using W3C EPUBCheck 5.4.0.
- Print PDF rendering and structural/bilingual preflight.
- Paperback full-wrap cover PDF generation.
- Visual proof rendering and artifact packaging.

Three artifacts were retained by GitHub Actions: generated artwork (127,214 bytes), print-ready package (1,491,999 bytes), and artwork preflight diagnostics (527 bytes). They expire on 2026-11-23 or 2026-12-09 as reported by GitHub.

**Evidence boundary:** successful CI validates the pipeline and structural checks, not artistic approval, KDP account/language eligibility, or acceptance in KDP Print Previewer. The release job was skipped. The feature branch is not the default branch.
