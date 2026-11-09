"""Read-only consistency validator for agent catalogs and skill references."""
import argparse
import json
from pathlib import Path


def _unique_strings(values):
    return len(set(values)) == len(values)


def validate(root):
    root = Path(root).resolve(strict=True)
    issues = []
    catalog_root = root / "catalog"
    roles_path = catalog_root / "roles.json"
    chain_path = catalog_root / "resource-chain.json"
    if (catalog_root.is_symlink() or roles_path.is_symlink() or chain_path.is_symlink()
            or not roles_path.is_file() or not chain_path.is_file()):
        return {"status": "FAIL", "errors": ["catalog files are missing or unsafe"]}
    try:
        roles_doc = json.loads(roles_path.read_text(encoding="utf-8"))
        chain_doc = json.loads(chain_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "FAIL", "errors": [str(exc)]}
    if not isinstance(roles_doc, dict) or not isinstance(chain_doc, dict):
        return {"status": "FAIL", "errors": ["catalog roots must be objects"]}
    roles, stages, resources = roles_doc.get("roles"), chain_doc.get("stages"), chain_doc.get("resources")
    if not isinstance(roles, list) or not isinstance(stages, list) or not isinstance(resources, list):
        return {"status": "FAIL", "errors": ["catalog lists are missing or invalid"]}

    role_records = [role for role in roles if isinstance(role, dict)]
    stage_records = [stage for stage in stages if isinstance(stage, dict)]
    if len(role_records) != len(roles):
        issues.append("role entries must be objects")
    if len(stage_records) != len(stages):
        issues.append("stage entries must be objects")
    roleids = [role.get("id") for role in role_records]
    stageids = [stage.get("id") for stage in stage_records]
    if any(not isinstance(value, str) or not value for value in roleids):
        issues.append("role identifiers must be non-empty strings")
    if any(not isinstance(value, str) or not value for value in stageids):
        issues.append("stage identifiers must be non-empty strings")
    valid_roleids = [value for value in roleids if isinstance(value, str) and value]
    valid_stageids = [value for value in stageids if isinstance(value, str) and value]
    if not _unique_strings(valid_roleids) or not _unique_strings(valid_stageids):
        issues.append("duplicate role or stage identifier")
    if any(not isinstance(value, str) or not value for value in resources):
        issues.append("resource names must be non-empty strings")
    valid_resources = [value for value in resources if isinstance(value, str) and value]
    if not _unique_strings(valid_resources):
        issues.append("duplicate resource")

    agents_root = root / ".agents"
    skills_root = agents_root / "skills"
    for role in role_records:
        ident, skill = role.get("id"), role.get("skill")
        label = ident if isinstance(ident, str) else "<invalid role>"
        if not isinstance(skill, str) or not skill or "/" in skill or "\\" in skill or skill in (".", ".."):
            issues.append(f"{label}: invalid skill name")
            continue
        target = skills_root / skill
        entrypoint = target / "SKILL.md"
        metadata_root = target / "agents"
        metadata = metadata_root / "openai.yaml"
        if (agents_root.is_symlink() or skills_root.is_symlink() or target.is_symlink()
                or entrypoint.is_symlink() or not entrypoint.is_file()):
            issues.append(f"{label}: missing or unsafe SKILL.md")
        if (agents_root.is_symlink() or skills_root.is_symlink() or target.is_symlink()
                or metadata_root.is_symlink()
                or metadata.is_symlink() or not metadata.is_file()):
            issues.append(f"{label}: missing or unsafe openai.yaml")
        parent = role.get("reports_to")
        human = roles_doc.get("human_authority")
        if parent not in valid_roleids + ([human] if isinstance(human, str) else []):
            issues.append(f"{label}: unknown reporting parent")

    graph = {}
    for stage in stage_records:
        sid = stage.get("id")
        if not isinstance(sid, str) or not sid:
            continue
        dependencies = stage.get("depends_on", [])
        if not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies):
            issues.append(f"{sid}: dependencies must be a list of stage identifiers")
            dependencies = []
        graph[sid] = dependencies
        if stage.get("role") not in valid_roleids:
            issues.append(f"{sid}: unknown role")
        for dependency in dependencies:
            if dependency not in valid_stageids:
                issues.append(f"{sid}: unknown dependency {dependency}")
        for key in ("consumes", "produces"):
            values = stage.get(key, [])
            if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
                issues.append(f"{sid}: {key} must be a list of resource names")
                continue
            for item in values:
                if item not in valid_resources:
                    issues.append(f"{sid}: unknown {key} resource {item}")

    state = {}
    for start in graph:
        if state.get(start, 0):
            continue
        state[start] = 1
        stack = [(start, iter(graph[start]))]
        while stack:
            node, dependencies = stack[-1]
            try:
                dependency = next(dependencies)
            except StopIteration:
                state[node] = 2
                stack.pop()
                continue
            if dependency not in graph:
                continue
            dependency_state = state.get(dependency, 0)
            if dependency_state == 1:
                issues.append(f"cycle in stages: {dependency}")
            elif dependency_state == 0:
                state[dependency] = 1
                stack.append((dependency, iter(graph[dependency])))
    return {"status": "FAIL" if issues else "PASS", "role_count": len(roles),
            "stage_count": len(stages), "errors": sorted(set(issues))}


def main():
    parser = argparse.ArgumentParser(description="Validate agent role and resource references")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    try:
        result = validate(args.repo)
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
