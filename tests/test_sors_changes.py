"""Review summaries report semantic sections and escape untrusted filenames."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sors_changes", ROOT / "standards/SORS/tools/summarize_changes.py")
changes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(changes)


class ChangeSummaryTests(unittest.TestCase):
    def test_changed_environment_and_criteria_are_identified(self):
        before = {"environments": [{"id": "base"}], "criteria": [{"threshold": 1}], "model": {"description": "same"}}
        after = {"environments": [{"id": "new"}], "criteria": [{"threshold": 2}], "model": {"description": "same"}}
        with patch.object(changes, "git", return_value="research.yaml\0"), patch.object(changes, "load_at", side_effect=[before, after]):
            message = changes.summarize(ROOT, "a" * 40)
        self.assertIn("运行环境", message)
        self.assertIn("判断依据", message)
        self.assertNotIn("模型说明", message)

    def test_filename_cannot_inject_summary_html(self):
        with patch.object(changes, "git", return_value="tests/<script>alert(1)</script>.py\0"):
            message = changes.summarize(ROOT, "a" * 40)
        self.assertNotIn("<script>", message)
        self.assertIn("&lt;script&gt;", message)

    def test_no_match_is_not_scientific_approval(self):
        with patch.object(changes, "git", return_value="docs/welcome.md\0"):
            message = changes.summarize(ROOT, "a" * 40)
        self.assertIn("没有命中", message)
        self.assertIn("仍可", message)


if __name__ == "__main__":
    unittest.main()
