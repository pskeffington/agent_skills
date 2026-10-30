import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import time
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
    def test_codex_default_is_disabled(self):
        self.assertEqual("BLOCKED",CodexCLIAdapter().prepare({},{}).status)
        self.assertEqual("BLOCKED",CodexCLIAdapter().execute({},{}).status)

    def test_codex_requires_external_process_containment_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); binary=self._fake_codex(temp)
            result=CodexCLIAdapter(enabled=True,executable=binary).execute(self._task(repo),{"worktree":str(repo),"dedicated_worktree":True})
            self.assertEqual("BLOCKED",result.status)
            self.assertIn("external process containment",result.message)

    def _task(self, root):
        head=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
        return {"schema_version":"1.0.0","task_id":"DEV-001","repository":"example/project","base_commit":head,"objective":"Implement a bounded fixture change.","scope":{"include":["allowed.txt"],"exclude":[]},"acceptance":["The fixture file is updated correctly"],"risk":"low","owner_role":"implementer","status":"ready"}

    def _fake_codex(self, directory, *, outside=False, ignored=False, sleep_seconds=0, ready_file=None, late_child=False):
        script=pathlib.Path(directory)/"codex-fake"
        child_code=f"import pathlib,time; time.sleep(0.5); pathlib.Path({str(pathlib.Path(directory)/'late-outside.txt')!r}).write_text('late')"
        launch_child="subprocess.Popen([sys.executable, '-c', "+repr(child_code)+"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n" if late_child else ""
        script.write_text("#!/usr/bin/env python3\nimport json, pathlib, subprocess, sys, time\nargs=sys.argv[1:]\nif args == ['--version']:\n print('codex-cli 0.147.0')\n raise SystemExit(0)\nif args == ['exec', '--help']:\n print('--strict-config --json --ephemeral --ignore-user-config --sandbox --cd --output-last-message')\n raise SystemExit(0)\nroot=pathlib.Path(args[args.index('--cd')+1])\nfor line in sys.stdin: pass\n" + (f"pathlib.Path({str(ready_file)!r}).write_text('ready')\n" if ready_file else "") + (f"time.sleep({sleep_seconds})\n" if sleep_seconds else "") + launch_child + "(root / 'allowed.txt').write_text('updated\\n')\n" + ("(root / 'outside.txt').write_text('out\\n')\n" if outside else "") + ("(root / 'ignored.txt').write_text('ignored\\n')\n" if ignored else "") + "print(json.dumps({'type':'turn.completed','status':'completed'}), flush=True)\n")
        script.chmod(0o755)
        return str(script)

    def _worktree(self, directory):
        primary=pathlib.Path(directory)/"primary"
        primary.mkdir()
        subprocess.run(["git","init","-q",str(primary)],check=True)
        (primary/"allowed.txt").write_text("before\n")
        (primary/".gitignore").write_text("ignored.txt\n")
        subprocess.run(["git","-C",str(primary),"add","allowed.txt",".gitignore"],check=True)
        subprocess.run(["git","-C",str(primary),"-c","user.name=Test","-c","user.email=test@example.invalid","commit","-qm","fixture"],check=True)
        repo=pathlib.Path(directory)/"task-worktree"
        subprocess.run(["git","-C",str(primary),"worktree","add","-q","-b","task-fixture",str(repo)],check=True)
        return repo

    def test_codex_opt_in_executes_in_clean_worktree_and_checks_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); binary=self._fake_codex(temp); marker=pathlib.Path(temp)/"fsmonitor-ran"
            subprocess.run(["git","-C",str(repo),"config","core.fsmonitor",f"!touch {marker}"],check=True)
            task=self._task(repo)
            adapter=CodexCLIAdapter(enabled=True,executable=binary)
            sandbox={"worktree":str(repo),"dedicated_worktree":True,"external_process_containment":True,"containment_ref":"test://contained-runtime"}
            result=adapter.execute(task,sandbox)
            self.assertEqual("PASS",result.status,f"{result.message}: {result.provenance}")
            self.assertEqual(["allowed.txt"],result.provenance["changed_paths"])
            self.assertTrue(result.provenance["turn_completed"])
            self.assertEqual("updated\n",(repo/"allowed.txt").read_text())
            self.assertFalse(marker.exists(),"repository fsmonitor config executed during validation")

    def test_codex_blocks_dirty_wrong_base_and_out_of_scope_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); binary=self._fake_codex(temp,outside=True)
            task=self._task(repo); adapter=CodexCLIAdapter(enabled=True,executable=binary)
            sandbox={"worktree":str(repo),"dedicated_worktree":True,"external_process_containment":True,"containment_ref":"test://contained-runtime"}
            (repo/"dirty.txt").write_text("dirty")
            self.assertEqual("BLOCKED",adapter.execute(task,sandbox).status)
            (repo/"dirty.txt").unlink()
            bad={**task,"base_commit":"0"*40}
            self.assertEqual("BLOCKED",adapter.execute(bad,sandbox).status)
            result=adapter.execute(task,sandbox)
            self.assertEqual("FAIL",result.status)
            self.assertFalse(result.provenance["scope_verified"])

    def test_codex_detects_ignored_out_of_scope_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); binary=self._fake_codex(temp,ignored=True)
            result=CodexCLIAdapter(enabled=True,executable=binary).execute(self._task(repo),{"worktree":str(repo),"dedicated_worktree":True,"external_process_containment":True,"containment_ref":"test://contained-runtime"})
            self.assertEqual("FAIL",result.status)
            self.assertIn("ignored.txt",result.message)

    def test_codex_kills_descendant_before_reporting_success(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); late=pathlib.Path(temp)/"late-outside.txt"; binary=self._fake_codex(temp,late_child=True)
            result=CodexCLIAdapter(enabled=True,executable=binary).execute(self._task(repo),{"worktree":str(repo),"dedicated_worktree":True,"external_process_containment":True,"containment_ref":"test://contained-runtime"})
            self.assertIn(result.status,{"PASS","BLOCKED"},result.message)
            if result.status == "PASS":
                self.assertTrue(result.provenance["process_tree_stopped"])
            else:
                self.assertIn("process tree",result.message)
            time.sleep(.7)
            self.assertFalse(late.exists(),"descendant wrote after the runner reported completion")

    def test_codex_timeout_terminates_process_and_reports_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); binary=self._fake_codex(temp,sleep_seconds=3)
            adapter=CodexCLIAdapter(enabled=True,executable=binary,timeout_seconds=1)
            result=adapter.execute(self._task(repo),{"worktree":str(repo),"dedicated_worktree":True,"external_process_containment":True,"containment_ref":"test://contained-runtime"})
            self.assertEqual("BLOCKED",result.status)
            self.assertTrue(result.provenance["timed_out"])

    def test_codex_cancel_terminates_active_process(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); ready=pathlib.Path(temp)/"ready"; binary=self._fake_codex(temp,sleep_seconds=5,ready_file=ready)
            adapter=CodexCLIAdapter(enabled=True,executable=binary,timeout_seconds=10)
            results=[]
            worker=threading.Thread(target=lambda:results.append(adapter.execute(self._task(repo),{"worktree":str(repo),"dedicated_worktree":True,"run_id":"test-cancel-run","external_process_containment":True,"containment_ref":"test://contained-runtime"})))
            worker.start()
            deadline=time.monotonic()+4
            while time.monotonic()<deadline and not ready.exists():
                time.sleep(.02)
            cancelled=adapter.cancel("test-cancel-run")
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive())
            self.assertEqual("PASS",cancelled.status)
            self.assertTrue(cancelled.provenance["cancelled"])
            self.assertEqual("BLOCKED",results[0].status)

    def test_codex_rejects_duplicate_active_run_id(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=self._worktree(temp); ready=pathlib.Path(temp)/"ready"; binary=self._fake_codex(temp,sleep_seconds=2,ready_file=ready)
            adapter=CodexCLIAdapter(enabled=True,executable=binary,timeout_seconds=5)
            sandbox={"worktree":str(repo),"dedicated_worktree":True,"run_id":"same-run","external_process_containment":True,"containment_ref":"test://contained-runtime"}
            first=[]
            worker=threading.Thread(target=lambda:first.append(adapter.execute(self._task(repo),sandbox)))
            worker.start()
            deadline=time.monotonic()+4
            while time.monotonic()<deadline and not ready.exists():
                time.sleep(.02)
            second=adapter.execute(self._task(repo),sandbox)
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive())
            self.assertEqual("BLOCKED",second.status)
            self.assertIn("already active",second.message)
            self.assertEqual("PASS",first[0].status)
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
