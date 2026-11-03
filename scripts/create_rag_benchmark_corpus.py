#!/usr/bin/env python3
"""Create a deterministic source corpus for the local RAG performance comparison."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="new or empty destination directory")
    parser.add_argument("--files", type=int, default=500)
    parser.add_argument("--lines-per-file", type=int, default=40)
    args = parser.parse_args()
    if args.files < 1 or args.lines_per_file < 1:
        parser.error("file and line counts must be positive")
    root = args.root.expanduser().absolute()
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        parser.error("destination must be empty; refusing to overwrite existing files")
    for file_index in range(args.files):
        directory = root / f"pkg{file_index % 25:02d}"
        directory.mkdir(exist_ok=True)
        contents = "".join(
            f"def function_{line_index}(value): return value + {file_index + line_index}\n"
            for line_index in range(args.lines_per_file)
        )
        (directory / f"module{file_index:04d}.py").write_text(contents, encoding="utf-8")
    print(f"created {args.files} files / {args.files * args.lines_per_file} lines under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
