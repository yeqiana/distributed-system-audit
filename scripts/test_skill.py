#!/usr/bin/env python3
"""Validate the publishable package; optionally create a clean install archive."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

import yaml


SKILL_NAME = "distributed-system-audit"
ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    "SKILL.md", "README.md", "README.zh-CN.md", "LICENSE",
    ".editorconfig", ".gitattributes", ".gitignore", "requirements-dev.txt",
}
RESOURCE_DIRS = {"agents", "references", "prompts", "examples", "evals", "docs", "scripts", "tests", ".github"}
REQUIRED = ROOT_FILES | {
    "agents/openai.yaml", "references/audit-sop.md",
    "prompts/audit.md", "prompts/triage.md", "prompts/repair-handoff.md",
    "examples/stale-worker.md", "evals/behavior-contracts.md",
    "evals/manual-evaluation.md", "docs/release-checklist.md",
    "docs/promotion-copy.md", "scripts/test_skill.py",
    "scripts/test-skill.ps1", "tests/test_package.py",
    "scripts/prepare_behavior_eval.py", "tests/test_behavior_fixtures.py",
    "evals/fixtures/cases.json", "evals/fixtures/scenarios.py", "evals/fixtures/observations.json",
    ".github/workflows/validate.yml",
}


def package_files(root):
    """Only publication sources, excluding VCS, IDE, build and evaluation output."""
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and (path.relative_to(root).as_posix() in ROOT_FILES
             or path.relative_to(root).parts[0] in RESOURCE_DIRS)
        and not any(part in {"__pycache__", ".venv", ".eval-runs"}
                    for part in path.relative_to(root).parts)
        and path.suffix != ".pyc"
    )


def validate(root):
    root = root.resolve()
    errors = []
    for relative in sorted(REQUIRED):
        if not (root / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    documents = {}
    for path in package_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            errors.append(f"Package source escapes root or is a symlink: {relative}")
            continue
        try:
            documents[relative] = path.read_text(encoding="utf-8-sig", errors="strict")
        except (UnicodeError, OSError) as exc:
            errors.append(f"Unreadable UTF-8 source {relative}: {exc}")

    skill = documents.get("SKILL.md", "")
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", skill, re.S)
    if not frontmatter:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        try:
            metadata = yaml.safe_load(frontmatter.group(1))
            if not isinstance(metadata, dict) or metadata.get("name") != SKILL_NAME:
                errors.append(f"SKILL.md: name must be {SKILL_NAME}")
            else:
                description = metadata.get("description")
                if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                    errors.append("SKILL.md: description must be a nonempty string up to 1024 characters")
        except yaml.YAMLError as exc:
            errors.append(f"SKILL.md: invalid YAML: {exc}")

    for relative, document in documents.items():
        if relative.endswith((".yaml", ".yml")):
            try:
                parsed = yaml.safe_load(document)
                if not isinstance(parsed, dict):
                    errors.append(f"{relative}: expected a YAML mapping")
                elif relative == "agents/openai.yaml":
                    interface = parsed.get("interface")
                    if not isinstance(interface, dict):
                        errors.append(f"{relative}: missing interface mapping")
                        continue
                    for field in ("display_name", "short_description", "default_prompt"):
                        if not isinstance(interface.get(field), str) or not interface[field].strip():
                            errors.append(f"{relative}: missing interface.{field}")
                    prompt = interface.get("default_prompt", "")
                    if not isinstance(prompt, str) or f"${SKILL_NAME}" not in prompt:
                        errors.append(f"{relative}: default_prompt must invoke ${SKILL_NAME}")
                    short = interface.get("short_description", "")
                    if isinstance(short, str) and not 25 <= len(short) <= 64:
                        errors.append(f"{relative}: short_description must be 25-64 characters")
                    policy = parsed.get("policy", {})
                    if not isinstance(policy, dict) or not isinstance(policy.get("allow_implicit_invocation", True), bool):
                        errors.append(f"{relative}: invocation policy must be boolean")
            except yaml.YAMLError as exc:
                errors.append(f"{relative}: invalid YAML: {exc}")

        if relative.endswith(".md"):
            # Ignore code examples; this repository uses inline Markdown links.
            prose = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", document)
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
                target = target.strip("<>")
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                resolved = (root / relative).parent / unquote(url.path)
                resolved = resolved.resolve()
                if not resolved.is_relative_to(root) or not resolved.exists():
                    errors.append(f"Broken/escaping local link in {relative}: {target}")
                elif resolved.is_file() and resolved.relative_to(root).as_posix() not in documents:
                    errors.append(f"Link targets an unpackaged file in {relative}: {target}")
    return errors


def create_package(root, output):
    root = root.resolve()
    output = output.resolve()
    if output.is_relative_to(root):
        relative_parts = output.relative_to(root).parts
        if not relative_parts or relative_parts[0] != "dist":
            raise ValueError("Package output inside the repository must be under dist/")
    errors = validate(root)
    if errors:
        raise ValueError("\n".join(errors))
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    sources = tuple(package_files(root))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "x", compression=ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, f"{SKILL_NAME}/{path.relative_to(root).as_posix()}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package", type=Path, help="Create a ZIP without overwriting an existing file")
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Static package checks passed ({len(package_files(root))} source files). Model behavior not evaluated.")
    if args.package:
        try:
            print(f"Created: {create_package(root, args.package)}")
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
