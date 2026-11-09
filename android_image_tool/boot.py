from __future__ import annotations

import gzip
import lzma
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BootImageInfo:
    version: int
    header_size: int
    page_size: int
    kernel_size: int
    ramdisk_size: int
    second_size: int
    dtb_size: int
    os_version: str
    kernel_offset: int
    ramdisk_offset: int
    dtb_offset: int


def _align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def parse_boot(path: Path) -> BootImageInfo:
    with path.open("rb") as stream:
        header = stream.read(4096)
    if len(header) < 44 or header[:8] != b"ANDROID!":
        raise ValueError("Not an Android boot image")
    kernel, ramdisk, second = struct.unpack_from("<III", header, 8)
    page_size = struct.unpack_from("<I", header, 36)[0]
    if page_size < 512 or page_size & (page_size - 1):
        raise ValueError("Invalid boot image page size")
    version = struct.unpack_from("<I", header, 40)[0]
    if version <= 2:
        header_size = struct.unpack_from("<I", header, 20)[0] or page_size
        dtb_size = struct.unpack_from("<I", header, 1648)[0] if version == 2 and len(header) >= 1652 else 0
        header_offset = page_size
        kernel_offset = header_offset
        ramdisk_offset = kernel_offset + _align(kernel, page_size)
        second_offset = ramdisk_offset + _align(ramdisk, page_size)
        dtb_offset = second_offset + _align(second, page_size)
    else:
        header_size = struct.unpack_from("<I", header, 1632)[0] if len(header) >= 1636 else 4096
        page_size = 4096
        dtb_size = struct.unpack_from("<I", header, 1660)[0] if len(header) >= 1664 else 0
        header_offset = page_size
        kernel_offset = header_offset
        ramdisk_offset = kernel_offset + _align(kernel, page_size)
        dtb_offset = ramdisk_offset + _align(ramdisk, page_size)
    os_version_raw = struct.unpack_from("<I", header, 44)[0] if len(header) >= 48 else 0
    os_version = f"{(os_version_raw >> 25) & 0x7f}.{(os_version_raw >> 14) & 0x7ff}.{(os_version_raw >> 7) & 0x7f}"
    return BootImageInfo(
        version, header_size, page_size, kernel, ramdisk, second, dtb_size, os_version,
        kernel_offset, ramdisk_offset, dtb_offset,
    )


def _read_part(stream, offset: int, size: int) -> bytes:
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Boot image component is truncated")
    return data


def detect_ramdisk_compression(data: bytes) -> str:
    if data.startswith(b"\x1f\x8b"):
        return "gzip"
    if data.startswith(b"\x28\xb5\x2f\xfd"):
        return "zstd"
    if data.startswith(b"\x02\x21\x4c\x18"):
        return "lz4"
    if data.startswith(b"\xfd7zXZ\x00"):
        return "xz"
    if data.startswith(b"\x04\x22\x4d\x18"):
        return "lz4 legacy"
    if data.startswith(b"070701") or data.startswith(b"070702"):
        return "cpio"
    return "unknown"


def decompress_ramdisk(data: bytes) -> bytes:
    compression = detect_ramdisk_compression(data)
    if compression == "gzip":
        return gzip.decompress(data)
    if compression == "xz":
        return lzma.decompress(data)
    if compression == "cpio":
        return data
    raise ValueError(f"Unsupported ramdisk compression: {compression}; install a zstd/lz4 tool for it")


def extract_boot_parts(path: Path, output: Path) -> BootImageInfo:
    info = parse_boot(path)
    with path.open("rb") as stream:
        output.mkdir(parents=True, exist_ok=True)
        kernel = _read_part(stream, info.kernel_offset, info.kernel_size)
        ramdisk = _read_part(stream, info.ramdisk_offset, info.ramdisk_size)
        (output / "kernel").write_bytes(kernel)
        (output / "ramdisk").write_bytes(ramdisk)
        (output / "ramdisk-compression.txt").write_text(detect_ramdisk_compression(ramdisk), encoding="utf-8")
        if info.dtb_size:
            (output / "dtb").write_bytes(_read_part(stream, info.dtb_offset, info.dtb_size))
    return info


def unpack_ramdisk(ramdisk: Path, output: Path) -> str:
    raw = decompress_ramdisk(ramdisk.read_bytes())
    if not raw.startswith((b"070701", b"070702")):
        raise ValueError("Ramdisk is not a newc/cran cpio archive")
    output.mkdir(parents=True, exist_ok=True)
    position = 0
    while position + 110 <= len(raw):
        header = raw[position:position + 110]
        magic = header[:6]
        if magic not in (b"070701", b"070702"):
            raise ValueError("Invalid cpio header")
        fields = [int(header[index:index + 8], 16) for index in range(6, 110, 8)]
        mode, size = fields[1], fields[6]
        name_size = fields[11]
        name_start = position + 110
        name_end = name_start + name_size
        name = raw[name_start:name_end - 1].decode("utf-8", "surrogateescape")
        data_start = (name_end + 3) & ~3
        data_end = data_start + size
        if name == "TRAILER!!!":
            break
        target = (output / name).resolve()
        if output.resolve() not in target.parents:
            raise ValueError("Unsafe path in ramdisk archive")
        if mode & 0o170000 == 0o040000:
            target.mkdir(parents=True, exist_ok=True)
        elif mode & 0o170000 == 0o120000:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(raw[data_start:data_end].decode("utf-8", "surrogateescape"))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw[data_start:data_end])
        position = (data_end + 3) & ~3
    return "cpio"


def pack_ramdisk(source: Path, output: Path, compression: str = "gzip") -> None:
    if not source.is_dir():
        raise NotADirectoryError(source)
    entries = sorted((path for path in source.rglob("*")), key=lambda path: path.relative_to(source).as_posix())
    archive = bytearray()
    inode = 1
    for path in entries:
        name = path.relative_to(source).as_posix()
        stat = path.lstat()
        if path.is_dir():
            mode = 0o040000 | (stat.st_mode & 0o7777)
            data = b""
            nlink = 2
        elif path.is_symlink():
            mode = 0o120000 | (stat.st_mode & 0o7777)
            data = path.readlink().as_posix().encode("utf-8", "surrogateescape")
            nlink = 1
        else:
            mode = 0o100000 | (stat.st_mode & 0o7777)
            data = path.read_bytes()
            nlink = 1
        fields = [inode, mode, 0, 0, nlink, 0, len(data), 0, 0, 0, 0, len(name) + 1, 0]
        archive.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields))
        archive.extend(name.encode() + b"\0")
        archive.extend(b"\0" * ((-len(archive)) & 3))
        archive.extend(data)
        archive.extend(b"\0" * ((-len(archive)) & 3))
        inode += 1
    trailer = b"TRAILER!!!"
    fields = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(trailer) + 1, 0]
    archive.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields))
    archive.extend(trailer + b"\0")
    archive.extend(b"\0" * ((-len(archive)) & 3))
    if compression == "gzip":
        output.write_bytes(gzip.compress(bytes(archive), mtime=0))
    elif compression == "cpio":
        output.write_bytes(archive)
    else:
        raise ValueError("Only gzip and uncompressed cpio ramdisks can be packed without external tools")
