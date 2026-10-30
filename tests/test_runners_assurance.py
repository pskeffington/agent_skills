import json
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.runners.dry_run import DryRunRunner
from agent_toolset.runners.codex_cli import CodexCLIAdapter
from agent_toolset.assurance.evidence import assess_evidence, reviewer_independence

class RunnerAssuranceTests(unittest.TestCase):
    def evidence(self):
        return {"schema_version":"1.0.0","task_id":"F6-review","stage":"verify","source_commit":"a"*40,"result":"PASS","checks":[{"name":"unit","result":"PASS","provenance":"command: unittest exit 0"}],"artifacts":[]}
    def test_dry_run_never_executes(self):
        r=DryRunRunner()
        self.assertEqual("PASS",r.prepare({"task_id":"a"},{}) .status)
        self.assertEqual("BLOCKED",r.execute({"task_id":"a"},{}).status)
    def test_codex_default_blocked_and_even_enabled_only_probes(self):
        self.assertEqual("BLOCKED",CodexCLIAdapter().prepare({},{}).status)
        adapter=CodexCLIAdapter(enabled=True)
        self.assertEqual("BLOCKED",adapter.execute({},{}).status)
        self.assertFalse(adapter.execute({},{}).provenance.get("execution_enabled", False))
    def test_stale_and_failed_evidence(self):
        doc=self.evidence()
        self.assertEqual("PASS",assess_evidence(doc,subject_commit="a"*40)["status"])
        self.assertEqual("FAIL",assess_evidence(doc,subject_commit="b"*40)["status"])
        doc["checks"][0]["result"]="FAIL"
        self.assertEqual("FAIL",assess_evidence(doc,subject_commit="a"*40)["status"])
    def test_independent_assurance_identity(self):
        self.assertEqual("PASS",reviewer_independence(author_invocation="one",reviewer_invocation="two",author_role="implementer",reviewer_role="reviewer")["status"])
        self.assertEqual("FAIL",reviewer_independence(author_invocation="same",reviewer_invocation="same",author_role="implementer",reviewer_role="reviewer")["status"])
        self.assertEqual("FAIL",reviewer_independence(author_invocation="one",reviewer_invocation="two",author_role="implementer",reviewer_role="implementer")["status"])

if __name__=="__main__": unittest.main()
