import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from version import APP_VERSION  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_candidate_version_is_shared_by_all_three_applications(self):
        self.assertEqual(APP_VERSION, "2.6.0")
        for relative_path in (
            "src/optimus_sun.py",
            "src/catalog/gui.py",
            "tools/compatibility_matrix_gui.py",
        ):
            source = (ROOT_DIR / relative_path).read_text(encoding="utf-8")
            self.assertIn("from version import APP_VERSION", source)
            self.assertIn("APP_VERSION", source)


if __name__ == "__main__":
    unittest.main()
