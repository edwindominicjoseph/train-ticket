import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "promote-image.py"
SPEC = importlib.util.spec_from_file_location("promote_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ZERO = "sha256:" + "0" * 64
VALID = "sha256:" + "a" * 64


class PromoteImageTest(unittest.TestCase):
    def test_replaces_exactly_one_digest(self):
        content = MODULE.replace_digest(
            f"images:\n  - name: ts-travel-service\n    digest: {ZERO}\n", VALID
        )
        self.assertIn(VALID, content)
        self.assertNotIn(ZERO, content)

    def test_rejects_invalid_digest(self):
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            MODULE.replace_digest(f"digest: {ZERO}\n", "latest")

    def test_rejects_missing_digest_field(self):
        with self.assertRaisesRegex(ValueError, "found 0"):
            MODULE.replace_digest("images: []\n", VALID)


if __name__ == "__main__":
    unittest.main()
