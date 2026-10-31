import pathlib
import sys
import stat
import tempfile
import unittest
from pathlib import Path
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.rag import _decode_cache_entry, _encode_cache_entry, cache_fingerprint, load_or_build_cache, search

class RagCacheTests(unittest.TestCase):
    def test_create_reuse_and_content_invalidation(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); source=repo/"notes.md"; source.write_text("amber release record\\n",encoding="utf-8")
            first,fingerprint1,hit1=load_or_build_cache(repo,cache)
            cache_entry=cache/f"index-v2-{fingerprint1}.json"
            self.assertEqual(0o600,stat.S_IMODE(cache_entry.stat().st_mode))
            second,fingerprint2,hit2=load_or_build_cache(repo,cache)
            self.assertFalse(hit1); self.assertTrue(hit2); self.assertEqual(fingerprint1,fingerprint2)
            self.assertEqual(search(first,"amber"),search(second,"amber"))
            source.write_text("violet release record\\n",encoding="utf-8")
            third,fingerprint3,hit3=load_or_build_cache(repo,cache)
            self.assertFalse(hit3); self.assertNotEqual(fingerprint1,fingerprint3)
            self.assertTrue(search(third,"violet"))

    def test_corrupt_cache_entry_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); (repo/"doc.md").write_text("cache content\\n",encoding="utf-8")
            _,fingerprint,_=load_or_build_cache(repo,cache)
            target=cache/f"index-v2-{fingerprint}.json"
            bad_index={"format":1,"root":str(repo.resolve()),"documents":[{"path":"doc.md","line":1,"text":"cache content\\n","sha256":"a"*64,"tf":[]}]}
            target.write_bytes(_encode_cache_entry(fingerprint,bad_index))
            with self.assertRaises(ValueError): load_or_build_cache(repo,cache)

    def test_cached_index_rejects_noncanonical_or_escaping_paths(self):
        from agent_toolset.rag import _valid_cached_index
        base=Path("/repo")
        valid_doc={"path":"docs/guide.md","line":1,"text":"safe","sha256":"a"*64,"tf":{"safe":1}}
        for invalid_path in ("", "/etc/passwd", "../outside", "docs//guide.md", "docs\\guide.md"):
            with self.subTest(path=invalid_path):
                document={**valid_doc,"path":invalid_path}
                self.assertFalse(_valid_cached_index({"format":1,"root":str(base),"documents":[document]},base))

    def test_cached_index_rejects_noninteger_format_versions(self):
        from agent_toolset.rag import _valid_cached_index
        base=Path("/repo")
        valid_doc={"path":"docs/guide.md","line":1,"text":"safe","sha256":"a"*64,"tf":{"safe":1}}
        for format_version in (True,1.0):
            with self.subTest(format=format_version):
                self.assertFalse(_valid_cached_index({"format":format_version,"root":str(base),"documents":[valid_doc]},base))

    def test_cache_digest_hex_validation_rejects_invalid_repeated_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); (repo/"doc.md").write_text("first line\nsecond line\n",encoding="utf-8")
            _,fingerprint,_=load_or_build_cache(repo,cache)
            target=cache/f"index-v2-{fingerprint}.json"
            bad_index={"format":1,"root":str(repo.resolve()),"documents":[
                {"path":"doc.md","line":1,"text":"first line","sha256":"a"*64,"tf":{"first":1}},
                {"path":"doc.md","line":2,"text":"second line","sha256":"z"*64,"tf":{"second":1}},
            ]}
            target.write_bytes(_encode_cache_entry(fingerprint,bad_index))
            with self.assertRaises(ValueError): load_or_build_cache(repo,cache)

    def test_cache_payload_tampering_fails_digest_check(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); (repo/"doc.md").write_text("payload integrity\n",encoding="utf-8")
            _,fingerprint,_=load_or_build_cache(repo,cache)
            target=cache/f"index-v2-{fingerprint}.json"
            data=bytearray(target.read_bytes()); data[-1]^=1; target.write_bytes(data)
            with self.assertRaisesRegex(ValueError,"digest mismatch"):
                load_or_build_cache(repo,cache)

    def test_cache_entry_rejects_malformed_framing_and_ignores_legacy_name(self):
        with self.assertRaisesRegex(ValueError,"unsupported format"):
            _decode_cache_entry(b'{"fingerprint":"legacy"}',"a"*64)
        with self.assertRaisesRegex(ValueError,"malformed header"):
            _decode_cache_entry(b"AGENT-TOOLSET-CACHE/2\nmissing-separator","a"*64)
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); cache.mkdir(); (repo/"doc.md").write_text("legacy ignored\n",encoding="utf-8")
            fingerprint,_,_=cache_fingerprint(repo)
            legacy=cache/("index-"+fingerprint+".json")
            legacy.write_text("not a valid cache entry",encoding="utf-8")
            index,loaded_fingerprint,hit=load_or_build_cache(repo,cache)
            self.assertFalse(hit)
            self.assertEqual(fingerprint,loaded_fingerprint)
            self.assertTrue((cache/("index-v2-"+fingerprint+".json")).is_file())
            self.assertTrue(index["documents"])

    def test_excluded_ancestor_of_repository_excludes_all_sources(self):
        from agent_toolset.rag import _source_records
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp); repo=parent/"repo"; repo.mkdir()
            (repo/"notes.md").write_text("excluded by ancestor\n",encoding="utf-8")
            self.assertEqual([],_source_records(repo, {".md"}, exclude_paths=(parent.resolve(),)))

    def test_symlinked_cache_directory_and_entry_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as other:
            base=pathlib.Path(temp); repo=base/"repo"; repo.mkdir(); (repo/"doc.md").write_text("link test\\n")
            alias=base/"cache-link"; alias.symlink_to(other,target_is_directory=True)
            with self.assertRaises(ValueError): load_or_build_cache(repo,alias)
            cache=base/"cache"; cache.mkdir()
            _,fingerprint,_=load_or_build_cache(repo,cache)
            target=cache/f"index-v2-{fingerprint}.json"; target.unlink(); target.symlink_to(pathlib.Path(other)/"outside.json")
            with self.assertRaises(ValueError): load_or_build_cache(repo,cache)

    def test_symlinked_cache_parent_inside_repository_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as other:
            base=pathlib.Path(temp); repo=base/"repo"; repo.mkdir()
            (repo/"doc.md").write_text("cache parent probe\n",encoding="utf-8")
            outside=pathlib.Path(other)
            (repo/"cache-link").symlink_to(outside,target_is_directory=True)
            with self.assertRaises(ValueError):
                load_or_build_cache(repo,repo/"cache-link"/"nested")
            self.assertEqual([],list(outside.iterdir()))

    def test_cache_parent_swap_cannot_redirect_entry_write(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); cache.mkdir()
            (repo/"doc.md").write_text("cache race content\n",encoding="utf-8")
            # Cache opens are anchored to the directory descriptor. Replacing its
            # pathname afterward must not redirect the atomic write elsewhere.
            import agent_toolset.rag as rag
            from unittest.mock import patch
            real_open=rag._ORIGINAL_OS_OPEN
            swapped=False
            moved=base/"moved-cache"
            redirected=base/"redirected-cache"
            redirected.mkdir()

            def swap_after_directory_open(path, flags, *args, **kwargs):
                nonlocal swapped
                fd=real_open(path,flags,*args,**kwargs)
                if path==cache.name and kwargs.get("dir_fd") is not None and not swapped:
                    cache.rename(moved)
                    cache.symlink_to(redirected,target_is_directory=True)
                    swapped=True
                return fd

            with patch.object(rag,"_ORIGINAL_OS_OPEN",side_effect=swap_after_directory_open):
                _,fingerprint,_=load_or_build_cache(repo,cache)
            self.assertTrue(swapped)
            self.assertTrue((moved/f"index-v2-{fingerprint}.json").exists())
            self.assertEqual([],list(redirected.iterdir()))

if __name__=="__main__": unittest.main()
