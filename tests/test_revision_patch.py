import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills/academic-revision/scripts/revision_patch.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


class RevisionPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.document = self.root / "draft.md"
        self.manifest = self.root / "manifest.json"
        self.proposal = self.root / "proposal.json"
        self.patch = self.root / "patch.json"
        self.output = self.root / "revised.md"
        self.report = self.root / "report.json"
        self.original = (
            "# 標題\n\n"
            "第一段保留。\n\n"
            "- 清單一\n- 清單二\n\n"
            "| 欄一 | 欄二 |\n|---|---|\n| A | B |\n\n"
            "> 引文保留\n\n"
            "```text\ncode | stays\n```\n"
        )
        self.document.write_text(self.original, encoding="utf-8")
        prepared = run("prepare", self.document, "--manifest", self.manifest)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)

    def tearDown(self):
        self.temp.cleanup()

    def write_proposal(self, block_ids):
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        blocks = {item["block_id"]: item for item in manifest["blocks"]}
        proposal = {
            "schema_version": "boya-revision-proposal/v1",
            "document_sha256": manifest["document_sha256"],
            "operations": [
                {
                    "op": "replace",
                    "block_id": block_id,
                    "expected_sha256": blocks[block_id]["sha256"],
                    "new_text": f"{block_id} 的批准後新文字。",
                    "reason": "收窄未被來源支持的說法",
                    "issue_ids": ["ISSUE-1"],
                }
                for block_id in block_ids
            ],
        }
        self.proposal.write_text(
            json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return manifest

    def approve(self, *block_ids, broad=False, confirmed=True):
        args = [
            "approve",
            "--manifest",
            self.manifest,
            "--proposal",
            self.proposal,
            "--note",
            "使用者批准指定區塊",
            "--output",
            self.patch,
        ]
        for block_id in block_ids:
            args.extend(["--block", block_id])
        if confirmed:
            args.append("--user-confirmed")
        if broad:
            args.append("--allow-broad-revision")
        return run(*args)

    def test_prepare_recognizes_academic_markdown_blocks(self):
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        kinds = [block["kind"] for block in manifest["blocks"]]
        self.assertEqual(
            kinds,
            ["heading", "paragraph", "list", "table", "blockquote", "fenced_code"],
        )

    def test_apply_only_changes_approved_block_and_preserves_original(self):
        self.write_proposal(["B0002"])
        checked = run("check", "--manifest", self.manifest, "--proposal", self.proposal)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        approved = self.approve("B0002")
        self.assertEqual(approved.returncode, 0, approved.stderr)
        applied = run(
            "apply",
            "--manifest",
            self.manifest,
            "--patch",
            self.patch,
            "--output",
            self.output,
            "--report",
            self.report,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(self.document.read_text(encoding="utf-8"), self.original)
        revised = self.output.read_text(encoding="utf-8")
        self.assertIn("B0002 的批准後新文字。", revised)
        self.assertIn("- 清單一\n- 清單二", revised)
        self.assertIn("```text\ncode | stays\n```", revised)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["changed_blocks"], 1)
        self.assertEqual(report["preserved_blocks"], 5)

    def test_approval_requires_user_confirmation(self):
        self.write_proposal(["B0002"])
        approved = self.approve("B0002", confirmed=False)
        self.assertEqual(approved.returncode, 2)
        self.assertFalse(self.patch.exists())

    def test_broad_revision_requires_explicit_approval(self):
        self.write_proposal(["B0001", "B0002", "B0003", "B0004"])
        denied = self.approve("B0001", "B0002", "B0003", "B0004")
        self.assertEqual(denied.returncode, 2)
        self.assertFalse(self.patch.exists())
        accepted = self.approve("B0001", "B0002", "B0003", "B0004", broad=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)

    def test_stale_document_stops_without_output(self):
        self.write_proposal(["B0002"])
        approved = self.approve("B0002")
        self.assertEqual(approved.returncode, 0, approved.stderr)
        self.document.write_text(self.original + "\n新內容。\n", encoding="utf-8")
        applied = run(
            "apply",
            "--manifest",
            self.manifest,
            "--patch",
            self.patch,
            "--output",
            self.output,
            "--report",
            self.report,
        )
        self.assertEqual(applied.returncode, 2)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())

    def test_crlf_is_preserved(self):
        document = self.root / "crlf.md"
        manifest = self.root / "crlf-manifest.json"
        document.write_bytes(b"# Title\r\n\r\nKeep\r\n")
        prepared = run("prepare", document, "--manifest", manifest)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(len(data["blocks"]), 2)
        self.assertEqual(document.read_bytes(), b"# Title\r\n\r\nKeep\r\n")


if __name__ == "__main__":
    unittest.main()
