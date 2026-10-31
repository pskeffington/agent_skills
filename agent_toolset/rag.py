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
CACHE_ENTRY_MAGIC = b"AGENT-TOOLSET-CACHE/2\n"
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
    excluded=[]
    exclude_root=False
    for item in exclude_paths:
        absolute=Path(item).expanduser().resolve(strict=False)
        try:
            relative=absolute.relative_to(root).as_posix()
            excluded.append(relative)
        except ValueError:
            if absolute==root or absolute in root.parents:
                exclude_root=True
            continue
    if exclude_root:
        return []
    records=[]
    flags=os.O_RDONLY | getattr(os,"O_CLOEXEC",0)
    directory_flags=flags | getattr(os,"O_DIRECTORY",0) | os.O_NOFOLLOW

    def is_excluded(relative: str) -> bool:
        return any(relative==item or item=="." or relative.startswith(item+"/") for item in excluded)

    def visit(directory_fd: int, prefix: str) -> None:
        # scandir consumes its descriptor, so scan a duplicate and retain the
        # original directory handle for safe dir_fd-relative child opens.
        try:
            with os.scandir(os.dup(directory_fd)) as iterator:
                entries=sorted(iterator,key=lambda entry:entry.name)
        except OSError:
            return
        for entry in entries:
            relative=f"{prefix}/{entry.name}" if prefix else entry.name
            if is_excluded(relative) or _is_sensitive(relative):
                continue
            try:
                metadata=os.stat(entry.name,dir_fd=directory_fd,follow_symlinks=False)
            except OSError:
                continue
            if stat.S_ISDIR(metadata.st_mode):
                try:
                    child_fd=_ORIGINAL_OS_OPEN(entry.name,directory_flags,dir_fd=directory_fd)
                except OSError:
                    continue
                try:
                    if stat.S_ISDIR(os.fstat(child_fd).st_mode):
                        visit(child_fd,relative)
                finally:
                    os.close(child_fd)
                continue
            if not stat.S_ISREG(metadata.st_mode) or Path(entry.name).suffix.lower() not in suffixes:
                continue
            try:
                file_fd=_ORIGINAL_OS_OPEN(entry.name,flags|os.O_NOFOLLOW,dir_fd=directory_fd)
                try:
                    metadata=os.fstat(file_fd)
                    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size>MAX_BYTES:
                        continue
                    chunks=[]
                    remaining=MAX_BYTES+1
                    while remaining:
                        chunk=os.read(file_fd,min(65536,remaining))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        remaining-=len(chunk)
                    raw=b"".join(chunks)
                    if len(raw)>MAX_BYTES:
                        continue
                finally:
                    os.close(file_fd)
                raw.decode("utf-8")
            except (UnicodeError,OSError,ValueError):
                continue
            records.append((relative,raw,hashlib.sha256(raw).hexdigest()))

    root_fd=_open_directory_nofollow(root)
    try:
        visit(root_fd,"")
    finally:
        os.close(root_fd)
    records.sort(key=lambda record:record[0])
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

def build_index(root: str | Path, *, suffixes=DEFAULT_SUFFIXES, exclude_paths: Iterable[Path] = ()) -> dict:
    """Index approved local text only; never follow symlinks or invoke remote services."""
    base=Path(root).resolve(strict=True)
    return _make_index(base,_source_records(base,suffixes,exclude_paths))

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
    df={term:0 for term in q}
    lengths=[]
    candidates=[]
    for document in docs:
        frequencies=document["tf"]
        length=sum(frequencies.values())
        lengths.append(length)
        matches=[]
        for term in q:
            if term in frequencies:
                df[term]+=1
                frequency=frequencies[term]
                if frequency:
                    matches.append((term,frequency))
        if matches:
            candidates.append((document,length,matches))
    avg=sum(lengths)/len(docs)
    results=[]
    for d,length,matches in candidates:
        score=0.0
        for term,frequency in matches:
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

def verify_hits(root: str | Path, hits: Iterable[dict]) -> list[bool]:
    """Verify ranked citations while reading and hashing each distinct source once."""
    try:
        base=Path(root).resolve(strict=True)
    except (OSError,ValueError):
        return [False for _ in hits]
    sources: dict[str,tuple[list[str],str] | None]={}
    verified=[]
    for hit in hits:
        if not isinstance(hit,dict) or not isinstance(hit.get("path"),str):
            verified.append(False)
            continue
        path=hit["path"]
        if path not in sources:
            try:
                raw=_read_confined_file(base,path)
                sources[path]=(raw.decode("utf-8").splitlines(),hashlib.sha256(raw).hexdigest())
            except (OSError,UnicodeError,TypeError,ValueError):
                sources[path]=None
        source=sources[path]
        line=hit.get("line")
        verified.append(bool(source is not None and isinstance(line,int) and not isinstance(line,bool)
                             and 1<=line<=len(source[0]) and source[0][line-1][:2000]==hit.get("text")
                             and source[1]==hit.get("sha256")))
    return verified

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
    if type(index) is not dict or set(index)!={"format","root","documents"}:
        return False
    if type(index.get("format")) is not int or index["format"]!=1 or index.get("root")!=str(expected_root) or type(index.get("documents")) is not list:
        return False
    validated_digests=set()
    validated_paths=set()
    for document in index["documents"]:
        if type(document) is not dict or set(document)!={"path","line","text","sha256","tf"}:
            return False
        path=document["path"]
        if type(path) is not str:
            return False
        # Cache paths are POSIX repository-relative names. Avoid constructing a
        # pathlib object for every indexed line: large indexes repeat each path
        # many times and validation is on every cache hit.
        if path not in validated_paths:
            try:
                _safe_relative_parts(path)
            except ValueError:
                return False
            validated_paths.add(path)
        if type(document["line"]) is not int or document["line"]<1:
            return False
        if type(document["text"]) is not str or len(document["text"])>2000:
            return False
        digest=document["sha256"]
        if type(digest) is not str or len(digest)!=64:
            return False
        if digest not in validated_digests:
            if any(char not in "0123456789abcdef" for char in digest):
                return False
            validated_digests.add(digest)
        tf=document["tf"]
        if type(tf) is not dict or not tf:
            return False
        for term,count in tf.items():
            if type(term) is not str or type(count) is not int or count<1:
                return False
    return True

def _encode_cache_entry(fingerprint: str, index: dict) -> bytes:
    """Frame canonical index JSON so its digest can be checked without re-encoding it."""
    payload=json.dumps(index,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    digest=hashlib.sha256(payload).hexdigest().encode("ascii")
    return CACHE_ENTRY_MAGIC+fingerprint.encode("ascii")+b"\n"+digest+b"\n"+payload

def _decode_cache_entry(data: bytes, expected_fingerprint: str) -> dict:
    if not data.startswith(CACHE_ENTRY_MAGIC):
        raise ValueError("corrupt cache entry: unsupported format")
    fingerprint_start=len(CACHE_ENTRY_MAGIC)
    fingerprint_end=data.find(b"\n",fingerprint_start)
    digest_end=data.find(b"\n",fingerprint_end+1) if fingerprint_end>=0 else -1
    try:
        if fingerprint_end<0 or digest_end<0:
            raise ValueError("corrupt cache entry: malformed header")
        fingerprint=data[fingerprint_start:fingerprint_end]
        digest=data[fingerprint_end+1:digest_end]
        if fingerprint.decode("ascii")!=expected_fingerprint:
            raise ValueError("corrupt cache entry: source fingerprint mismatch")
        if len(digest)!=64 or any(byte not in b"0123456789abcdef" for byte in digest):
            raise ValueError("corrupt cache entry: malformed digest")
        payload_start=digest_end+1
        if hashlib.sha256(memoryview(data)[payload_start:]).hexdigest().encode("ascii")!=digest:
            raise ValueError("corrupt cache entry: digest mismatch")
        index=json.loads(data[payload_start:])
    except (UnicodeError,json.JSONDecodeError,ValueError) as exc:
        if isinstance(exc,ValueError) and str(exc).startswith("corrupt cache entry:"):
            raise
        raise ValueError(f"corrupt cache entry: {exc}") from exc
    if type(index) is not dict:
        raise ValueError("corrupt cache entry: invalid index")
    return index

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
        entry_name=f"index-v2-{fingerprint}.json"
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
                data=_read_fd(entry_fd,64_000_000)
            finally:
                os.close(entry_fd)
            index=_decode_cache_entry(data,fingerprint)
            if not _valid_cached_index(index,base):
                raise ValueError("corrupt cache entry: invalid index")
            return index,fingerprint,True
        index=_make_index(base,records)
        data=_encode_cache_entry(fingerprint,index)
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
