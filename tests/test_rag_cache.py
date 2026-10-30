import json
import hashlib
import pathlib
import sys
import stat
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.rag import load_or_build_cache, search

class RagCacheTests(unittest.TestCase):
    def test_create_reuse_and_content_invalidation(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); repo=base/"repo"; cache=base/"cache"
            repo.mkdir(); source=repo/"notes.md"; source.write_text("amber release record\\n",encoding="utf-8")
            first,fingerprint1,hit1=load_or_build_cache(repo,cache)
            cache_entry=cache/f"index-{fingerprint1}.json"
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
            target=cache/f"index-{fingerprint}.json"
            envelope=json.loads(target.read_text(encoding="utf-8"))
            envelope["index"]["documents"][0]["tf"]=[]
            content={"fingerprint":envelope["fingerprint"],"index":envelope["index"]}
            envelope["sha256"]=hashlib.sha256(json.dumps(content,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
            target.write_text(json.dumps(envelope),encoding="utf-8")
            with self.assertRaises(ValueError): load_or_build_cache(repo,cache)

    def test_symlinked_cache_directory_and_entry_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as other:
            base=pathlib.Path(temp); repo=base/"repo"; repo.mkdir(); (repo/"doc.md").write_text("link test\\n")
            alias=base/"cache-link"; alias.symlink_to(other,target_is_directory=True)
            with self.assertRaises(ValueError): load_or_build_cache(repo,alias)
            cache=base/"cache"; cache.mkdir()
            _,fingerprint,_=load_or_build_cache(repo,cache)
            target=cache/f"index-{fingerprint}.json"; target.unlink(); target.symlink_to(pathlib.Path(other)/"outside.json")
            with self.assertRaises(ValueError): load_or_build_cache(repo,cache)

if __name__=="__main__": unittest.main()
