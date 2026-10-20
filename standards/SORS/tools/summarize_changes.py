"""List changed SORS sections and related maintenance files for a PR review."""
import argparse
import html
import os
from pathlib import Path
import re
import subprocess

import yaml

SECTIONS = {
    "environments": "运行环境", "execution": "执行步骤", "criteria": "判断依据",
    "references": "参考材料", "checks": "检查方法", "results": "结果记录",
    "model": "模型说明", "inputs": "输入材料", "outputs": "输出约定",
    "licensing": "来源与许可", "capabilities": "能力目录", "cases": "案例目录",
    "documents": "文档入口", "limitations": "适用范围", "extensions": "领域扩展",
}
PATTERN = re.compile(r"(^|/)(research\.(ya?ml|json)|case\.(ya?ml|json))$|reference|baseline|tolerance|criteria|verify|validat|requirements|pyproject|license|sources|\.github/|(^|/)(tools|tests)/", re.I)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, encoding="utf-8", errors="replace")


def load_at(root, revision, path):
    try:
        value = yaml.safe_load(git(root, "show", f"{revision}:{path}"))
        return value if isinstance(value, dict) else {}
    except (subprocess.CalledProcessError, yaml.YAMLError):
        return {}


def summarize(root, base):
    names = git(root, "diff", "--name-only", "-z", base, "HEAD").split("\0")
    rows = []
    for name in names:
        if not name or not PATTERN.search(name):
            continue
        changed = []
        if Path(name).name in ("research.yaml", "research.yml", "research.json", "case.yaml", "case.yml", "case.json"):
            before, after = load_at(root, base, name), load_at(root, "HEAD", name)
            changed = [label for key, label in SECTIONS.items() if before.get(key) != after.get(key)]
        rows.append((name, changed))
    message = "## 共同维护提示\n\n"
    if rows:
        for name, sections in rows:
            clean = html.escape(name).replace("\n", " ").replace("\r", " ")
            message += f"- <code>{clean}</code>"
            if sections:
                message += "：" + "、".join(sections)
            message += "\n"
        message += "\n请结合这些材料的用途，核对受影响的案例和说明。新增计算、参照或判据的科学含义由项目维护者审阅。\n"
    else:
        message += "本次改动没有命中上述索引与维护路径；其他代码和正文仍可按项目习惯审阅。\n"
    return message


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.base):
        parser.error("Use a full base commit SHA")
    message = summarize(args.root.resolve(), args.base)
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(message)


if __name__ == "__main__":
    main()
