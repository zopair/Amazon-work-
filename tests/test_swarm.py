"""Standard-library regression tests for swarm contracts and orchestration."""
import json
import unittest
from pathlib import Path

from book.agents.character_agent import build_scene_plan, load_bible
from book.agents.contracts import validate_page_records
from book.agents.orchestrator import ROOT, run, validate_manifest
from book.agents.story_agent import build_story


class SwarmContractTests(unittest.TestCase):
    def test_approved_story_has_exactly_24_ordered_bilingual_pages(self):
        story = build_story()
        self.assertEqual(story["page_count"], 24)
        self.assertEqual([p["page"] for p in story["pages"]], list(range(1, 25)))
        self.assertTrue(all(p["title"]["en"] and p["title"]["ar"] for p in story["pages"]))

    def test_page_contract_rejects_missing_locale(self):
        with self.assertRaises(ValueError):
            validate_page_records([{"page": 1, "title": {"en": "Only English"}}], 1)

    def test_character_bible_maps_every_story_scene(self):
        story = build_story()
        bible = load_bible(ROOT / "assets/style/character-bible.json")
        plan = build_scene_plan(story, bible)
        self.assertEqual(plan["scene_count"], 24)
        self.assertTrue(all("choo_choo" in scene["cast"] for scene in plan["scenes"]))

    def test_manifest_and_profile_are_consistent(self):
        manifest = json.loads((ROOT / "config/books/happy-little-train.json").read_text(encoding="utf-8"))
        profiles = json.loads((ROOT / "config/kdp_profiles.json").read_text(encoding="utf-8"))
        validate_manifest(manifest, profiles)

    def test_orchestrator_emits_machine_readable_reports_without_art_generation(self):
        report = run(ROOT / "config/books/happy-little-train.json",
                     ROOT / "config/kdp_profiles.json", generate_art=False)
        self.assertEqual(report["story_pages"], 24)
        self.assertEqual(report["artwork_status"], "not_generated")
        self.assertTrue((ROOT / "dist/swarm/scene-plan.json").is_file())


if __name__ == "__main__":
    unittest.main()
