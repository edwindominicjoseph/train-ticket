#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

DIGEST_PATTERN = r"sha256:[0-9a-f]{64}"


def replace_digest(content: str, digest: str) -> str:
    if not re.fullmatch(DIGEST_PATTERN, digest):
        raise ValueError(
            "digest must be sha256 followed by 64 lowercase hexadecimal characters"
        )

    updated, count = re.subn(
        rf"(?m)^(\s*digest:\s*){DIGEST_PATTERN}\s*$",
        rf"\g<1>{digest}",
        content,
    )
    if count != 1:
        raise ValueError(f"expected exactly one image digest, found {count}")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the pinned GitOps image digest")
    parser.add_argument("--digest", required=True)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    content = args.manifest.read_text(encoding="utf-8")
    try:
        updated = replace_digest(content, args.digest)
    except ValueError as error:
        parser.error(str(error))
    args.manifest.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
