#!/usr/bin/env python3
"""Create a deterministic ZIP for one validated canonical skill."""
import argparse
import os
import pathlib
import stat
import tempfile
import unicodedata
import zipfile

from index_skills import NAME_RE, ROOT, parse_skill

MAX_SKILL_BYTES = 25 * 1024 * 1024
MAX_SKILL_FILES = 1000
WINDOWS_RESERVED = {"con", "prn", "aux", "nul", "conin$", "conout$", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10)), *(f"com{suffix}" for suffix in ("¹", "²", "³")), *(f"lpt{suffix}" for suffix in ("¹", "²", "³"))}


def _archive_member(name, relative):
    parts = (name, *relative.parts)
    for part in parts:
        if (part in ("", ".", "..") or "\\" in part or ":" in part
                or part.endswith((".", " "))
                or any(char in part for char in '<>"|?*')
                or any(ord(char) < 32 or ord(char) == 127 for char in part)
                or part.split(".", 1)[0].casefold() in WINDOWS_RESERVED):
            raise ValueError(f"unsafe archive path component: {part!r}")
    return "/".join(parts)


def _validate_member_collisions(members):
    seen_paths = {}
    for member in members:
        components = member.split("/")
        for index in range(1, len(components) + 1):
            original = "/".join(components[:index])
            normalized = unicodedata.normalize("NFC", original).casefold()
            previous = seen_paths.get(normalized)
            if previous is not None and previous != original:
                raise ValueError(f"archive paths collide on case-insensitive filesystems: {previous!r}, {original!r}")
            seen_paths[normalized] = original


def _open_directory_chain(root, parts):
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(root, flags)
    try:
        for part in parts:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _open_regular_file(directory_fd, parts):
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    parent_fd = os.dup(directory_fd)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            os.close(file_fd)
            raise ValueError("skill member is not a regular file")
        return file_fd
    finally:
        os.close(parent_fd)


def package_skill(root, name, output):
    if (os.name != "posix" or os.open not in os.supports_dir_fd
            or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")):
        raise ValueError("secure skill packaging requires POSIX dir_fd, O_NOFOLLOW, and O_DIRECTORY support")
    root = pathlib.Path(root).resolve(strict=True)
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError("skill name must be lowercase kebab-case")
    skill = root / ".agents" / "skills" / name
    try:
        skill_fd = _open_directory_chain(root, (".agents", "skills", name))
    except OSError as exc:
        raise ValueError("skill and its canonical ancestors must be real directories") from exc
    try:
        return _package_open_skill(root, skill, skill_fd, name, output)
    finally:
        os.close(skill_fd)


def _package_open_skill(root, skill, skill_fd, name, output):
    manifest = skill / "SKILL.md"
    try:
        manifest_fd = _open_regular_file(skill_fd, ("SKILL.md",))
        with os.fdopen(manifest_fd, "rb") as source:
            manifest_data = source.read(MAX_SKILL_BYTES + 1)
    except OSError as exc:
        raise ValueError("skill must have a bounded, regular SKILL.md") from exc
    if len(manifest_data) > MAX_SKILL_BYTES:
        raise ValueError("skill must have a bounded, regular SKILL.md")
    # Validate exactly the manifest bytes that will be included in the ZIP.
    manifest_text = manifest_data.decode("utf-8")
    meta = parse_skill(manifest, repository_root=root, content=manifest_text)
    if meta["name"] != name:
        raise ValueError("skill name does not match its canonical directory")

    files = []
    total_bytes = 0
    entries = 0
    for path in skill.rglob("*"):
        entries += 1
        if entries > MAX_SKILL_FILES:
            raise ValueError("skill contains too many entries")
        if path.is_symlink():
            raise ValueError(f"symbolic link is not allowed: {path.relative_to(skill)}")
        if not path.is_file():
            continue
        files.append(path)
        total_bytes += path.lstat().st_size
        if total_bytes > MAX_SKILL_BYTES:
            raise ValueError("skill exceeds 25 MiB")
    files.sort()

    requested = pathlib.Path(output).expanduser()
    parent = requested.parent.resolve(strict=True)
    target = parent / requested.name
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"output already exists: {target}")
    if target.is_relative_to(root):
        raise ValueError("output must be outside the repository")

    members = []
    for path in files:
        relative_parts = path.relative_to(skill).parts
        member = _archive_member(name, pathlib.Path(*relative_parts))
        members.append((path, member))
    _validate_member_collisions([member for _path, member in members])

    temp_name = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=f".{name}-", suffix=".zip.tmp", dir=parent)
        os.close(fd)
        with zipfile.ZipFile(temp_name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            actual_total = 0
            for path, member in members:
                info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                relative_parts = path.relative_to(skill).parts
                if relative_parts == ("SKILL.md",):
                    data = manifest_data
                    actual_total += len(data)
                    if actual_total > MAX_SKILL_BYTES:
                        raise ValueError("skill exceeds 25 MiB")
                    archive.writestr(info, data)
                    continue
                fd = _open_regular_file(skill_fd, relative_parts)
                try:
                    file_stat = os.fstat(fd)
                    if file_stat.st_size > MAX_SKILL_BYTES:
                        raise ValueError(f"skill file changed during packaging: {path.relative_to(skill)}")
                    with os.fdopen(fd, "rb", closefd=False) as source:
                        data = source.read(MAX_SKILL_BYTES + 1)
                    if len(data) != file_stat.st_size or len(data) > MAX_SKILL_BYTES:
                        raise ValueError(f"skill file changed during packaging: {path.relative_to(skill)}")
                    actual_total += len(data)
                    if actual_total > MAX_SKILL_BYTES:
                        raise ValueError("skill exceeds 25 MiB")
                    archive.writestr(info, data)
                finally:
                    os.close(fd)
        os.link(temp_name, target)
        return target
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name")
    parser.add_argument("--output", required=True, help="new ZIP path outside the repository")
    args = parser.parse_args()
    try:
        result = package_skill(ROOT, args.skill_name, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
    print(f"PASS: packaged {args.skill_name} at {result}")


if __name__ == "__main__":
    main()
