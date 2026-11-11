"""Discover enabled book manifests and emit a GitHub Actions matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def discover(queue_dir: Path) -> dict:
    if not queue_dir.is_dir():
        raise FileNotFoundError(f"Book queue directory does not exist: {queue_dir}")
    entries = []
    seen_ids = set()
    for queue_file in sorted(queue_dir.glob("*.json")):
        item = json.loads(queue_file.read_text(encoding="utf-8"))
        if not item.get("enabled", True):
            continue
        manifest_rel = item.get("manifest")
        if not isinstance(manifest_rel, str) or not manifest_rel:
            raise ValueError(f"{queue_file}: 'manifest' must be a repository-relative path")
        manifest_path = (ROOT / manifest_rel).resolve()
        if ROOT.resolve() not in manifest_path.parents or manifest_path.suffix != ".json":
            raise ValueError(f"{queue_file}: manifest path escapes the repository or is not JSON")
        if not manifest_path.is_file():
            raise FileNotFoundError(f"{queue_file}: manifest not found: {manifest_rel}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        book_id = manifest.get("book_id")
        if not isinstance(book_id, str) or not book_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in book_id):
            raise ValueError(f"{manifest_rel}: book_id must be lowercase kebab-case")
        if book_id in seen_ids:
            raise ValueError(f"Duplicate book_id in queue: {book_id}")
        seen_ids.add(book_id)
        if manifest.get("content_source") != "approved_python_module":
            raise ValueError(f"{book_id}: unsupported content_source; only approved_python_module is enabled")
        artwork = manifest.get("artwork", {})
        entries.append({
            "book_id": book_id,
            "manifest": manifest_rel,
            "page_count": int(manifest["page_count"]),
            "seed": int(manifest["seed"]),
            "kdp_profile": manifest["kdp_profile"],
            "artwork_dir": artwork["output_dir"],
        })
    if not entries:
        raise ValueError(f"No enabled book manifests found in {queue_dir}")
    return {"include": entries}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default="books-queue")
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args()
    matrix = discover(ROOT / args.queue)
    encoded = json.dumps(matrix, separators=(",", ":"))
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as stream:
            stream.write(f"matrix={encoded}\n")
            stream.write(f"book_count={len(matrix['include'])}\n")
    print(json.dumps(matrix, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
