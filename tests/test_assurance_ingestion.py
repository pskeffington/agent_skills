import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.assurance.ci import classify_github_run
from agent_toolset.assurance.security import summarize_findings

class AssuranceIngestionTests(unittest.TestCase):
    def test_current_successful_ci_and_required_check(self):
        commit="a"*40
        report=classify_github_run({"id":42,"head_sha":commit,"conclusion":"success","jobs":[{"name":"structural","conclusion":"success"}]},expected_commit=commit,required_checks={"structural"})
        self.assertEqual("PASS",report["status"])
    def test_stale_failed_missing_and_in_progress_ci_fail_closed(self):
        commit="a"*40
        self.assertEqual("FAIL",classify_github_run({"head_sha":"b"*40,"conclusion":"success","jobs":[]},expected_commit=commit)["status"])
        self.assertEqual("FAIL",classify_github_run({"head_sha":commit,"conclusion":"failure","jobs":[]},expected_commit=commit)["status"])
        self.assertEqual("BLOCKED",classify_github_run({"head_sha":commit,"conclusion":"in_progress","jobs":[]},expected_commit=commit)["status"])
        self.assertEqual("BLOCKED",classify_github_run({"head_sha":commit,"conclusion":"weird-new-state","jobs":[]},expected_commit=commit)["status"])
        self.assertTrue(classify_github_run({"head_sha":commit,"conclusion":"success","jobs":[]},expected_commit=commit,required_checks={"test"})["issues"])
    def test_security_severity_threshold_and_missing_export(self):
        self.assertEqual("PASS",summarize_findings({"findings":[{"severity":"low"}]})["status"])
        self.assertEqual("FAIL",summarize_findings({"findings":[{"severity":"critical"}]})["status"])
        self.assertEqual("BLOCKED",summarize_findings({})["status"])
        self.assertEqual("FAIL",summarize_findings({"findings":[{}]})["status"])

if __name__=="__main__": unittest.main()
