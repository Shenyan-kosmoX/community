"""Plan/apply local organization routing changes. Never calls GitHub or Git."""
import argparse
import json
import re
from pathlib import Path

from build import ROOT, load_config, write


def rebrand(root, profile, organization, maintainers, apply=False):
    if not re.fullmatch(r"[A-Za-z0-9-]+", organization):
        raise ValueError("Organization must be a GitHub login")
    if not maintainers or any(not re.fullmatch(r"[A-Za-z0-9-]+", x) for x in maintainers):
        raise ValueError("Supply actual destination maintainer logins")
    cfg = load_config(root)
    if apply and (cfg["applications_open"] or (root / ".github/ISSUE_TEMPLATE/api-support.yml").exists()):
        raise ValueError("Explicitly deactivate and document resource intake before applying migration")
    old = cfg["organization"]
    replacements = [(f"https://github.com/{old}/", f"https://github.com/{organization}/"),
                    (f"https://github.com/{old})", f"https://github.com/{organization})"),
                    (f"https://raw.githubusercontent.com/{old}/", f"https://raw.githubusercontent.com/{organization}/")]
    # Public maintainer contact is a role binding, not historical authorship.
    for previous in cfg["maintainers"]:
        replacements += [(f"[@{previous}](https://github.com/{previous})", f"[@{maintainers[0]}](https://github.com/{maintainers[0]})")]
    changes = []
    for base in (root, profile):
        for p in base.rglob("*.md"):
            if any(x in p.parts for x in (".git", ".venv", ".local", "review-output")):
                continue
            before = p.read_text(encoding="utf-8")
            after = before
            for src, dst in replacements:
                after = after.replace(src, dst)
            if after != before:
                changes.append(str(p.relative_to(base)))
                if apply:
                    p.write_text(after, encoding="utf-8")
    cfg.update(organization=organization, maintainers=maintainers,
               discussions_enabled=False, applications_open=False)
    # Keep project URLs: moving the organization does NOT imply every upstream project moved.
    if apply:
        status_path = root / "docs/DISCUSSIONS.md"
        text = status_path.read_text(encoding="utf-8")
        text = re.sub(r"<!-- status:start -->.*?<!-- status:end -->", "<!-- status:start -->\n讨论区尚未启用。下列类别为迁移目标配置，需在新组织实际核验后再开放入口。\n<!-- status:end -->", text, flags=re.S)
        status_path.write_text(text, encoding="utf-8")
        (root / "community.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write(root, profile)
    return {"from": old, "to": organization, "applied_locally": apply,
            "changed_documents": changes, "reset_activation": ["discussions", "api_support"],
            "manual_checks": ["actual organization/repository permissions", "project URLs", "Discussions and issue history", "Secrets", "branch rules", "avatar", "source license authorship"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--organization", required=True)
    p.add_argument("--maintainer", action="append", required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    print(json.dumps(rebrand(a.root.resolve(), a.profile.resolve(), a.organization, a.maintainer, a.apply), ensure_ascii=False, indent=2))
