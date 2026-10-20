"""Render community entry points and the project catalog from one configuration."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

LINK_LABELS = {
    "run": "安装与第一次运行", "capabilities": "完整能力地图", "cases": "全部案例",
    "results": "研究结果", "development": "作者开发记录", "skills": "Skills 使用指南",
}


def catalog_text(value, field):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "|\n\r[]<>"):
        raise ValueError(f"Invalid project {field}: expected plain text")
    return value


def project_link(project, target, branch="main"):
    """Resolve a documented repository-relative path without changing its owner."""
    if not isinstance(target, str) or not target or any(c in target for c in "\r\n\t ()<>\\"):
        raise ValueError("Invalid project link")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        base = urlsplit(project["url"])
        if parsed.scheme != "https" or parsed.netloc != "github.com" or not (
            parsed.path == base.path or parsed.path.startswith(base.path + "/")
        ):
            raise ValueError("Project links must belong to their project repository")
        path = parsed.path
    else:
        path = parsed.path
        if not path or path.startswith("/") or parsed.query:
            raise ValueError("Project links must use repository-relative paths")
    decoded = unquote(path)
    if any(part in (".", "..") for part in decoded.split("/")) or "\\" in decoded:
        raise ValueError("Project links cannot traverse parent directories")
    if parsed.scheme:
        return target
    return f"{project['url']}/blob/{project.get('branch', branch)}/{target}"


def catalog_projects(cfg):
    """Validate all entries and return only projects ready for public navigation.

    Existing v1 name/direction/status/url entries remain valid. Their repository
    name supplies a stable ID; extended entries carry explicit classification.
    """
    projects = cfg.get("projects", [])
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")
    published, seen_ids, seen_urls = [], set(), set()
    for source in projects:
        if not isinstance(source, dict):
            raise ValueError("Each project must be an object")
        p = dict(source)
        if not isinstance(p.get("url"), str) or not re.fullmatch(
            r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", p["url"]
        ):
            raise ValueError("Project URL must identify a GitHub repository")
        p.setdefault("id", p["url"].rsplit("/", 1)[-1].lower().replace("_", "-"))
        if not isinstance(p["id"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["id"]):
            raise ValueError("Project id must use lowercase words joined with hyphens")
        if p["id"] in seen_ids or p["url"].lower() in seen_urls:
            raise ValueError("Project IDs and repository URLs must be unique")
        seen_ids.add(p["id"])
        seen_urls.add(p["url"].lower())
        for field in ("name", "direction", "status"):
            catalog_text(p.get(field), field)
        for field in ("verified", "featured"):
            p.setdefault(field, field == "featured")
            if type(p[field]) is not bool:
                raise ValueError(f"Project {field} must be a boolean")
        if "branch" in p and not re.fullmatch(r"[A-Za-z0-9_.-]+", p["branch"]):
            raise ValueError("Invalid project branch")
        for field, fallback in (("domains", ["其他研究与工具"]), ("formats", ["项目仓库"])):
            p.setdefault(field, fallback)
            if not isinstance(p[field], list) or not p[field]:
                raise ValueError(f"Project {field} must be a nonempty list")
            for tag in p[field]:
                catalog_text(tag, field)
            if len(p[field]) != len(set(p[field])):
                raise ValueError(f"Repeated project {field} label")
        for field in ("summary", "case_summary", "use"):
            if field in p:
                catalog_text(p[field], field)
        links = p.get("links", {})
        if not isinstance(links, dict) or any(key not in LINK_LABELS for key in links):
            raise ValueError("Unknown project link role")
        for target in links.values():
            project_link(p, target, cfg["default_branch"])
        for field in ("capabilities", "examples", "skills"):
            entries = p.get(field, [])
            if not isinstance(entries, list):
                raise ValueError(f"Project {field} must be a list")
            skill_ids = set()
            for item in entries:
                if not isinstance(item, dict):
                    raise ValueError(f"Project {field} entries must be objects")
                catalog_text(item.get("name"), field)
                catalog_text(item.get("description"), field)
                if field in ("examples", "skills"):
                    project_link(p, item.get("path"), cfg["default_branch"])
                if field == "skills":
                    sid = item.get("id", "")
                    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid) or sid in skill_ids:
                        raise ValueError("Skill IDs must be valid and unique within their project")
                    skill_ids.add(sid)
        if p["verified"]:
            published.append(p)
    return published


def project_table(projects):
    if not projects:
        return "项目正在整理中，欢迎先来讨论你关心的问题。"
    rows = ["| 项目 | 可以做什么 | 提供形式 |", "| --- | --- | --- |"]
    for p in projects:
        rows.append(f"| [{p['name']}]({p['url']}) | {p.get('use', p['direction'])} | {'、'.join(p['formats'])} |")
    return "\n".join(rows)


def render_catalog(cfg, projects):
    community = f"https://github.com/{cfg['organization']}/{cfg['community_repository']}"
    lines = ["# 研究与工具", "",
             "想看一个结果，先去案例；想把工具用到自己的问题上，可以从运行说明开始。这里按领域和使用方式整理了社区的项目，每个条目都连接到作者维护的完整文档。", "",
             "## 按领域找", "", "| 领域 | 项目 |", "| --- | --- |"]
    for field, title in (("domains", None), ("formats", "按使用方式找")):
        if title:
            lines += ["", f"## {title}", "", "| 提供形式 | 项目 |", "| --- | --- |"]
        tags = dict.fromkeys(tag for p in projects for tag in p[field])
        for tag in tags:
            entries = " · ".join(f"[{p['name']}](#project-{p['id']})" for p in projects if tag in p[field])
            lines.append(f"| {tag} | {entries} |")
        if not tags:
            lines.append("| 整理中 | 可以先从社区讨论开始 |")
    for p in projects:
        lines += ["", f'<a id="project-{p["id"]}"></a>', "", f"## {p['name']}", "",
                  f"**{'、'.join(p['domains'])}** · {'、'.join(p['formats'])}", "",
                  p.get("summary", p["direction"]), "", p["status"], ""]
        links = [f"[进入项目]({p['url']})"]
        links += [f"[{LINK_LABELS[role]}]({project_link(p, path, cfg['default_branch'])})"
                  for role, path in p.get("links", {}).items()]
        lines += [" · ".join(links)]
        if p.get("capabilities"):
            lines += ["", "### 可以开展的工作", "", "| 工作 | 工具与方法 |", "| --- | --- |"]
            for item in p["capabilities"]:
                lines.append(f"| {item['name']} | {item['description']} |")
        if p.get("case_summary"):
            lines += ["", p["case_summary"]]
        if p.get("examples"):
            lines += ["", "### 从一个例子开始", ""]
            for item in p["examples"]:
                lines.append(f"- [{item['name']}]({project_link(p, item['path'], cfg['default_branch'])})：{item['description']}")
        if p.get("skills"):
            lines += ["", "### 这个项目提供的 Skills", "", "| Skill | 能帮你做什么 |", "| --- | --- |"]
            for item in p["skills"]:
                lines.append(f"| [{item['name']}]({project_link(p, item['path'], cfg['default_branch'])}) | {item['description']} |")
    lines += ["", "## 继续参与", "",
              "使用时遇到问题，可以在项目的 Issue 里附上输入、命令和实际结果。想讨论一个还没有定下来的方向，或分享自己做的工具，也欢迎来社区聊聊。", "",
              f"[参与讨论]({community}/discussions) · [提交自己的项目]({community}/blob/{cfg['default_branch']}/docs/PROJECT-INTAKE.md)", ""]
    return "\n".join(lines)


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
    catalog_projects(cfg)
    return cfg


def render(root=ROOT):
    cfg = load_config(root)
    org = cfg["organization"]
    branch = cfg["default_branch"]
    community_url = f"https://github.com/{org}/{cfg['community_repository']}"
    profile_url = f"https://github.com/{org}/{cfg['profile_repository']}"
    data = dict(cfg)
    data["lead_maintainer"] = cfg["maintainers"][0]
    data.update(community_base=f"{community_url}/blob/{branch}",
                profile_base=f"{profile_url}/blob/{branch}",
                asset_base=f"https://raw.githubusercontent.com/{org}/{cfg['profile_repository']}/{branch}/profile/assets")
    projects = catalog_projects(cfg)
    data["project_section"] = project_table(projects)
    data["featured_project_section"] = project_table([p for p in projects if p["featured"]])
    discussion = (f"[进入讨论区]({community_url}/discussions)" if cfg["discussions_enabled"]
                  else "讨论区尚未启用；分类和参与指引已准备")
    support = (f"[申请 API 支持]({community_url}/issues/new?template=api-support.yml)" if cfg["applications_open"]
               else "我们正在寻求资金支持，后续将开放免费的 API 额度申请，详情见[研究支持计划](docs/RESOURCES.md)")
    data["availability"] = f"{discussion}。{support}。"
    outputs = {}
    for name in ("community", "profile"):
        source = (root / "content" / f"{name}.md").read_text(encoding="utf-8")
        rendered = re.sub(r"\{\{([a-z_]+)\}\}", lambda m: str(data[m[1]]), source)
        if "{{" in rendered:
            raise ValueError("Unresolved template variable")
        outputs[name] = rendered
    outputs["catalog"] = render_catalog(cfg, projects)
    return outputs


def write(root, profile):
    cfg = load_config(root)
    rendered = render(root)
    support = root / ".github" / "ISSUE_TEMPLATE" / "api-support.yml"
    if cfg["applications_open"] and "<!-- resource-status:fundraising -->" in (root / "docs" / "RESOURCES.md").read_text(encoding="utf-8"):
        raise ValueError("Update actual resource conditions before enabling applications")
    if not cfg["applications_open"] and support.exists():
        raise ValueError("An active support form exists while applications are closed; review it explicitly")
    if cfg["discussions_enabled"] and "讨论区尚未启用" in (root / "docs" / "DISCUSSIONS.md").read_text(encoding="utf-8"):
        raise ValueError("Verify discussion settings and update status before activating the link")
    (root / "README.md").write_text(rendered["community"], encoding="utf-8")
    (root / "docs" / "RESEARCH.md").write_text(rendered["catalog"], encoding="utf-8")
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
    print("Rendered community README, profile README, project catalog, CODEOWNERS and issue navigation locally.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profile", type=Path, required=True)
    args = parser.parse_args()
    write(args.root.resolve(), args.profile.resolve())
