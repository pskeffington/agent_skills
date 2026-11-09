import json
import pathlib
import tempfile
import unittest
from scripts.profile_rag_cache import profile

class ProfileRagCacheTests(unittest.TestCase):
    def test_profile_small_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            (repo / "test.md").write_text("release readiness task journal lease\n", encoding="utf-8")
            result = profile(repo, repetitions=2)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["mode"], "strict SHA-256")
            self.assertEqual(len(result["corpus_fingerprint"]), 64)
            self.assertIsNone(result["source_commit"])
            self.assertIsNone(result["working_tree_dirty"])
            self.assertIn("python", result["environment"])
            self.assertIn("platform", result["environment"])
            self.assertEqual(len(result["operations"]["strict_warm_cache"]["samples"]), 2)
            self.assertGreaterEqual(result["operations"]["cold_build"]["median_ms"], 0)
            self.assertEqual(result["operations"]["cold_build"]["p95_ms"],
                             max(sample["elapsed_ms"] for sample in result["operations"]["cold_build"]["samples"]))

    def test_existing_output_is_excluded_from_repeated_measurements(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            (repo / "test.md").write_text("release readiness\n", encoding="utf-8")
            output = repo / "docs/benchmarks/rag-o0-profile.json"
            output.parent.mkdir(parents=True)
            output.write_text("previous report has distinctive tokens\n", encoding="utf-8")
            result = profile(repo, repetitions=1, exclude_paths=(output,))
            self.assertEqual(result["indexed_files"], 1)
            self.assertEqual(result["indexed_lines"], 1)

    def test_invalid_repetitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                profile(pathlib.Path(tmp), repetitions=0)

if __name__ == "__main__":
    unittest.main()
