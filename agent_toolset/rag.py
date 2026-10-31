"""Offline, repo-confined lexical retrieval with source provenance."""
from __future__ import annotations
import hashlib
import json
import math
import os
import errno
import re
import secrets
import stat
from collections import Counter
from pathlib import Path
from typing import Iterable

TOKENS = re.compile(r"[a-z0-9_]+", re.IGNORECASE)
DEFAULT_SUFFIXES = frozenset({".md", ".py", ".json", ".toml", ".yml", ".yaml", ".rs"})
MAX_BYTES = 256_000
IGNORED_DIRS = {
    ".git", ".venv", "__pycache__", "node_modules", "target",
    ".aws", ".ssh", ".gnupg", ".azure", ".kube", ".config",
    "secret", "secrets", "credential", "credentials", "private", "keys",
}
IGNORED_FILES = {".env", ".npmrc", ".pypirc", "id_rsa", "id_ed25519", "id_ecdsa", "known_hosts"}
IGNORED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
CACHE_FORMAT = 1
_ORIGINAL_OS_OPEN = os.open

def terms(value: str) -> list[str]:
    return TOKENS.findall(value.lower())

def _open_directory_nofollow(path: Path) -> int:
    """Open a canonical directory by walking components without following symlinks."""
    if not hasattr(os, "O_NOFOLLOW"):
        raise OSError("safe retrieval requires O_NOFOLLOW and directory-relative open support")
    absolute=path.resolve(strict=True)
    flags=os.O_RDONLY | getattr(os,"O_DIRECTORY",0) | getattr(os,"O_CLOEXEC",0)
    fd=_ORIGINAL_OS_OPEN(absolute.anchor,flags)
    try:
        for component in absolute.parts[1:]:
            next_fd=_ORIGINAL_OS_OPEN(component,flags|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd)
            fd=next_fd
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("path is not a directory")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _safe_relative_parts(relative: str) -> tuple[str,...]:
    if not isinstance(relative,str) or not relative or "\\" in relative or relative.startswith("/"):
        raise ValueError("invalid repository-relative path")
    parts=tuple(relative.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("invalid repository-relative path")
    return parts


def _read_confined_file(root: Path, relative: str, *, limit: int = MAX_BYTES) -> bytes:
    """Read a regular file beneath root via no-follow directory-relative opens."""
    parts=_safe_relative_parts(relative)
    directory_fd=_open_directory_nofollow(root)
    current_fd=directory_fd
    try:
        flags=os.O_RDONLY | getattr(os,"O_CLOEXEC",0)
        directory_flags=flags | getattr(os,"O_DIRECTORY",0) | os.O_NOFOLLOW
        for component in parts[:-1]:
            next_fd=_ORIGINAL_OS_OPEN(component,directory_flags,dir_fd=current_fd)
            if current_fd != directory_fd:
                os.close(current_fd)
            current_fd=next_fd
        file_fd=_ORIGINAL_OS_OPEN(parts[-1],flags|os.O_NOFOLLOW,dir_fd=current_fd)
        try:
            metadata=os.fstat(file_fd)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size>limit:
                raise ValueError("source is not a regular file or exceeds size limit")
            chunks=[]
            remaining=limit+1
            while remaining:
                chunk=os.read(file_fd,min(65536,remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining-=len(chunk)
            data=b"".join(chunks)
            if len(data)>limit:
                raise ValueError("source exceeds size limit")
            return data
        finally:
            os.close(file_fd)
    finally:
        if current_fd != directory_fd:
            os.close(current_fd)
        os.close(directory_fd)


def _is_sensitive(relative: str) -> bool:
    parts=tuple(part.casefold() for part in relative.split("/"))
    name=parts[-1]
    if any(part in IGNORED_DIRS for part in parts):
        return True
    if name in IGNORED_FILES or name.startswith(".env."):
        return True
    if Path(name).suffix.casefold() in IGNORED_SUFFIXES:
        return True
    if name.startswith(("credentials", "credential", "secret", "secrets")):
        return True
    return False


def _source_records(root: Path, suffixes: Iterable[str], exclude_paths: Iterable[Path] = ()) -> list[tuple[str, bytes, str]]:
    root = root.resolve(strict=True)
    excluded=[Path(item).absolute() for item in exclude_paths]
    records=[]
    for path in sorted(root.rglob("*")):
        absolute=path.absolute()
        if any(absolute == item or item in absolute.parents for item in excluded):
            continue
        relative=path.relative_to(root)
        relative_name=relative.as_posix()
        if _is_sensitive(relative_name):
            continue
        if path.is_symlink() or path.suffix.lower() not in suffixes:
            continue
        try:
            raw=_read_confined_file(root,relative_name)
            raw.decode("utf-8")
        except (UnicodeError,OSError,ValueError):
            continue
        records.append((relative_name,raw,hashlib.sha256(raw).hexdigest()))
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
        raw=_read_confined_file(base,hit["path"])
        lines=raw.decode("utf-8").splitlines()
        line=hit.get("line")
        return (isinstance(line,int) and not isinstance(line,bool) and 1<=line<=len(lines)
                and lines[line-1][:2000]==hit.get("text")
                and hashlib.sha256(raw).hexdigest()==hit.get("sha256"))
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


def _reject_repo_cache_symlink(root: Path, requested: Path) -> None:
    """Reject any existing symlink component when a cache is placed under root."""
    lexical_root=Path(root).expanduser().absolute()
    lexical_path=Path(requested).expanduser().absolute()
    try:
        relative=lexical_path.relative_to(lexical_root)
    except ValueError:
        return
    current=lexical_root
    for component in relative.parts:
        current=current/component
        if current.is_symlink():
            raise ValueError(f"symlinked cache path component is not allowed: {current}")


def _read_fd(fd: int, limit: int) -> bytes:
    chunks=[]
    remaining=limit+1
    while remaining:
        chunk=os.read(fd,min(65536,remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining-=len(chunk)
    data=b"".join(chunks)
    if len(data)>limit:
        raise ValueError("cache entry exceeds size limit")
    return data

def _valid_cached_index(index: object, expected_root: Path) -> bool:
    if not isinstance(index,dict) or set(index)!={"format","root","documents"}:
        return False
    if index.get("format")!=1 or index.get("root")!=str(expected_root) or not isinstance(index.get("documents"),list):
        return False
    for document in index["documents"]:
        if not isinstance(document,dict) or set(document)!={"path","line","text","sha256","tf"}:
            return False
        path=document["path"]
        if not isinstance(path,str):
            return False
        # Cache paths are POSIX repository-relative names. Avoid constructing a
        # pathlib object for every indexed line: large indexes repeat each path
        # many times and validation is on every cache hit.
        try:
            _safe_relative_parts(path)
        except ValueError:
            return False
        if not isinstance(document["line"],int) or isinstance(document["line"],bool) or document["line"]<1:
            return False
        if not isinstance(document["text"],str) or len(document["text"])>2000:
            return False
        digest=document["sha256"]
        if not isinstance(digest,str) or len(digest)!=64 or any(char not in "0123456789abcdef" for char in digest):
            return False
        tf=document["tf"]
        if not isinstance(tf,dict) or not tf:
            return False
        for term,count in tf.items():
            if not isinstance(term,str) or not isinstance(count,int) or isinstance(count,bool) or count<1:
                return False
    return True

def load_or_build_cache(root: str | Path, cache_dir: str | Path, *, suffixes=DEFAULT_SUFFIXES) -> tuple[dict,str,bool]:
    """Load/create an atomic content-addressed cache; corrupt or symlinked entries fail closed."""
    base=Path(root).resolve(strict=True)
    requested=Path(cache_dir).expanduser().absolute()
    _reject_repo_cache_symlink(Path(root),requested)
    _reject_symlink(requested,"cache directory")
    directory=requested.resolve(strict=False)
    if directory.exists() and not directory.is_dir():
        raise ValueError("cache path must be a directory")
    directory.mkdir(parents=True,exist_ok=True)
    _reject_symlink(directory,"cache directory")
    directory_fd=_open_directory_nofollow(directory)
    try:
        fingerprint,_,records=cache_fingerprint(base,suffixes=suffixes,exclude_paths=(directory.resolve(strict=True),))
        entry_name=f"index-{fingerprint}.json"
        try:
            entry_fd=_ORIGINAL_OS_OPEN(entry_name,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,"O_CLOEXEC",0),dir_fd=directory_fd)
        except FileNotFoundError:
            entry_fd=None
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise ValueError("symlinked cache entry is not allowed") from exc
            raise
        if entry_fd is not None:
            try:
                metadata=os.fstat(entry_fd)
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_size>64_000_000:
                    raise ValueError("corrupt cache entry: invalid file or size limit exceeded")
                try:
                    envelope=json.loads(_read_fd(entry_fd,64_000_000).decode("utf-8"))
                except (UnicodeError,json.JSONDecodeError) as exc:
                    raise ValueError(f"corrupt cache entry: {exc}") from exc
            finally:
                os.close(entry_fd)
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
        temporary=f".index-{secrets.token_hex(12)}.tmp"
        flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|getattr(os,"O_CLOEXEC",0)
        temp_fd=_ORIGINAL_OS_OPEN(temporary,flags,0o600,dir_fd=directory_fd)
        try:
            view=memoryview(data)
            while view:
                written=os.write(temp_fd,view)
                if written<=0:
                    raise OSError("short cache write")
                view=view[written:]
            os.fsync(temp_fd)
        except BaseException:
            os.close(temp_fd)
            try: os.unlink(temporary,dir_fd=directory_fd)
            except FileNotFoundError: pass
            raise
        else:
            os.close(temp_fd)
        try:
            os.replace(temporary,entry_name,src_dir_fd=directory_fd,dst_dir_fd=directory_fd)
            os.fsync(directory_fd)
        except BaseException:
            try: os.unlink(temporary,dir_fd=directory_fd)
            except FileNotFoundError: pass
            raise
        return index,fingerprint,False
    finally:
        os.close(directory_fd)

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
