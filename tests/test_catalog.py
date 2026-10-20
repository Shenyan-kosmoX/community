"""Catalog navigation, publication status, and migration behavior."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build import catalog_projects, project_link, render


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shenyan-catalog-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "content").mkdir()
        # Check the rendering contract independently of editorial homepage changes.
        (self.root / "content/community.md").write_text(
            "{{community_base}}\n{{project_section}}\n", encoding="utf-8")
        (self.root / "content/profile.md").write_text(
            "{{community_base}}\n{{featured_project_section}}\n", encoding="utf-8")
        self.cfg = json.loads((ROOT / "community.json").read_text(encoding="utf-8"))
        self.project = {
            "id": "example-research", "name": "Example Research", "direction": "Field research",
            "status": "Public", "url": "https://github.com/Original-Org/example-research",
            "verified": True, "featured": True,
            "domains": ["物理", "数学"], "formats": ["Python 库", "CLI"],
            "use": "Calculate an example", "summary": "An example for catalog behavior.",
            "links": {"run": "docs/RUN.md", "development": "docs/HISTORY.md"},
        }
        self.cfg["projects"] = [self.project]

    def rendered(self):
        (self.root / "community.json").write_text(json.dumps(self.cfg), encoding="utf-8")
        return render(self.root)

    def test_multilabel_indexes_link_to_one_project_entry(self):
        catalog = self.rendered()["catalog"]
        self.assertEqual(catalog.count("## Example Research\n"), 1)
        self.assertEqual(catalog.count('id="project-example-research"'), 1)
        self.assertEqual(catalog.count("[Example Research](#user-content-project-example-research)"), 4)
        for label in ("物理", "数学", "Python 库", "CLI"):
            self.assertIn(f"| {label} | [Example Research]", catalog)

    def test_nonfeatured_project_is_kept_in_full_directory(self):
        extra = dict(self.project, id="other", name="Other Project", featured=False,
                     url="https://github.com/Original-Org/other")
        self.cfg["projects"].append(extra)
        rendered = self.rendered()
        self.assertNotIn("Other Project", rendered["profile"])
        self.assertIn("Other Project", rendered["community"])
        self.assertIn("## Other Project", rendered["catalog"])

    def test_unpublished_project_has_no_public_links_or_category(self):
        self.project.update(verified=False, domains=["Hidden domain"], formats=["Hidden format"])
        for page in self.rendered().values():
            self.assertNotIn("Example Research", page)
            self.assertNotIn("Original-Org", page)
            self.assertNotIn("Hidden domain", page)
            self.assertNotIn("Hidden format", page)

    def test_unpublished_entry_still_requires_boolean_status(self):
        self.project["verified"] = "false"
        with self.assertRaisesRegex(ValueError, "boolean"):
            self.rendered()

    def test_duplicate_identity_or_repository_is_rejected(self):
        for change in ({"id": "other"}, {"url": "https://github.com/Original-Org/other"}):
            with self.subTest(change=change):
                self.cfg["projects"] = [self.project, dict(self.project, **change)]
                with self.assertRaisesRegex(ValueError, "unique"):
                    self.rendered()

    def test_invalid_project_id_is_rejected(self):
        for pid in ("a b", "../escape", "Uppercase", "html\"id", ""):
            with self.subTest(pid=pid):
                self.project["id"] = pid
                with self.assertRaisesRegex(ValueError, "id"):
                    self.rendered()

    def test_skill_entries_belong_to_their_project(self):
        self.project["skills"] = [
            {"id": "style-learn", "name": "Learn Style", "description": "Study a supplied example.",
             "path": "skills/style-learn/SKILL.md"},
            {"id": "compose", "name": "Compose", "description": "Prepare a draft.",
             "path": "skills/compose/SKILL.md"},
        ]
        catalog = self.rendered()["catalog"]
        self.assertIn("### 这个项目提供的 Skills", catalog)
        self.assertIn("https://github.com/Original-Org/example-research/blob/main/skills/compose/SKILL.md", catalog)
        self.assertEqual(catalog.count("## Example Research\n"), 1)
        self.assertNotIn("## Compose", catalog)

    def test_duplicate_skill_id_is_rejected(self):
        skill = {"id": "compose", "name": "Compose", "description": "Prepare a draft.", "path": "skills/compose.md"}
        self.project["skills"] = [skill, dict(skill)]
        with self.assertRaisesRegex(ValueError, "Skill IDs"):
            self.rendered()

    def test_foreign_repository_and_unsafe_links_are_rejected(self):
        for path in ("../outside.md", "%2e%2e/outside.md", "/absolute.md", "a\\b.md",
                     "javascript:alert(1)", "https://example.com/doc", "//example.com/doc",
                     "https://github.com/Original-Org/unrelated/docs/RUN.md",
                     "https://github.com/Original-Org/example-research-other/docs/RUN.md",
                     "https://github.com/Original-Org/example-research/blob/main/../private.md"):
            with self.subTest(path=path):
                self.project["links"] = {"run": path}
                with self.assertRaises(ValueError):
                    self.rendered()

    def test_link_roles_do_not_silently_disappear(self):
        self.project["links"] = {"typo": "docs/RUN.md"}
        with self.assertRaisesRegex(ValueError, "link role"):
            self.rendered()

    def test_relative_links_keep_project_owner_when_community_moves(self):
        self.cfg["organization"] = "New-Org"
        catalog = self.rendered()["catalog"]
        self.assertIn("https://github.com/New-Org/community/discussions", catalog)
        self.assertIn("https://github.com/Original-Org/example-research/blob/main/docs/RUN.md", catalog)
        self.assertNotIn("https://github.com/New-Org/example-research", catalog)

    def test_moved_project_updates_every_relative_entry(self):
        self.project["url"] = "https://github.com/New-Org/example-research"
        self.project["examples"] = [{"name": "Demo", "description": "Try the example.", "path": "cases/demo.md"}]
        catalog = self.rendered()["catalog"]
        self.assertNotIn("Original-Org", catalog)
        for path in ("docs/RUN.md", "docs/HISTORY.md", "cases/demo.md"):
            self.assertIn(f"https://github.com/New-Org/example-research/blob/main/{path}", catalog)

    def test_project_specific_branch_and_anchor_are_preserved(self):
        self.project["branch"] = "stable"
        self.assertEqual(project_link(self.project, "README.md#installation"),
                         "https://github.com/Original-Org/example-research/blob/stable/README.md#installation")

    def test_legacy_project_configuration_remains_usable(self):
        for key in ("id", "domains", "formats", "featured", "links", "summary", "use"):
            self.project.pop(key)
        rendered = self.rendered()
        self.assertIn("Example Research", rendered["profile"])
        self.assertIn('id="project-example-research"', rendered["catalog"])

    def test_existing_science_entries_keep_full_capability_and_case_routes(self):
        actual = json.loads((ROOT / "community.json").read_text(encoding="utf-8"))
        scientific = {p["id"]: p for p in catalog_projects(actual)}
        for pid in ("floquet-maxwell", "ecodynamics"):
            with self.subTest(project=pid):
                p = scientific[pid]
                self.assertEqual(p["links"]["capabilities"], "docs/sors/CAPABILITIES.md")
                self.assertEqual(p["links"]["cases"], "docs/sors/CASES.md")
                self.assertGreater(len(p["capabilities"]), 1)
                self.assertGreater(len(p["examples"]), 1)


if __name__ == "__main__":
    unittest.main()
