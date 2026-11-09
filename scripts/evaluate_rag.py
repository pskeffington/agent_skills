#!/usr/bin/env python3
"""Evaluate lexical retrieval against a labeled local fixture; no network or model use."""
from __future__ import annotations
import argparse
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.rag import build_index, search, verify_hit

def evaluate(corpus: pathlib.Path, labels: pathlib.Path) -> dict:
    spec=json.loads(labels.read_text(encoding="utf-8"))
    if not isinstance(spec,dict) or spec.get("format")!=1 or not isinstance(spec.get("cases"),list):
        raise ValueError("invalid evaluation manifest")
    k=spec.get("k")
    if not isinstance(k,int) or isinstance(k,bool) or not 1<=k<=100:
        raise ValueError("evaluation k must be in 1..100")
    index=build_index(corpus)
    cases=[]; total_precision=0.0; recalls=[]; no_answer_false_positives=0; answerable=0
    for case in spec["cases"]:
        if not isinstance(case,dict) or not isinstance(case.get("query"),str) or not isinstance(case.get("relevant"),list):
            raise ValueError("malformed evaluation case")
        hits=search(index,case["query"],limit=k)
        if not all(verify_hit(corpus,hit) for hit in hits):
            raise ValueError("retrieval returned a stale or invalid source citation")
        relevant=set(case["relevant"])
        unique=[]; seen=set()
        for hit in hits:
            if hit["path"] not in seen:
                seen.add(hit["path"]); unique.append(hit)
        found={hit["path"] for hit in unique[:k]}
        precision=0.0; recall=1.0
        if relevant:
            answerable += 1
            precision=len(found & relevant)/min(k,len(found)) if found else 0.0
            recall=len(found & relevant)/len(relevant)
            total_precision += precision
            recalls.append(recall)
        else:
            no_answer_false_positives += bool(found)
            recall=1.0 if not found else 0.0
        cases.append({"id":case.get("id"),"precision_at_k":round(precision,4),"recall_at_k":round(recall,4),"retrieved":sorted(found),"relevant":sorted(relevant),"untrusted_data_case":bool(case.get("untrusted_data_case"))})
    count=len(cases)
    return {"status":"PASS","scope":"fixture-only; file-level metrics over unique paths; no claim of general retrieval quality or instruction-following safety","k":k,"case_count":count,"answerable_case_count":answerable,"mean_precision_at_k":round(total_precision/answerable,4) if answerable else 0.0,"mean_recall_at_k":round(sum(recalls)/answerable,4) if answerable else 0.0,"no_answer_false_positives":no_answer_false_positives,"cases":cases}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus",type=pathlib.Path,default=ROOT/"tests/fixtures/rag_eval")
    parser.add_argument("--labels",type=pathlib.Path,default=ROOT/"examples/rag-evaluation.json")
    args=parser.parse_args()
    try:
        print(json.dumps(evaluate(args.corpus,args.labels),indent=2))
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)},indent=2)); raise SystemExit(2)
