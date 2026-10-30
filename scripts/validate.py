#!/usr/bin/env python3
"""Dependency-free structural checks for the agent_skills control plane."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def validate():
    errors = []
    roles = load("catalog/roles.json")["roles"]
    chain = load("catalog/resource-chain.json")
    ids = {r["id"] for r in roles}
    if len(ids) != len(roles):
        errors.append("duplicate role IDs")
    names = set()
    for r in roles:
        name = r["skill"]
        if name in names:
            errors.append("duplicate skill: " + name)
        names.add(name)
        path = SKILLS / name / "SKILL.md"
        if not path.is_file():
            errors.append("missing " + str(path.relative_to(ROOT)))
            continue
        body = path.read_text(encoding="utf-8")
        if not re.match(r"^---\nname: " + re.escape(name) + r"\ndescription: .+\n---\n", body):
            errors.append("invalid skill frontmatter: " + name)
        if not (SKILLS / name / "agents" / "openai.yaml").is_file():
            errors.append("missing metadata for " + name)
    for p in SKILLS.glob("*/SKILL.md"):
        if p.parent.name not in names:
            errors.append("unregistered skill: " + p.parent.name)
    stages = chain["stages"]
    stage_ids = [s["id"] for s in stages]
    if len(set(stage_ids)) != len(stage_ids):
        errors.append("duplicate stages")
    resource_set = set(chain["resources"])
    produced = set(chain["external_resources"])
    seen = set()
    for s in stages:
        if s["role"] not in ids:
            errors.append("unknown role in " + s["id"])
        if not set(s["depends_on"]) <= seen:
            errors.append("forward or missing stage dependency in " + s["id"])
        if not set(s["consumes"]) <= produced:
            errors.append("missing upstream resource in " + s["id"])
        if not (set(s["produces"]) | set(s["consumes"])) <= resource_set:
            errors.append("undeclared resource in " + s["id"])
        produced.update(s["produces"])
        seen.add(s["id"])
    for path in (ROOT / "schemas").glob("*.json"):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            if schema.get("type") != "object" or "$schema" not in schema:
                errors.append("invalid schema structure: " + path.name)
        except (OSError, json.JSONDecodeError):
            errors.append("invalid schema JSON: " + path.name)
    for path in (ROOT / "examples").glob("*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if obj.get("schema_version") != "1.0.0":
                errors.append("invalid example version: " + path.name)
        except (OSError, json.JSONDecodeError):
            errors.append("invalid example JSON: " + path.name)
    return errors

if __name__ == "__main__":
    problems = validate()
    if problems:
        for p in problems:
            print("FAIL:", p, file=sys.stderr)
        sys.exit(1)
    print("PASS: roles, skills, DAG, resource provenance, schemas and examples")
