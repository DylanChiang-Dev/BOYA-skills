#!/usr/bin/env python3
"""Build and validate Boya claim-to-source audit records."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "boya-claim-audit/v1"
CLAIM_TYPES = {
    "number",
    "category",
    "trend",
    "comparison",
    "causal",
    "method",
    "interpretation",
    "other",
}
ACCESS_LEVELS = {"full_text", "abstract", "metadata"}
VERDICTS = {
    "supported",
    "partial",
    "distorted",
    "unsupported",
    "inaccessible",
    "not_checked",
    "not_applicable",
}
BLOCKING = {"distorted", "unsupported"}
REVIEW = {"partial", "inaccessible", "not_checked"}
EVIDENCE_VERDICTS = {"supported", "partial", "distorted"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("audit root must be a JSON object")
    return data


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_date(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def find_claim(data: dict[str, Any], claim_id: str) -> dict[str, Any] | None:
    for claim in data.get("claims", []):
        if isinstance(claim, dict) and claim.get("id") == claim_id:
            return claim
    return None


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "document", "audited_at", "claims"}
    missing = required - set(data)
    if missing:
        return [f"missing top-level field: {field}" for field in sorted(missing)]
    if data["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    document = data["document"]
    if not isinstance(document, dict):
        errors.append("document must be an object")
    else:
        for field in ("id", "path", "sha256"):
            if not nonempty(document.get(field)):
                errors.append(f"document.{field} must be a non-empty string")
    claims = data["claims"]
    if not isinstance(claims, list):
        errors.append("claims must be an array")
        return errors

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        prefix = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "text", "location", "claim_type", "sources", "verdict", "reason", "repair_action"):
            if field not in claim:
                errors.append(f"{prefix} missing field: {field}")
        claim_id = claim.get("id")
        if not nonempty(claim_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        else:
            claim_ids.add(claim_id)
        if not nonempty(claim.get("text")):
            errors.append(f"{prefix}.text must be a non-empty string")
        if not nonempty(claim.get("location")):
            errors.append(f"{prefix}.location must be a non-empty string")
        if claim.get("claim_type") not in CLAIM_TYPES:
            errors.append(f"{prefix}.claim_type is invalid")
        verdict = claim.get("verdict")
        if verdict not in VERDICTS:
            errors.append(f"{prefix}.verdict is invalid")
        if verdict != "not_checked" and not nonempty(claim.get("reason")):
            errors.append(f"{prefix}.reason is required after a verdict is set")
        if verdict in BLOCKING | REVIEW and verdict != "not_checked" and not nonempty(claim.get("repair_action")):
            errors.append(f"{prefix}.repair_action is required for {verdict}")

        sources = claim.get("sources")
        if not isinstance(sources, list):
            errors.append(f"{prefix}.sources must be an array")
            continue
        source_ids: set[str] = set()
        substantive_sources: list[dict[str, Any]] = []
        for source_index, source in enumerate(sources):
            source_prefix = f"{prefix}.sources[{source_index}]"
            if not isinstance(source, dict):
                errors.append(f"{source_prefix} must be an object")
                continue
            for field in ("id", "pointer", "locator", "checked_at", "access_level", "excerpt", "note"):
                if field not in source:
                    errors.append(f"{source_prefix} missing field: {field}")
            source_id = source.get("id")
            if not nonempty(source_id):
                errors.append(f"{source_prefix}.id must be a non-empty string")
            elif source_id in source_ids:
                errors.append(f"duplicate source id in {claim_id}: {source_id}")
            else:
                source_ids.add(source_id)
            if not nonempty(source.get("pointer")):
                errors.append(f"{source_prefix}.pointer must be a non-empty string")
            if not valid_date(source.get("checked_at")):
                errors.append(f"{source_prefix}.checked_at must be YYYY-MM-DD")
            access_level = source.get("access_level")
            if access_level not in ACCESS_LEVELS:
                errors.append(f"{source_prefix}.access_level is invalid")
            excerpt = source.get("excerpt")
            if not isinstance(excerpt, str):
                errors.append(f"{source_prefix}.excerpt must be a string")
            elif len(excerpt) > 500:
                errors.append(f"{source_prefix}.excerpt exceeds 500 characters")
            if access_level != "metadata":
                substantive_sources.append(source)

        if verdict in EVIDENCE_VERDICTS:
            eligible = [
                source
                for source in substantive_sources
                if nonempty(source.get("locator")) and nonempty(source.get("excerpt"))
            ]
            if not eligible:
                errors.append(f"{prefix} verdict {verdict} requires located non-metadata evidence")
        if verdict == "unsupported":
            eligible = [source for source in substantive_sources if nonempty(source.get("locator"))]
            if not eligible:
                errors.append(f"{prefix} unsupported requires a located non-metadata source")
        if verdict == "inaccessible" and not sources:
            errors.append(f"{prefix} inaccessible requires an attempted source pointer")
    return errors


def load_valid(path: Path) -> tuple[dict[str, Any] | None, int]:
    try:
        data = read_record(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"invalid audit: {exc}")
        return None, 2
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return None, 2
    return data, 0


def command_init(args: argparse.Namespace) -> int:
    document = Path(args.document)
    output = Path(args.output)
    if not document.is_file():
        print(f"document not found: {document}")
        return 2
    if output.exists():
        print(f"refusing to overwrite existing audit: {output}")
        return 2
    data = {
        "schema_version": SCHEMA_VERSION,
        "document": {
            "id": args.document_id,
            "path": str(document.resolve()),
            "sha256": digest(document),
        },
        "audited_at": utc_now(),
        "claims": [],
    }
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return 2
    atomic_write(output, data)
    print(f"created {output}")
    return 0


def command_add_claim(args: argparse.Namespace) -> int:
    audit = Path(args.audit)
    data, code = load_valid(audit)
    if data is None:
        return code
    if find_claim(data, args.id):
        print(f"duplicate claim id: {args.id}")
        return 2
    data["claims"].append(
        {
            "id": args.id,
            "text": args.text,
            "location": args.location,
            "claim_type": args.claim_type,
            "sources": [],
            "verdict": "not_checked",
            "reason": "",
            "repair_action": "",
        }
    )
    data["audited_at"] = utc_now()
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return 2
    atomic_write(audit, data)
    print(f"added claim {args.id}")
    return 0


def command_add_source(args: argparse.Namespace) -> int:
    audit = Path(args.audit)
    data, code = load_valid(audit)
    if data is None:
        return code
    claim = find_claim(data, args.claim_id)
    if claim is None:
        print(f"claim not found: {args.claim_id}")
        return 2
    if any(source.get("id") == args.id for source in claim["sources"]):
        print(f"duplicate source id in {args.claim_id}: {args.id}")
        return 2
    source = {
        "id": args.id,
        "pointer": args.pointer,
        "locator": args.locator,
        "checked_at": args.checked_at,
        "access_level": args.access_level,
        "excerpt": args.excerpt,
        "note": args.note,
    }
    claim["sources"].append(source)
    data["audited_at"] = utc_now()
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return 2
    atomic_write(audit, data)
    print(f"added source {args.id} to {args.claim_id}")
    return 0


def command_set_verdict(args: argparse.Namespace) -> int:
    audit = Path(args.audit)
    data, code = load_valid(audit)
    if data is None:
        return code
    claim = find_claim(data, args.claim_id)
    if claim is None:
        print(f"claim not found: {args.claim_id}")
        return 2
    previous = (claim["verdict"], claim["reason"], claim["repair_action"])
    claim["verdict"] = args.verdict
    claim["reason"] = args.reason
    claim["repair_action"] = args.repair_action
    errors = validate(data)
    if errors:
        claim["verdict"], claim["reason"], claim["repair_action"] = previous
        print("\n".join(errors))
        return 2
    data["audited_at"] = utc_now()
    atomic_write(audit, data)
    print(f"set {args.claim_id} to {args.verdict}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    data, code = load_valid(Path(args.audit))
    if data is None:
        return code
    print("claim audit valid")
    return 0


def freshness_error(data: dict[str, Any]) -> str | None:
    document = Path(data["document"]["path"])
    if not document.is_file():
        return "document is missing; audit cannot be reused"
    if digest(document) != data["document"]["sha256"]:
        return "document sha256 changed; audit is stale"
    return None


def gate_status(data: dict[str, Any]) -> str:
    if freshness_error(data):
        return "block"
    if not data["claims"]:
        return "review"
    verdicts = {claim["verdict"] for claim in data["claims"]}
    if verdicts & BLOCKING:
        return "block"
    if verdicts & REVIEW:
        return "review"
    return "pass"


def command_summary(args: argparse.Namespace) -> int:
    data, code = load_valid(Path(args.audit))
    if data is None:
        return code
    counts = Counter(claim["verdict"] for claim in data["claims"])
    result = {
        "document_id": data["document"]["id"],
        "claims": len(data["claims"]),
        "verdicts": {verdict: counts.get(verdict, 0) for verdict in sorted(VERDICTS)},
        "gate": gate_status(data),
        "freshness_error": freshness_error(data),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_gate(args: argparse.Namespace) -> int:
    data, code = load_valid(Path(args.audit))
    if data is None:
        return code
    status = gate_status(data)
    problem = freshness_error(data)
    print(status)
    if problem:
        print(problem)
    return {"pass": 0, "review": 1, "block": 2}[status]


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("document")
    init.add_argument("--output", required=True)
    init.add_argument("--document-id", required=True)
    init.set_defaults(func=command_init)

    add_claim = commands.add_parser("add-claim")
    add_claim.add_argument("audit")
    add_claim.add_argument("--id", required=True)
    add_claim.add_argument("--text", required=True)
    add_claim.add_argument("--location", required=True)
    add_claim.add_argument("--claim-type", choices=sorted(CLAIM_TYPES), required=True)
    add_claim.set_defaults(func=command_add_claim)

    add_source = commands.add_parser("add-source")
    add_source.add_argument("audit")
    add_source.add_argument("--claim-id", required=True)
    add_source.add_argument("--id", required=True)
    add_source.add_argument("--pointer", required=True)
    add_source.add_argument("--locator", default="")
    add_source.add_argument("--checked-at", required=True)
    add_source.add_argument("--access-level", choices=sorted(ACCESS_LEVELS), required=True)
    add_source.add_argument("--excerpt", default="")
    add_source.add_argument("--note", default="")
    add_source.set_defaults(func=command_add_source)

    verdict = commands.add_parser("set-verdict")
    verdict.add_argument("audit")
    verdict.add_argument("--claim-id", required=True)
    verdict.add_argument("--verdict", choices=sorted(VERDICTS), required=True)
    verdict.add_argument("--reason", required=True)
    verdict.add_argument("--repair-action", default="")
    verdict.set_defaults(func=command_set_verdict)

    for name, function in (
        ("validate", command_validate),
        ("summary", command_summary),
        ("gate", command_gate),
    ):
        subcommand = commands.add_parser(name)
        subcommand.add_argument("audit")
        subcommand.set_defaults(func=function)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
