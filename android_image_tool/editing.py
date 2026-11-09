from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatchResult:
    output: Path
    backup: Path
    offset: int
    length: int
    sha256: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def patch_binary(source: Path, output: Path, offset: int, replacement: bytes) -> PatchResult:
    if not source.is_file():
        raise FileNotFoundError(f"Source image does not exist: {source}")
    if offset < 0:
        raise ValueError("Offset must be zero or greater")
    if not replacement:
        raise ValueError("Replacement bytes must not be empty")
    source_size = source.stat().st_size
    if offset + len(replacement) > source_size:
        raise ValueError("The replacement extends beyond the source image")
    if output.resolve() == source.resolve():
        raise ValueError("The source image cannot be edited in place")
    output.parent.mkdir(parents=True, exist_ok=True)
    backup = source.with_name(source.name + ".bak")
    if not backup.exists():
        shutil.copy2(source, backup)
    shutil.copy2(source, output)
    with output.open("r+b") as stream:
        stream.seek(offset)
        stream.write(replacement)
    return PatchResult(output, backup, offset, len(replacement), sha256(output))
