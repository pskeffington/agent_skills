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
            s.transition("F3-A", "review", owner="worker", lease_token=lease["token"], now=101)
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
            with self.assertRaises(ScheduleError): s.acquire("F3-A", "two", now=111)
            with self.assertRaises(ScheduleError): s.reclaim_expired("F3-A","two","worker stopped",process_check=lambda _:None,now=111)
            with self.assertRaises(ScheduleError): s.reclaim_expired("F3-A","two","worker stopped",process_check=lambda _:False,now=111)
            reclaimed=s.reclaim_expired("F3-A","two","confirmed worker process ended",process_check=lambda _:True,now=111)
            with self.assertRaises(ScheduleError): s.release("F3-A", "one", lease["token"])
            s.release("F3-A", "two", reclaimed["token"])

    def test_overlapping_writer_scopes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp)
            first=self.task("F3-A"); second=self.task("F3-B")
            second["scope"]["include"]=["src/a.py"]
            third=self.task("F3-C"); third["scope"]["include"]=["tests/test.py"]
            s.add_tasks([first,second,third])
            s.acquire("F3-A","writer-one",now=100)
            with self.assertRaises(ScheduleError): s.acquire("F3-B","writer-two",now=100)
            self.assertEqual("queued",s.status()["tasks"]["F3-B"]["status"])
            self.assertEqual("running",s.status()["tasks"]["F3-A"]["status"])
            s.acquire("F3-C","writer-three",now=100)

    def test_cancelling_leased_task_requires_verified_worker_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp)
            first=self.task("F3-A"); second=self.task("F3-B")
            first["scope"]["include"]=["src/shared.py"]
            second["scope"]["include"]=["src/shared.py"]
            s.add_tasks([first,second])
            lease=s.acquire("F3-A","worker-a",now=100)
            with self.assertRaises(ScheduleError): s.cancel("F3-A","operator requested stop")
            with self.assertRaises(ScheduleError): s.cancel("F3-A","operator requested stop",process_check=lambda _:False)
            with self.assertRaises(ScheduleError): s.acquire("F3-B","worker-b",now=101)
            s.cancel("F3-A","operator requested stop",process_check=lambda current:current["token"]==lease["token"])
            self.assertEqual("worker-b",s.acquire("F3-B","worker-b",now=102)["owner"])

    def test_concurrent_task_lease_acquisition_is_atomic(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"events.jsonl"
            Scheduler(Journal(path)).add_tasks([self.task("F3-A")])
            def acquire(owner):
                try: return Scheduler(Journal(path)).acquire("F3-A",owner,now=100)["owner"]
                except ScheduleError: return "REJECTED"
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes=list(pool.map(acquire,["one","two"]))
            self.assertEqual(1,sum(outcome!="REJECTED" for outcome in outcomes))
            events=Journal(path).replay()
            self.assertEqual(1,sum(event["event_type"]=="LEASE_ACQUIRED" for event in events))

    def test_running_transition_requires_lease_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.scheduler(tmp); s.add_tasks([self.task("F3-A")]); s.acquire("F3-A","worker",now=100)
            with self.assertRaises(ScheduleError): s.transition("F3-A","review",now=101)

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
