#!/usr/bin/env python3
"""Create one skill from local templates; refuse overwrites and invalid names."""
import argparse
import json
from pathlib import Path
from index_skills import NAME_RE, ROOT


def new_skill(root, name, description):
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError("skill name must be lowercase kebab-case, maximum 64 characters")
    if not 1 <= len(description) <= 1024 or "\n" in description:
        raise ValueError("description must be a single line of 1-1024 characters")
    if any(x in description for x in ('{{', '}}')):
        raise ValueError("description cannot contain template delimiters")
    folder = root / ".agents" / "skills" / name
    if folder.exists():
        raise FileExistsError(f"skill already exists: {folder}")
    display = name.replace("-", " ").title()
    src = root / "templates" / "skill"
    template_files = [src / "SKILL.md.tmpl", src / "agents" / "openai.yaml.tmpl"]
    rendered = []
    for file in template_files:
        contents = file.read_text(encoding="utf-8")
        for marker, value in (("{{NAME}}", name), ("{{DISPLAY_NAME}}", display), ("{{DESCRIPTION}}", json.dumps(description, ensure_ascii=False))):
            contents = contents.replace(marker, value)
        relative = file.relative_to(src)
        target = folder / relative.with_suffix("")
        rendered.append((target, contents))
    for target, contents in rendered:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
    return folder


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("name")
    p.add_argument("--description", required=True)
    args = p.parse_args()
    try:
        path = new_skill(ROOT, args.name, args.description)
    except (OSError, ValueError) as exc:
        p.exit(1, f"FAIL: {exc}\n")
    print(f"CREATED: {path}\nNEXT: refine SKILL.md; index --write; validate; add behavior tests")


if __name__ == "__main__":
    main()
