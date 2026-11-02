#!/usr/bin/env python3
"""Validate and package one Agent Skill to a deterministic skill.zip."""
import argparse
import pathlib
import zipfile
from validate_skill import validate

def package_skill(folder, output):
    folder = pathlib.Path(folder).resolve()
    output = pathlib.Path(output).resolve()
    errors = validate(folder)
    if errors:
        raise ValueError("; ".join(errors))
    if output.name != "skill.zip":
        raise ValueError("Output filename must be skill.zip")
    if output.is_relative_to(folder):
        raise ValueError("Output must be outside the skill directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(folder.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts:
                continue
            if file.is_symlink() or not file.resolve().is_relative_to(folder):
                raise ValueError("Symlinks or external files cannot be packaged")
            relative = pathlib.Path(folder.name) / file.relative_to(folder)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, file.read_bytes())
    return output

def main():
    p = argparse.ArgumentParser()
    p.add_argument("skill_directory")
    p.add_argument("--output", default="dist/skill.zip")
    args = p.parse_args()
    try:
        print("Packaged:", package_skill(args.skill_directory, args.output))
    except ValueError as exc:
        p.error(str(exc))
if __name__ == "__main__":
    main()
