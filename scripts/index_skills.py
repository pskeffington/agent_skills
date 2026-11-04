#!/usr/bin/env python3
"""Scan the canonical skills tree and generate a deterministic catalog (stdlib only)."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def parse_skill(path):
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{path}: missing opening YAML delimiter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"{path}: missing closing YAML delimiter")
    front = content[4:end]
    body = content[end + 5:].strip()
    fields = {}
    for line in front.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = FIELD_RE.fullmatch(line)
        if not match:
            raise ValueError(f"{path}: unsupported YAML frontmatter line: {line!r}")
        key, value = match.groups()
        if key in fields:
            raise ValueError(f"{path}: duplicate key: {key}")
        if value.startswith('"') and value.endswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        elif not value or value.startswith(("|", ">", "[", "{")):
            raise ValueError(f"{path}: only simple single-line YAML fields supported")
        fields[key] = value
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError(f"{path}: invalid skill name: {name!r}")
    if name != path.parent.name:
        raise ValueError(f"{path}: name does not match directory")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        raise ValueError(f"{path}: invalid description")
    if not body:
        raise ValueError(f"{path}: missing instructions")
    root = path.parent.resolve()
    for link in LINK_RE.findall(body):
        if "://" in link or link.startswith(("#", "mailto:")):
            continue
        target = link.split("#", 1)[0]
        if not target:
            continue
        resolved = (root / target).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError(f"{path}: invalid or missing local reference: {link}")
    return {"name": name, "description": description}


def build_catalog(root=ROOT):
    base = root / ".agents" / "skills"
    entries = []
    if base.is_dir():
        for path in sorted(base.iterdir()):
            if not path.is_dir():
                continue
            manifest = path / "SKILL.md"
            if not manifest.is_file():
                raise ValueError(f"{path}: missing SKILL.md")
            meta = parse_skill(manifest)
            if any(p.is_symlink() for p in path.rglob("*")):
                raise ValueError(f"{path}: symbolic links are not allowed in skill bundles")
            members = sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file())
            if sum((path / member).stat().st_size for member in members) > 25 * 1024 * 1024:
                raise ValueError(f"{path}: skill size exceeds 25 MB")
            entries.append({
                "name": meta["name"],
                "description": meta["description"],
                "path": path.relative_to(root).as_posix(),
                "entrypoint": manifest.relative_to(root).as_posix(),
                "resources": [f for f in members if f != "SKILL.md"],
            })
    return {"schema_version": 1, "generated_by": "scripts/index_skills.py", "skills": entries}


def render_catalog(root=ROOT):
    return json.dumps(build_catalog(root), indent=2, ensure_ascii=False) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="fail on catalog drift")
    g.add_argument("--write", action="store_true", help="regenerate catalog")
    a = p.parse_args()
    target = ROOT / "catalog" / "skills.json"
    try:
        expected = render_catalog()
        if a.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8")
            print(f"WRITE: {target}")
        elif not target.is_file() or target.read_text(encoding="utf-8") != expected:
            raise ValueError("catalog/skills.json is stale; run python3 scripts/index_skills.py --write")
        else:
            print(f"PASS: {len(build_catalog()['skills'])} skills indexed")
    except (ValueError, OSError) as exc:
        p.exit(1, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
