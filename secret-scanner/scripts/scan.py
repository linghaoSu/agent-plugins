#!/usr/bin/env python3
"""Scan changed lines in a git repo for leaked secrets.

By default scans only *added* lines in the diff, so long-standing matches
elsewhere don't swamp a single-commit review. Supports scanning the whole
project (`--mode all`) when you want a first-time audit.

Modes:
    staged    git diff --cached (index vs HEAD)       [default]
    working   git diff + untracked working-tree files
    head      last commit (HEAD~1..HEAD)
    range     --base <ref> [--head <ref>]
    all       every tracked file + untracked (respects .gitignore)

Object fidelity:
    For staged/head/range modes with --full-file, file content is read from
    the git object (git show :path / git show HEAD:path / git show <head>:path)
    rather than the worktree, so edits made after `git add` can't hide a
    staged secret.

Exit codes:
    0  no findings
    1  findings present
    2  usage / git error
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field

# (name, regex). Patterns compiled with MULTILINE OFF (single line context).
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws-access-key",       re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-pat",           re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,255}\b")),
    ("gitlab-pat",           re.compile(r"\bglpat-[0-9A-Za-z_\-]{20}\b")),
    ("stripe-live-key",      re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{24,}\b")),
    ("stripe-test-key",      re.compile(r"\bsk_test_[0-9A-Za-z]{24,}\b")),
    ("slack-token",          re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b")),
    ("openai-key",           re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{20,}\b")),
    ("anthropic-key",        re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("sendgrid-key",         re.compile(r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b")),
    ("twilio-sid",           re.compile(r"\bA[CKS][0-9a-fA-F]{32}\b")),
    ("google-api-key",       re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("jwt",                  re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("private-key-header",   re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("basic-auth-url",       re.compile(r"\bhttps?://[^:/\s]+:[^@/\s]{3,}@[^\s\"']+")),
    ("db-conn-string",       re.compile(r"\b(?:mongodb|postgres(?:ql)?|mysql|redis|amqp)(?:\+srv)?://[^:/\s]+:[^@/\s]+@[^\s\"']+")),
    ("generic-secret",       re.compile(r"""(?ix)
        (?:password|passwd|secret|api[_\-]?key|auth[_\-]?token|access[_\-]?token|bearer)
        \s*[=:]\s*
        ['"]?
        (?P<val>[A-Za-z0-9_\-\./+=]{16,})
        """)),
]

SKIP_PATH = re.compile(
    r"(?:^|/)(?:"
    r"node_modules|vendor|\.git|dist|build|target|out|bin|obj|"
    r"\.next|\.turbo|\.nuxt|\.svelte-kit|coverage|__pycache__|\.venv|venv|"
    r"\.pytest_cache|\.tox|\.cache|\.parcel-cache"
    r")/"
)
SKIP_EXT = {
    ".lock", ".snap",
    ".min.js", ".min.css", ".map",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".tgz", ".gz", ".bz2", ".7z",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".mov", ".wav",
    ".pyc", ".pyo", ".class", ".o", ".a", ".so", ".dylib",
}

FP_HINT = re.compile(
    r"(?i)\b(?:example|dummy|placeholder|fake|sample|xxx+|"
    r"change[_\-]?me|your[_\-]?(?:key|token|secret|password)|"
    r"replace[_\-]?me|redacted)\b"
)


@dataclass
class FileRef:
    path: str
    is_untracked: bool = False


@dataclass
class Finding:
    file: str
    line: int
    pattern: str
    preview: str
    context: str
    likely_false_positive: bool


def git_run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def git(*args: str) -> str:
    res = git_run(*args)
    if res.returncode != 0:
        print(f"git {' '.join(args)} failed: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return res.stdout


def split(output: str) -> list[str]:
    return [line for line in output.splitlines() if line]


def list_files(mode: str, base: str | None, head: str, paths: list[str]) -> list[FileRef]:
    path_args = ["--"] + paths if paths else []

    if mode == "staged":
        out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", *path_args)
        return [FileRef(p, is_untracked=False) for p in split(out)]

    if mode == "working":
        tracked = split(git("diff", "--name-only", "--diff-filter=ACMR", *path_args))
        untracked = split(git("ls-files", "--others", "--exclude-standard", *(paths or [])))
        # De-dup while preserving order
        seen: set[str] = set()
        refs: list[FileRef] = []
        for p in tracked:
            if p not in seen:
                seen.add(p)
                refs.append(FileRef(p, is_untracked=False))
        for p in untracked:
            if p not in seen:
                seen.add(p)
                refs.append(FileRef(p, is_untracked=True))
        return refs

    if mode == "head":
        out = git("diff", "HEAD~1", "HEAD", "--name-only", "--diff-filter=ACMR", *path_args)
        return [FileRef(p, is_untracked=False) for p in split(out)]

    if mode == "range":
        if not base:
            print("range mode requires --base", file=sys.stderr)
            sys.exit(2)
        out = git("diff", f"{base}..{head}", "--name-only", "--diff-filter=ACMR", *path_args)
        return [FileRef(p, is_untracked=False) for p in split(out)]

    if mode == "all":
        tracked = split(git("ls-files", *(paths or [])))
        untracked = split(git("ls-files", "--others", "--exclude-standard", *(paths or [])))
        seen = set()
        refs = []
        for p in tracked:
            if p not in seen:
                seen.add(p)
                refs.append(FileRef(p, is_untracked=False))
        for p in untracked:
            if p not in seen:
                seen.add(p)
                refs.append(FileRef(p, is_untracked=True))
        return refs

    print(f"unknown mode: {mode}", file=sys.stderr)
    sys.exit(2)


def read_worktree(path: str) -> str | None:
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def read_git_object(obj: str) -> str | None:
    res = git_run("show", obj)
    if res.returncode != 0:
        return None
    return res.stdout


def file_content(mode: str, ref: FileRef, base: str | None, head: str) -> str | None:
    """Read file content from the correct source for the mode.

    - working / all / untracked → worktree
    - staged  → index blob (`git show :path`)
    - head    → commit blob  (`git show HEAD:path`)
    - range   → commit blob  (`git show <head>:path`)
    """
    if ref.is_untracked or mode in ("working", "all"):
        return read_worktree(ref.path)
    if mode == "staged":
        return read_git_object(f":{ref.path}")
    if mode == "head":
        return read_git_object(f"HEAD:{ref.path}")
    if mode == "range":
        return read_git_object(f"{head}:{ref.path}")
    return None


def added_lines_from_diff(mode: str, path: str, base: str | None, head: str) -> list[tuple[int, str]]:
    if mode == "staged":
        args = ("diff", "--cached", "-U0", "--no-color", "--", path)
    elif mode == "working":
        args = ("diff", "-U0", "--no-color", "--", path)
    elif mode == "head":
        args = ("diff", "HEAD~1", "HEAD", "-U0", "--no-color", "--", path)
    elif mode == "range":
        args = ("diff", f"{base}..{head}", "-U0", "--no-color", "--", path)
    else:
        return []
    out = git(*args)
    result: list[tuple[int, str]] = []
    cur = 0
    for line in out.splitlines():
        if line.startswith("@@"):
            m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if m:
                cur = int(m.group(1))
        elif line.startswith("+++"):
            continue
        elif line.startswith("+"):
            result.append((cur, line[1:]))
            cur += 1
    return result


def iter_scan_lines(mode: str, ref: FileRef, base: str | None, head: str,
                    full_file: bool) -> list[tuple[int, str]]:
    # Untracked or `all` mode: no diff to compute; scan entire file from worktree.
    if ref.is_untracked or mode == "all":
        content = file_content(mode, ref, base, head)
        if content is None:
            return []
        return [(i + 1, ln) for i, ln in enumerate(content.splitlines())]

    # Full-file: read from the *source of truth* for the mode.
    if full_file:
        content = file_content(mode, ref, base, head)
        if content is None:
            return []
        return [(i + 1, ln) for i, ln in enumerate(content.splitlines())]

    # Default: added lines from the diff.
    return added_lines_from_diff(mode, ref.path, base, head)


def should_skip(path: str) -> bool:
    norm = "/" + path
    if SKIP_PATH.search(norm):
        return True
    for ext in SKIP_EXT:
        if path.endswith(ext):
            return True
    return False


def redact(s: str, reveal: bool) -> str:
    if reveal:
        return s
    if len(s) <= 8:
        return "***"
    return s[:4] + "…" + s[-4:]


def redact_context(line: str, spans: list[tuple[int, int]], reveal: bool) -> str:
    """Replace matched substrings in the line with their redacted form.

    Keeps surrounding context intact so the finding is still reviewable,
    but prevents the secret itself from leaking via the JSON output.
    """
    if reveal or not spans:
        return line
    # Collapse overlapping / adjacent spans.
    spans = sorted(spans)
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    out: list[str] = []
    last = 0
    for s, e in merged:
        out.append(line[last:s])
        out.append(redact(line[s:e], reveal=False))
        last = e
    out.append(line[last:])
    return "".join(out)


def scan(mode: str, base: str | None, head: str, full_file: bool,
         reveal: bool, paths: list[str]) -> list[Finding]:
    refs = list_files(mode, base, head, paths)
    findings: list[Finding] = []

    for ref in refs:
        if should_skip(ref.path):
            continue
        for lineno, line in iter_scan_lines(mode, ref, base, head, full_file):
            if "\x00" in line:
                continue
            line_matches: list[tuple[str, int, int, str]] = []
            for name, rx in PATTERNS:
                for m in rx.finditer(line):
                    if "val" in rx.groupindex:
                        val = m.group("val")
                        s, e = m.span("val")
                    else:
                        val = m.group(0)
                        s, e = m.span(0)
                    line_matches.append((name, s, e, val))
            if not line_matches:
                continue
            spans = [(s, e) for _, s, e, _ in line_matches]
            safe_context = redact_context(line, spans, reveal).strip()[:240]
            fp = bool(FP_HINT.search(line))
            for name, _, _, val in line_matches:
                findings.append(Finding(
                    file=ref.path,
                    line=lineno,
                    pattern=name,
                    preview=redact(val, reveal),
                    context=safe_context,
                    likely_false_positive=fp,
                ))
    return findings


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--mode", default="staged",
                   choices=["staged", "working", "head", "range", "all"],
                   help="what to scan (default: staged)")
    p.add_argument("--base", help="base ref for --mode range")
    p.add_argument("--head", default="HEAD", help="head ref for --mode range (default: HEAD)")
    p.add_argument("--full-file", action="store_true",
                   help="scan entire changed files (from the git object for staged/head/range, "
                        "from worktree for working) instead of only added lines")
    p.add_argument("--reveal", action="store_true",
                   help="print full matched secret and unredacted context (default: redacted)")
    p.add_argument("--format", default="text", choices=["text", "json"])
    p.add_argument("paths", nargs="*", help="optional path filter")
    args = p.parse_args()

    # Sanity check: are we in a git repo?
    res = git_run("rev-parse", "--is-inside-work-tree")
    if res.returncode != 0 or res.stdout.strip() != "true":
        print("not inside a git work tree", file=sys.stderr)
        sys.exit(2)

    findings = scan(args.mode, args.base, args.head, args.full_file,
                    args.reveal, args.paths)

    if args.format == "json":
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            tag = " [likely FP]" if f.likely_false_positive else ""
            print(f"{f.file}:{f.line}\t{f.pattern}\t{f.preview}{tag}")
        print(f"\n{len(findings)} finding(s)", file=sys.stderr)

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
