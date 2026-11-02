#!/usr/bin/env python3
"""Stdlib-only structural Agent Skills validator (not behavioral verification)."""
import argparse
import pathlib
import re
import sys

MARKER = re.compile(r"\{\{[^}]+\}\}|\bTODO\b")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")
def validate(path):
    errors = []
    path = pathlib.Path(path)
    f = path / "SKILL.md"
    if not f.is_file():
        return ["Missing SKILL.md"]
    text = f.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return ["Missing YAML frontmatter"]
    front = match.group(1)
    keys = re.findall(r"^([A-Za-z_][\w-]*):", front, re.M)
    if sorted(keys) != ["description", "name"]:
        errors.append("Frontmatter must have exactly name and description")
    props = dict(re.findall(r"^(name|description):\s*(.*)$",front,re.M))
    name = props.get("name", "").strip(" '\"")
    if not NAME.fullmatch(name):
        errors.append("Name must be lowercase hyphenated")
    if name != path.name:
        errors.append("Name must match directory")
    if len(props.get("description", "").strip()) < 40:
        errors.append("Description should state capabilities and trigger boundaries (>=40 chars)")
    if MARKER.search(text):
        errors.append("Unresolved template marker or TODO")
    if len(text.splitlines()) > 500:
        errors.append("Entrypoint over 500 lines; move detail to references")
    for target in LINK.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        resolved = (path / target).resolve()
        if not resolved.is_relative_to(path.resolve()):
            errors.append("Missing referenced file: " + target)
        elif not resolved.is_file():
            errors.append("Missing referenced file: " + target)
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("skill_directory")
    args = p.parse_args()
    errors = validate(args.skill_directory)
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    print("PASS: structural validation:", args.skill_directory)
    return 0
if __name__ == "__main__":
    sys.exit(main())
