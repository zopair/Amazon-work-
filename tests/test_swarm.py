"""Standard-library regression tests for swarm contracts and orchestration."""
import json
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from book.agents.art_agent import generate_all
from book.agents.character_agent import build_scene_plan, load_bible
from book.agents.contracts import validate_page_records
from book.agents.orchestrator import ROOT, run, validate_manifest
from book.agents.publisher_agent import build_epub, build_static_site
from book.agents.localization_agent import audit_locales
from book.agents.story_agent import build_story
from book.cover import calculate_cover_geometry


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

    def test_localization_agent_checks_english_arabic_and_rtl(self):
        story = build_story()
        report = audit_locales(story, ["en", "ar"])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["direction"], {"en": "ltr", "ar": "rtl"})
        self.assertFalse(report["automatic_translation_performed"])
        self.assertEqual(report["checked_fields"], 24 * 3 * 2)

    def test_localization_agent_rejects_missing_arabic_script(self):
        story = build_story()
        story["pages"][0]["body"]["ar"] = "English-only replacement"
        with self.assertRaises(ValueError):
            audit_locales(story, ["en", "ar"])

    def test_manifest_and_profile_are_consistent(self):
        manifest = json.loads((ROOT / "config/books/happy-little-train.json").read_text(encoding="utf-8"))
        profiles = json.loads((ROOT / "config/kdp_profiles.json").read_text(encoding="utf-8"))
        validate_manifest(manifest, profiles)

    def test_kdp_premium_color_cover_geometry_for_24_pages(self):
        profiles = json.loads((ROOT / "config/kdp_profiles.json").read_text(encoding="utf-8"))
        profile = profiles["profiles"]["square-8.5-premium-color-24p"]
        geometry = calculate_cover_geometry(profile, 24)
        self.assertAlmostEqual(geometry["spine_width_in"], 0.056328, places=6)
        self.assertAlmostEqual(geometry["cover_width_in"], 17.306328, places=6)
        self.assertAlmostEqual(geometry["cover_height_in"], 8.75, places=6)
        self.assertFalse(geometry["spine_text_allowed"])

    def test_kdp_cover_rejects_invalid_page_counts_and_paper_profiles(self):
        profiles = json.loads((ROOT / "config/kdp_profiles.json").read_text(encoding="utf-8"))
        profile = profiles["profiles"]["square-8.5-premium-color-24p"]
        with self.assertRaises(ValueError):
            calculate_cover_geometry(profile, 23)
        with self.assertRaises(ValueError):
            calculate_cover_geometry({**profile, "color_mode": "unknown"}, 24)

    def test_svg_illustrator_generates_24_valid_vector_pages(self):
        story = build_story()
        bible = load_bible(ROOT / "assets/style/character-bible.json")
        with tempfile.TemporaryDirectory() as temp:
            paths = generate_all(story, bible, temp, seed=24001)
            self.assertEqual(len(paths), 24)
            self.assertEqual([p.name for p in paths], [f"page-{i:02d}.svg" for i in range(1,25)])
            for path in paths:
                root = ET.parse(path).getroot()
                self.assertTrue(root.tag.endswith("svg"))
                self.assertEqual(root.attrib["width"], "2588px")
                self.assertEqual(root.attrib["height"], "1716px")

    def test_svg_output_is_reproducible_for_same_seed(self):
        story = build_story()
        bible = load_bible(ROOT / "assets/style/character-bible.json")
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = generate_all(story, bible, a, seed=77)
            second = generate_all(story, bible, b, seed=77)
            self.assertEqual(first[0].read_bytes(), second[0].read_bytes())

    def test_epub3_and_static_site_publishers_create_24_page_outputs(self):
        story = build_story()
        manifest = json.loads((ROOT / "config/books/happy-little-train.json").read_text(encoding="utf-8"))
        bible = load_bible(ROOT / "assets/style/character-bible.json")
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            artwork_dir = temp / "artwork"
            generate_all(story, bible, artwork_dir, seed=24001)
            epub_path = build_epub(story, manifest, artwork_dir, temp / "book.epub")
            site_path = build_static_site(story, manifest, artwork_dir, temp / "site")
            with zipfile.ZipFile(epub_path) as archive:
                names = archive.namelist()
                self.assertEqual(names[0], "mimetype")
                self.assertEqual(archive.read("mimetype"), b"application/epub+zip")
                opf = archive.read("OEBPS/content.opf").decode("utf-8")
                self.assertNotIn('properties="svg"', opf)
                self.assertIn('media-type="image/svg+xml"', opf)
                epub_css = archive.read("OEBPS/styles/book.css").decode("utf-8")
                self.assertNotIn("direction:", epub_css)
                self.assertEqual(sum(name.startswith("OEBPS/text/page-") for name in names), 24)
                self.assertEqual(sum(name.startswith("OEBPS/images/page-") for name in names), 24)
            self.assertTrue((site_path / "index.html").is_file())
            self.assertEqual(len(list((site_path / "pages").glob("page-*.html"))), 24)
            self.assertEqual(len(list((site_path / "assets/images").glob("page-*.svg"))), 24)

    def test_orchestrator_emits_machine_readable_reports_without_art_generation(self):
        report = run(ROOT / "config/books/happy-little-train.json",
                     ROOT / "config/kdp_profiles.json", generate_art=False)
        self.assertEqual(report["story_pages"], 24)
        self.assertEqual(report["artwork_status"], "not_generated")
        self.assertTrue((ROOT / "dist/swarm/scene-plan.json").is_file())
        self.assertTrue((ROOT / "dist/swarm/localization-report.json").is_file())


if __name__ == "__main__":
    unittest.main()
