#!/usr/bin/env python3
"""Dependency-free validation of skills, catalogs, schemas and examples."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
EXAMPLE_SCHEMAS = {
    "feature-task.json": "task-contract.schema.json",
    "security-hardening-task.json": "task-contract.schema.json",
    "release-approval-verifier-task.json": "task-contract.schema.json",
    "artifact-digest-task.json": "task-contract.schema.json",
    "codex-runner-task.json": "task-contract.schema.json",
    "f5-containment-verifier-task.json": "task-contract.schema.json",
    "f5-probe-containment-readiness-task.json": "task-contract.schema.json",
    "release-artifact-path-hardening-task.json": "task-contract.schema.json",
    "rag-cache-framing-followup-task.json": "task-contract.schema.json",
    "rag-search-length-cache-investigation-task.json": "task-contract.schema.json",
    "rag-search-streaming-topk-task.json": "task-contract.schema.json",
    "rag-search-idf-precompute-task.json": "task-contract.schema.json",
    "rag-search-candidate-memory-task.json": "task-contract.schema.json",
    "release-artifact-binding-task.json": "task-contract.schema.json",
    "release-dossier-binding-task.json": "task-contract.schema.json",
    "release-dossier-schema-version-task.json": "task-contract.schema.json",
    "release-not-applicable-gates-task.json": "task-contract.schema.json",
    "rag-cache-optimization-task.json": "task-contract.schema.json",
    "rag-source-scan-optimization-task.json": "task-contract.schema.json",
    "rag-cache-digest-validation-optimization-task.json": "task-contract.schema.json",
    "rag-search-candidate-optimization-task.json": "task-contract.schema.json",
    "rag-cache-validator-optimization-task.json": "task-contract.schema.json",
    "rag-cache-entry-framing-optimization-task.json": "task-contract.schema.json",
    "rag-citation-verification-optimization-task.json": "task-contract.schema.json",
    "rag-cache-memory-optimization-task.json": "task-contract.schema.json",
    "rag-source-scan-optimization-task.json": "task-contract.schema.json",
    "feature-handoff.json": "handoff.schema.json",
    "feature-evidence.json": "evidence.schema.json",
    "rag-evaluation.json": "rag-evaluation.schema.json",
    "release-dossier.json": "release-dossier.schema.json",
}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _matches_type(value, expected):
    types = expected if isinstance(expected, list) else [expected]
    for kind in types:
        if kind == "null" and value is None: return True
        if kind == "object" and isinstance(value, dict): return True
        if kind == "array" and isinstance(value, list): return True
        if kind == "string" and isinstance(value, str): return True
        if kind == "boolean" and isinstance(value, bool): return True
        if kind == "integer" and isinstance(value, int) and not isinstance(value, bool): return True
        if kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool): return True
    return False


def validate_document(document, schema, path="$", errors=None):
    """Validate the JSON Schema subset used by this repository without dependencies."""
    if errors is None: errors=[]
    expected=schema.get("type")
    if expected is not None and not _matches_type(document, expected):
        errors.append(f"{path}: expected type {expected}"); return errors
    if "const" in schema and document != schema["const"]: errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and document not in schema["enum"]: errors.append(f"{path}: value is outside enum")
    if isinstance(document,str):
        if len(document)<schema.get("minLength",0): errors.append(f"{path}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"],document): errors.append(f"{path}: string does not match pattern")
    if isinstance(document,(int,float)) and not isinstance(document,bool):
        if "minimum" in schema and document<schema["minimum"]: errors.append(f"{path}: number is below minimum")
        if "maximum" in schema and document>schema["maximum"]: errors.append(f"{path}: number is above maximum")
    if isinstance(document,list):
        if len(document)<schema.get("minItems",0): errors.append(f"{path}: array has too few items")
        if schema.get("uniqueItems") and len(document)!=len({json.dumps(item,sort_keys=True) for item in document}): errors.append(f"{path}: array items are not unique")
        if "items" in schema:
            for index,item in enumerate(document): validate_document(item,schema["items"],f"{path}[{index}]",errors)
    if isinstance(document,dict):
        for key in schema.get("required",[]):
            if key not in document: errors.append(f"{path}: missing required property {key}")
        properties=schema.get("properties",{})
        for key,value in document.items():
            if key in properties: validate_document(value,properties[key],f"{path}.{key}",errors)
            elif schema.get("additionalProperties") is False: errors.append(f"{path}: unknown property {key}")
    return errors


def validate():
    errors=[]
    try:
        catalog=load("catalog/roles.json")
        roles=catalog["roles"]
        if not isinstance(roles,list): raise ValueError("roles must be an array")
        ids={role["id"] for role in roles}
        if len(ids)!=len(roles): errors.append("duplicate role IDs")
        names=set()
        for role in roles:
            name=role["skill"]
            if name in names: errors.append("duplicate skill: "+name)
            names.add(name)
            path=SKILLS/name/"SKILL.md"
            if not path.is_file():
                errors.append("missing "+str(path.relative_to(ROOT))); continue
            body=path.read_text(encoding="utf-8")
            if not re.match(r"^---\nname: "+re.escape(name)+r"\ndescription: .+\n---\n",body): errors.append("invalid skill frontmatter: "+name)
            metadata=SKILLS/name/"agents"/"openai.yaml"
            if not metadata.is_file() or not metadata.read_text(encoding="utf-8").strip(): errors.append("missing or empty metadata for "+name)
        for path in SKILLS.glob("*/SKILL.md"):
            if path.parent.name not in names: errors.append("unregistered skill: "+path.parent.name)
        chain=load("catalog/resource-chain.json")
        stages=chain["stages"]
        stage_ids=[stage["id"] for stage in stages]
        if len(set(stage_ids))!=len(stage_ids): errors.append("duplicate stages")
        resources=set(chain["resources"]); produced=set(chain["external_resources"]); seen=set()
        for stage in stages:
            if stage["role"] not in ids: errors.append("unknown role in "+stage["id"])
            if not set(stage["depends_on"])<=seen: errors.append("forward or missing stage dependency in "+stage["id"])
            if not set(stage["consumes"])<=produced: errors.append("missing upstream resource in "+stage["id"])
            if not (set(stage["produces"])|set(stage["consumes"]))<=resources: errors.append("undeclared resource in "+stage["id"])
            produced.update(stage["produces"]); seen.add(stage["id"])
    except (OSError,KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
        errors.append("invalid catalog or skill registry: "+str(exc))
    schema_docs={}
    for path in sorted((ROOT/"schemas").glob("*.json")):
        try:
            schema=json.loads(path.read_text(encoding="utf-8")); schema_docs[path.name]=schema
            if schema.get("type")!="object" or "$schema" not in schema: errors.append("invalid schema structure: "+path.name)
            properties=schema.get("properties",{})
            if not isinstance(properties,dict) or not set(schema.get("required",()))<=properties.keys(): errors.append("schema required/properties mismatch: "+path.name)
        except (OSError,json.JSONDecodeError,AttributeError) as exc: errors.append("invalid schema JSON: "+path.name+": "+str(exc))
    for schema_name in set(schema_docs)-set(EXAMPLE_SCHEMAS.values()):
        errors.append("schema has no registered example: "+schema_name)
    for path in sorted((ROOT/"examples").glob("*.json")):
        try:
            example=json.loads(path.read_text(encoding="utf-8"))
            schema_name=EXAMPLE_SCHEMAS.get(path.name)
            if schema_name is None: errors.append("example has no registered schema: "+path.name)
            elif schema_name not in schema_docs: errors.append("missing schema "+schema_name+" for "+path.name)
            else:
                version_schema=schema_docs[schema_name].get("properties",{}).get("schema_version",{})
                expected_version=version_schema.get("const","1.0.0")
                if example.get("schema_version")!=expected_version: errors.append("invalid example version: "+path.name)
                errors.extend(f"{path.name}{error[1:]}" for error in validate_document(example,schema_docs[schema_name]))
        except (OSError,json.JSONDecodeError,AttributeError) as exc: errors.append("invalid example JSON: "+path.name+": "+str(exc))
    return errors

if __name__=="__main__":
    problems=validate()
    if problems:
        for problem in problems: print("FAIL:",problem,file=sys.stderr)
        sys.exit(1)
    print("PASS: skills, role/resource catalogs, JSON schemas and schema-validated examples")
