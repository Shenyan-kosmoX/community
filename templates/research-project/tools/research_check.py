"""Check a scientific delivery contract; --run executes reviewed project commands.

This is not a sandbox or a certificate of scientific correctness. Run untrusted
projects only in disposable, credential-free environments.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

FILE_FIELDS = ("dependency_file", "license_file", "runbook", "criteria_file",
               "evidence_file", "limits_file", "provenance_file")


def local_file(root, value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Use a non-empty repository-relative POSIX path")
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Paths must stay in the repository")
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Symlink escapes the repository")
    return resolved


def validate(root, data):
    errors = []
    if not isinstance(data, dict):
        return ["research.json must contain an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("project_name"), str) or not data["project_name"].strip():
        errors.append("A real project_name is required")
    if not isinstance(data.get("maintainers"), list) or not data["maintainers"] or any(not isinstance(m, str) or not m.strip() for m in data["maintainers"]):
        errors.append("At least one real maintainer is required")
    if data.get("kind") not in ("reproduction", "development", "exploration"):
        errors.append("Unknown research kind")
    if data.get("python_version") != "3.12":
        errors.append("Starter workflow currently supports Python 3.12 only; update workflow and contract together")
    platforms = data.get("supported_platforms")
    if not isinstance(platforms, list) or not platforms or any(p not in ("linux", "win32", "darwin") for p in platforms):
        errors.append("supported_platforms must name supported Python platforms")
    for field in FILE_FIELDS:
        try:
            path = local_file(root, data.get(field))
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"{field}: missing or empty file")
        except ValueError as exc:
            errors.append(f"{field}: {exc}")
    commands = data.get("commands")
    if not isinstance(commands, dict):
        commands = {}
        errors.append("commands must be an object")
    for stage in ("install", "smoke", "verify"):
        argv = commands.get(stage)
        if not isinstance(argv, list) or any(not isinstance(x, str) or not x.strip() for x in argv):
            errors.append(f"{stage}: command must be an argument array")
        elif not argv:
            if stage != "verify" or data.get("kind") != "exploration" or not str(data.get("manual_review_reason", "")).strip():
                errors.append(f"{stage}: actual command required; only exploration may omit verify with a reason")
    timeout = data.get("timeout_seconds")
    if type(timeout) is not int or not 1 <= timeout <= 1200:
        errors.append("timeout_seconds must be an integer from 1 to 1200")
    refs = data.get("references")
    if not isinstance(refs, list):
        refs = []
        errors.append("references must be an array")
    for ref in refs:
        if not isinstance(ref, dict) or not all(isinstance(ref.get(k), str) and ref[k].strip() for k in ("source", "license", "scope")):
            errors.append("Each reference needs source, license and scientific scope")
            continue
        if ref.get("file"):
            try:
                path = local_file(root, ref["file"])
                digest = ref.get("sha256", "")
                if not path.is_file() or len(digest) != 64 or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    errors.append("Reference file checksum mismatch or missing checksum")
            except ValueError as exc:
                errors.append(f"Reference: {exc}")
    if data.get("kind") == "reproduction" and not refs:
        errors.append("Reproduction requires an explicit source/reference")
    outputs = data.get("expected_outputs")
    if not isinstance(outputs, list):
        errors.append("expected_outputs must be an array")
    else:
        for value in outputs:
            try:
                local_file(root, value)
            except ValueError as exc:
                errors.append(f"Output: {exc}")
    return errors


def execute(root, data):
    result = {stage: {"status": "not_run"} for stage in ("install", "smoke", "verify")}
    for stage in result:
        argv = data["commands"][stage]
        if not argv:
            result[stage]["reason"] = data["manual_review_reason"]
            continue
        if argv[0] in ("python", "python3"):
            argv = [sys.executable, *argv[1:]]
        started = time.monotonic()
        try:
            # No captured stdout in the report; project output may contain private data.
            completed = subprocess.run(argv, cwd=root, shell=False, timeout=data["timeout_seconds"], check=False)
            status = "passed" if completed.returncode == 0 else "failed"
            result[stage] = {"status": status, "exit_code": completed.returncode}
        except subprocess.TimeoutExpired:
            result[stage] = {"status": "failed", "reason": "timeout"}
        except OSError as exc:
            result[stage] = {"status": "failed", "reason": type(exc).__name__}
        result[stage]["seconds"] = round(time.monotonic() - started, 3)
        if result[stage]["status"] != "passed":
            break
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", type=Path, default=Path("research-report.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    report = {"structure": "failed", "execution": {s: {"status": "not_run"} for s in ("install", "smoke", "verify")},
              "scientific_review": "pending", "scope": "Declared checks only; no general scientific certification."}
    try:
        data = json.loads((root / "research.json").read_text(encoding="utf-8"))
        errors = validate(root, data)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    report["errors"] = errors
    if not errors:
        report["structure"] = "passed"
        if args.run:
            if sys.platform not in data["supported_platforms"]:
                errors.append(f"Execution platform {sys.platform} is not declared supported")
            elif f"{sys.version_info.major}.{sys.version_info.minor}" != data["python_version"]:
                errors.append("Execution Python version differs from contract")
            else:
                report["execution"] = execute(root, data)
                if not any(v["status"] == "failed" for v in report["execution"].values()):
                    for value in data["expected_outputs"]:
                        if not local_file(root, value).is_file():
                            errors.append(f"Declared output missing: {value}")
    ok = not errors and not any(v["status"] == "failed" for v in report["execution"].values())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Declared research checks\n\n| Stage | Status |\n| --- | --- |\n")
            f.write(f"| Structure | {report['structure']} |\n")
            for stage, value in report["execution"].items():
                f.write(f"| {stage} | {value['status']} |\n")
            f.write("| Scientific review | pending — human review required |\n\nNo general scientific certification.\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
