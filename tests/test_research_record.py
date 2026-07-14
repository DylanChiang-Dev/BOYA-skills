import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills/research-record/scripts/research_record.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


class ResearchRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.record = self.root / "research-record.json"
        result = run(
            "init",
            "--output",
            self.record,
            "--project-id",
            "P-1",
            "--title",
            "碳費政策研究",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self):
        self.temp.cleanup()

    def add_artifact(self):
        result = run(
            "add-artifact",
            self.record,
            "--id",
            "A1",
            "--type",
            "framework",
            "--title",
            "候選框架比較表",
            "--pointer",
            "examples/framework.md",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def propose(self):
        result = run(
            "propose-decision",
            self.record,
            "--id",
            "D1",
            "--question",
            "選定主框架",
            "--evidence-id",
            "A1",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_confirmed_decision_allows_ready_checkpoint(self):
        self.add_artifact()
        self.propose()
        confirm = run(
            "confirm-decision",
            self.record,
            "--id",
            "D1",
            "--choice",
            "多準則政策分析",
            "--user-confirmed",
        )
        self.assertEqual(confirm.returncode, 0, confirm.stderr)
        checkpoint = run(
            "sync-checkpoint",
            self.record,
            "--stage",
            "5",
            "--status",
            "ready_to_advance",
            "--artifact-id",
            "A1",
            "--decision-required",
            "選定主框架",
            "--decision-status",
            "confirmed",
            "--decision-id",
            "D1",
            "--active-skill",
            "theoretical-framework",
            "--next-skill",
            "research-design",
        )
        self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["decisions"][0]["confirmed_by"], "user")
        self.assertEqual(data["checkpoint"]["status"], "ready_to_advance")
        self.assertGreaterEqual(len(data["events"]), 5)

    def test_confirm_requires_explicit_user_flag(self):
        self.add_artifact()
        self.propose()
        confirm = run(
            "confirm-decision",
            self.record,
            "--id",
            "D1",
            "--choice",
            "多準則政策分析",
        )
        self.assertEqual(confirm.returncode, 2)
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["decisions"][0]["status"], "pending")

    def test_pending_decision_cannot_advance(self):
        self.add_artifact()
        self.propose()
        checkpoint = run(
            "sync-checkpoint",
            self.record,
            "--stage",
            "5",
            "--status",
            "ready_to_advance",
            "--artifact-id",
            "A1",
            "--decision-required",
            "選定主框架",
            "--decision-status",
            "pending",
            "--decision-id",
            "D1",
        )
        self.assertEqual(checkpoint.returncode, 2)
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertIsNone(data["checkpoint"])

    def test_duplicate_artifact_is_rejected_without_write(self):
        self.add_artifact()
        duplicate = run(
            "add-artifact",
            self.record,
            "--id",
            "A1",
            "--type",
            "paper",
            "--title",
            "duplicate",
            "--pointer",
            "duplicate.md",
        )
        self.assertEqual(duplicate.returncode, 2)
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(len(data["artifacts"]), 1)

    def test_empty_artifact_title_is_rejected_without_write(self):
        result = run(
            "add-artifact",
            self.record,
            "--id",
            "A1",
            "--type",
            "paper",
            "--title",
            "",
            "--pointer",
            "paper.md",
        )
        self.assertEqual(result.returncode, 2)
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["artifacts"], [])


if __name__ == "__main__":
    unittest.main()
