from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

SPARSE_MAGIC = 0xED26FF3A
EXT4_MAGIC = 0xEF53
LP_MAGIC = b"gDla"
PAYLOAD_MAGIC = b"CrAU"


@dataclass(frozen=True)
class ImageInfo:
    path: Path
    format: str
    size: int
    details: str
    editable: bool


def detect_format(path: Path) -> ImageInfo:
    size = path.stat().st_size
    with path.open("rb") as stream:
        head = stream.read(4096)
    if len(head) >= 4 and struct.unpack_from("<I", head)[0] == SPARSE_MAGIC:
        return ImageInfo(path, "Android sparse", size, "Sparse image", True)
    if len(head) >= 4 and head[:4] == PAYLOAD_MAGIC:
        return ImageInfo(path, "payload.bin", size, "Android OTA payload", False)
    if len(head) >= 4 and head[:4] == LP_MAGIC:
        return ImageInfo(path, "super.img", size, "Logical partition metadata", False)
    if len(head) >= 8 and head[:8] == b"ANDROID!":
        return ImageInfo(path, "Android boot image", size, "boot/vendor_boot/init_boot image", True)
    if len(head) >= 4 and head[:4] == b"AVB0":
        return ImageInfo(path, "AVB vbmeta", size, "Android Verified Boot metadata", True)
    if len(head) >= 0x43A and struct.unpack_from("<H", head, 0x438)[0] == EXT4_MAGIC:
        return ImageInfo(path, "ext4", size, "Linux ext4 filesystem", True)
    if b"EROFS" in head[:1024]:
        return ImageInfo(path, "EROFS", size, "EROFS filesystem (read-only)", False)
    return ImageInfo(path, "raw/unknown", size, "Unknown Android image", True)
