import json
import pathlib
import subprocess
import hashlib
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
    def test_rag_search_with_provenance_no_answer_and_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); (root/"doc.md").write_text("durable release gate evidence\n",encoding="utf-8")
            hit=self.run_cli("search","--repo",str(root),"--query","release gate")
            self.assertEqual(0,hit.returncode,hit.stderr)
            hits=json.loads(hit.stdout)["hits"]
            self.assertTrue(hits)
            self.assertIn("sha256",hits[0])
            self.assertIsInstance(hits[0]["line"],int)
            empty=self.run_cli("search","--repo",str(root),"--query","zzzzqwertyuiop998877")
            self.assertEqual(0,empty.returncode)
            self.assertEqual([],json.loads(empty.stdout)["hits"])
            bad=self.run_cli("search","--repo",str(root),"--query","anything","--limit","0")
            self.assertEqual(2,bad.returncode)
            unsafe=self.run_cli("search","--repo",str(root/"missing"),"--query","anything")
            self.assertEqual(2,unsafe.returncode)

    def test_ci_and_security_ingestion_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            ci=pathlib.Path(tmp)/"run.json"; commit="a"*40
            ci.write_text(json.dumps({"id":1,"head_sha":commit,"conclusion":"success","jobs":[{"name":"structural","conclusion":"success"}]}))
            self.assertEqual(0,self.run_cli("ci-ingest",str(ci),"--commit",commit,"--required-check","structural").returncode)
            findings=pathlib.Path(tmp)/"findings.json"; findings.write_text(json.dumps({"findings":[{"severity":"critical"}]}))
            self.assertEqual(1,self.run_cli("security-summary",str(findings)).returncode)
    def test_deterministic_standalone_zipapp(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=pathlib.Path(tmp)/"one.pyz"; second=pathlib.Path(tmp)/"two.pyz"
            build=self.run_cli("doctor")
            self.assertEqual(0,build.returncode)
            subprocess.run([sys.executable,str(ROOT/"scripts/build_zipapp.py"),str(first)],check=True,capture_output=True,text=True)
            subprocess.run([sys.executable,str(ROOT/"scripts/build_zipapp.py"),str(second)],check=True,capture_output=True,text=True)
            self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(),hashlib.sha256(second.read_bytes()).hexdigest())
            result=subprocess.run([sys.executable,str(first),"doctor"],cwd=tmp,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin","PYTHONDONTWRITEBYTECODE":"1"})
            self.assertEqual(0,result.returncode,result.stderr)
            self.assertEqual("PASS",json.loads(result.stdout)["status"])
    def test_bad_arguments_and_corrupted_journal_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"events.jsonl"; path.write_text("not-json\n")
            result=self.run_cli("replay","--state",str(path)); self.assertEqual(2,result.returncode); self.assertEqual("BLOCKED",json.loads(result.stdout)["status"])
        self.assertEqual(2,self.run_cli("unknown").returncode)

if __name__=="__main__": unittest.main()
