#!/usr/bin/env python3
"""Prepare fixed blind inputs and isolated workspaces, without expected answers."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Evaluation workspaces must be outside the repository")
    output.mkdir(parents=True, exist_ok=False)
    git_env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    fixture_root = ROOT / "evals/fixtures"
    fixtures = json.loads((fixture_root / "cases.json").read_text(encoding="utf-8"))
    observations = json.loads((fixture_root / "observations.json").read_text(encoding="utf-8"))
    manifest = {"provenance": fixtures["provenance"], "skill_hashes": {}, "fixture_hashes": {}, "cases": {}}
    for path in [ROOT / "SKILL.md", ROOT / "references/audit-sop.md"]:
        manifest["skill_hashes"][path.relative_to(ROOT).as_posix()] = digest(path)
    for path in fixture_root.iterdir():
        if path.is_file():
            manifest["fixture_hashes"][path.name] = digest(path)
    for case in fixtures["cases"]:
        case_root = output / case["id"]
        skill = case_root / "skill"
        skill.mkdir(parents=True)
        shutil.copyfile(ROOT / "SKILL.md", skill / "SKILL.md")
        shutil.copytree(ROOT / "references", skill / "references")
        (case_root / "request.md").write_text(fixtures["provenance"] + "\n\n" + case["request"] + "\n", encoding="utf-8")
        artifacts = case_root / "artifacts"
        artifacts.mkdir()
        for name, content in case["artifacts"].items():
            (artifacts / name).write_text(content, encoding="utf-8")
        if "observation" in case:
            shutil.copyfile(fixture_root / "scenarios.py", artifacts / "scenarios.py")
            (artifacts / "observed.json").write_text(json.dumps(observations[case["observation"]], ensure_ascii=False, indent=2), encoding="utf-8")
        workspace = case_root / "workspace"
        workspace.mkdir()
        for name, content in case.get("baseline_files", {}).items():
            (workspace / name).write_text(content, encoding="utf-8")
        if case.get("baseline_files"):
            for args in [("init", "-b", "fixture"), ("add", "."),
                         ("-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "Synthetic baseline")]:
                subprocess.run(["git", *args], cwd=workspace, check=True, capture_output=True, env=git_env)
        for name, content in case.get("workspace_files", {}).items():
            (workspace / name).write_text(content, encoding="utf-8")
        manifest["cases"][case["id"]] = {
            "input_hashes": {p.relative_to(case_root).as_posix(): digest(p) for p in sorted(case_root.rglob("*")) if p.is_file() and ".git" not in p.parts},
            "git_status_before": subprocess.run(["git", "status", "--porcelain"], cwd=workspace, capture_output=True, text=True, check=True, env=git_env).stdout if case.get("baseline_files") else None,
        }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    destination = args.output or Path(tempfile.gettempdir()) / ("distributed-audit-eval-" + uuid4().hex)
    print(prepare(destination))
