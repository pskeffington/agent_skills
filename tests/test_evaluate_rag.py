import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from evaluate_rag import evaluate

class RagEvaluationTests(unittest.TestCase):
    def test_labeled_metrics_and_no_answer_behavior(self):
        report=evaluate(ROOT/"tests/fixtures/rag_eval",ROOT/"examples/rag-evaluation.json")
        self.assertEqual("PASS",report["status"])
        self.assertEqual(5,report["case_count"])
        self.assertEqual(0,report["no_answer_false_positives"])
        self.assertGreaterEqual(report["mean_precision_at_k"],0.8)
        injection=next(case for case in report["cases"] if case["untrusted_data_case"])
        self.assertIn("injection.md",injection["retrieved"])
        self.assertEqual("fixture-only; file-level metrics over unique paths; no claim of general retrieval quality or instruction-following safety",report["scope"])

if __name__=="__main__": unittest.main()
