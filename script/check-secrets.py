#!/usr/bin/env python3
"""Fail when active tracked source contains known or structurally embedded secrets."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"node_modules", "old-docs", "target", ".git"}
SKIP_FILES = {".env.example", "check-secrets.py"}
RULES = {
    "credential placeholder has an embedded fallback": re.compile(
        r"\$\{[A-Za-z0-9_]*(?:PASSWORD|PASSWD|SECRET|TOKEN)[A-Za-z0-9_]*:(?!\?)[^}]+\}",
        re.IGNORECASE,
    ),
    "known repository credential": re.compile(
        r"(?:GZKSCXHBOLKMCLDQ|Abcd1234#|Ts_123456)"
    ),
    "hard-coded JWT signing key": re.compile(
        r"(?:secretKey\s*=\s*[\"']secret[\"']|encodeToString\([\"']secret[\"'])"
    ),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return [ROOT / line for line in output.splitlines()]


findings = []
for path in tracked_files():
    relative = path.relative_to(ROOT)
    if path.name in SKIP_FILES or any(part in SKIP_PARTS for part in relative.parts):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for line_number, line in enumerate(text.splitlines(), start=1):
        for message, rule in RULES.items():
            if rule.search(line):
                findings.append(f"{relative}:{line_number}: {message}")

if findings:
    print("Secret policy violations:")
    for finding in findings:
        print(f"  - {finding}")
    raise SystemExit(1)

print("Secret policy check passed.")
