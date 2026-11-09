from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AvbInfo:
    algorithm_type: int
    hash_size: int
    signature_size: int
    public_key_size: int
    rollback_index: int
    flags: int


def parse_vbmeta(path: Path) -> AvbInfo:
    with path.open("rb") as stream:
        header = stream.read(256)
    if len(header) < 256 or header[:4] != b"AVB0":
        raise ValueError("Not a vbmeta image")
    algorithm = int.from_bytes(header[28:32], "big")
    hash_size = int.from_bytes(header[32:36], "big")
    signature_size = int.from_bytes(header[36:40], "big")
    public_key_size = int.from_bytes(header[52:56], "big")
    rollback = int.from_bytes(header[96:104], "big")
    flags = int.from_bytes(header[120:124], "big")
    return AvbInfo(algorithm, hash_size, signature_size, public_key_size, rollback, flags)


def avbtool_info(path: Path) -> str:
    tool = shutil.which("avbtool")
    if not tool:
        raise FileNotFoundError("avbtool is required for full AVB descriptor inspection")
    result = subprocess.run(
        [tool, "info_image", "--image", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "avbtool failed")
    return result.stdout.strip()
