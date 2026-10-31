import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RagCLITests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, "-m", "agent_toolset", "rag-search", *args],
                              cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                              capture_output=True, text=True)

    def test_grounded_hit_and_no_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "evidence.md").write_text("release candidate provenance\n")
            hit = self.invoke("--repo", tmp, "--query", "provenance")
            self.assertEqual(hit.returncode, 0, hit.stderr + hit.stdout)
            doc = json.loads(hit.stdout)
            self.assertEqual(doc["status"], "PASS")
            self.assertEqual(doc["hits"][0]["line"], 1)
            self.assertEqual(doc["hits"][0]["path"], "evidence.md")
            self.assertEqual(len(doc["hits"][0]["sha256"]), 64)
            miss = self.invoke("--repo", tmp, "--query", "unmatched_term_9382")
            self.assertEqual(miss.returncode, 0)
            self.assertEqual(json.loads(miss.stdout)["hits"], [])

    def test_invalid_limit_and_missing_repo_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = self.invoke("--repo", tmp, "--query", "a", "--limit", "0")
            self.assertEqual(invalid.returncode, 2)
            self.assertEqual(json.loads(invalid.stdout)["status"], "BLOCKED")
            missing = self.invoke("--repo", str(pathlib.Path(tmp) / "missing"), "--query", "a")
            self.assertEqual(missing.returncode, 2)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "notes.md").write_text("allowedtoken\n")
            outside = pathlib.Path(tmp).parent / (root.name + "-outside-secret.md")
            outside.write_text("forbiddentoken\n")
            try:
                (root / "docs" / "escape.md").symlink_to(outside)
                doc = json.loads(self.invoke("--repo", tmp, "--query", "forbiddentoken").stdout)
                self.assertEqual(doc["hits"], [])
            finally:
                outside.unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
