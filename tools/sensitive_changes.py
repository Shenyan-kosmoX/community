"""Report changed verification/policy files without asserting scientific approval."""
import argparse
import os
import re
import subprocess
from pathlib import Path

PATTERN = re.compile(r"reference|baseline|tolerance|criteria|evidence|verify|validat|research\.json|research_check|requirements|pyproject|\.github/workflows|tools/|tests/", re.I)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-fA-F0-9]{40}", args.base):
        parser.error("Use a full base commit SHA")
    # HEAD is GitHub's PR merge checkout; compare it with the current base.
    output = subprocess.check_output(["git", "diff", "--name-only", "-z", args.base, "HEAD"], text=True)
    names = [n for n in output.split("\0") if n and PATTERN.search(n)]
    message = "## Changes requiring explicit review\n\n"
    if names:
        # Escape Markdown/HTML in untrusted filenames before producing the job summary.
        import html
        message += "".join("- <code>" + html.escape(n).replace("\n", " ") + "</code>\n" for n in names)
        message += "\nExplain changes to references, tolerances, dependencies and checkers. A successful job is NOT scientific approval.\n"
    else:
        message += "No matching paths detected. This path heuristic is not a complete review.\n"
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(message)


if __name__ == "__main__":
    main()
