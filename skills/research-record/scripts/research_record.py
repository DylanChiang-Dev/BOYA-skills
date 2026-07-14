#!/usr/bin/env python3
"""Create and maintain opt-in Boya research project records."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "boya-research-record/v1"
ARTIFACT_STATUSES = {"present", "missing", "superseded"}
DECISION_STATUSES = {"pending", "confirmed", "rejected", "superseded"}
UNKNOWN_STATUSES = {"open", "resolved", "blocked"}
CHECKPOINT_STATUSES = {
    "locating",
    "running",
    "waiting_for_user",
    "ready_to_advance",
    "blocked",
    "complete",
}
CHECKPOINT_DECISIONS = {"pending", "confirmed", "not_applicable"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def read_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("record root must be a JSON object")
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


def append_event(data: dict[str, Any], action: str, target_id: str, reason: str) -> None:
    data["events"].append(
        {"at": utc_now(), "action": action, "target_id": target_id, "reason": reason}
    )
    data["updated_at"] = data["events"][-1]["at"]


def duplicate_ids(items: list[Any]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if isinstance(item, dict) and nonempty(item.get("id")):
            if item["id"] in seen:
                duplicates.add(item["id"])
            seen.add(item["id"])
    return duplicates


def validate_checkpoint(
    checkpoint: Any,
    artifacts: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> list[str]:
    if checkpoint is None:
        return []
    errors: list[str] = []
    if not isinstance(checkpoint, dict):
        return ["checkpoint must be an object or null"]
    required = {
        "stage",
        "status",
        "artifacts_present",
        "decision_required",
        "decision_status",
        "decision_id",
        "active_skill",
        "next_skill",
    }
    missing = required - set(checkpoint)
    errors.extend(f"checkpoint missing field: {field}" for field in sorted(missing))
    stage = checkpoint.get("stage")
    if stage is not None and (not isinstance(stage, int) or isinstance(stage, bool) or not 1 <= stage <= 14):
        errors.append("checkpoint.stage must be null or an integer from 1 to 14")
    if checkpoint.get("status") not in CHECKPOINT_STATUSES:
        errors.append("checkpoint.status is invalid")
    artifact_ids = checkpoint.get("artifacts_present")
    if not isinstance(artifact_ids, list) or not all(nonempty(value) for value in artifact_ids):
        errors.append("checkpoint.artifacts_present must be an array of IDs")
        artifact_ids = []
    for artifact_id in artifact_ids:
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            errors.append(f"checkpoint references missing artifact: {artifact_id}")
        elif artifact.get("status") != "present":
            errors.append(f"checkpoint artifact is not present: {artifact_id}")
    decision_status = checkpoint.get("decision_status")
    if decision_status not in CHECKPOINT_DECISIONS:
        errors.append("checkpoint.decision_status is invalid")
    decision_id = checkpoint.get("decision_id")
    if decision_status in {"pending", "confirmed"}:
        if not nonempty(decision_id):
            errors.append("checkpoint.decision_id is required for pending or confirmed decisions")
        else:
            decision = decisions.get(decision_id)
            if decision is None:
                errors.append(f"checkpoint references missing decision: {decision_id}")
            elif decision.get("status") != decision_status:
                errors.append(f"checkpoint decision status does not match {decision_id}")
    elif decision_id is not None:
        errors.append("checkpoint.decision_id must be null when decision is not_applicable")
    if checkpoint.get("status") in {"ready_to_advance", "complete"} and decision_status not in {
        "confirmed",
        "not_applicable",
    }:
        errors.append("ready_to_advance or complete requires confirmed or not_applicable decision")
    if checkpoint.get("status") == "waiting_for_user" and decision_status != "pending":
        errors.append("waiting_for_user requires a pending decision")
    return errors


def validate(data: dict[str, Any]) -> list[str]:
    required = {
        "schema_version",
        "project",
        "checkpoint",
        "artifacts",
        "decisions",
        "unknowns",
        "events",
        "updated_at",
    }
    missing = required - set(data)
    if missing:
        return [f"missing top-level field: {field}" for field in sorted(missing)]
    errors: list[str] = []
    if data["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    project = data["project"]
    if not isinstance(project, dict):
        errors.append("project must be an object")
    else:
        for field in ("id", "title", "created_at"):
            if not nonempty(project.get(field)):
                errors.append(f"project.{field} must be a non-empty string")
    for field in ("artifacts", "decisions", "unknowns", "events"):
        if not isinstance(data[field], list):
            errors.append(f"{field} must be an array")
    if errors:
        return errors

    artifacts_by_id: dict[str, dict[str, Any]] = {}
    for index, artifact in enumerate(data["artifacts"]):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "type", "title", "pointer", "status", "added_at"):
            if not nonempty(artifact.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if artifact.get("status") not in ARTIFACT_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        if nonempty(artifact.get("id")):
            artifacts_by_id[artifact["id"]] = artifact
    for duplicate in sorted(duplicate_ids(data["artifacts"])):
        errors.append(f"duplicate artifact id: {duplicate}")

    decisions_by_id: dict[str, dict[str, Any]] = {}
    for index, decision in enumerate(data["decisions"]):
        prefix = f"decisions[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in (
            "id",
            "question",
            "status",
            "choice",
            "evidence_ids",
            "proposed_at",
            "confirmed_at",
            "confirmed_by",
        ):
            if field not in decision:
                errors.append(f"{prefix} missing field: {field}")
        if not nonempty(decision.get("id")):
            errors.append(f"{prefix}.id must be a non-empty string")
        if not nonempty(decision.get("question")):
            errors.append(f"{prefix}.question must be a non-empty string")
        status = decision.get("status")
        if status not in DECISION_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        evidence_ids = decision.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not all(nonempty(value) for value in evidence_ids):
            errors.append(f"{prefix}.evidence_ids must be an array of IDs")
            evidence_ids = []
        for artifact_id in evidence_ids:
            if artifact_id not in artifacts_by_id:
                errors.append(f"{prefix} references missing artifact: {artifact_id}")
        if status == "confirmed":
            if not nonempty(decision.get("choice")):
                errors.append(f"{prefix}.choice is required when confirmed")
            if not nonempty(decision.get("confirmed_at")):
                errors.append(f"{prefix}.confirmed_at is required when confirmed")
            if decision.get("confirmed_by") != "user":
                errors.append(f"{prefix}.confirmed_by must be user when confirmed")
        if nonempty(decision.get("id")):
            decisions_by_id[decision["id"]] = decision
    for duplicate in sorted(duplicate_ids(data["decisions"])):
        errors.append(f"duplicate decision id: {duplicate}")

    for index, unknown in enumerate(data["unknowns"]):
        prefix = f"unknowns[{index}]"
        if not isinstance(unknown, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "question", "status", "created_at"):
            if not nonempty(unknown.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if unknown.get("status") not in UNKNOWN_STATUSES:
            errors.append(f"{prefix}.status is invalid")
    for duplicate in sorted(duplicate_ids(data["unknowns"])):
        errors.append(f"duplicate unknown id: {duplicate}")

    for index, event in enumerate(data["events"]):
        prefix = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("at", "action", "target_id", "reason"):
            if not nonempty(event.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
    errors.extend(validate_checkpoint(data["checkpoint"], artifacts_by_id, decisions_by_id))
    return errors


def load_valid(path: Path) -> tuple[dict[str, Any] | None, int]:
    try:
        data = read_record(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"invalid research record: {exc}")
        return None, 2
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return None, 2
    return data, 0


def save_valid(path: Path, data: dict[str, Any]) -> int:
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return 2
    atomic_write(path, data)
    return 0


def command_init(args: argparse.Namespace) -> int:
    output = Path(args.output)
    if output.exists():
        print(f"refusing to overwrite existing record: {output}")
        return 2
    timestamp = utc_now()
    data = {
        "schema_version": SCHEMA_VERSION,
        "project": {"id": args.project_id, "title": args.title, "created_at": timestamp},
        "checkpoint": None,
        "artifacts": [],
        "decisions": [],
        "unknowns": [],
        "events": [
            {
                "at": timestamp,
                "action": "record_initialized",
                "target_id": args.project_id,
                "reason": "user requested a persistent research record",
            }
        ],
        "updated_at": timestamp,
    }
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        return 2
    atomic_write(output, data)
    print(f"created {output}")
    return 0


def command_add_artifact(args: argparse.Namespace) -> int:
    path = Path(args.record)
    data, code = load_valid(path)
    if data is None:
        return code
    if any(item["id"] == args.id for item in data["artifacts"]):
        print(f"duplicate artifact id: {args.id}")
        return 2
    timestamp = utc_now()
    data["artifacts"].append(
        {
            "id": args.id,
            "type": args.type,
            "title": args.title,
            "pointer": args.pointer,
            "status": args.status,
            "added_at": timestamp,
        }
    )
    append_event(data, "artifact_added", args.id, args.reason)
    if save_valid(path, data):
        return 2
    print(f"added artifact {args.id}")
    return 0


def command_add_unknown(args: argparse.Namespace) -> int:
    path = Path(args.record)
    data, code = load_valid(path)
    if data is None:
        return code
    if any(item["id"] == args.id for item in data["unknowns"]):
        print(f"duplicate unknown id: {args.id}")
        return 2
    timestamp = utc_now()
    data["unknowns"].append(
        {"id": args.id, "question": args.question, "status": "open", "created_at": timestamp}
    )
    append_event(data, "unknown_added", args.id, args.reason)
    if save_valid(path, data):
        return 2
    print(f"added unknown {args.id}")
    return 0


def command_propose_decision(args: argparse.Namespace) -> int:
    path = Path(args.record)
    data, code = load_valid(path)
    if data is None:
        return code
    if any(item["id"] == args.id for item in data["decisions"]):
        print(f"duplicate decision id: {args.id}")
        return 2
    artifact_ids = {item["id"] for item in data["artifacts"]}
    missing = sorted(set(args.evidence_id) - artifact_ids)
    if missing:
        print(f"missing evidence artifact(s): {', '.join(missing)}")
        return 2
    timestamp = utc_now()
    data["decisions"].append(
        {
            "id": args.id,
            "question": args.question,
            "status": "pending",
            "choice": "",
            "evidence_ids": args.evidence_id,
            "proposed_at": timestamp,
            "confirmed_at": "",
            "confirmed_by": "",
        }
    )
    append_event(data, "decision_proposed", args.id, args.reason)
    if save_valid(path, data):
        return 2
    print(f"proposed decision {args.id}")
    return 0


def command_confirm_decision(args: argparse.Namespace) -> int:
    if not args.user_confirmed:
        print("confirm-decision requires --user-confirmed after an explicit user reply")
        return 2
    path = Path(args.record)
    data, code = load_valid(path)
    if data is None:
        return code
    decision = next((item for item in data["decisions"] if item["id"] == args.id), None)
    if decision is None:
        print(f"decision not found: {args.id}")
        return 2
    if decision["status"] != "pending":
        print(f"decision is not pending: {args.id}")
        return 2
    timestamp = utc_now()
    decision.update(
        {
            "status": "confirmed",
            "choice": args.choice,
            "confirmed_at": timestamp,
            "confirmed_by": "user",
        }
    )
    append_event(data, "decision_confirmed", args.id, args.reason)
    if save_valid(path, data):
        return 2
    print(f"confirmed decision {args.id}")
    return 0


def command_sync_checkpoint(args: argparse.Namespace) -> int:
    path = Path(args.record)
    data, code = load_valid(path)
    if data is None:
        return code
    checkpoint = {
        "stage": args.stage,
        "status": args.status,
        "artifacts_present": args.artifact_id,
        "decision_required": args.decision_required,
        "decision_status": args.decision_status,
        "decision_id": args.decision_id,
        "active_skill": args.active_skill,
        "next_skill": args.next_skill,
    }
    artifacts = {item["id"]: item for item in data["artifacts"]}
    decisions = {item["id"]: item for item in data["decisions"]}
    errors = validate_checkpoint(checkpoint, artifacts, decisions)
    if errors:
        print("\n".join(errors))
        return 2
    data["checkpoint"] = checkpoint
    append_event(data, "checkpoint_synced", data["project"]["id"], args.reason)
    if save_valid(path, data):
        return 2
    print(f"synced checkpoint: {args.status}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    data, code = load_valid(Path(args.record))
    if data is None:
        return code
    print("research record valid")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    data, code = load_valid(Path(args.record))
    if data is None:
        return code
    result = {
        "project_id": data["project"]["id"],
        "checkpoint": data["checkpoint"],
        "artifacts": {
            status: sum(1 for item in data["artifacts"] if item["status"] == status)
            for status in sorted(ARTIFACT_STATUSES)
        },
        "confirmed_decisions": sum(
            1 for item in data["decisions"] if item["status"] == "confirmed"
        ),
        "pending_decisions": sum(
            1 for item in data["decisions"] if item["status"] == "pending"
        ),
        "open_unknowns": sum(1 for item in data["unknowns"] if item["status"] == "open"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("--output", required=True)
    init.add_argument("--project-id", required=True)
    init.add_argument("--title", required=True)
    init.set_defaults(func=command_init)

    artifact = commands.add_parser("add-artifact")
    artifact.add_argument("record")
    artifact.add_argument("--id", required=True)
    artifact.add_argument("--type", required=True)
    artifact.add_argument("--title", required=True)
    artifact.add_argument("--pointer", required=True)
    artifact.add_argument("--status", choices=sorted(ARTIFACT_STATUSES), default="present")
    artifact.add_argument("--reason", default="user registered project material")
    artifact.set_defaults(func=command_add_artifact)

    unknown = commands.add_parser("add-unknown")
    unknown.add_argument("record")
    unknown.add_argument("--id", required=True)
    unknown.add_argument("--question", required=True)
    unknown.add_argument("--reason", default="open question recorded")
    unknown.set_defaults(func=command_add_unknown)

    propose = commands.add_parser("propose-decision")
    propose.add_argument("record")
    propose.add_argument("--id", required=True)
    propose.add_argument("--question", required=True)
    propose.add_argument("--evidence-id", action="append", default=[])
    propose.add_argument("--reason", default="decision gate opened")
    propose.set_defaults(func=command_propose_decision)

    confirm = commands.add_parser("confirm-decision")
    confirm.add_argument("record")
    confirm.add_argument("--id", required=True)
    confirm.add_argument("--choice", required=True)
    confirm.add_argument("--user-confirmed", action="store_true")
    confirm.add_argument("--reason", default="user explicitly confirmed the decision")
    confirm.set_defaults(func=command_confirm_decision)

    checkpoint = commands.add_parser("sync-checkpoint")
    checkpoint.add_argument("record")
    checkpoint.add_argument("--stage", type=int)
    checkpoint.add_argument("--status", choices=sorted(CHECKPOINT_STATUSES), required=True)
    checkpoint.add_argument("--artifact-id", action="append", default=[])
    checkpoint.add_argument("--decision-required", default="")
    checkpoint.add_argument("--decision-status", choices=sorted(CHECKPOINT_DECISIONS), required=True)
    checkpoint.add_argument("--decision-id")
    checkpoint.add_argument("--active-skill")
    checkpoint.add_argument("--next-skill")
    checkpoint.add_argument("--reason", default="boya checkpoint synchronized")
    checkpoint.set_defaults(func=command_sync_checkpoint)

    for name, function in (("validate", command_validate), ("summary", command_summary)):
        subcommand = commands.add_parser(name)
        subcommand.add_argument("record")
        subcommand.set_defaults(func=function)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
