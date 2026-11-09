"""Regression tests for Phase 4 queue, geometry and retry primitives."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from book.discover_books import discover
from book.agents.retry import retry_with_backoff
from book.validate_cover_geometry import validate

ROOT = Path(__file__).resolve().parents[1]


class Phase4Tests(unittest.TestCase):
    def test_queue_discovery_emits_stable_matrix_for_enabled_books(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            queue = Path(tmp)
            (queue / "one.json").write_text(json.dumps({
                "enabled": True, "manifest": "config/books/happy-little-train.json"
            }), encoding="utf-8")
            matrix = discover(queue)
        self.assertEqual(len(matrix["include"]), 1)
        self.assertEqual(matrix["include"][0]["book_id"], "happy-little-train")
        self.assertEqual(matrix["include"][0]["page_count"], 24)

    def test_queue_discovery_rejects_duplicate_book_ids(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            queue = Path(tmp)
            entry = {"enabled": True, "manifest": "config/books/happy-little-train.json"}
            (queue / "a.json").write_text(json.dumps(entry), encoding="utf-8")
            (queue / "b.json").write_text(json.dumps(entry), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate book_id"):
                discover(queue)

    def test_retry_uses_bounded_exponential_delays(self):
        calls = {"count": 0}
        delays = []
        def operation():
            calls["count"] += 1
            if calls["count"] < 4:
                raise TimeoutError("temporary")
            return "ok"
        result = retry_with_backoff(operation, attempts=4, base_delay=1, max_delay=3, sleep=delays.append)
        self.assertEqual(result, "ok")
        self.assertEqual(delays, [1, 2, 3])

    def test_retry_does_not_retry_non_transient_errors(self):
        calls = {"count": 0}
        def operation():
            calls["count"] += 1
            raise ValueError("bad request")
        with self.assertRaises(ValueError):
            retry_with_backoff(operation, attempts=4, sleep=lambda _: None)
        self.assertEqual(calls["count"], 1)

    @patch("book.validate_cover_geometry.subprocess.run")
    def test_cover_geometry_accepts_exact_image_dimensions(self, run):
        run.return_value.stdout = "5192 2625"
        with tempfile.NamedTemporaryFile(suffix=".png") as image:
            report = validate(Path(image.name), ROOT / "config/books/happy-little-train.json",
                              ROOT / "config/kdp_profiles.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["actual"], {"width_px": 5192, "height_px": 2625})


if __name__ == "__main__":
    unittest.main()
