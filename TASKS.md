# AI Swarm Production Task List
_Last reviewed: 2026-11-10_

Legend: [x] verified / present, [ ] pending, [!] blocker or decision required.

## Phase 1 — Repository and tool research

- [x] Confirm repository access, default branch and write permission.
- [x] Inventory current book pipeline and identify existing 24-page bilingual manuscript.
- [x] Confirm current renderer (WeasyPrint/Pango), PDF validator (pypdf/qpdf), image gate (Pillow) and Actions artifact path.
- [x] Verify KDP trim/bleed/margin rules against official help.
- [x] Verify 24-page 8.5 x 8.5 color paperback requires Premium Color; Standard Color starts at 72 pages.
- [x] Verify current KDP Arabic paperback restriction.
- [x] Compare GitHub-native/open-source storybook references and reject paid API / heavyweight CI dependencies.
- [x] Select deterministic, no-secret, low-resource architecture.
- [ ] Re-check licenses and pin exact versions/SHAs before importing any third-party source.
- [ ] Resolve strict GitHub-only dependency provenance: current pip default-index and apt-get installs are not GitHub-only; audit and replace/pin the complete transitive dependency chain or document a runner-image exception.

## Phase 2 — Project plan and structure

- [x] Document current repository baseline and missing assets.
- [x] Define agent responsibilities and JSON contracts.
- [x] Define target directory structure.
- [x] Record KDP publishing blocker and distinguish structural PDF validation from KDP approval.
- [x] Create this task list and `ARCHITECTURE.md`.
- [ ] Add `config/kdp_profiles.json` and `config/books/happy-little-train.json`.
- [ ] Add JSON Schema for the book manifest.
- [ ] Add agent package skeleton and orchestrator entry point.
- [ ] Add tests before changing the production renderer.

## Phase 3 — Build the deterministic production swarm

- [ ] Implement orchestrator with fail-fast stages, stable run IDs and JSON reports.
- [ ] Implement story agent using approved content or explicit structured inputs; preserve 24-page count and bilingual fields.
- [ ] Add story quality checks: age suitability, readability, repeated phrases, continuity, moral/learning goal and prohibited-content checks.
- [ ] Implement character bible, art direction, fixed palette and deterministic scene prompts.
- [ ] Implement Pillow-based original illustration generation for all 24 pages; no external image calls or downloaded stock art.
- [ ] Validate each image's size, RGB/RGBA mode, file integrity and page-to-scene mapping.
- [ ] Integrate generated artwork with the existing renderer.
- [ ] Correct/verify text safe zones and per-side gutter geometry on odd/even pages.
- [ ] Implement a separate KDP full-wrap cover builder using the exact KDP calculator values for trim, paper, ink and page count.
- [ ] Add font licensing notices and pin tested Arabic font versions.
- [ ] Add unit/integration tests for all geometry and content contracts.

## Phase 4 — GitHub Actions automation

- [ ] Add manual workflow inputs: book profile, seed, output format and optional preview-only mode.
- [ ] Keep content, art, layout, QA and artifact packaging as explicit jobs/steps.
- [ ] Pin all third-party Actions to reviewed full commit SHAs.
- [ ] Use least-privilege permissions, job timeouts, concurrency and bounded artifact retention.
- [ ] Cache only safe dependency downloads; do not cache generated personal content or credentials.
- [ ] Upload interior PDF, cover PDF, contact sheet, page proofs and JSON QA reports.
- [ ] Keep release publishing restricted to signed-off version tags.
- [ ] Verify fork/PR workflows cannot obtain write permissions or secrets.

## Phase 5 — Trial book and acceptance

- [ ] Generate all 24 original illustrations.
- [ ] Render the 24-page interior PDF.
- [ ] Generate the full-wrap cover PDF.
- [ ] Run content, image, font, geometry and qpdf checks.
- [ ] Render every page to proof PNG and inspect a contact sheet plus sampled full-resolution pages.
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

1. **No production artwork exists yet.** `assets/artwork/` currently contains only its README. The current pipeline correctly stops until 24 qualifying illustrations are supplied.
2. **Arabic paperback availability.** KDP's official Arabic help currently says paperback publishing in Arabic is unavailable. A bilingual Arabic/English print edition is therefore not guaranteed to be accepted. Resolve language/metadata eligibility before treating the print PDF as publishable.
3. **No cover builder.** The current workflow produces an interior PDF only; KDP cover is a separate full-wrap file.
4. **Dependency source provenance is not yet GitHub-only.** Current workflow uses pip's default package index and Ubuntu apt repositories; a full transitive dependency provenance audit and replacement/pinning plan is required.
5. **No true local LLM/diffusion in CI.** To preserve free, low-resource GitHub-hosted execution, the first release uses deterministic story templates and original Pillow-generated illustrations. Heavy model inference is explicitly out of scope for hosted runners.

## Phase 2 exit criteria

- [x] Repository baseline documented.
- [x] Technical choices and exclusions documented.
- [x] KDP constraints and blockers documented.
- [x] Work breakdown and target tree documented.

Next: implement Phase 3 in a feature branch, starting with manifest schema, tests and the procedural illustration agent.
