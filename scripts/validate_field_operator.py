#!/usr/bin/env python3
"""Validate the field operator literature -> requirement -> equipment/software graph."""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/"data"/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter="\t"))
def validate():
    src=read("field_operator_literature.tsv")
    req=read("field_operator_requirements.tsv")
    eq=read("field_operator_equipment.tsv")
    sw=read("field_operator_software.tsv")
    errors=[]
    sids={x["source_id"] for x in src}
    rids={x["requirement_id"] for x in req}
    for label,rows,field in [("sources",src,"source_id"),("requirements",req,"requirement_id"),("equipment",eq,"equipment_id"),("software",sw,"software_id")]:
        ids=[x[field] for x in rows]
        if len(ids)!=len(set(ids)): errors.append("duplicate "+label)
        for row in rows:
            if any(not v.strip() for v in row.values() if isinstance(v,str)):
                errors.append("empty field "+label+" "+row[field])
    for r in req:
        if r["priority"] not in {"P0","P1","P2"}: errors.append("invalid priority "+r["requirement_id"])
        for sid in r["source_ids"].split(";"):
            if sid not in sids: errors.append("unknown source "+sid)
    for typ,rows in [("equipment",eq),("software",sw)]:
        seen=set()
        for row in rows:
            for rid in row["requirement_ids"].split(";"):
                if rid not in rids: errors.append("unknown requirement "+typ+" "+rid)
                seen.add(rid)
        if not seen: errors.append("empty coverage "+typ)
    combined={rid for x in eq+sw for rid in x["requirement_ids"].split(";")}
    for rid in rids-combined: errors.append("uncovered requirement "+rid)
    return errors

if __name__=="__main__":
    errors=validate()
    if errors:
        for e in errors: print("FAIL",e)
        raise SystemExit(1)
    print("PASS: field operator literature, requirements and deployments are cross-linked")
