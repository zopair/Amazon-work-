"""Small fail-fast orchestrator for the no-secret production pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .character_agent import build_scene_plan, load_bible
from .localization_agent import audit_locales
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


def run(manifest_path: Path, profile_path: Path, generate_art: bool = False, seed_override: int | None = None, build_epub: bool = False, build_site: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = json.loads(profile_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, profiles)
    if seed_override is not None:
        if seed_override < 0:
            raise ValueError('seed must be non-negative')
        manifest['seed'] = seed_override
    story = build_story()
    if story["page_count"] != manifest["page_count"]:
        raise ValueError("Manifest and approved manuscript page counts differ")
    localization_report = audit_locales(story, manifest["locales"])
    bible_path = ROOT / manifest.get("character_bible", "assets/style/character-bible.json")
    bible = load_bible(bible_path)
    scene_plan = build_scene_plan(story, bible)
    output = ROOT / "dist" / "swarm"
    _write_json(output / "story.json", story)
    _write_json(output / "scene-plan.json", scene_plan)
    _write_json(output / "localization-report.json", localization_report)

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

    outputs = {}
    if build_epub or build_site:
        from .publisher_agent import build_epub as export_epub, build_static_site
        artwork_dir = ROOT / manifest["artwork"]["output_dir"]
        if build_epub:
            epub_path = export_epub(story, manifest, artwork_dir, ROOT / "dist/publish/the-happy-little-train.epub")
            outputs["epub"] = str(epub_path.relative_to(ROOT))
        if build_site:
            site_path = build_static_site(story, manifest, artwork_dir, ROOT / "dist/site")
            outputs["static_site"] = str(site_path.relative_to(ROOT))

    report = {
        "book_id": manifest["book_id"],
        "seed": manifest["seed"],
        "status": "PASS" if not generate_art or artwork_status == "generated" else "PLANNED",
        "story_pages": story["page_count"],
        "scene_count": scene_plan["scene_count"],
        "localization_status": localization_report["status"],
        "artwork_status": artwork_status,
        "structural_status": "NOT_YET_RENDERED",
        "kdp_status": "STRUCTURALLY_VALIDATED_NOT_KDP_APPROVED",
        "external_api_calls": 0,
        "digital_outputs": outputs,
    }
    _write_json(output / "swarm-report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="config/books/happy-little-train.json")
    parser.add_argument("--profiles", default="config/kdp_profiles.json")
    parser.add_argument("--generate-art", action="store_true")
    parser.add_argument("--seed", type=int, default=None, help="Override the manifest seed for a reproducible run")
    parser.add_argument("--build-epub", action="store_true", help="Build an EPUB 3 edition from generated SVG artwork")
    parser.add_argument("--build-site", action="store_true", help="Build a zero-JavaScript static web edition")
    args = parser.parse_args()
    report = run(ROOT / args.manifest, ROOT / args.profiles, args.generate_art, args.seed, args.build_epub, args.build_site)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
