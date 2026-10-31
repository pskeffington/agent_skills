from collections import Counter
import hashlib
import itertools
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agent_toolset import rag
from agent_toolset.rag import build_index, search, verify_hit


def legacy_search(index, query, limit=8):
    """Reference the pre-optimization accumulation and key-presence semantics."""
    documents=index["documents"]
    query_terms=set(rag.terms(query))
    df=Counter(term for document in documents for term in query_terms if term in document["tf"])
    lengths=[sum(document["tf"].values()) for document in documents]
    average=sum(lengths)/len(documents) if documents else 0
    results=[]
    for document,length in zip(documents,lengths):
        score=0.0
        for term in query_terms:
            frequency=document["tf"].get(term,0)
            if frequency:
                idf=math.log(1+(len(documents)-df[term]+0.5)/(df[term]+0.5))
                score+=idf*(frequency*2.2/(frequency+1.2*(0.25+0.75*length/average)))
        if score:
            results.append({"path":document["path"],"line":document["line"],"sha256":document["sha256"],"text":document["text"],"score":round(score,8)})
    return sorted(results,key=lambda hit:(-hit["score"],hit["path"],hit["line"]))[:limit]

class RagTests(unittest.TestCase):
    def test_search_preserves_float_accumulation_order_exactly(self):
        words=("amber","birch","cobalt","delta","ember","forest","garnet","harbor","indigo")
        identifier=hashlib.sha256(b"order-sensitive").hexdigest()
        for combo in itertools.combinations(words,5):
            query_terms=set(combo)
            if list(query_terms)==sorted(query_terms):
                continue
            for values in itertools.permutations((5,15,25,83,92)):
                frequencies=dict(zip(sorted(query_terms),values))
                frequencies["filler"] = 1
                document={"path":"order.md","line":1,"text":"order sensitive","sha256":identifier,"tf":frequencies}
                index={"format":1,"root":"/repo","documents":[document]}
                query=" ".join(query_terms)
                expected=legacy_search(index,query)
                sorted_order_score=0.0
                length=sum(frequencies.values())
                idf=math.log(4/3)
                for term in sorted(query_terms):
                    frequency=frequencies[term]
                    sorted_order_score+=idf*(frequency*2.2/(frequency+1.2*(0.25+0.75*length/length)))
                if expected and expected[0]["score"]!=round(sorted_order_score,8):
                    self.assertEqual(expected,search(index,query))
                    return
        self.fail("could not construct an order-sensitive score fixture")

    def test_search_document_frequency_uses_key_presence_for_zero_frequency(self):
        docs=[
            {"path":"a.md","line":1,"text":"zero then beta","sha256":"a"*64,"tf":{"alpha":0,"beta":1}},
            {"path":"b.md","line":1,"text":"alpha beta","sha256":"b"*64,"tf":{"alpha":1,"beta":1}},
        ]
        index={"format":1,"root":"/repo","documents":docs}
        self.assertEqual(legacy_search(index,"alpha beta"),search(index,"alpha beta"))

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

    def test_top_k_preserves_stable_order_for_equal_sort_keys(self):
        documents=[{"path":"same.md","line":1,"text":f"entry {i}","sha256":"a"*64,"tf":{"shared":1}}
                   for i in range(30)]
        index={"format":1,"root":"/repo","documents":documents}
        expected=legacy_search(index,"shared",limit=8)
        self.assertEqual(expected,search(index,"shared",limit=8))
        self.assertEqual([f"entry {i}" for i in range(8)],[hit["text"] for hit in search(index,"shared",limit=8)])

    def test_search_computes_idf_once_per_query_term(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for i in range(20):
                (root/f"{i:02}.md").write_text("alpha beta alpha\n",encoding="utf-8")
            index=build_index(root)
            with patch.object(rag.math,"log",wraps=math.log) as logarithm:
                search(index,"alpha beta",limit=8)
            self.assertEqual(2,logarithm.call_count)

    def test_batch_verification_reads_each_source_once(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"many.md").write_text("alpha\nalpha beta\nbeta alpha\n",encoding="utf-8")
            (root/"other.md").write_text("alpha gamma\n",encoding="utf-8")
            hits=search(build_index(root),"alpha",limit=4)
            calls=[]
            read=rag._read_confined_file
            def counted(base,path,**kwargs):
                calls.append(path)
                return read(base,path,**kwargs)
            with patch.object(rag,"_read_confined_file",side_effect=counted):
                batch=rag.verify_hits(root,hits)
            self.assertEqual([verify_hit(root,hit) for hit in hits],batch)
            self.assertEqual(len(set(hit["path"] for hit in hits)),len(calls))
            self.assertEqual(len(calls),len(set(calls)))
            expected=[verify_hit(root,hit) for hit in hits]
            benchmark=rag.verify_hits(root,hits)
            self.assertEqual(expected,benchmark)

    def test_batch_verification_rejects_invalid_and_stale_hits(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"doc.md").write_text("alpha beta\n",encoding="utf-8")
            hit=search(build_index(root),"alpha")[0]
            bad_line={**hit,"line":True}
            bad_text={**hit,"text":"forged"}
            self.assertEqual([True,False,False,False],rag.verify_hits(root,[hit,bad_line,bad_text,{"path":"../escape"}]))

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
