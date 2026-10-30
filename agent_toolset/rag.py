"""Offline, repo-confined lexical retrieval with source provenance."""
from __future__ import annotations
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable

TOKENS = re.compile(r"[a-z0-9_]+", re.IGNORECASE)
DEFAULT_SUFFIXES = frozenset({".md", ".py", ".json", ".toml", ".yml", ".yaml", ".rs"})
MAX_BYTES = 256_000
IGNORED_DIRS = {".git", ".venv", "__pycache__", "node_modules", "target"}
CACHE_FORMAT = 1

def terms(value: str) -> list[str]:
    return TOKENS.findall(value.lower())

def _safe_file(root: Path, path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        return False
    return path.stat().st_size <= MAX_BYTES

def _source_records(root: Path, suffixes: Iterable[str], exclude_paths: Iterable[Path] = ()) -> list[tuple[str, bytes, str]]:
    root = root.resolve(strict=True)
    excluded=[Path(item).absolute() for item in exclude_paths]
    records=[]
    for path in sorted(root.rglob("*")):
        absolute=path.absolute()
        if any(absolute == item or item in absolute.parents for item in excluded):
            continue
        relative=path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() not in suffixes or not _safe_file(root,path):
            continue
        try:
            raw=path.read_bytes()
            raw.decode("utf-8")
        except (UnicodeError,OSError):
            continue
        records.append((relative.as_posix(),raw,hashlib.sha256(raw).hexdigest()))
    return records

def _make_index(root: Path, records: list[tuple[str,bytes,str]]) -> dict:
    docs=[]
    for relative,raw,digest in records:
        content=raw.decode("utf-8")
        for number,line in enumerate(content.splitlines(),1):
            if not line.strip():
                continue
            tokens=terms(line)
            if tokens:
                docs.append({"path":relative,"line":number,"text":line[:2000],"sha256":digest,"tf":dict(Counter(tokens))})
    return {"format":1,"root":str(root),"documents":docs}

def build_index(root: str | Path, *, suffixes=DEFAULT_SUFFIXES) -> dict:
    """Index approved local text only; never follow symlinks or invoke remote services."""
    base=Path(root).resolve(strict=True)
    return _make_index(base,_source_records(base,suffixes))

def search(index: dict, query: str, *, limit: int = 8) -> list[dict]:
    """Deterministic BM25-like lexical ranking; each hit includes a file/line/hash."""
    if not isinstance(query,str) or not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=100:
        raise ValueError("Invalid query or limit")
    q=set(terms(query))
    if not q:
        return []
    docs=index["documents"]
    if not docs:
        return []
    df=Counter(t for d in docs for t in q if t in d["tf"])
    lengths=[sum(d["tf"].values()) for d in docs]
    avg=sum(lengths)/len(docs)
    results=[]
    for d,length in zip(docs,lengths):
        score=0.0
        for term in q:
            frequency=d["tf"].get(term,0)
            if frequency:
                idf=math.log(1+(len(docs)-df[term]+0.5)/(df[term]+0.5))
                score+=idf*(frequency*2.2/(frequency+1.2*(0.25+0.75*length/avg)))
        if score:
            results.append({"path":d["path"],"line":d["line"],"sha256":d["sha256"],"text":d["text"],"score":round(score,8)})
    return sorted(results,key=lambda hit:(-hit["score"],hit["path"],hit["line"]))[:limit]

def verify_hit(root: str | Path, hit: dict) -> bool:
    """Reject stale citations or changed files before using them as evidence."""
    try:
        base=Path(root).resolve(strict=True)
        if not isinstance(hit,dict) or not isinstance(hit.get("path"),str):
            return False
        target=base/hit["path"]
        if not _safe_file(base,target):
            return False
        lines=target.read_text(encoding="utf-8").splitlines()
        line=hit.get("line")
        return (isinstance(line,int) and not isinstance(line,bool) and 1<=line<=len(lines)
                and lines[line-1][:2000]==hit.get("text")
                and hashlib.sha256(target.read_bytes()).hexdigest()==hit.get("sha256"))
    except (OSError,UnicodeError,KeyError,TypeError,ValueError):
        return False

def cache_fingerprint(root: str | Path, *, suffixes=DEFAULT_SUFFIXES, exclude_paths: Iterable[Path] = ()) -> tuple[str, Path, list[tuple[str,bytes,str]]]:
    base=Path(root).resolve(strict=True)
    records=_source_records(base,suffixes,exclude_paths)
    manifest={"format":CACHE_FORMAT,"root":str(base),"sources":[[path,digest] for path,_,digest in records]}
    fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return fingerprint,base,records

def _reject_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise ValueError(f"symlinked {label} is not allowed: {path}")

def _valid_cached_index(index: object, expected_root: Path) -> bool:
    if not isinstance(index,dict) or set(index)!={"format","root","documents"}:
        return False
    if index.get("format")!=1 or index.get("root")!=str(expected_root) or not isinstance(index.get("documents"),list):
        return False
    for document in index["documents"]:
        if not isinstance(document,dict) or set(document)!={"path","line","text","sha256","tf"}:
            return False
        path=document["path"]
        if not isinstance(path,str) or Path(path).is_absolute() or ".." in Path(path).parts or "\\" in path:
            return False
        if not isinstance(document["line"],int) or isinstance(document["line"],bool) or document["line"]<1:
            return False
        if not isinstance(document["text"],str) or len(document["text"])>2000:
            return False
        digest=document["sha256"]
        if not isinstance(digest,str) or len(digest)!=64 or any(char not in "0123456789abcdef" for char in digest):
            return False
        tf=document["tf"]
        if not isinstance(tf,dict) or not tf or any(not isinstance(term,str) or not isinstance(count,int) or isinstance(count,bool) or count<1 for term,count in tf.items()):
            return False
    return True

def load_or_build_cache(root: str | Path, cache_dir: str | Path, *, suffixes=DEFAULT_SUFFIXES) -> tuple[dict,str,bool]:
    """Load/create an atomic content-addressed cache; corrupt entries fail closed."""
    directory=Path(cache_dir).expanduser().absolute()
    _reject_symlink(directory,"cache directory")
    if directory.exists() and not directory.is_dir():
        raise ValueError("cache path must be a directory")
    directory.mkdir(parents=True,exist_ok=True)
    _reject_symlink(directory,"cache directory")
    fingerprint,base,records=cache_fingerprint(root,suffixes=suffixes,exclude_paths=(directory.resolve(strict=True),))
    target=directory/f"index-{fingerprint}.json"
    _reject_symlink(target,"cache entry")
    if target.exists():
        if target.stat().st_size > 64_000_000:
            raise ValueError("corrupt cache entry: size limit exceeded")
        try:
            envelope=json.loads(target.read_text(encoding="utf-8"))
        except (OSError,UnicodeError,json.JSONDecodeError) as exc:
            raise ValueError(f"corrupt cache entry: {exc}") from exc
        if not isinstance(envelope,dict) or set(envelope)!={"fingerprint","index","sha256"}:
            raise ValueError("corrupt cache entry: invalid envelope")
        content={"fingerprint":envelope["fingerprint"],"index":envelope["index"]}
        digest=hashlib.sha256(json.dumps(content,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        index=envelope["index"]
        if envelope["fingerprint"]!=fingerprint or envelope["sha256"]!=digest:
            raise ValueError("corrupt cache entry: digest or source fingerprint mismatch")
        if not _valid_cached_index(index,base):
            raise ValueError("corrupt cache entry: invalid index")
        return index,fingerprint,True
    index=_make_index(base,records)
    content={"fingerprint":fingerprint,"index":index}
    digest=hashlib.sha256(json.dumps(content,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    envelope={**content,"sha256":digest}
    data=(json.dumps(envelope,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
    fd,temp_name=tempfile.mkstemp(prefix=".index-",suffix=".tmp",dir=directory)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        _reject_symlink(target,"cache entry")
        os.replace(temp_name,target)
        try:
            dir_fd=os.open(directory,os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        except OSError:
            pass
    except BaseException:
        try: os.unlink(temp_name)
        except FileNotFoundError: pass
        raise
    return index,fingerprint,False

def main() -> None:
    import argparse
    parser=argparse.ArgumentParser(description="Offline repository retrieval")
    parser.add_argument("--repo",default=".")
    parser.add_argument("--query",required=True)
    parser.add_argument("--limit",type=int,default=8)
    args=parser.parse_args()
    idx=build_index(args.repo)
    print(json.dumps({"hits":search(idx,args.query,limit=args.limit)},indent=2))

if __name__=="__main__":
    main()
