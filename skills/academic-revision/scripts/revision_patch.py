#!/usr/bin/env python3
"""Prepare and apply explicitly approved, hash-checked Markdown replacements."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_VERSION = "boya-revision-manifest/v1"
PROPOSAL_VERSION = "boya-revision-proposal/v1"
PATCH_VERSION = "boya-revision-patch/v1"
REPORT_VERSION = "boya-revision-report/v1"
FENCE_START = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
LIST_ITEM = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")
BLOCKQUOTE = re.compile(r"^\s*>")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def write_json_new(path: Path, data: dict[str, Any]) -> None:
    write_new(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


@dataclass(frozen=True)
class Line:
    body: str
    start: int
    content_end: int
    full_end: int

    @property
    def blank(self) -> bool:
        return not self.body.strip()


@dataclass(frozen=True)
class Block:
    block_id: str
    kind: str
    start: int
    end: int
    start_line: int
    end_line: int
    text: str

    @property
    def sha256(self) -> str:
        return text_hash(self.text)


def lines_with_offsets(text: str) -> list[Line]:
    result: list[Line] = []
    offset = 0
    for raw in text.splitlines(keepends=True):
        body = raw.rstrip("\r\n")
        result.append(
            Line(
                body=body,
                start=offset,
                content_end=offset + len(body),
                full_end=offset + len(raw),
            )
        )
        offset += len(raw)
    if text and (not result or result[-1].full_end < len(text)):
        body = text[offset:]
        result.append(Line(body=body, start=offset, content_end=len(text), full_end=len(text)))
    return result


def line_kind(body: str, next_body: str | None = None) -> str:
    if FENCE_START.match(body):
        return "fenced_code"
    if HEADING.match(body):
        return "heading"
    if LIST_ITEM.match(body):
        return "list"
    if BLOCKQUOTE.match(body):
        return "blockquote"
    if "|" in body and (next_body is None or "|" in next_body):
        return "table"
    return "paragraph"


def parse_blocks(text: str) -> list[Block]:
    if not text.strip():
        raise ValueError("document is empty")
    lines = lines_with_offsets(text)
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        if lines[index].blank:
            index += 1
            continue
        start = index
        next_body = lines[index + 1].body if index + 1 < len(lines) else None
        kind = line_kind(lines[index].body, next_body)
        if kind == "fenced_code":
            match = FENCE_START.match(lines[index].body)
            assert match is not None
            marker = match.group(1)
            marker_char = marker[0]
            marker_length = len(marker)
            index += 1
            closed = False
            while index < len(lines):
                stripped = lines[index].body.lstrip()
                if stripped.startswith(marker_char * marker_length):
                    closed = True
                    index += 1
                    break
                index += 1
            if not closed:
                raise ValueError(f"unclosed fenced code block at line {start + 1}")
        elif kind == "heading":
            index += 1
        elif kind == "table":
            index += 1
            while index < len(lines) and not lines[index].blank and "|" in lines[index].body:
                index += 1
        elif kind == "blockquote":
            index += 1
            while index < len(lines) and not lines[index].blank and BLOCKQUOTE.match(lines[index].body):
                index += 1
        elif kind == "list":
            index += 1
            while index < len(lines) and not lines[index].blank:
                if FENCE_START.match(lines[index].body) or HEADING.match(lines[index].body):
                    break
                index += 1
        else:
            index += 1
            while index < len(lines) and not lines[index].blank:
                upcoming = line_kind(
                    lines[index].body,
                    lines[index + 1].body if index + 1 < len(lines) else None,
                )
                if upcoming != "paragraph":
                    break
                index += 1
        end_line_index = index - 1
        start_offset = lines[start].start
        end_offset = lines[end_line_index].content_end
        block_text = text[start_offset:end_offset]
        blocks.append(
            Block(
                block_id=f"B{len(blocks) + 1:04d}",
                kind=kind,
                start=start_offset,
                end=end_offset,
                start_line=start + 1,
                end_line=end_line_index + 1,
                text=block_text,
            )
        )
    if not blocks:
        raise ValueError("document contains no editable Markdown blocks")
    return blocks


def manifest_for(source: Path, text: str, blocks: list[Block]) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_VERSION,
        "source_path": str(source.resolve()),
        "document_sha256": text_hash(text),
        "blocks": [
            {
                "block_id": block.block_id,
                "kind": block.kind,
                "start_line": block.start_line,
                "end_line": block.end_line,
                "sha256": block.sha256,
                "preview": block.text.splitlines()[0][:120],
            }
            for block in blocks
        ],
    }


def current_document(manifest: dict[str, Any]) -> tuple[Path, str, list[Block], list[str]]:
    errors: list[str] = []
    if manifest.get("schema_version") != MANIFEST_VERSION:
        return Path("."), "", [], [f"manifest schema_version must be {MANIFEST_VERSION}"]
    source_value = manifest.get("source_path")
    if not isinstance(source_value, str) or not source_value:
        return Path("."), "", [], ["manifest source_path is required"]
    source = Path(source_value)
    if not source.is_file():
        return source, "", [], [f"source document not found: {source}"]
    try:
        text = read_text(source)
        blocks = parse_blocks(text)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return source, "", [], [f"cannot parse source document: {exc}"]
    if manifest.get("document_sha256") != text_hash(text):
        errors.append("document sha256 changed; manifest is stale")
    manifest_blocks = {
        item.get("block_id"): item
        for item in manifest.get("blocks", [])
        if isinstance(item, dict)
    }
    if len(manifest_blocks) != len(blocks):
        errors.append("manifest block count does not match document")
    for block in blocks:
        expected = manifest_blocks.get(block.block_id)
        if expected is None:
            errors.append(f"manifest missing block: {block.block_id}")
        elif expected.get("sha256") != block.sha256:
            errors.append(f"manifest hash mismatch: {block.block_id}")
    return source, text, blocks, errors


def validate_operations(
    data: dict[str, Any],
    schema_version: str,
    document_sha256: str,
    blocks: list[Block],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    if data.get("schema_version") != schema_version:
        errors.append(f"schema_version must be {schema_version}")
    if data.get("document_sha256") != document_sha256:
        errors.append("operation document_sha256 does not match manifest")
    operations = data.get("operations")
    if not isinstance(operations, list) or not operations:
        errors.append("operations must be a non-empty array")
        return [], errors
    current = {block.block_id: block for block in blocks}
    seen: set[str] = set()
    valid_operations: list[dict[str, Any]] = []
    for index, operation in enumerate(operations):
        prefix = f"operations[{index}]"
        if not isinstance(operation, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if operation.get("op") != "replace":
            errors.append(f"{prefix}.op must be replace")
        block_id = operation.get("block_id")
        if not isinstance(block_id, str) or block_id not in current:
            errors.append(f"{prefix}.block_id does not exist")
            continue
        if block_id in seen:
            errors.append(f"duplicate operation for {block_id}")
        seen.add(block_id)
        if operation.get("expected_sha256") != current[block_id].sha256:
            errors.append(f"{prefix}.expected_sha256 mismatch for {block_id}")
        new_text = operation.get("new_text")
        if not isinstance(new_text, str) or not new_text.strip("\r\n"):
            errors.append(f"{prefix}.new_text must be non-empty; delete is not supported")
        if not isinstance(operation.get("reason"), str) or not operation["reason"].strip():
            errors.append(f"{prefix}.reason must be non-empty")
        issue_ids = operation.get("issue_ids")
        if not isinstance(issue_ids, list) or not all(isinstance(value, str) for value in issue_ids):
            errors.append(f"{prefix}.issue_ids must be an array of strings")
        valid_operations.append(operation)
    return valid_operations, errors


def command_prepare(args: argparse.Namespace) -> int:
    source = Path(args.document)
    manifest_path = Path(args.manifest)
    if not source.is_file():
        print(f"document not found: {source}")
        return 2
    if manifest_path.exists():
        print(f"refusing to overwrite existing manifest: {manifest_path}")
        return 2
    try:
        text = read_text(source)
        blocks = parse_blocks(text)
        write_json_new(manifest_path, manifest_for(source, text, blocks))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"prepare failed: {exc}")
        return 2
    print(f"prepared {len(blocks)} blocks")
    return 0


def checked_proposal(
    manifest_path: Path, proposal_path: Path
) -> tuple[dict[str, Any] | None, list[Block], list[dict[str, Any]], list[str]]:
    try:
        manifest = read_json(manifest_path)
        proposal = read_json(proposal_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return None, [], [], [f"cannot read inputs: {exc}"]
    _, text, blocks, errors = current_document(manifest)
    operations, operation_errors = validate_operations(
        proposal, PROPOSAL_VERSION, text_hash(text), blocks
    )
    errors.extend(operation_errors)
    return proposal, blocks, operations, errors


def command_check(args: argparse.Namespace) -> int:
    _, blocks, operations, errors = checked_proposal(Path(args.manifest), Path(args.proposal))
    if errors:
        print("\n".join(errors))
        return 2
    ratio = len(operations) / len(blocks)
    print(f"proposal valid: {len(operations)}/{len(blocks)} blocks ({ratio:.1%})")
    if ratio > 0.5:
        print("broad revision: approval must explicitly allow more than 50% of blocks")
    return 0


def command_approve(args: argparse.Namespace) -> int:
    if not args.user_confirmed:
        print("approve requires --user-confirmed after the user approves exact block IDs")
        return 2
    output = Path(args.output)
    if output.exists():
        print(f"refusing to overwrite existing patch: {output}")
        return 2
    proposal, blocks, operations, errors = checked_proposal(
        Path(args.manifest), Path(args.proposal)
    )
    if errors or proposal is None:
        print("\n".join(errors))
        return 2
    requested = args.block
    if len(set(requested)) != len(requested):
        print("approved block IDs must be unique")
        return 2
    by_id = {operation["block_id"]: operation for operation in operations}
    missing = [block_id for block_id in requested if block_id not in by_id]
    if missing:
        print(f"approved block not found in proposal: {', '.join(missing)}")
        return 2
    approved = [by_id[block_id] for block_id in requested]
    ratio = len(approved) / len(blocks)
    if ratio > 0.5 and not args.allow_broad_revision:
        print("approval covers more than 50% of blocks; explicit --allow-broad-revision is required")
        return 2
    patch = {
        "schema_version": PATCH_VERSION,
        "document_sha256": proposal["document_sha256"],
        "approval": {
            "user_confirmed": True,
            "approved_at": utc_now(),
            "approved_blocks": requested,
            "note": args.note,
            "allow_broad_revision": bool(args.allow_broad_revision),
        },
        "operations": approved,
    }
    try:
        write_json_new(output, patch)
    except ValueError as exc:
        print(f"approve failed: {exc}")
        return 2
    print(f"approved {len(approved)} block(s)")
    return 0


def normalize_replacement(text: str, newline: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    return normalized.replace("\n", newline)


def command_apply(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    patch_path = Path(args.patch)
    output = Path(args.output)
    report_path = Path(args.report)
    try:
        manifest = read_json(manifest_path)
        patch = read_json(patch_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"apply failed: {exc}")
        return 2
    source, text, blocks, errors = current_document(manifest)
    operations, operation_errors = validate_operations(
        patch, PATCH_VERSION, text_hash(text), blocks
    )
    errors.extend(operation_errors)
    approval = patch.get("approval")
    if not isinstance(approval, dict) or approval.get("user_confirmed") is not True:
        errors.append("patch has no explicit user approval")
        approval = {}
    approved_blocks = approval.get("approved_blocks")
    operation_ids = [operation.get("block_id") for operation in operations]
    if approved_blocks != operation_ids:
        errors.append("approved_blocks must exactly match patch operation order")
    ratio = len(operations) / len(blocks) if blocks else 1.0
    if ratio > 0.5 and approval.get("allow_broad_revision") is not True:
        errors.append("patch changes more than 50% of blocks without broad-revision approval")
    resolved = [source.resolve(), output.resolve(), report_path.resolve()]
    if len(set(resolved)) != len(resolved):
        errors.append("source, output, and report paths must all differ")
    if output.exists() or report_path.exists():
        errors.append("refusing to overwrite existing output or report")
    if errors:
        print("\n".join(errors))
        return 2

    current = {block.block_id: block for block in blocks}
    newline = "\r\n" if "\r\n" in text else "\n"
    revised = text
    changes: list[dict[str, Any]] = []
    for operation in sorted(operations, key=lambda item: current[item["block_id"]].start, reverse=True):
        block = current[operation["block_id"]]
        replacement = normalize_replacement(operation["new_text"], newline)
        revised = revised[: block.start] + replacement + revised[block.end :]
        changes.append(
            {
                "block_id": block.block_id,
                "old_sha256": block.sha256,
                "new_sha256": text_hash(replacement),
                "reason": operation["reason"],
                "issue_ids": operation["issue_ids"],
            }
        )
    changes.reverse()
    report = {
        "schema_version": REPORT_VERSION,
        "source_path": str(source),
        "output_path": str(output.resolve()),
        "base_document_sha256": text_hash(text),
        "revised_document_sha256": text_hash(revised),
        "total_blocks": len(blocks),
        "changed_blocks": len(changes),
        "preserved_blocks": len(blocks) - len(changes),
        "preserved_ratio": (len(blocks) - len(changes)) / len(blocks),
        "changes": changes,
        "approval": approval,
    }
    try:
        write_new(output, revised)
        write_json_new(report_path, report)
    except (OSError, ValueError) as exc:
        output.unlink(missing_ok=True)
        report_path.unlink(missing_ok=True)
        print(f"apply failed: {exc}")
        return 2
    print(
        f"applied {len(changes)} change(s); preserved "
        f"{report['preserved_blocks']}/{len(blocks)} blocks"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser("prepare")
    prepare.add_argument("document")
    prepare.add_argument("--manifest", required=True)
    prepare.set_defaults(func=command_prepare)

    check = commands.add_parser("check")
    check.add_argument("--manifest", required=True)
    check.add_argument("--proposal", required=True)
    check.set_defaults(func=command_check)

    approve = commands.add_parser("approve")
    approve.add_argument("--manifest", required=True)
    approve.add_argument("--proposal", required=True)
    approve.add_argument("--block", action="append", required=True)
    approve.add_argument("--note", required=True)
    approve.add_argument("--output", required=True)
    approve.add_argument("--user-confirmed", action="store_true")
    approve.add_argument("--allow-broad-revision", action="store_true")
    approve.set_defaults(func=command_approve)

    apply = commands.add_parser("apply")
    apply.add_argument("--manifest", required=True)
    apply.add_argument("--patch", required=True)
    apply.add_argument("--output", required=True)
    apply.add_argument("--report", required=True)
    apply.set_defaults(func=command_apply)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
