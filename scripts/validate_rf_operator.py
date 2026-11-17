#!/usr/bin/env python3
"""Stdlib-only semantic validation for the RF master operator catalog."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def check(root=ROOT):
    errors = []
    data = json.loads((root / "catalog/rf-software-master-operator.json").read_text())
    if data.get("schema_version") != "1.0.0":
        errors.append("unexpected schema version")
    if data.get("operator", {}).get("id") != "rf-software-master-operator":
        errors.append("missing master operator")
    agents = data.get("agents", [])
    agent_ids = [a["id"] for a in agents]
    if len(agent_ids) != len(set(agent_ids)):
        errors.append("duplicate agents")
    for agent in agents:
        if not (root / agent["skill_path"]).is_file():
            errors.append("missing agent skill: " + agent["id"])
    profiles = data.get("profiles", {})
    for key, val in profiles.items():
        for parent in val.get("depends_on", []):
            if parent not in profiles:
                errors.append("unknown profile dependency: " + key + "/" + parent)
    def visit(key, ancestors):
        if key in ancestors:
            errors.append("profile cycle: " + key)
            return
        for dep in profiles[key].get("depends_on", []):
            if dep in profiles:
                visit(dep, ancestors | {key})
    for key in profiles:
        visit(key, set())
    components = data.get("components", [])
    ids = [c["id"] for c in components]
    if len(ids) != len(set(ids)):
        errors.append("duplicate components")
    known_external = {"synthetic-iq"}
    for c in components:
        if c["owner"] not in agent_ids or c["reviewer"] not in agent_ids:
            errors.append("unknown agent for " + c["id"])
        if c["owner"] == c["reviewer"]:
            errors.append("self-review: " + c["id"])
        if c["profile"] not in profiles:
            errors.append("unknown profile: " + c["id"])
        if c["installation_policy"] not in {"pacman-candidate","manual-review","venv-manual-review","os-provided"}:
            errors.append("bad installer policy: " + c["id"])
        for dep in c.get("dependencies", []):
            if dep not in ids and dep not in known_external:
                errors.append("unknown component dependency: " + c["id"] + " -> " + dep)
        if c.get("status") == "HARDWARE_PASS" and not c.get("acceptance_record"):
            errors.append("hardware pass without evidence: " + c["id"])
    with (root / "data/rf_software_deployments.tsv").open(newline="") as stream:
        matrix = list(csv.DictReader(stream, delimiter="\t"))
    matrix_ids = {row["component"] for row in matrix}
    if set(ids) != matrix_ids:
        errors.append("software matrix and master catalog mismatch")
    roles = {row["skill"] for row in csv.DictReader(
        (root / "data/rf_agent_capabilities.tsv").open(newline=""), delimiter="\t")}
    if set(agent_ids) != roles:
        errors.append("RF agent capability matrix mismatch")
    if data.get("policy", {}).get("default_radio_mode") != "rx_only":
        errors.append("receive-only default missing")
    return errors

if __name__ == "__main__":
    issues = check()
    if issues:
        for issue in issues:
            print("FAIL:", issue)
        raise SystemExit(1)
    print("PASS: RF master operator identities, profiles, dependencies, ownership and matrices")
