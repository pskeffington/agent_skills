import tempfile
import unittest
from pathlib import Path
from agent_toolset.rag import build_index, search, verify_hit

class RagTests(unittest.TestCase):
    def test_ranking_and_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "one.md").write_text("alpha beta alpha\nother\n", encoding="utf-8")
            (root / "two.md").write_text("alpha only\n", encoding="utf-8")
            hits = search(build_index(root), "alpha beta")
            self.assertEqual(hits[0]["path"], "one.md")
            self.assertTrue(verify_hit(root, hits[0]))
            (root / "one.md").write_text("tampered\n", encoding="utf-8")
            self.assertFalse(verify_hit(root, hits[0]))

    def test_symlink_escape_and_ignored_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root.parent / (root.name + "-outside.md")
            outside.write_text("secretmarker", encoding="utf-8")
            try:
                (root / "leak.md").symlink_to(outside)
                (root / ".git").mkdir()
                (root / ".git" / "private.md").write_text("secretmarker")
                self.assertEqual(search(build_index(root), "secretmarker"), [])
            finally:
                outside.unlink(missing_ok=True)

    def test_empty_and_bad_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            index = build_index(temp)
            self.assertEqual(search(index, "anything"), [])
            with self.assertRaises(ValueError):
                search(index, "anything", limit=0)

if __name__ == "__main__":
    unittest.main()
