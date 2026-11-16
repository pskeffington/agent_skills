#!/usr/bin/env python3
"""Structural screening for R Markdown reports; not an R or LaTeX parser."""
import argparse
import json
import re
from pathlib import Path


def audit(source: str) -> dict:
    issues = []
    chunk_names = []
    in_fence = False
    prose = []
    for line_no, line in enumerate(source.splitlines(), 1):
        match = re.match(r'^\x60\x60\x60\{r\s+([^,\s}]+)', line)
        if not in_fence and match:
            in_fence = True
            chunk_names.append(match.group(1))
            continue
        if not in_fence and line.startswith('\x60\x60\x60'):
            in_fence = True
            continue
        if in_fence and line.strip() == '\x60\x60\x60':
            in_fence = False
            continue
        if not in_fence:
            prose.append((line_no, line))
    if in_fence:
        issues.append({'kind': 'unclosed_fence'})
    for name in sorted(set(chunk_names)):
        if chunk_names.count(name) > 1:
            issues.append({'kind': 'duplicate_chunk', 'name': name})
    math_open = sum(bool(re.match(r'^\s*\\\[\s*$', s)) for _, s in prose)
    math_close = sum(bool(re.match(r'^\s*\\\]\s*$', s)) for _, s in prose)
    if math_open != math_close:
        issues.append({'kind': 'display_math_mismatch', 'open': math_open, 'close': math_close})
    plain = '\n'.join(line for _, line in prose)
    if plain.count('\\begin{aligned}') != plain.count('\\end{aligned}'):
        issues.append({'kind': 'aligned_environment_mismatch'})
    for line_no, line in prose:
        if re.search(r'\\\\(?:clearpage|Needspace)\b', line):
            issues.append({'kind': 'possible_escaped_tex', 'line': line_no})
        if re.search(r'\bp[- ]value\s+is\s*=', line, re.I):
            issues.append({'kind': 'malformed_p_value', 'line': line_no})
        if re.search(r'\boverall\b', line, re.I):
            issues.append({'kind': 'house_style_word', 'line': line_no})
        if re.search(r'\b(?:I|we|my|our|ours)\b', line):
            issues.append({'kind': 'possible_first_person', 'line': line_no})
    return {'chunks': len(chunk_names), 'distinct_chunks': len(set(chunk_names)),
            'math_open': math_open, 'math_close': math_close,
            'issues': issues, 'status': 'source_screen_pass' if not issues else 'review'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    result = audit(args.source.read_text(encoding='utf-8'))
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['issues']))
