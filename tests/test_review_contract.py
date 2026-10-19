"""Behavior tests: failed execution, omitted verification and altered references."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "templates/research-project/tools/research_check.py"
spec = importlib.util.spec_from_file_location("research_check", CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
sys.path.insert(0, str(ROOT / "tools"))
from check import validate_yaml
from build import render


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shenyan-review-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = {
            "schema_version": 1, "project_name": "Checker test fixture; not a research project",
            "maintainers": ["test-maintainer"], "kind": "development", "python_version": "3.12",
            "supported_platforms": [sys.platform], "timeout_seconds": 5,
            "commands": {s: ["python", "-c", "print('fixture command')"] for s in ("install", "smoke", "verify")},
            "manual_review_reason": "", "references": [], "expected_outputs": []}
        for field in checker.FILE_FIELDS:
            self.data[field] = field + ".txt"
            (self.root / self.data[field]).write_text("Explicit checker fixture content\n", encoding="utf-8")

    def run_check(self, run=True):
        (self.root / "research.json").write_text(json.dumps(self.data), encoding="utf-8")
        report = self.root / "report.json"
        cmd = [sys.executable, str(CHECKER), "--root", str(self.root), "--report", str(report)]
        if run:
            cmd.append("--run")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, json.loads(report.read_text(encoding="utf-8"))

    def test_structure_only_never_claims_execution(self):
        code, report = self.run_check(False)
        self.assertEqual(code, 0)
        self.assertTrue(all(x["status"] == "not_run" for x in report["execution"].values()))
        self.assertEqual(report["scientific_review"], "pending")

    def test_actual_success_still_requires_human_review(self):
        code, report = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(report["execution"]["verify"]["status"], "passed")
        self.assertEqual(report["scientific_review"], "pending")

    def test_missing_criteria_fails_before_execution(self):
        (self.root / self.data["criteria_file"]).unlink()
        code, report = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["install"]["status"], "not_run")

    def test_failed_smoke_does_not_run_verify(self):
        self.data["commands"]["smoke"] = ["python", "-c", "raise SystemExit(4)"]
        code, report = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["smoke"]["exit_code"], 4)
        self.assertEqual(report["execution"]["verify"]["status"], "not_run")

    def test_failed_verify_stays_failed(self):
        self.data["commands"]["verify"] = ["python", "-c", "raise SystemExit(3)"]
        code, report = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["verify"]["status"], "failed")

    def test_exploration_may_defer_science_but_cannot_pass_it(self):
        self.data.update(kind="exploration", manual_review_reason="Interpretation requires a human reviewer")
        self.data["commands"]["verify"] = []
        code, report = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(report["execution"]["verify"]["status"], "not_run")

    def test_development_cannot_silently_skip_verification(self):
        self.data["commands"]["verify"] = []
        self.assertTrue(checker.validate(self.root, self.data))

    def test_changed_reference_fails_checksum(self):
        p = self.root / "reference.txt"
        p.write_text("original", encoding="utf-8")
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        self.data["references"] = [{"source": "Independent fixture", "license": "MIT", "scope": "Checker fixture only", "file": "reference.txt", "sha256": digest}]
        self.assertEqual(checker.validate(self.root, self.data), [])
        p.write_text("changed", encoding="utf-8")
        self.assertTrue(checker.validate(self.root, self.data))

    def test_path_escape_is_rejected(self):
        self.data["criteria_file"] = "../outside.md"
        self.assertTrue(checker.validate(self.root, self.data))

    def test_shell_command_string_is_rejected(self):
        self.data["commands"]["smoke"] = "python a.py && echo approved"
        self.assertTrue(checker.validate(self.root, self.data))

    def test_platform_mismatch_blocks_execution(self):
        self.data["supported_platforms"] = ["darwin" if sys.platform != "darwin" else "linux"]
        code, report = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["install"]["status"], "not_run")

    def test_missing_output_fails_after_commands(self):
        self.data["expected_outputs"] = ["absent-result.json"]
        code, report = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn("Declared output missing", " ".join(report["errors"]))

    def test_reproduction_requires_reference(self):
        self.data["kind"] = "reproduction"
        self.assertTrue(checker.validate(self.root, self.data))

    def test_untouched_template_does_not_claim_readiness(self):
        template = ROOT / "templates/research-project"
        data = json.loads((template / "research.json").read_text(encoding="utf-8"))
        self.assertTrue(checker.validate(template, data))

    def test_secret_bearing_pr_workflow_is_rejected(self):
        d = self.root / "workflows"
        d.mkdir()
        p = d / "unsafe.yml"
        p.write_text("on:\n  pull_request_target:\npermissions:\n  contents: write\njobs: {}\n", encoding="utf-8")
        self.assertTrue(validate_yaml(p))

    def test_new_organization_renders_without_old_links(self):
        (self.root / "content").mkdir()
        import shutil
        for path in (ROOT / "content").glob("*.md"):
            shutil.copy2(path, self.root / "content" / path.name)
        cfg = json.loads((ROOT / "community.json").read_text(encoding="utf-8"))
        cfg["organization"] = "Migration-Rehearsal"
        cfg["maintainers"] = ["another-maintainer"]
        (self.root / "community.json").write_text(json.dumps(cfg), encoding="utf-8")
        for text in render(self.root).values():
            self.assertNotIn("github.com/Shenyan-kosmoX/", text)
            self.assertIn("Migration-Rehearsal", text)

    def test_full_local_migration_preserves_valid_links_and_resets_activation(self):
        import shutil
        from rebrand import rebrand
        from check import check
        source_profile = ROOT.parent / "Shenyan-kosmoX-profile"
        if not source_profile.is_dir():
            self.skipTest("Cross-repository migration rehearsal requires the local profile checkout")
        community = self.root / "community"
        profile = self.root / "profile"
        shutil.copytree(ROOT, community, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", ".local"))
        shutil.copytree(source_profile, profile, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        result = rebrand(community, profile, "Migration-Rehearsal", ["another-maintainer"], apply=True)
        self.assertTrue(result["applied_locally"])
        self.assertEqual(check(community, profile), [])
        cfg = json.loads((community / "community.json").read_text(encoding="utf-8"))
        self.assertFalse(cfg["discussions_enabled"])
        self.assertFalse(cfg["applications_open"])
        self.assertNotIn("Shenyan-kosmoX", (profile / "profile/README.md").read_text(encoding="utf-8").split("https://github.com/")[-1])


if __name__ == "__main__":
    unittest.main()
