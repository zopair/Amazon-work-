"""Small fail-fast orchestrator for the no-secret production pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .character_agent import build_scene_plan, load_bible
from .story_agent import build_story

ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_manifest(manifest: dict, profile: dict) -> None:
    required = ("schema_version", "book_id", "title", "locales", "page_count",
                "content_source", "artwork", "kdp_profile", "seed")
    missing = [key for key in required if key not in manifest]
    if missing:
        raise ValueError(f"Manifest missing required fields: {missing}")
    if manifest["schema_version"] != "1.0":
        raise ValueError("Unsupported manifest schema_version")
    if manifest["content_source"] != "approved_python_module":
        raise ValueError("Only approved manuscript source is enabled in this release")
    if manifest["page_count"] != 24:
        raise ValueError("This production release is locked to the approved 24-page manuscript")
    if manifest["kdp_profile"] not in profile["profiles"]:
        raise ValueError(f"Unknown KDP profile: {manifest['kdp_profile']}")
    if manifest["artwork"]["mode"] not in ("procedural_svg", "approved_external_art"):
        raise ValueError("Unsupported artwork mode")
    if not isinstance(manifest["seed"], int) or manifest["seed"] < 0:
        raise ValueError("seed must be a non-negative integer")


def run(manifest_path: Path, profile_path: Path, generate_art: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = json.loads(profile_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, profiles)
    story = build_story()
    if story["page_count"] != manifest["page_count"]:
        raise ValueError("Manifest and approved manuscript page counts differ")
    bible_path = ROOT / manifest.get("character_bible", "assets/style/character-bible.json")
    bible = load_bible(bible_path)
    scene_plan = build_scene_plan(story, bible)
    output = ROOT / "dist" / "swarm"
    _write_json(output / "story.json", story)
    _write_json(output / "scene-plan.json", scene_plan)

    artwork_status = "not_generated"
    if generate_art:
        if manifest["artwork"]["mode"] != "procedural_svg":
            raise ValueError("This release only implements procedural_svg artwork")
        from .art_agent import generate_all
        generated = generate_all(
            story, bible, ROOT / manifest["artwork"]["output_dir"],
            manifest["seed"], manifest["artwork"]["width"], manifest["artwork"]["height"],
        )
        artwork_status = "generated"
        _write_json(output / "artwork.json", {
            "status": artwork_status,
            "count": len(generated),
            "files": [str(path.relative_to(ROOT)) for path in generated],
            "dimensions": [manifest["artwork"]["width"], manifest["artwork"]["height"]],
            "resolution": "vector",
            "method": "Python standard-library SVG generation; no remote model/API",
        })

    report = {
        "book_id": manifest["book_id"],
        "status": "PASS" if not generate_art or artwork_status == "generated" else "PLANNED",
        "story_pages": story["page_count"],
        "scene_count": scene_plan["scene_count"],
        "artwork_status": artwork_status,
        "structural_status": "NOT_YET_RENDERED",
        "kdp_status": "STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED",
        "external_api_calls": 0,
    }
    _write_json(output / "swarm-report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="config/books/happy-little-train.json")
    parser.add_argument("--profiles", default="config/kdp_profiles.json")
    parser.add_argument("--generate-art", action="store_true")
    args = parser.parse_args()
    report = run(ROOT / args.manifest, ROOT / args.profiles, args.generate_art)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
