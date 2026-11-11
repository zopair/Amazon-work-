import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from book.generate_artwork import generate_all, make_artwork


class OriginalArtworkTests(unittest.TestCase):
    def test_generator_rejects_unknown_scene_keys(self):
        with self.assertRaises(ValueError):
            make_artwork("unknown-scene", 1)

    def test_all_24_pages_generate_unique_print_resolution_rgb_artwork(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = generate_all(Path(directory))
            self.assertEqual(len(outputs), 24)
            self.assertEqual(len({path.name for path in outputs}), 24)

            digests = set()
            for path in outputs:
                self.assertTrue(path.is_file())
                with Image.open(path) as image:
                    self.assertEqual(image.size, (2588, 1716))
                    self.assertEqual(image.mode, "RGB")
                    self.assertGreaterEqual(image.info["dpi"][0], 299)
                    self.assertGreaterEqual(image.info["dpi"][1], 299)
                    digests.add(hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(len(digests), 24)


if __name__ == "__main__":
    unittest.main()
