#!/usr/bin/env python3
"""Fingerprint apt indexes and the package definition without depending on cache paths."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def file_digest(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.digest()


def fingerprint(index_dir: Path, action_file: Path, extra_packages: str) -> str:
    digest = hashlib.sha256(b"blueprint-apt-indexes-v1\0")
    indexes = sorted(
        path for path in index_dir.iterdir() if path.is_file() and path.name != "lock"
    )
    if not indexes:
        raise ValueError(f"No apt package indexes found in {index_dir}")
    for path in indexes:
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(file_digest(path))
    digest.update(b"action\0" + file_digest(action_file))
    digest.update(b"extra-packages\0" + extra_packages.encode("utf-8"))
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index_dir", type=Path)
    parser.add_argument("action_file", type=Path)
    parser.add_argument("extra_packages")
    args = parser.parse_args()
    print(fingerprint(args.index_dir, args.action_file, args.extra_packages))


if __name__ == "__main__":
    main()
