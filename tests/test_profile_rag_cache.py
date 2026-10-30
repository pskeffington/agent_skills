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
            self.assertEqual(len(result["operations"]["strict_warm_cache"]["samples"]), 2)
            self.assertGreaterEqual(result["operations"]["cold_build"]["median_ms"], 0)

    def test_invalid_repetitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                profile(pathlib.Path(tmp), repetitions=0)

if __name__ == "__main__":
    unittest.main()
