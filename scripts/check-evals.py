#!/usr/bin/env python3
"""Validate Boya structured model-evaluation cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
CASES = REPO / "evals" / "cases"
REQUIRED_CATEGORIES = {"happy_path", "insufficient_input", "adversarial"}
BOYA_EXTRA = {"gate", "resume", "direct_action", "missing_skill"}
CASE_KEYS = {"id", "category", "prompt", "must", "must_not", "required_patterns", "forbidden_patterns"}


def main() -> int:
    errors: list[str] = []
    skill_names = {
        path.parent.name for path in SKILLS.glob("*/SKILL.md") if path.is_file()
    }
    case_files = {path.stem: path for path in CASES.glob("*.json")}

    for skill in sorted(skill_names):
        if skill not in case_files:
            errors.append(f"[{skill}] missing evals/cases/{skill}.json")
    for stem in sorted(set(case_files) - skill_names):
        errors.append(f"[{stem}] case file has no matching skill")

    seen_ids: set[str] = set()
    total = 0
    for stem, path in sorted(case_files.items()):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[{stem}] invalid JSON: {exc}")
            continue
        if data.get("skill") != stem:
            errors.append(f"[{stem}] top-level skill must equal filename")
        cases = data.get("cases")
        if not isinstance(cases, list):
            errors.append(f"[{stem}] cases must be a list")
            continue
        categories = set()
        for index, case in enumerate(cases, 1):
            total += 1
            if not isinstance(case, dict):
                errors.append(f"[{stem} #{index}] case must be an object")
                continue
            missing = CASE_KEYS - set(case)
            extra = set(case) - CASE_KEYS
            if missing:
                errors.append(f"[{stem} #{index}] missing keys: {sorted(missing)}")
            if extra:
                errors.append(f"[{stem} #{index}] unsupported keys: {sorted(extra)}")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id:
                errors.append(f"[{stem} #{index}] id must be a non-empty string")
            elif case_id in seen_ids:
                errors.append(f"[{stem} #{index}] duplicate id: {case_id}")
            else:
                seen_ids.add(case_id)
            category = case.get("category")
            if isinstance(category, str):
                categories.add(category)
            if not isinstance(case.get("prompt"), str) or not case.get("prompt", "").strip():
                errors.append(f"[{stem} #{index}] prompt must be non-empty")
            for key in ("must", "must_not", "required_patterns", "forbidden_patterns"):
                value = case.get(key)
                if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                    errors.append(f"[{stem} #{index}] {key} must be a list of strings")
            if isinstance(case.get("must"), list) and not case["must"]:
                errors.append(f"[{stem} #{index}] must cannot be empty")
            if isinstance(case.get("must_not"), list) and not case["must_not"]:
                errors.append(f"[{stem} #{index}] must_not cannot be empty")
        missing_categories = REQUIRED_CATEGORIES - categories
        if missing_categories:
            errors.append(f"[{stem}] missing categories: {sorted(missing_categories)}")
        if stem == "boya":
            missing_boya = BOYA_EXTRA - categories
            if missing_boya:
                errors.append(f"[boya] missing dispatcher categories: {sorted(missing_boya)}")

    if errors:
        print("Boya structured eval check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Boya structured eval check passed: {len(case_files)} skills, {total} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
