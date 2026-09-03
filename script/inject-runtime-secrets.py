#!/usr/bin/env python3
"""Inject the shared JWT Secret into Java deployments that validate tokens."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def jwt_services() -> set[str]:
    services = set()
    for service in ROOT.glob("ts-*-service"):
        java_root = service / "src/main/java"
        if not java_root.is_dir():
            continue
        for source in java_root.rglob("*.java"):
            text = source.read_text(encoding="utf-8")
            if "new JWTFilter" in text or "JWTUtil" in text:
                services.add(service.name)
                break
    return services


def inject(document: str, services: set[str]) -> str:
    name_match = re.search(r"(?m)^metadata:\s*\n\s+name:\s+(ts-[a-z0-9-]+)\s*$", document)
    if not name_match or name_match.group(1) not in services:
        return document
    if re.search(r"(?m)^\s+name:\s+ts-jwt\s*$", document):
        return document

    marker = re.search(r"(?m)^(\s+)envFrom:\s*$", document)
    if not marker:
        raise ValueError(f"Deployment {name_match.group(1)} has no envFrom section")
    indent = marker.group(1)
    addition = (
        f"{marker.group(0)}\n"
        f"{indent}  - secretRef:\n"
        f"{indent}      name: ts-jwt"
    )
    return document[: marker.start()] + addition + document[marker.end() :]


def render(content: str, services: set[str]) -> str:
    documents = re.split(r"\r?\n---\r?\n", content)
    return "\n---\n".join(inject(document, services) for document in documents)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: inject-runtime-secrets.py <deployment.yaml>")
    path = Path(sys.argv[1])
    services = jwt_services()
    rendered = render(path.read_text(encoding="utf-8"), services)
    path.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
