#!/usr/bin/env python3
"""Validate the Boya 2.0 skill contract and live documentation."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO / "skills"
ROUTER = REPO / "ROUTER.md"
SKILLS_MANIFEST = REPO / "skills-manifest.json"
EXPECTED_SKILLS = {
    "academic-revision",
    "ai-use-disclosure",
    "bilingual-abstract",
    "boya",
    "claim-audit",
    "citation-format",
    "journal-fit",
    "literature-analysis",
    "literature-search",
    "manuscript-review",
    "paper-outline",
    "reference-check",
    "research-design",
    "research-question",
    "research-record",
    "theoretical-framework",
    "thesis-defense-prep",
}
OLD_SKILLS = {
    "abstract-bilingual",
    "ai-disclosure",
    "citation-verify",
    "cite-format",
    "defense-prep",
    "framework-build",
    "lit-discovery",
    "lit-matrix",
    "method-design",
    "outline-builder",
    "self-review",
    "style-tune",
    "topic-refine",
    "venue-fit",
}
FRONTMATTER_KEYS = {"name", "description"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
SKILL_CALL = re.compile(r"\$([a-z0-9]+(?:-[a-z0-9]+)*)")
SKILL_PATH = re.compile(
    r"(?<![a-z0-9_.-])skills/([a-z0-9]+(?:-[a-z0-9]+)*)(?=[/#)\s`]|$)"
)
HISTORICAL_REFERENCE_FILES = {"GUIDE.md", "MEMORY.md", "VERIFICATION.md"}
ALLOWED_EXTERNAL_SKILL_CALLS = {"skill-installer"}


def parse_frontmatter(path: Path) -> tuple[list[str] | None, dict[str, str], int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, {}, len(lines)
    keys: list[str] = []
    values: dict[str, str] = {}
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        match = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", line)
        if match:
            keys.append(match.group(1))
            values[match.group(1)] = match.group(2).strip()
    return (keys if closed else None), values, len(lines)


def live_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in (
        "README*.md",
        "GUIDE.md",
        "ROUTER.md",
        "CONVENTIONS.md",
        "RULES.md",
        "AGENTS.md",
        "CLAUDE.md",
        "VERIFICATION.md",
        "MEMORY.md",
        ".codex-plugin/*.md",
        ".codex-plugin/*.json",
        ".claude-plugin/*.json",
        "skills/**/*.md",
        "skills/**/*.yaml",
        "evals/*.md",
        "evals/cases/*.json",
        "templates/*.md",
        "knowledge/*.md",
    ):
        files.update(path for path in REPO.glob(pattern) if path.is_file())
    return sorted(files)


def check_links(path: Path, errors: list[str]) -> None:
    if path.suffix != ".md":
        return
    text = path.read_text(encoding="utf-8")
    for raw_target in LINK.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = urllib.parse.unquote(target.split("#", 1)[0])
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"[{path.relative_to(REPO)}] broken link: {raw_target}")


def explicit_skill_references(text: str) -> set[str]:
    """Return IDs used as explicit skill calls or skills/<id> paths."""
    return set(SKILL_CALL.findall(text)) | set(SKILL_PATH.findall(text))


def nonexistent_skill_references(text: str) -> set[str]:
    """Return explicit references that cannot resolve locally or as approved externals."""
    calls = set(SKILL_CALL.findall(text)) - ALLOWED_EXTERNAL_SKILL_CALLS
    paths = set(SKILL_PATH.findall(text))
    return (calls | paths) - EXPECTED_SKILLS - OLD_SKILLS


def parse_router_targets() -> list[str]:
    targets = []
    for line in ROUTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[1] in {"skill", "---"}:
            continue
        if set(cells[1]) <= {"-", ":", " "}:
            continue
        match = re.search(r"([a-z0-9]+(?:-[a-z0-9]+)*)", cells[1])
        if match and match.group(1) in EXPECTED_SKILLS:
            targets.append(match.group(1))
    return targets


def check_openai_yaml(skill: str, path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"[{skill}] missing agents/openai.yaml")
        return
    text = path.read_text(encoding="utf-8")
    values = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s+{key}:\s+\"([^\"]+)\"\s*$", text, re.MULTILINE)
        if not match:
            errors.append(f"[{skill}] openai.yaml missing quoted interface.{key}")
        else:
            values[key] = match.group(1)
    short = values.get("short_description", "")
    if short and not 25 <= len(short) <= 64:
        errors.append(f"[{skill}] short_description must be 25-64 characters, got {len(short)}")
    prompt = values.get("default_prompt", "")
    if prompt and f"${skill}" not in prompt:
        errors.append(f"[{skill}] default_prompt must mention ${skill}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="kept for compatibility")
    parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    actual = {path.parent.name for path in SKILLS_DIR.glob("*/SKILL.md")}
    if actual != EXPECTED_SKILLS:
        errors.append(f"skill set mismatch: missing={sorted(EXPECTED_SKILLS-actual)} extra={sorted(actual-EXPECTED_SKILLS)}")

    try:
        release_manifest = json.loads(SKILLS_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"[skills-manifest.json] invalid JSON: {exc}")
        release_manifest = {}

    manifest_skills = release_manifest.get("skills", [])
    manifest_ids = [item.get("id") for item in manifest_skills if isinstance(item, dict)]
    if release_manifest.get("schema_version") != 1:
        errors.append("[skills-manifest.json] schema_version must be 1")
    if release_manifest.get("name") != "boya":
        errors.append("[skills-manifest.json] name must be boya")
    if release_manifest.get("version") != "2.1.0":
        errors.append("[skills-manifest.json] version must be 2.1.0")
    if release_manifest.get("skill_count") != len(manifest_ids):
        errors.append("[skills-manifest.json] skill_count must equal skills length")
    if len(manifest_ids) != len(set(manifest_ids)):
        errors.append("[skills-manifest.json] skill IDs must be unique")
    if set(manifest_ids) != actual:
        errors.append(
            "[skills-manifest.json] IDs must exactly match skill directories: "
            f"missing={sorted(actual-set(manifest_ids))} extra={sorted(set(manifest_ids)-actual)}"
        )
    roles = {item.get("id"): item.get("role") for item in manifest_skills if isinstance(item, dict)}
    if roles.get("boya") != "entry" or roles.get("research-record") != "optional":
        errors.append("[skills-manifest.json] boya must be entry and research-record optional")
    workflow_ids = [skill for skill, role in roles.items() if role == "workflow"]
    if len(workflow_ids) != 15:
        errors.append("[skills-manifest.json] exactly 15 skills must have role workflow")
    if any(
        not isinstance(item.get("stage"), int) or item.get("stage", -1) < 0
        for item in manifest_skills
        if isinstance(item, dict)
    ):
        errors.append("[skills-manifest.json] every skill needs a non-negative integer stage")

    for skill in sorted(actual):
        skill_file = SKILLS_DIR / skill / "SKILL.md"
        keys, frontmatter, line_count = parse_frontmatter(skill_file)
        if keys is None:
            errors.append(f"[{skill}] invalid or unclosed frontmatter")
            continue
        if set(keys) != FRONTMATTER_KEYS or len(keys) != 2:
            errors.append(f"[{skill}] frontmatter must contain only name and description")
        if frontmatter.get("name") != skill or not KEBAB.fullmatch(frontmatter.get("name", "")):
            errors.append(f"[{skill}] frontmatter name must equal directory and use kebab-case")
        description = frontmatter.get("description", "")
        if "時使用" not in description:
            errors.append(f"[{skill}] description must state when to use the skill")
        if "「" not in description or "」" not in description:
            errors.append(f"[{skill}] description must include concrete trigger examples")
        if len(description) > 240:
            warnings.append(f"[{skill}] description is {len(description)} characters; consider shortening")
        if line_count > 200:
            warnings.append(f"[{skill}] SKILL.md is {line_count} lines; review progressive disclosure")
        if not (REPO / "evals" / f"{skill}.md").is_file():
            errors.append(f"[{skill}] missing evals/{skill}.md")
        if not (REPO / "evals" / "cases" / f"{skill}.json").is_file():
            errors.append(f"[{skill}] missing structured eval cases")
        check_openai_yaml(skill, SKILLS_DIR / skill / "agents" / "openai.yaml", errors)

    targets = parse_router_targets()
    if set(targets) != EXPECTED_SKILLS or len(targets) != len(EXPECTED_SKILLS):
        errors.append("ROUTER must contain each Boya 2.0 skill exactly once")

    for manifest_path in (REPO / ".codex-plugin/plugin.json", REPO / ".claude-plugin/plugin.json"):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[{manifest_path.relative_to(REPO)}] invalid JSON: {exc}")
            continue
        if manifest.get("version") != release_manifest.get("version"):
            errors.append(
                f"[{manifest_path.relative_to(REPO)}] version must match skills-manifest.json"
            )
        if "17" not in manifest.get("description", ""):
            errors.append(f"[{manifest_path.relative_to(REPO)}] description must state 17 skills")

    for path in live_files():
        text = path.read_text(encoding="utf-8")
        for old in OLD_SKILLS:
            retired = re.compile(rf"(?<![a-z0-9-]){re.escape(old)}(?![a-z0-9-])")
            if path.name not in HISTORICAL_REFERENCE_FILES and retired.search(text):
                errors.append(f"[{path.relative_to(REPO)}] contains retired skill ID: {old}")
        if path.name not in HISTORICAL_REFERENCE_FILES:
            for reference in sorted(nonexistent_skill_references(text)):
                errors.append(
                    f"[{path.relative_to(REPO)}] references nonexistent skill: {reference}"
                )
        check_links(path, errors)

    if warnings:
        print("WARN")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("ERROR")
        for error in errors:
            print(f"  - {error}")
        print(f"ERROR {len(errors)}  WARN {len(warnings)}")
        return 1
    print(f"Boya skill check passed: {len(actual)} skills, ERROR 0, WARN {len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
