"""Check SORS 0.1 indexes and, only on request, selected execution steps.

Run untrusted project commands in a separate disposable environment. This program
validates paths and uses shell=False; it is not a process sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator
import yaml

VERSION = "0.1"
SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    pairs = loader.construct_pairs(node, deep=deep)
    return unique_pairs(pairs)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate mapping key: {key}")
        result[key] = value
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load(path):
    text = path.read_text(encoding="utf-8-sig")
    data = json.loads(text, object_pairs_hook=unique_pairs) if path.suffix == ".json" else yaml.load(text, Loader=UniqueLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: index must be a mapping")
    return data


def local_path(root, value, *, must_exist=True, directory=False, document=False):
    if not isinstance(value, str) or not value.strip() or "\\" in value:
        raise ValueError(f"Use a nonempty repository-relative path with /: {value!r}")
    parsed = urlsplit(value)
    raw = unquote(parsed.path)
    if parsed.scheme or parsed.netloc or PureWindowsPath(raw).drive or Path(raw).is_absolute():
        raise ValueError(f"Absolute path or URL is not a local reference: {value}")
    path = (root / raw).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes project root: {value}")
    if must_exist and not path.exists():
        raise ValueError(f"Missing local reference: {value}")
    if directory and not path.is_dir():
        raise ValueError(f"Working directory does not exist: {value}")
    if document and (not path.is_file() or path.stat().st_size == 0):
        raise ValueError(f"Document must be a nonempty file: {value}")
    return path


def schema_errors(data, kind):
    schema = json.loads((SCHEMAS / f"{kind}.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in sorted(validator.iter_errors(data), key=lambda e: str(e.absolute_path))]


def ids(items, label, errors):
    found = set()
    for item in items:
        name = item["id"]
        if name in found:
            errors.append(f"{label}: duplicate ID {name}")
        found.add(name)
    return found


def references_exist(root, obj, errors, label="", *, expected_output=False):
    """Walk reference-shaped fields, including additional domain properties."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            loc = f"{label}.{key}" if label else key
            if key == "path":
                try:
                    local_path(root, value, must_exist=not expected_output)
                except ValueError as exc:
                    errors.append(f"{loc}: {exc}")
            elif key == "url" and isinstance(value, str):
                parsed = urlsplit(value)
                if parsed.scheme not in ("https", "http") or not parsed.netloc:
                    errors.append(f"{loc}: use an http(s) source URL")
            else:
                references_exist(root, value, errors, loc)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            references_exist(root, value, errors, f"{label}[{index}]")


def check_markdown(root, path):
    """Inspect local destinations in declared entry documents; do not fetch URLs."""
    if path.suffix.lower() != ".md":
        return []
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", "", text)
    destinations = re.findall(r"\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[\"'][^\n]*?[\"'])?\s*\)", text)
    targets = [a or b for a, b in destinations]
    targets += re.findall(r"^\s*\[[^\]]+\]:\s*<?([^\s>]+)>?", text, flags=re.M)
    targets += re.findall(r'(?:href|src)="([^"]+)"', text)
    errors = []
    for target in targets:
        if target.startswith("#") or "{{" in target:
            continue
        parts = urlsplit(target)
        if parts.scheme in ("http", "https", "mailto"):
            continue
        if parts.scheme or parts.netloc or PureWindowsPath(target).drive:
            errors.append(f"{path.relative_to(root)}: unsupported link {target}")
            continue
        try:
            # Markdown links are relative to their document, unlike index paths.
            value = (path.parent.relative_to(root) / unquote(parts.path)).as_posix()
            if parts.path.startswith("/"):
                raise ValueError(f"Absolute local link: {target}")
            local_path(root, value)
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return errors


def check_refs(values, allowed, label, errors):
    for value in values:
        if value not in allowed:
            errors.append(f"{label}: unknown reference {value}")


def ordered_steps(steps):
    by_id = {step["id"]: step for step in steps}
    order, active, finished = [], set(), set()

    def visit(name):
        if name in active:
            raise ValueError(f"Execution dependency cycle at {name}")
        if name in finished:
            return
        if name not in by_id:
            raise ValueError(f"Unknown dependency step {name}")
        active.add(name)
        for dependency in by_id[name].get("depends_on", []):
            visit(dependency)
        active.remove(name)
        finished.add(name)
        order.append(by_id[name])

    for step in steps:
        visit(step["id"])
    return order


def validate(root):
    errors, cases = [], {}
    candidates = [root / name for name in ("research.yaml", "research.yml", "research.json") if (root / name).is_file()]
    if len(candidates) != 1:
        return None, {}, ["Provide exactly one project index: research.yaml, research.yml or research.json"]
    try:
        project = load(local_path(root, candidates[0].name))
        errors.extend(schema_errors(project, "project"))
    except (OSError, ValueError, yaml.YAMLError, TypeError) as exc:
        return None, {}, [str(exc)]
    if errors:
        return project, {}, errors
    capability_ids = ids(project["capabilities"], "capabilities", errors)
    environment_ids = ids(project["environments"], "environments", errors)
    ids(project["assets"], "assets", errors)
    ids(project["cases"], "cases", errors)
    documents = set()
    for label, value in project["documents"].items():
        try:
            documents.add(local_path(root, value, document=True))
        except ValueError as exc:
            errors.append(f"documents.{label}: {exc}")
    for env in project["environments"]:
        for value in env.get("dependency_files", []):
            try:
                local_path(root, value)
            except ValueError as exc:
                errors.append(f"environment {env['id']}: {exc}")
        for step in env.get("setup_steps", []):
            try:
                local_path(root, step.get("cwd", "."), directory=True)
            except ValueError as exc:
                errors.append(f"environment {env['id']}: {exc}")
    for capability in project["capabilities"]:
        value = capability.get("documentation")
        if isinstance(value, str):
            try:
                local_path(root, value)
            except ValueError as exc:
                errors.append(f"capability {capability['id']}: {exc}")
    licensing = project["licensing"]
    for key in ("license_file", "sources", "details"):
        if isinstance(licensing.get(key), str):
            try:
                local_path(root, licensing[key], document=True)
            except ValueError as exc:
                errors.append(f"licensing.{key}: {exc}")
    references_exist(root, project, errors)
    for entry in project["cases"]:
        try:
            case = load(local_path(root, entry["manifest"]))
            case_errors = schema_errors(case, "case")
            if case_errors:
                errors.extend(f"case {entry['id']}: {e}" for e in case_errors)
                continue
            if case["id"] != entry["id"] or case["project_id"] != project["project"]["id"]:
                errors.append(f"case {entry['id']}: case/project identity mismatch")
            cases[entry["id"]] = case
            check_refs(case["capability_refs"], capability_ids, f"case {entry['id']} capabilities", errors)
            groups = {key: ids(case[key], f"{entry['id']}.{key}", errors) for key in ("inputs", "outputs", "references", "criteria", "checks")}
            execution = case["execution"]
            check_refs([execution["environment_ref"]], environment_ids, f"{entry['id']} environment", errors)
            local_path(root, execution["cwd"], directory=True)
            step_ids = ids(execution["steps"], f"{entry['id']}.steps", errors)
            for step in execution["steps"]:
                check_refs([step.get("environment_ref", execution["environment_ref"])], environment_ids, f"step {step['id']} environment", errors)
                check_refs(step.get("depends_on", []), step_ids, f"step {step['id']} dependencies", errors)
                for key in ("inputs", "outputs"):
                    check_refs(step.get(key[:-1] + "_refs", []), groups[key], f"step {step['id']} {key}", errors)
                local_path(root, step.get("cwd", execution["cwd"]), directory=True)
            ordered_steps(execution["steps"])
            for check in case["checks"]:
                for field, group in (("criterion_refs", "criteria"), ("reference_refs", "references"), ("output_refs", "outputs"), ("input_refs", "inputs")):
                    check_refs(check.get(field, []), groups[group], f"check {check['id']} {field}", errors)
            for key, value in case.items():
                if key != "outputs":
                    references_exist(root, value, errors, f"{entry['id']}.{key}")
            for output in case["outputs"]:
                # Only the declared output path may be absent; its documentation must exist.
                references_exist(root, output, errors, f"{entry['id']}.outputs.{output['id']}", expected_output=True)
            if isinstance(case["limitations"], str):
                local_path(root, case["limitations"])
            if case["results"]["status"] == "observed" and not any(r.get("availability") != "not_bundled" for r in case["results"]["records"]):
                errors.append(f"{entry['id']}: observed results need at least one available record")
        except (OSError, ValueError, yaml.YAMLError, TypeError) as exc:
            errors.append(f"case {entry['id']}: {exc}")
    for path in sorted(documents):
        errors.extend(check_markdown(root, path))
    return project, cases, errors


def fingerprint(path):
    if not path.exists():
        return None
    files = sorted(path.rglob("*")) if path.is_dir() else [path]
    digest = hashlib.sha256()
    for item in files:
        if item.is_symlink():
            raise ValueError(f"Output must not contain a symbolic link: {item.name}")
        if item.is_file():
            stat = item.stat()
            digest.update(str((str(item.relative_to(path) if path.is_dir() else item.name), stat.st_size, stat.st_mtime_ns)).encode())
    return digest.hexdigest()


def run_steps(root, project, case, requested):
    steps = case["execution"]["steps"]
    selected = set(requested)
    known = {s["id"] for s in steps}
    errors = []
    unknown = selected - known
    if unknown:
        return [], [f"Unknown requested steps: {', '.join(sorted(unknown))}"]
    selected_steps = [s for s in ordered_steps(steps) if s["id"] in selected]
    for step in selected_steps:
        missing = set(step.get("depends_on", [])) - selected
        if missing:
            errors.append(f"{step['id']}: explicitly select dependency steps: {', '.join(sorted(missing))}")
    if errors:
        return [], errors
    output_map = {o["id"]: o for o in case["outputs"]}
    environments = {e["id"]: e for e in project["environments"]}
    records = []
    blocked = False
    for step in selected_steps:
        result = {"id": step["id"], "role": step["role"], "status": "not_run"}
        records.append(result)
        if blocked:
            continue
        if step["mode"] != "command":
            errors.append(f"{step['id']}: follow its documented instructions; no command was executed")
            blocked = True
            continue
        environment = environments[step.get("environment_ref", case["execution"]["environment_ref"])]
        aliases = {"win32": {"windows", "win32"}, "linux": {"linux"}, "darwin": {"macos", "darwin"}}
        supported = {p.lower() for p in environment["platforms"]}
        if not supported.intersection(aliases.get(sys.platform, {sys.platform}) | {"any", "all"}):
            errors.append(f"{step['id']}: current platform {sys.platform} is not declared for {environment['id']}")
            blocked = True
            continue
        argv = step["argv"][:]
        if argv[0] in ("python", "python3"):
            argv[0] = sys.executable
        try:
            cwd = local_path(root, step.get("cwd", case["execution"]["cwd"]), directory=True)
            outputs = {name: local_path(root, output_map[name]["path"], must_exist=False) for name in step.get("output_refs", []) if "path" in output_map[name]}
            if len(outputs) != len(step.get("output_refs", [])):
                raise ValueError("Every output selected for execution needs an expected path")
            before = {name: fingerprint(path) for name, path in outputs.items()}
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                completed = subprocess.run(argv, cwd=cwd, shell=False, stdin=subprocess.DEVNULL,
                                           stdout=stdout, stderr=stderr,
                                           timeout=step.get("timeout_seconds", 300), check=False)
                result["exit_code"] = completed.returncode
                for field, stream in (("stdout", stdout), ("stderr", stderr)):
                    stream.seek(0)
                    result[field] = stream.read(16000).decode("utf-8", errors="replace")
                if completed.returncode:
                    raise ValueError(f"Command exited with {completed.returncode}")
            for name in outputs:
                path = local_path(root, output_map[name]["path"])
                if fingerprint(path) == before[name]:
                    raise ValueError(f"Declared output unchanged from before this run: {name}")
            result["status"] = "planned" if step["role"] == "plan" else "passed"
            result["outputs_checked"] = list(outputs)
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            result["status"] = "failed"
            result["error"] = str(exc)
            errors.append(f"{step['id']}: {exc}")
            blocked = True
    return records, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--report", type=Path)
    parser.add_argument("--case", help="Case ID (required with --run)")
    parser.add_argument("--step", action="append", default=[], help="Explicit step ID; repeat to select dependencies")
    parser.add_argument("--run", action="store_true", help="Execute selected commands in the current environment")
    args = parser.parse_args(argv)
    if args.run and (not args.case or not args.step):
        parser.error("--run requires --case and at least one --step")
    root = args.root.resolve()
    try:
        project, cases, errors = validate(root)
    except (OSError, ValueError, TypeError) as exc:
        project, cases, errors = None, {}, [str(exc)]
    report = {"schema_version": VERSION, "structure": {"status": "failed" if errors else "passed", "errors": errors},
              "execution": {"status": "not_run", "steps": [], "errors": []}, "scientific_review": "pending",
              "scope": "Project structure and declared references; selected commands only when --run is supplied."}
    if args.case and args.case not in cases and not errors:
        errors.append(f"Unknown case: {args.case}")
        report["structure"]["status"] = "failed"
    if args.run and not errors:
        records, execution_errors = run_steps(root, project, cases[args.case], args.step)
        state = "failed" if execution_errors else ("planned" if records and all(r["role"] == "plan" for r in records) else "passed")
        report["execution"] = {"status": state, "case": args.case, "steps": records, "errors": execution_errors}
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    return int(report["structure"]["status"] == "failed" or report["execution"]["status"] == "failed")


if __name__ == "__main__":
    sys.exit(main())
