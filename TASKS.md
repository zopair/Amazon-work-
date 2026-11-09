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
- [ ] Re-check licenses and pin exact versions/SHAs before importing any third-party source.
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
- [x] Implement standard-library SVG illustration agent with fixed locomotive geometry and deterministic per-page seeds.
- [x] Add standard-library regression tests for page contracts, character mappings, manifest/profile and orchestrator outputs.
- [x] Add a quality workflow for compile, tests and JSON validation.
- [ ] Add story quality checks: age suitability, readability, repeated phrases, continuity, learning goal and prohibited-content checks.
- [ ] Run image generation on Actions and inspect all 24 page proofs; procedural art is not yet approved production artwork.
- [x] Validate SVG XML, canvas dimensions, page mapping and deterministic output in regression tests.
- [ ] Run generated SVGs through the print renderer and inspect the resulting PDF proofs.
- [ ] Integrate the swarm into a manual production workflow after dependency provenance is resolved.
- [ ] Integrate generated artwork with the existing renderer and visually verify text safe zones and odd/even gutter geometry.
- [ ] Implement a separate KDP full-wrap cover builder using exact KDP calculator values for selected paper, ink and page count.
- [ ] Add font licensing notices and pin tested Arabic font versions.
- [ ] Add unit/integration tests for all geometry and content contracts.

## Phase 4 — GitHub Actions automation

- [x] Add PR/push quality workflow with least-privilege read-only permissions and timeout.
- [ ] Add manual workflow inputs: book profile, seed, output format and optional preview-only mode.
- [ ] Keep content, art, layout, QA and artifact packaging as explicit jobs.
- [ ] Pin all third-party Actions to reviewed full commit SHAs.
- [ ] Resolve strict dependency source provenance before claiming GitHub-only acquisition.
- [ ] Use bounded artifact retention and resource/time budgets.
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

1. **Procedural artwork needs execution and human review.** The new SVG agent can generate 24 deterministic, original vector illustrations without third-party image dependencies; it still needs full PDF integration and human visual approval.
2. **Arabic paperback availability.** KDP's official Arabic help currently says paperback publishing in Arabic is unavailable. A bilingual Arabic/English print edition is therefore not guaranteed to be accepted. Resolve language/metadata eligibility before treating the print PDF as publishable.
3. **No cover builder.** The current workflow produces an interior PDF only; KDP cover is a separate full-wrap file.
4. **Dependency source provenance is not yet GitHub-only.** Current workflow uses pip's default package index and Ubuntu apt repositories; a full transitive dependency provenance audit and replacement/pinning plan is required.
5. **No true local LLM/diffusion in CI.** The first release uses deterministic story adapters and original SVG illustrations. Heavy model inference is explicitly out of scope for hosted runners.

## Phase 3 implementation checkpoint

The feature branch `feature/deterministic-swarm-phase-3` contains the manifest/schema, KDP profile, book configuration, character bible, story and character agents, SVG illustration agent, orchestrator, regression tests and quality workflow. These changes are not yet merged to `main`; the production renderer and existing build workflow remain unchanged.

Next: execute the quality workflow, fix any CI findings, then run and inspect the procedural artwork generation before connecting it to the print renderer.
