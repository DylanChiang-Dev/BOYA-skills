import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills/claim-audit/scripts/claim_audit.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


class ClaimAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.document = self.root / "draft.md"
        self.audit = self.root / "audit.json"
        self.document.write_text("一般費率為每公噸 300 元。\n", encoding="utf-8")
        result = run(
            "init",
            self.document,
            "--output",
            self.audit,
            "--document-id",
            "DOC-1",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self):
        self.temp.cleanup()

    def add_claim(self, claim_id="C1"):
        result = run(
            "add-claim",
            self.audit,
            "--id",
            claim_id,
            "--text",
            "一般費率為每公噸 300 元",
            "--location",
            "第 1 段",
            "--claim-type",
            "number",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_supported_claim_passes_with_located_source(self):
        self.add_claim()
        source = run(
            "add-source",
            self.audit,
            "--claim-id",
            "C1",
            "--id",
            "S1",
            "--pointer",
            "https://example.test/policy",
            "--locator",
            "公告第 2 段",
            "--checked-at",
            "2026-07-14",
            "--access-level",
            "full_text",
            "--excerpt",
            "一般費率每公噸 300 元。",
        )
        self.assertEqual(source.returncode, 0, source.stderr)
        verdict = run(
            "set-verdict",
            self.audit,
            "--claim-id",
            "C1",
            "--verdict",
            "supported",
            "--reason",
            "數值、單位與適用費率一致",
        )
        self.assertEqual(verdict.returncode, 0, verdict.stderr)
        gate = run("gate", self.audit)
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        self.assertIn("pass", gate.stdout)

    def test_metadata_cannot_be_promoted_to_supported(self):
        self.add_claim()
        source = run(
            "add-source",
            self.audit,
            "--claim-id",
            "C1",
            "--id",
            "S1",
            "--pointer",
            "doi:10.1000/example",
            "--checked-at",
            "2026-07-14",
            "--access-level",
            "metadata",
        )
        self.assertEqual(source.returncode, 0, source.stderr)
        verdict = run(
            "set-verdict",
            self.audit,
            "--claim-id",
            "C1",
            "--verdict",
            "supported",
            "--reason",
            "DOI exists",
        )
        self.assertEqual(verdict.returncode, 2)
        data = json.loads(self.audit.read_text(encoding="utf-8"))
        self.assertEqual(data["claims"][0]["verdict"], "not_checked")

    def test_duplicate_claim_is_rejected_without_second_write(self):
        self.add_claim()
        duplicate = run(
            "add-claim",
            self.audit,
            "--id",
            "C1",
            "--text",
            "duplicate",
            "--location",
            "第 2 段",
            "--claim-type",
            "other",
        )
        self.assertEqual(duplicate.returncode, 2)
        data = json.loads(self.audit.read_text(encoding="utf-8"))
        self.assertEqual(len(data["claims"]), 1)

    def test_changed_document_blocks_gate(self):
        self.add_claim()
        self.document.write_text("一般費率改成別的數字。\n", encoding="utf-8")
        gate = run("gate", self.audit)
        self.assertEqual(gate.returncode, 2)
        self.assertIn("stale", gate.stdout)

    def test_empty_claim_is_rejected_without_write(self):
        result = run(
            "add-claim",
            self.audit,
            "--id",
            "C1",
            "--text",
            "",
            "--location",
            "第 1 段",
            "--claim-type",
            "other",
        )
        self.assertEqual(result.returncode, 2)
        data = json.loads(self.audit.read_text(encoding="utf-8"))
        self.assertEqual(data["claims"], [])


if __name__ == "__main__":
    unittest.main()
