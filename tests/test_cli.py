import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]

class CLITests(unittest.TestCase):
    def run_cli(self,*args):
        env={"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","PYTHONDONTWRITEBYTECODE":"1"}
        return subprocess.run([sys.executable,"-m","agent_toolset",*args],cwd=ROOT,env=env,capture_output=True,text=True)
    def test_doctor_inventory_and_dry_run(self):
        self.assertEqual(0,self.run_cli("doctor").returncode)
        inv=self.run_cli("inventory","--repo",str(ROOT)); self.assertEqual(0,inv.returncode); self.assertIn("inventory_sha256",json.loads(inv.stdout))
        run=self.run_cli("run","examples/feature-task.json"); self.assertEqual(0,run.returncode); self.assertEqual("dry-run",json.loads(run.stdout)["runner"])
    def test_plan_status_replay_export_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            task=ROOT/"examples/feature-task.json"; state=pathlib.Path(tmp)/"events.jsonl"
            plan=self.run_cli("plan",str(task),"--state",str(state)); self.assertEqual(0,plan.returncode,plan.stdout)
            self.assertEqual(0,self.run_cli("status","--state",str(state)).returncode)
            self.assertEqual(0,self.run_cli("replay","--state",str(state)).returncode)
            self.assertEqual(0,self.run_cli("export","--state",str(state)).returncode)
    def test_verify_and_release_blocked_exit_codes(self):
        ev=self.run_cli("verify","examples/feature-evidence.json","--commit","0"*40); self.assertEqual(2,ev.returncode)
        with tempfile.TemporaryDirectory() as tmp:
            dossier=pathlib.Path(tmp)/"bad.json"; dossier.write_text("{}")
            release=self.run_cli("release-check",str(dossier)); self.assertEqual(2,release.returncode)
    def test_ci_and_security_ingestion_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            ci=pathlib.Path(tmp)/"run.json"; commit="a"*40
            ci.write_text(json.dumps({"id":1,"head_sha":commit,"conclusion":"success","jobs":[{"name":"structural","conclusion":"success"}]}))
            self.assertEqual(0,self.run_cli("ci-ingest",str(ci),"--commit",commit,"--required-check","structural").returncode)
            findings=pathlib.Path(tmp)/"findings.json"; findings.write_text(json.dumps({"findings":[{"severity":"critical"}]}))
            self.assertEqual(1,self.run_cli("security-summary",str(findings)).returncode)
    def test_bad_arguments_and_corrupted_journal_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"events.jsonl"; path.write_text("not-json\n")
            result=self.run_cli("replay","--state",str(path)); self.assertEqual(2,result.returncode); self.assertEqual("BLOCKED",json.loads(result.stdout)["status"])
        self.assertEqual(2,self.run_cli("unknown").returncode)

if __name__=="__main__": unittest.main()
