import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from benchmark_rag_citations import run_benchmark

class CitationBenchmarkTests(unittest.TestCase):
    def test_report_requires_equal_verification_and_records_repetitions(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/"notes.md").write_text("release readiness task journal lease\nCodex runner containment attestation\ncache fingerprint validation\n",encoding="utf-8")
            report=run_benchmark(root,repetitions=2)
            self.assertEqual("PASS",report["status"])
            self.assertEqual(3,len(report["results"]))
            self.assertTrue(all(item["validity_results_equal"] for item in report["results"]))
            self.assertTrue(all(len(item["per_hit_samples_ms"])==2 and len(item["batched_samples_ms"])==2 for item in report["results"]))

    def test_repetition_count_is_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                run_benchmark(pathlib.Path(temp),repetitions=0)

    def test_report_path_is_excluded_for_repeatable_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp); (root/"notes.md").write_text("release readiness task journal lease\n",encoding="utf-8")
            report=root/"report.json"
            first=run_benchmark(root,repetitions=1,exclude_paths=(report,))
            report.write_text("Codex runner containment attestation cache fingerprint validation",encoding="utf-8")
            second=run_benchmark(root,repetitions=1,exclude_paths=(report,))
            self.assertEqual(first["environment"]["corpus_fingerprint"],second["environment"]["corpus_fingerprint"])
            self.assertEqual([(r["hit_count"],r["distinct_sources"]) for r in first["results"]],
                             [(r["hit_count"],r["distinct_sources"]) for r in second["results"]])

if __name__=="__main__": unittest.main()
