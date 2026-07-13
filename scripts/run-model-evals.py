#!/usr/bin/env python3
"""Run Boya eval cases explicitly through Codex or Claude CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CASES = REPO / "evals" / "cases"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("codex", "claude"), required=True)
    parser.add_argument("--model", required=True, help="exact model ID or supported alias")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument(
        "--skills",
        required=True,
        help="comma-separated skill IDs, or all",
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="required for real model calls",
    )
    return parser.parse_args()


def load_cases(skill_ids: list[str]) -> list[dict[str, Any]]:
    result = []
    for skill in skill_ids:
        path = CASES / f"{skill}.json"
        if not path.is_file():
            raise ValueError(f"missing case file: {path.relative_to(REPO)}")
        data = json.loads(path.read_text(encoding="utf-8"))
        for case in data["cases"]:
            result.append({"skill": skill, **case})
    return result


def command_for(provider: str, model: str, prompt: str) -> list[str]:
    if provider == "codex":
        return [
            "codex",
            "exec",
            "--ephemeral",
            "--model",
            model,
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--cd",
            str(REPO),
            prompt,
        ]
    return [
        "claude",
        "--print",
        "--model",
        model,
        "--permission-mode",
        "plan",
        "--no-session-persistence",
        "--output-format",
        "text",
        "--plugin-dir",
        str(REPO),
        "--allowedTools=Read",
        prompt,
    ]


def pattern_result(output: str, case: dict[str, Any]) -> dict[str, Any]:
    required = {
        pattern: pattern.casefold() in output.casefold()
        for pattern in case["required_patterns"]
    }
    forbidden = {
        pattern: pattern.casefold() not in output.casefold()
        for pattern in case["forbidden_patterns"]
    }
    return {
        "required": required,
        "forbidden": forbidden,
        "static_pass": all(required.values()) and all(forbidden.values()),
        "human_review": "pending",
    }


def main() -> int:
    args = parse_args()
    if args.runs < 1 or args.runs > 20:
        print("error: --runs must be between 1 and 20", file=sys.stderr)
        return 2
    if not args.dry_run and not args.confirm_paid_run:
        print(
            "error: real model calls may consume quota; pass --confirm-paid-run explicitly",
            file=sys.stderr,
        )
        return 2
    if shutil.which(args.provider) is None:
        print(f"error: {args.provider} CLI not found", file=sys.stderr)
        return 2
    available = sorted(path.stem for path in CASES.glob("*.json"))
    skill_ids = available if args.skills == "all" else [s.strip() for s in args.skills.split(",") if s.strip()]
    try:
        cases = load_cases(skill_ids)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = args.output_dir or REPO / "evals" / "results" / f"{args.provider}-{args.model}-{stamp}"
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for case in cases:
        skill_path = REPO / "skills" / case["skill"] / "SKILL.md"
        prompt = (
            f"Read and use the Boya skill at {skill_path}. "
            "Act on the following user request without reading eval expectations or other eval files.\n\n"
            f"User request:\n{case['prompt']}"
        )
        for run in range(1, args.runs + 1):
            command = command_for(args.provider, args.model, prompt)
            if args.dry_run:
                print(json.dumps({"case": case["id"], "run": run, "command": command}, ensure_ascii=False))
                continue
            completed = subprocess.run(
                command,
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            output = completed.stdout.strip()
            record = {
                "case_id": case["id"],
                "skill": case["skill"],
                "category": case["category"],
                "provider": args.provider,
                "model": args.model,
                "run": run,
                "returncode": completed.returncode,
                "output": output,
                "stderr": completed.stderr.strip(),
                "criteria": {"must": case["must"], "must_not": case["must_not"]},
                "checks": pattern_result(output, case),
            }
            records.append(record)
            with (output_dir / "results.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(
                f"{case['id']} run {run}: "
                f"exit={completed.returncode} static_pass={record['checks']['static_pass']}"
            )
    if not args.dry_run:
        manifest = {
            "provider": args.provider,
            "model": args.model,
            "runs": args.runs,
            "skills": skill_ids,
            "case_count": len(cases),
            "result_count": len(records),
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "note": "Review must and must_not criteria manually before promoting results.",
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"results: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
