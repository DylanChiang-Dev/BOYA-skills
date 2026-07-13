import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECK_SKILLS = REPO / "scripts/check-skills.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validation = load_module("check_skills", CHECK_SKILLS)


class SkillReferenceTests(unittest.TestCase):
    def test_extracts_calls_and_paths(self):
        text = "Use $boya, then read skills/reference-check/SKILL.md."
        self.assertEqual(
            validation.explicit_skill_references(text),
            {"boya", "reference-check"},
        )

    def test_ignores_unmarked_hyphenated_terms(self):
        self.assertEqual(
            validation.explicit_skill_references("human-in-the-loop and source-id"),
            set(),
        )

    def test_allows_documented_external_skill_calls(self):
        self.assertEqual(
            validation.nonexistent_skill_references("Use $skill-installer."),
            set(),
        )

    def test_reports_missing_local_skill_paths(self):
        self.assertEqual(
            validation.nonexistent_skill_references(
                "Read skills/submission-pack/SKILL.md."
            ),
            {"submission-pack"},
        )


if __name__ == "__main__":
    unittest.main()
