import copy
import json
import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.journal import Journal
from agent_toolset.scheduler import Scheduler, ScheduleError

class SchedulerTests(unittest.TestCase):
    def task(self, task_id, deps=()):
        return {"schema_version":"1.0.0","task_id":task_id,"repository":"example/repo","base_commit":"a"*40,"objective":"Implement this scoped feature safely.","scope":{"include":["src/a.py"],"exclude":[]},"acceptance":["Relevant deterministic tests pass"],"risk":"low","owner_role":"implementer","status":"queued","depends_on":list(deps)}

    def scheduler(self, tmp, **kwargs):
        return Scheduler(Journal(pathlib.Path(tmp)/"events.jsonl"), **kwargs)

    def test_dag_readiness_and_dependency_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp)
            s.add_tasks([self.task("F3-A"), self.task("F3-B", ["F3-A"])])
            self.assertEqual(["F3-A"], s.plan())
            with self.assertRaises(ScheduleError): s.transition("F3-B", "ready")
            s.transition("F3-A", "ready")
            lease=s.acquire("F3-A", "worker", now=100)
            self.assertEqual("running", s.status()["tasks"]["F3-A"]["status"])
            s.transition("F3-A", "review")
            s.transition("F3-A", "done")
            s.release("F3-A", "worker", lease["token"])
            self.assertEqual(["F3-B"], s.plan())

    def test_missing_parent_and_cycle_rejected_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp)
            with self.assertRaises(ScheduleError): s.add_tasks([self.task("F3-A", ["F3-X"])])
            a,b=self.task("F3-A", ["F3-B"]),self.task("F3-B", ["F3-A"])
            with self.assertRaises(ScheduleError): s.add_tasks([a,b])
            self.assertEqual({}, s.status()["tasks"])

    def test_lease_conflict_expiry_and_owner_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp, lease_seconds=10)
            s.add_tasks([self.task("F3-A")])
            lease=s.acquire("F3-A", "one", now=100)
            with self.assertRaises(ScheduleError): s.acquire("F3-A", "two", now=105)
            reclaimed=s.acquire("F3-A", "two", now=111)
            with self.assertRaises(ScheduleError): s.release("F3-A", "one", lease["token"])
            s.release("F3-A", "two", reclaimed["token"])

    def test_retry_budget_and_cancellation(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp, max_retries=2)
            s.add_tasks([self.task("F3-A")])
            self.assertEqual(1,s.retry("F3-A", "same-root-cause"))
            self.assertEqual(2,s.retry("F3-A", "same-root-cause"))
            with self.assertRaises(ScheduleError): s.retry("F3-A", "same-root-cause")
            s.cancel("F3-A", "operator requested stop")
            self.assertEqual("cancelled",s.status()["tasks"]["F3-A"]["status"])

if __name__=="__main__": unittest.main()
