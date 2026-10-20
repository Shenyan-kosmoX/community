"""Behavioral coverage of the SORS indexes and explicit execution boundary."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "standards/SORS/tools/check_project.py"
spec = importlib.util.spec_from_file_location("sors_check", CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SorsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sors-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "README.md").write_text("# Fixture\n\nA real document for structural tests.\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("Fixture license text", encoding="utf-8")
        self.project = {
            "schema_version": "0.1", "kind": "project",
            "project": {"id": "fixture", "name": "Fixture", "domain": "test", "stage": "development", "maintainers": ["test-maintainer"]},
            "documents": {key: "README.md" for key in ("overview", "research", "usage", "validation", "limitations", "sources", "contributing")},
            "capabilities": [{"id": "calculation", "description": "Fixture calculation"}],
            "environments": [{"id": "python", "description": "Test Python", "platforms": [sys.platform]}],
            "assets": [], "cases": [{"id": "example", "manifest": "case.json"}],
            "licensing": {"code_license": "MIT", "license_file": "LICENSE", "sources": "README.md"}, "extensions": []}
        self.case = {
            "schema_version": "0.1", "kind": "case", "id": "example", "project_id": "fixture", "title": "Fixture", "stage": "planned",
            "question": {"summary": "Can the checker identify malformed cases?"}, "capability_refs": ["calculation"],
            "model": {"description": "A subprocess fixture"}, "inputs": [],
            "execution": {"environment_ref": "python", "cwd": ".", "steps": [{"id": "run", "role": "run", "mode": "command", "argv": ["python", "-c", "from pathlib import Path; Path('result.txt').write_text('fresh result')"], "output_refs": ["result"]}]},
            "outputs": [{"id": "result", "description": "Output", "path": "result.txt"}],
            "references": [{"id": "theory", "description": "Explanation", "record": {"path": "README.md"}}],
            "criteria": [{"id": "readable", "description": "File can be read", "representation": "documented", "record": {"path": "README.md"}}],
            "checks": [{"id": "inspect", "method": "Read result", "criterion_refs": ["readable"], "reference_refs": ["theory"], "output_refs": ["result"]}],
            "results": {"status": "planned", "records": [], "artifacts": []}, "limitations": "README.md"}

    def save(self):
        (self.root / "research.json").write_text(json.dumps(self.project), encoding="utf-8")
        (self.root / "case.json").write_text(json.dumps(self.case), encoding="utf-8")

    def errors(self):
        self.save()
        return checker.validate(self.root)[2]

    def cli(self, *args):
        self.save()
        report = self.root / "report.json"
        result = subprocess.run([sys.executable, str(CHECKER), "--root", str(self.root), "--report", str(report), *args], capture_output=True, text=True)
        return result.returncode, json.loads(report.read_text(encoding="utf-8"))

    def test_structure_never_runs_commands(self):
        code, report = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(report["execution"]["status"], "not_run")
        self.assertEqual(report["scientific_review"], "pending")
        self.assertFalse((self.root / "result.txt").exists())

    def test_missing_part_and_empty_mapping_fail(self):
        del self.project["documents"]["validation"]
        self.assertTrue(self.errors())
        self.project = {}
        self.assertTrue(self.errors())

    def test_unknown_environment_fails(self):
        self.case["execution"]["environment_ref"] = "unknown"
        self.assertIn("unknown reference", " ".join(self.errors()))

    def test_documents_and_license_require_nonempty_files(self):
        self.project["documents"]["research"] = "."
        self.assertIn("nonempty file", " ".join(self.errors()))
        self.project["documents"]["research"] = "README.md"
        (self.root / "LICENSE").write_text("", encoding="utf-8")
        self.assertIn("nonempty file", " ".join(self.errors()))

    def test_duplicate_ids_fail(self):
        self.project["capabilities"] *= 2
        self.assertIn("duplicate ID", " ".join(self.errors()))

    def test_dependency_cycle_fails(self):
        self.case["execution"]["steps"][0]["depends_on"] = ["run"]
        self.assertIn("cycle", " ".join(self.errors()))

    def test_unknown_input_output_and_criterion_refs_fail(self):
        self.case["execution"]["steps"][0]["input_refs"] = ["missing-input"]
        self.case["checks"][0]["criterion_refs"] = ["missing-criterion"]
        self.case["checks"][0]["output_refs"] = ["missing-output"]
        errors = " ".join(self.errors())
        for name in ("missing-input", "missing-criterion", "missing-output"):
            self.assertIn(name, errors)

    def test_path_escape_and_windows_absolute_fail(self):
        for value in ("../outside.md", "C:/private.md", "/private.md", "..%2Foutside.md"):
            self.project["documents"]["research"] = value
            self.assertTrue(self.errors(), value)

    def test_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "secret.md"
            target.write_text("outside", encoding="utf-8")
            try:
                (self.root / "link.md").symlink_to(target)
            except OSError:
                self.skipTest("Host does not permit symbolic links")
            self.project["documents"]["research"] = "link.md"
            self.assertIn("escapes", " ".join(self.errors()))

    def test_missing_reference_and_link_fail(self):
        self.case["references"][0]["record"] = {"path": "missing.json"}
        (self.root / "README.md").write_text("[Missing](absent.md)\n", encoding="utf-8")
        errors = " ".join(self.errors())
        self.assertIn("missing.json", errors)
        self.assertIn("absent.md", errors)

    def test_expected_outputs_can_be_absent(self):
        self.assertEqual(self.errors(), [])

    def test_observed_results_require_existing_records(self):
        self.case["results"] = {"status": "observed", "records": [{"path": "missing.json"}], "artifacts": []}
        self.assertTrue(self.errors())
        self.case["results"]["records"] = []
        self.assertTrue(self.errors())

    def test_external_historical_material_has_explicit_retrieval(self):
        self.case["references"][0]["record"] = {"availability": "not_bundled", "description": "Large historical output", "retrieval": "Rerun the published entry point"}
        self.assertEqual(self.errors(), [])
        del self.case["references"][0]["record"]["retrieval"]
        self.assertTrue(self.errors())
        self.case["references"][0]["record"]["retrieval"] = "Rerun the published entry point"
        self.case["references"][0]["record"]["path"] = "fake-available-file.json"
        self.assertTrue(self.errors())

    def test_planned_documented_case_is_valid(self):
        self.case["execution"]["steps"] = [{"id": "plan", "role": "plan", "mode": "documented", "instructions": {"path": "README.md"}}]
        self.assertEqual(self.errors(), [])

    def test_old_output_cannot_pass_new_execution(self):
        (self.root / "result.txt").write_text("old result", encoding="utf-8")
        self.case["execution"]["steps"][0]["argv"] = ["python", "-c", "print('no calculation')"]
        code, report = self.cli("--run", "--case", "example", "--step", "run")
        self.assertNotEqual(code, 0)
        self.assertIn("unchanged", " ".join(report["execution"]["errors"]))

    def test_failed_command_remains_failed(self):
        self.case["execution"]["steps"][0]["argv"] = ["python", "-c", "raise SystemExit(7)"]
        code, report = self.cli("--run", "--case", "example", "--step", "run")
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["steps"][0]["exit_code"], 7)
        self.assertEqual(report["structure"]["status"], "passed")

    def test_success_keeps_scientific_review_separate(self):
        code, report = self.cli("--run", "--case", "example", "--step", "run")
        self.assertEqual(code, 0)
        self.assertEqual(report["execution"]["status"], "passed")
        self.assertEqual(report["scientific_review"], "pending")

    def test_plan_is_not_reported_as_calculation(self):
        self.case["execution"]["steps"][0]["role"] = "plan"
        code, report = self.cli("--run", "--case", "example", "--step", "run")
        self.assertEqual(code, 0)
        self.assertEqual(report["execution"]["status"], "planned")

    def test_dependencies_need_explicit_selection(self):
        self.case["execution"]["steps"].append({"id": "plot", "mode": "command", "role": "plot", "argv": ["python", "-c", "print('plot')"], "depends_on": ["run"]})
        code, report = self.cli("--run", "--case", "example", "--step", "plot")
        self.assertNotEqual(code, 0)
        self.assertFalse((self.root / "result.txt").exists())
        self.assertIn("explicitly select", " ".join(report["execution"]["errors"]))

    def test_yaml_duplicate_keys_fail(self):
        self.save()
        (self.root / "research.json").unlink()
        (self.root / "research.yaml").write_text("kind: project\nkind: case\n", encoding="utf-8")
        self.assertIn("Duplicate mapping key", " ".join(checker.validate(self.root)[2]))

    def test_shell_string_is_rejected(self):
        self.case["execution"]["steps"][0]["argv"] = "python a.py && echo pass"
        self.assertTrue(self.errors())

    def test_platform_mismatch_blocks_execution(self):
        self.project["environments"][0]["platforms"] = ["unavailable-os"]
        code, report = self.cli("--run", "--case", "example", "--step", "run")
        self.assertNotEqual(code, 0)
        self.assertEqual(report["execution"]["steps"][0]["status"], "not_run")


if __name__ == "__main__":
    unittest.main()
