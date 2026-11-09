"""Character-bible loader and deterministic scene prompt planner."""
from __future__ import annotations

import json
from pathlib import Path


def load_bible(path: str | Path) -> dict:
    bible = json.loads(Path(path).read_text(encoding="utf-8"))
    if bible.get("schema_version") != "1.0":
        raise ValueError("Unsupported character bible schema_version")
    if not bible.get("characters") or "choo_choo" not in bible["characters"]:
        raise ValueError("Character bible must define the lead character choo_choo")
    if not bible.get("scene_cast"):
        raise ValueError("Character bible must define scene_cast")
    return bible


def build_scene_plan(story: dict, bible: dict) -> dict:
    scenes = []
    cast_map = bible["scene_cast"]
    for page in story["pages"]:
        key = page["scene_key"]
        if key not in cast_map:
            raise ValueError(f"Page {page['page']}: no character mapping for scene '{key}'")
        cast = cast_map[key]
        missing = [name for name in cast if name not in bible["characters"]]
        if missing:
            raise ValueError(f"Page {page['page']}: unknown characters {missing}")
        descriptions = {
            name: {
                "body": bible["characters"][name]["body"],
                "fixed_features": bible["characters"][name]["fixed_features"],
            }
            for name in cast
        }
        scenes.append({
            "page": page["page"],
            "scene_key": key,
            "cast": cast,
            "character_specs": descriptions,
            "art_direction": bible["style"],
            "prompt": (
                f"Original children's picture-book scene '{key}'. "
                "Preserve every character's fixed_features exactly. "
                "Use the shared palette, soft daylight, rounded forms, "
                "and a clean composition with no lettering."
            ),
        })
    return {"schema_version": "1.0", "scene_count": len(scenes), "scenes": scenes}
