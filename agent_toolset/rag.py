"""Offline, repo-confined, lexical retrieval with source provenance."""
from __future__ import annotations
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

TOKENS = re.compile(r"[a-z0-9_]+", re.IGNORECASE)
DEFAULT_SUFFIXES = frozenset({".md", ".py", ".json", ".toml", ".yml", ".yaml", ".rs"})
MAX_BYTES = 256_000

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

def build_index(root: str | Path, *, suffixes=DEFAULT_SUFFIXES) -> dict:
    """Index approved local text only; never follow symlinks or invoke remote services."""
    root = Path(root).resolve(strict=True)
    docs = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in {".git", ".venv", "__pycache__", "node_modules", "target"} for part in relative.parts):
            continue
        if path.suffix.lower() not in suffixes or not _safe_file(root, path):
            continue
        try:
            raw = path.read_bytes()
            content = raw.decode("utf-8")
        except (UnicodeError, OSError):
            continue
        digest = hashlib.sha256(raw).hexdigest()
        for n, line in enumerate(content.splitlines(), 1):
            if not line.strip():
                continue
            tokens = terms(line)
            if tokens:
                docs.append({"path": relative.as_posix(), "line": n, "text": line[:2000],
                             "sha256": digest, "tf": dict(Counter(tokens))})
    return {"format": 1, "root": str(root), "documents": docs}

def search(index: dict, query: str, *, limit: int = 8) -> list[dict]:
    """Deterministic BM25-like lexical ranking; each hit includes a file/line/hash."""
    if not isinstance(query, str) or not 1 <= limit <= 100:
        raise ValueError("Invalid query or limit")
    q = set(terms(query))
    if not q:
        return []
    docs = index["documents"]
    if not docs:
        return []
    df = Counter(t for d in docs for t in q if t in d["tf"])
    lengths = [sum(d["tf"].values()) for d in docs]
    avg = sum(lengths) / len(docs)
    results = []
    for d, length in zip(docs, lengths):
        score = 0.0
        for term in q:
            frequency = d["tf"].get(term, 0)
            if frequency:
                idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
                score += idf * (frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / avg)))
        if score:
            results.append({"path": d["path"], "line": d["line"], "sha256": d["sha256"],
                            "text": d["text"], "score": round(score, 8)})
    return sorted(results, key=lambda x: (-x["score"], x["path"], x["line"]))[:limit]

def verify_hit(root: str | Path, hit: dict) -> bool:
    """Reject stale citations or changed files before using them as evidence."""
    root = Path(root).resolve(strict=True)
    target = root / hit["path"]
    if not _safe_file(root, target):
        return False
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
        line = hit["line"]
        return (isinstance(line, int) and 1 <= line <= len(lines)
                and lines[line - 1][:2000] == hit["text"]
                and hashlib.sha256(target.read_bytes()).hexdigest() == hit["sha256"])
    except (OSError, UnicodeError, KeyError, TypeError, ValueError):
        return False

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Offline repository retrieval")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    idx = build_index(args.repo)
    print(json.dumps({"hits": search(idx, args.query, limit=args.limit)}, indent=2))

if __name__ == "__main__":
    main()
