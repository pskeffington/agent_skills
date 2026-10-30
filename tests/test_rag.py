import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agent_toolset import rag
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

    def test_secret_canaries_are_not_indexed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidates = {
                "secrets/credential.json": "canarysecret",
                ".aws/credentials": "canarysecret",
                "private/notes.md": "canarysecret",
                ".env.production.json": "canarysecret",
                "id_rsa": "canarysecret",
                "certificate.pem": "canarysecret",
                "credentials-prod.md": "canarysecret",
            }
            for name, content in candidates.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            index = build_index(root)
            self.assertEqual([], search(index, "canarysecret"))
            indexed_paths = {document["path"] for document in index["documents"]}
            self.assertTrue(indexed_paths.isdisjoint(candidates))

    def test_descriptor_relative_read_survives_parent_symlink_swap(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            safe = root / "safe"
            outside = base / "outside"
            safe.mkdir(parents=True)
            outside.mkdir()
            (safe / "doc.md").write_text("safe canary", encoding="utf-8")
            (outside / "doc.md").write_text("outside canary", encoding="utf-8")

            real_open = rag._ORIGINAL_OS_OPEN
            swapped = False

            def swap_after_open(path, flags, *args, **kwargs):
                nonlocal swapped
                fd = real_open(path, flags, *args, **kwargs)
                if path == "safe" and kwargs.get("dir_fd") is not None and not swapped:
                    (root / "safe").rename(root / "moved")
                    (root / "safe").symlink_to(outside, target_is_directory=True)
                    swapped = True
                return fd

            with patch.object(rag, "_ORIGINAL_OS_OPEN", side_effect=swap_after_open):
                data = rag._read_confined_file(root, "safe/doc.md")
            self.assertTrue(swapped)
            self.assertEqual(b"safe canary", data)

    def test_confined_read_rejects_symlinked_directory_and_file(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as other:
            root = Path(temp)
            outside = Path(other) / "secret.md"
            outside.write_text("secret", encoding="utf-8")
            (root / "linked-dir").symlink_to(Path(other), target_is_directory=True)
            (root / "linked-file.md").symlink_to(outside)
            with self.assertRaises(OSError):
                rag._read_confined_file(root, "linked-dir/secret.md")
            with self.assertRaises(OSError):
                rag._read_confined_file(root, "linked-file.md")

if __name__ == "__main__":
    unittest.main()
