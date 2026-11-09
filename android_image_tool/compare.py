from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BinaryDiff:
    same: bool
    first_difference: int | None
    changed_bytes: int
    source_sha256: str
    target_sha256: str


def binary_diff(source: Path, target: Path) -> BinaryDiff:
    left = source.read_bytes()
    right = target.read_bytes()
    first = next((index for index, (a, b) in enumerate(zip(left, right)) if a != b), None)
    if first is None and len(left) != len(right):
        first = min(len(left), len(right))
    changed = sum(a != b for a, b in zip(left, right)) + abs(len(left) - len(right))
    return BinaryDiff(
        left == right, first, changed, hashlib.sha256(left).hexdigest(),
        hashlib.sha256(right).hexdigest(),
    )


def text_diff(source: Path, target: Path) -> str:
    left = source.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    right = target.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    return "".join(difflib.unified_diff(left, right, fromfile=str(source), tofile=str(target)))
