#!/usr/bin/env python3
"""Build a deterministic, dependency-free executable Python zipapp."""
from __future__ import annotations
import argparse
import pathlib
import stat
import zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]

def build(output: pathlib.Path) -> pathlib.Path:
    output=output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    files=sorted((ROOT/"agent_toolset").rglob("*.py"))
    if not files:
        raise RuntimeError("agent_toolset package contains no Python modules")
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for source in files:
            relative=source.relative_to(ROOT).as_posix()
            _write(archive,relative,source.read_bytes())
        _write(archive,"__main__.py",b"from agent_toolset.cli import main\nraise SystemExit(main())\n")
    return output

def _write(archive,name,data):
    info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=(stat.S_IFREG|0o644)<<16
    archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=pathlib.Path)
    args=parser.parse_args()
    print(build(args.output))
