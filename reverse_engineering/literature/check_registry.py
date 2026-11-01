#!/usr/bin/env python3
import json
from pathlib import Path
p=Path(__file__).resolve().parent
r=json.loads((p/"registry.json").read_text())
a=json.loads((p.parent/"index.json").read_text())
ids=[x["id"] for x in r["records"]]
valid={x["id"] for x in a["agents"]}
assert len(ids)==len(set(ids))
assert len(ids)==r["record_count"]
assert all(x["agent_id"] in valid for x in r["records"])
assert all(x["source_url"].startswith("https://") for x in r["records"])
assert all(x["execution_status"]=="not_tested" for x in r["records"])
print("PASS: registry integrity and agent links",len(ids))
