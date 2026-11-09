from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PayloadInfo:
    version: int
    manifest_size: int
    metadata_signature_size: int
    data_offset: int


def parse_payload(path: Path) -> PayloadInfo:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:4] != b"CrAU":
        raise ValueError("Not a payload.bin file")
    _, version, manifest_size, signature_size = struct.unpack("<4sQQI", header)
    return PayloadInfo(version, manifest_size, signature_size, 24 + manifest_size + signature_size)


@dataclass(frozen=True)
class SuperInfo:
    major: int
    minor: int
    metadata_size: int
    metadata_slot: int


def parse_super(path: Path) -> SuperInfo:
    with path.open("rb") as stream:
        header = stream.read(40)
    if len(header) < 40 or header[:4] != b"gDla":
        raise ValueError("Not a super.img file")
    major, minor, _, _, metadata_size, metadata_slot = struct.unpack_from(">HHIIII", header, 4)
    return SuperInfo(major, minor, metadata_size, metadata_slot)
