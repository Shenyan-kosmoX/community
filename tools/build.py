"""Render the two public entry points from one identity configuration. No network."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config(root=ROOT):
    cfg = json.loads((root / "community.json").read_text(encoding="utf-8"))
    for key in ("organization", "community_repository", "profile_repository", "default_branch"):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", cfg[key]):
            raise ValueError(f"Invalid routing value: {key}")
    if not cfg["maintainers"] or any(not re.fullmatch(r"[A-Za-z0-9-]+", x) for x in cfg["maintainers"]):
        raise ValueError("At least one explicit maintainer is required")
    for key in ("applications_open", "discussions_enabled"):
        if type(cfg[key]) is not bool:
            raise ValueError(f"{key} must be a boolean")
    return cfg


def render(root=ROOT):
    cfg = load_config(root)
    org = cfg["organization"]
    branch = cfg["default_branch"]
    community_url = f"https://github.com/{org}/{cfg['community_repository']}"
    profile_url = f"https://github.com/{org}/{cfg['profile_repository']}"
    data = dict(cfg)
    data.update(community_base=f"{community_url}/blob/{branch}",
                profile_base=f"{profile_url}/blob/{branch}",
                asset_base=f"https://raw.githubusercontent.com/{org}/{cfg['profile_repository']}/{branch}/profile/assets")
    if cfg["projects"]:
        rows = ["| 项目 | 研究方向 | 当前状态 |", "| --- | --- | --- |"]
        for p in cfg["projects"]:
            if not p.get("verified") or not p["url"].startswith("https://github.com/"):
                raise ValueError("Only verified public project entries can be published")
            for field in ("name", "direction", "status"):
                if not isinstance(p.get(field), str) or not p[field].strip() or any(c in p[field] for c in "|\n[]"):
                    raise ValueError(f"Invalid project {field}")
            rows.append(f"| [{p['name']}]({p['url']}) | {p['direction']} | {p['status']} |")
        data["project_section"] = "\n".join(rows)
    else:
        data["project_section"] = "**首批项目整理中。** 公开后，你可以在这里找到代码、运行案例和接下来想一起解决的问题。"
    discussion = (f"[进入讨论区]({community_url}/discussions)" if cfg["discussions_enabled"]
                  else "讨论区尚未启用；分类和参与指引已准备")
    support = (f"[申请 API 支持]({community_url}/issues/new?template=api-support.yml)" if cfg["applications_open"]
               else "API 支持申请尚未开放，进展会更新在[支持计划](docs/RESOURCES.md)")
    data["availability"] = f"**当前状态：** {discussion}。{support}。"
    outputs = {}
    for name in ("community", "profile"):
        source = (root / "content" / f"{name}.md").read_text(encoding="utf-8")
        rendered = re.sub(r"\{\{([a-z_]+)\}\}", lambda m: str(data[m[1]]), source)
        if "{{" in rendered:
            raise ValueError("Unresolved template variable")
        outputs[name] = rendered
    return outputs


def write(root, profile):
    cfg = load_config(root)
    rendered = render(root)
    support = root / ".github" / "ISSUE_TEMPLATE" / "api-support.yml"
    if cfg["applications_open"] and "申请尚未开放" in (root / "docs" / "RESOURCES.md").read_text(encoding="utf-8"):
        raise ValueError("Update actual resource conditions before enabling applications")
    if not cfg["applications_open"] and support.exists():
        raise ValueError("An active support form exists while applications are closed; review it explicitly")
    if cfg["discussions_enabled"] and "讨论区尚未启用" in (root / "docs" / "DISCUSSIONS.md").read_text(encoding="utf-8"):
        raise ValueError("Verify discussion settings and update status before activating the link")
    (root / "README.md").write_text(rendered["community"], encoding="utf-8")
    (profile / "profile").mkdir(parents=True, exist_ok=True)
    (profile / "profile" / "README.md").write_text(rendered["profile"], encoding="utf-8")
    owners = "* " + " ".join("@" + name for name in cfg["maintainers"]) + "\n"
    (root / ".github" / "CODEOWNERS").write_text(owners, encoding="utf-8")
    (profile / ".github").mkdir(exist_ok=True)
    (profile / ".github" / "CODEOWNERS").write_text(owners, encoding="utf-8")
    config = "blank_issues_enabled: false\ncontact_links:\n  - name: 参与与讨论指引\n    url: https://github.com/" + cfg["organization"] + "/" + cfg["community_repository"] + "/blob/" + cfg["default_branch"] + "/START-HERE.md\n    about: 先了解讨论、项目贡献与资源支持的入口\n"
    (root / ".github" / "ISSUE_TEMPLATE" / "config.yml").write_text(config, encoding="utf-8")
    # Activation is deliberate: documents must first be updated and settings verified.
    if cfg["applications_open"]:
        support.write_text((root / "templates" / "forms" / "api-support.yml").read_text(encoding="utf-8"), encoding="utf-8")
    import shutil
    shutil.copy2(root / "tools/sensitive_changes.py", root / "templates/research-project/tools/sensitive_changes.py")
    print("Rendered community README, profile README, CODEOWNERS and issue navigation locally.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profile", type=Path, required=True)
    args = parser.parse_args()
    write(args.root.resolve(), args.profile.resolve())
