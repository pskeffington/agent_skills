import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from benchmark_rag import run_benchmark

class BenchmarkRagTests(unittest.TestCase):
    def test_benchmark_report_contains_required_measurements(self):
        report=run_benchmark(ROOT/"tests/fixtures/rag_eval",repetitions=2)
        self.assertEqual("PASS",report["status"])
        self.assertIn("corpus_fingerprint",report["environment"])
        self.assertIn("worktree_clean",report["environment"])
        self.assertGreater(report["corpus"]["indexed_nonempty_lines"],0)
        self.assertEqual(2,len(report["cold_build"]["samples"]))
        self.assertEqual(2,len(report["warm_search"]["samples"]))
        self.assertEqual(2,len(report["warm_cache_load"]["samples"]))
        self.assertTrue(report["invalidation"]["rebuild_detected"])
        self.assertIn("no speedup claim",report["scope"])
    def test_benchmark_repetition_bounds(self):
        with self.assertRaises(ValueError): run_benchmark(ROOT/"tests/fixtures/rag_eval",repetitions=0)

if __name__=="__main__": unittest.main()
