import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REFERENCE_SCRIPT = REPO / "skills/reference-check/scripts/collect_evidence.py"
SEARCH_SCRIPT = REPO / "skills/literature-search/scripts/search_sources.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


reference = load_module("reference_evidence", REFERENCE_SCRIPT)
search = load_module("literature_search_sources", SEARCH_SCRIPT)


class ReferenceEvidenceTests(unittest.TestCase):
    def test_normalize_doi(self):
        self.assertEqual(
            reference.normalize_doi("https://doi.org/10.1000/ABC.1."),
            "10.1000/abc.1",
        )
        self.assertIsNone(reference.normalize_doi("not a doi"))

    def test_dry_run_builds_queries_without_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "references.json"
            output_path = root / "evidence.json"
            input_path.write_text(
                json.dumps(
                    {
                        "references": [
                            {
                                "id": "R1",
                                "title": "Attention Is All You Need",
                                "year": 2017,
                                "doi": "10.48550/arXiv.1706.03762",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REFERENCE_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertIsNone(data["records"][0]["decision"])
            self.assertTrue(data["records"][0]["queries"])
            self.assertTrue(
                all(query["status"] == "planned" for query in data["records"][0]["queries"])
            )


class LiteratureSearchTests(unittest.TestCase):
    def test_deduplicate_preserves_evidence(self):
        hits = [
            {
                "source": "openalex",
                "query_label": "Q1",
                "query": "public AI",
                "candidate": {"title": "Public AI", "source_id": "W1"},
            },
            {
                "source": "crossref",
                "query_label": "Q2",
                "query": "AI public sector",
                "candidate": {"title": "Public AI!", "source_id": "D1"},
            },
        ]
        merged = search.deduplicate(hits)
        self.assertEqual(len(merged), 1)
        self.assertEqual(len(merged[0]["evidence"]), 2)
        self.assertIsNone(merged[0]["relevance"])
        self.assertIsNone(merged[0]["include_decision"])

    def test_dry_run_builds_source_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "strategy.json"
            output_path = root / "candidates.json"
            input_path.write_text(
                json.dumps(
                    {
                        "research_question": "How does generative AI affect assessment?",
                        "queries": [{"label": "Q1", "query": "generative AI assessment"}],
                        "from_year": 2020,
                        "to_year": 2026,
                        "limit": 5,
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SEARCH_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(len(data["queries"]), 3)
            self.assertEqual(data["candidates"], [])
            self.assertTrue(all(query["status"] == "planned" for query in data["queries"]))


if __name__ == "__main__":
    unittest.main()
