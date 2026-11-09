from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .android import parse_payload, parse_super
from .avb import parse_vbmeta
from .boot import parse_boot
from .formats import detect_format


@dataclass(frozen=True)
class Check:
    level: str
    message: str


def validate_image(path: Path) -> list[Check]:
    checks: list[Check] = []
    info = detect_format(path)
    if info.size == 0:
        checks.append(Check("error", "Image is empty"))
        return checks
    checks.append(Check("ok", f"Detected {info.format} ({info.size:,} bytes)"))
    if info.format == "Android boot image":
        boot = parse_boot(path)
        if boot.ramdisk_size == 0:
            checks.append(Check("warning", "Boot image has no ramdisk; this may be an init_boot/vendor_boot layout"))
        if boot.ramdisk_offset + boot.ramdisk_size > info.size:
            checks.append(Check("error", "Ramdisk extends beyond image"))
    elif info.format == "AVB vbmeta":
        avb = parse_vbmeta(path)
        checks.append(Check("warning", "AVB flags are non-zero; inspect before flashing")) if avb.flags else None
    elif info.format == "payload.bin":
        payload = parse_payload(path)
        if payload.data_offset > info.size:
            checks.append(Check("error", "Payload metadata extends beyond image"))
    elif info.format == "super.img":
        super_info = parse_super(path)
        if super_info.metadata_size == 0:
            checks.append(Check("warning", "super metadata size is zero"))
    checks.append(Check("info", f"SHA-256 {sha256(path)}"))
    return checks


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
