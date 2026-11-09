# Phase 4 — Multi-book CI and release gates

## Queue contract

Each `books-queue/*.json` file points to a repository-local book manifest:

```json
{
  "enabled": true,
  "manifest": "config/books/happy-little-train.json"
}
```

The discovery step rejects missing manifests, path traversal, duplicate IDs, malformed IDs, and unsupported content source declarations. It emits a compact `include` matrix to `$GITHUB_OUTPUT`.

## CI execution and resource controls

- One matrix item is built per enabled queue entry.
- `max-parallel: 1` and `fail-fast: true` conserve Actions minutes and stop downstream work early.
- Build artifacts expire after 14 days.
- Third-party Actions are pinned to full commit SHAs.
- The ImageMagick gate checks the 300-DPI PNG raster proof of the vector PDF; the expected geometry is derived from the manifest's KDP profile and page count. A one-pixel raster rounding tolerance is allowed.
- W3C EPUBCheck 5.4.0 is downloaded from its GitHub release and checksum-verified. The job fails on validator non-zero exit and explicitly scans for ERROR/FATAL.
- gh-pages publication runs only on a push to main and depends on all book builds and all EPUBCheck matrix jobs. Pull requests never receive write permissions.

## Important scope boundary

The matrix is dynamic, but the current story adapter and print renderer remain bound to the existing approved 24-page manuscript. The queue can orchestrate manifest entries, but it is not yet safe to claim that each new manifest represents a distinct book manuscript. Generalizing story loading, content QA and PDF rendering per manifest is a separate required extension before adding independently authored books.

## Backoff policy

`book/agents/retry.py` retries only transient `TimeoutError` and `ConnectionError` by default, with a bounded exponential schedule. Callers must restrict retries to idempotent operations and supply a narrow retry predicate for provider-specific errors. No model/API transport is currently present, so the helper is not wired to an outbound model call.
