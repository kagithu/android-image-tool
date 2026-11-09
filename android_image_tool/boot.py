from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BootImageInfo:
    version: int
    header_size: int
    kernel_size: int
    ramdisk_size: int
    second_size: int
    dtb_size: int
    os_version: str


def parse_boot(path: Path) -> BootImageInfo:
    with path.open("rb") as stream:
        header = stream.read(4096)
    if len(header) < 44 or header[:8] != b"ANDROID!":
        raise ValueError("Not an Android boot image")
    kernel, ramdisk, second = struct.unpack_from("<III", header, 8)
    page_size = struct.unpack_from("<I", header, 36)[0]
    if page_size < 512 or page_size & (page_size - 1):
        raise ValueError("Invalid boot image page size")
    version = struct.unpack_from("<I", header, 40)[0] if len(header) >= 44 else 0
    header_size = struct.unpack_from("<I", header, 20)[0] if version else 608
    dtb = struct.unpack_from("<I", header, 40)[0] if version >= 2 and len(header) >= 44 else 0
    os_version_raw = struct.unpack_from("<I", header, 44)[0] if len(header) >= 48 else 0
    os_version = f"{(os_version_raw >> 25) & 0x7f}.{(os_version_raw >> 14) & 0x7ff}.{(os_version_raw >> 7) & 0x7f}"
    return BootImageInfo(version, header_size, kernel, ramdisk, second, dtb, os_version)


def extract_boot_parts(path: Path, output: Path) -> BootImageInfo:
    info = parse_boot(path)
    with path.open("rb") as stream:
        stream.seek(info.header_size)
        output.mkdir(parents=True, exist_ok=True)
        for name, size in (("kernel", info.kernel_size), ("ramdisk", info.ramdisk_size)):
            (output / name).write_bytes(stream.read(size))
    return info
