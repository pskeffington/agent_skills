"""Read-only consistency validator for agent catalogs and skill references."""
import argparse
import json
from pathlib import Path

def validate(root):
    root = Path(root).resolve(strict=True)
    issues = []
    try:
        roles = json.loads((root / "catalog/roles.json").read_text())
        chain = json.loads((root / "catalog/resource-chain.json").read_text())
    except (OSError, ValueError) as exc:
        return {"status": "FAIL", "errors": [str(exc)]}
    people, stages, resources = roles.get("roles"), chain.get("stages"), chain.get("resources")
    if not all(isinstance(v, list) for v in (people, stages, resources)):
        return {"status": "FAIL", "errors": ["catalog lists are missing or invalid"]}
    roleids = [r.get("id") for r in people]
    stageids = [s.get("id") for s in stages]
    if len(set(roleids)) != len(roleids) or len(set(stageids)) != len(stageids):
        issues.append("duplicate role or stage identifier")
    if len(set(resources)) != len(resources):
        issues.append("duplicate resource")
    for role in people:
        ident, skill = role.get("id"), role.get("skill")
        if not isinstance(skill, str) or not skill or "/" in skill or "\\" in skill or skill in (".", ".."):
            issues.append(f"{ident}: invalid skill name")
            continue
        target = root / ".agents" / "skills" / skill
        if target.is_symlink() or (target / "SKILL.md").is_symlink() or not (target / "SKILL.md").is_file():
            issues.append(f"{ident}: missing or unsafe SKILL.md")
        if not (target / "agents" / "openai.yaml").is_file():
            issues.append(f"{ident}: missing openai.yaml")
        if role.get("reports_to") not in roleids + [roles.get("human_authority")]:
            issues.append(f"{ident}: unknown reporting parent")
    graph = {}
    for stage in stages:
        sid = stage.get("id")
        graph[sid] = stage.get("depends_on", [])
        if stage.get("role") not in roleids:
            issues.append(f"{sid}: unknown role")
        for dependency in stage.get("depends_on", []):
            if dependency not in stageids:
                issues.append(f"{sid}: unknown dependency {dependency}")
        for key in ("consumes", "produces"):
            for item in stage.get(key, []):
                if item not in resources:
                    issues.append(f"{sid}: unknown {key} resource {item}")
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            issues.append(f"cycle in stages: {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    return {"status": "FAIL" if issues else "PASS", "role_count": len(people), "stage_count": len(stages), "errors": sorted(set(issues))}

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
