"""Local/CI checks for public community content. No network or scientific claims."""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from build import ROOT, load_config, render


def local_links(path):
    text = path.read_text(encoding="utf-8")
    # Code examples are not navigable links.
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    targets = re.findall(r"\]\(<?([^\s)>]+)>?\)", text)
    targets += re.findall(r'(?:href|src)="([^"]+)"', text)
    for target in targets:
        if target.startswith(("https://", "http://", "#", "mailto:")) or "{{" in target:
            continue
        from urllib.parse import unquote
        local = unquote(target.split("#")[0].split("?")[0])
        if local and not (path.parent / local).exists():
            yield f"{path.name}: missing local link {local}"


def validate_yaml(path):
    errors = []
    try:
        obj = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if not isinstance(obj, dict):
            return [f"{path.name}: YAML must contain a mapping"]
    except yaml.YAMLError as exc:
        return [f"{path.name}: invalid YAML: {exc}"]
    if path.parent.name in ("ISSUE_TEMPLATE", "DISCUSSION_TEMPLATE") or path.parent.name == "forms":
        if path.name == "config.yml":
            return errors
        body = obj.get("body")
        if not isinstance(body, list) or not body:
            errors.append(f"{path.name}: form needs body fields")
        else:
            ids = []
            for field in body:
                kind = field.get("type")
                if kind not in ("markdown", "input", "textarea", "dropdown", "checkboxes"):
                    errors.append(f"{path.name}: unsupported form field {kind}")
                if kind != "markdown":
                    ids.append(field.get("id"))
                    if not field.get("attributes", {}).get("label"):
                        errors.append(f"{path.name}: field needs label")
            if None in ids or len(ids) != len(set(ids)):
                errors.append(f"{path.name}: field IDs must exist and be unique")
    if path.parent.name == "workflows":
        events = obj.get("on", {})
        if "pull_request_target" in events:
            errors.append(f"{path.name}: pull_request_target is forbidden")
        if obj.get("permissions") != {"contents": "read"}:
            errors.append(f"{path.name}: use read-only contents permission")
        for job in obj.get("jobs", {}).values():
            if job.get("runs-on") != "ubuntu-latest":
                errors.append(f"{path.name}: starter PR jobs require a disposable GitHub Linux runner")
            if not job.get("timeout-minutes"):
                errors.append(f"{path.name}: each job requires a timeout")
            for step in job.get("steps", []):
                if "uses" in step and not re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", step["uses"]):
                    errors.append(f"{path.name}: pin official actions to verified commit SHAs")
        if "secrets." in path.read_text(encoding="utf-8"):
            errors.append(f"{path.name}: PR checks must not receive secrets")
    return errors


def check(root, profile=None):
    errors = []
    required = ["README.md", "START-HERE.md", "MANIFESTO-NOTE.md", "CONTRIBUTING.md", "GOVERNANCE.md", "LICENSE", "LICENSING.md", "ABOUT.md", "CODE_OF_CONDUCT.md", "docs/REVIEW.md", "docs/MIGRATION.md"]
    for name in required:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    cfg = load_config(root)
    rendered = render(root)
    if (root / "README.md").read_text(encoding="utf-8") != rendered["community"]:
        errors.append("README drift: run tools/build.py")
    expected_owners = "* " + " ".join("@" + name for name in cfg["maintainers"]) + "\n"
    if (root / ".github/CODEOWNERS").read_text(encoding="utf-8") != expected_owners:
        errors.append("CODEOWNERS drift: rebuild and verify maintainer permissions")
    if (root / "tools/sensitive_changes.py").read_bytes() != (root / "templates/research-project/tools/sensitive_changes.py").read_bytes():
        errors.append("Research starter sensitive-change detector drift: rebuild")
    for category in cfg["discussion_categories"]:
        if not (root / ".github/DISCUSSION_TEMPLATE" / (category["slug"] + ".yml")).is_file():
            errors.append(f"Missing discussion form for {category['slug']}")
    if not cfg["applications_open"] and (root / ".github/ISSUE_TEMPLATE/api-support.yml").exists():
        errors.append("Resource intake form is enabled while applications are closed")
    if cfg["applications_open"] and ("<!-- resource-status:fundraising -->" in (root / "docs/RESOURCES.md").read_text(encoding="utf-8") or not (root / ".github/ISSUE_TEMPLATE/api-support.yml").exists()):
        errors.append("Resource status/form does not match active configuration")
    if cfg["discussions_enabled"] and "讨论区尚未启用" in (root / "docs/DISCUSSIONS.md").read_text(encoding="utf-8"):
        errors.append("Discussion status does not match active configuration")
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(p in (".git", ".venv", ".local", "__pycache__", "review-output") for p in rel.parts) or not path.is_file():
            continue
        # content/ links are relative to their generated destination, checked above/below.
        if path.suffix == ".md" and rel.parts[0] != "content":
            errors.extend(local_links(path))
        if path.suffix in (".yml", ".yaml"):
            errors.extend(validate_yaml(path))
    if profile:
        if (profile / "profile/README.md").read_text(encoding="utf-8") != rendered["profile"]:
            errors.append("Profile README drift: rebuild")
        for path in profile.rglob("*.md"):
            errors.extend(local_links(path))
        for required_asset in ("profile/assets/hero.png", "profile/assets/avatar.png", "profile/assets/mark.svg", "ASSET-SOURCES.md", "MANIFESTO.md", "LICENSE"):
            if not (profile / required_asset).is_file():
                errors.append(f"Missing profile asset: {required_asset}")
        # Resolve our own cross-repository links against the staged repositories.
        route = {cfg["community_repository"]: root, cfg["profile_repository"]: profile}
        pattern = re.compile(r"https://github\.com/" + re.escape(cfg["organization"]) + r"/([^/]+)/blob/" + re.escape(cfg["default_branch"]) + r"/([^\s)\"<>#]+)")
        for base in (root, profile):
            for path in base.rglob("*.md"):
                if ".git" in path.parts:
                    continue
                for repo, target in pattern.findall(path.read_text(encoding="utf-8")):
                    if repo in route and not (route[repo] / target).exists():
                        errors.append(f"{path.name}: broken staged cross-repo link {repo}/{target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        errors = check(args.root.resolve(), args.profile.resolve() if args.profile else None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [str(exc)]
    result = {"status": "failed" if errors else "passed", "errors": errors,
              "scope": "Local structure, forms, workflows and links; remote activation and science not verified."}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
