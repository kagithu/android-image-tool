from __future__ import annotations

import os
import struct
from dataclasses import dataclass
from pathlib import Path

EXT4_MAGIC = 0xEF53


@dataclass(frozen=True)
class Extent:
    logical: int
    physical: int
    length: int


class Ext4Image:
    def __init__(self, path: Path):
        self.path = path
        self.stream = path.open("rb")
        self.superblock = self.stream.read(2048)
        if len(self.superblock) < 0x460 or struct.unpack_from("<H", self.superblock, 0x38)[0] != EXT4_MAGIC:
            self.close()
            raise ValueError("Not an ext4 image")
        self.inode_size = struct.unpack_from("<H", self.superblock, 0x58)[0]
        self.block_size = 1024 << struct.unpack_from("<I", self.superblock, 0x18)[0]
        self.inodes_per_group = struct.unpack_from("<I", self.superblock, 0x28)[0]
        self.blocks_per_group = struct.unpack_from("<I", self.superblock, 0x20)[0]
        self.first_data_block = struct.unpack_from("<I", self.superblock, 0x14)[0]
        self.inode_table_size = self.inodes_per_group * self.inode_size
        self.group_desc_size = max(32, struct.unpack_from("<H", self.superblock, 0xFE)[0] or 32)
        self.groups = (self.block_count + self.blocks_per_group - 1) // self.blocks_per_group
        self.desc_offset = (self.first_data_block + 1) * self.block_size

    @property
    def block_count(self) -> int:
        return struct.unpack_from("<I", self.superblock, 0x04)[0] | (
            struct.unpack_from("<I", self.superblock, 0x150)[0] << 32
        )

    @property
    def label(self) -> str:
        return self.superblock[0x78:0x88].split(b"\0", 1)[0].decode("utf-8", "replace")

    def close(self) -> None:
        if not self.stream.closed:
            self.stream.close()

    def __enter__(self) -> "Ext4Image":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _read(self, offset: int, size: int) -> bytes:
        self.stream.seek(offset)
        data = self.stream.read(size)
        if len(data) != size:
            raise ValueError("Truncated ext4 image")
        return data

    def _inode(self, number: int) -> bytes:
        if number < 1:
            raise ValueError("Invalid inode")
        group = (number - 1) // self.inodes_per_group
        index = (number - 1) % self.inodes_per_group
        desc = self._read(self.desc_offset + group * self.group_desc_size, self.group_desc_size)
        table = struct.unpack_from("<I", desc, 8)[0] | (struct.unpack_from("<I", desc, 40)[0] << 32)
        return self._read(table * self.block_size + index * self.inode_size, self.inode_size)

    def _extents(self, inode: bytes) -> list[Extent]:
        flags = struct.unpack_from("<I", inode, 0x20)[0]
        if not flags & 0x80000:
            raise ValueError("Only extent-based ext4 files are supported")
        root = inode[0x28:0x28 + 60]
        return self._extent_node(root)

    def _extent_node(self, node: bytes) -> list[Extent]:
        magic, entries, depth = struct.unpack_from("<HHH", node, 0)
        if magic != 0xF30A or entries > 340:
            raise ValueError("Invalid ext4 extent tree")
        result: list[Extent] = []
        if depth == 0:
            for pos in range(entries):
                logical, raw_len, physical_lo, physical_hi = struct.unpack_from("<IHHI", node, 12 + pos * 12)
                result.append(Extent(logical, physical_lo | (physical_hi << 32), raw_len & 0x7FFF))
            return result
        for pos in range(entries):
            _, leaf_lo, leaf_hi = struct.unpack_from("<IIH", node, 12 + pos * 12)
            child = self._read((leaf_lo | (leaf_hi << 32)) * self.block_size, self.block_size)
            result.extend(self._extent_node(child))
        return result

    def _read_file(self, inode: bytes) -> bytes:
        size = struct.unpack_from("<I", inode, 4)[0] | (struct.unpack_from("<I", inode, 0x6C)[0] << 32)
        data = bytearray()
        for extent in self._extents(inode):
            data.extend(self._read(extent.physical * self.block_size, extent.length * self.block_size))
        return bytes(data[:size])

    def list_dir(self, inode_number: int = 2, prefix: str = "") -> list[str]:
        inode = self._inode(inode_number)
        if struct.unpack_from("<H", inode, 0)[0] & 0xF000 != 0x4000:
            raise ValueError("Not a directory")
        raw = self._read_file(inode)
        names: list[str] = []
        pos = 0
        while pos + 8 <= len(raw):
            child, record_len, name_len, _ = struct.unpack_from("<IHBb", raw, pos)
            if record_len < 8 or pos + record_len > len(raw):
                break
            if child and name_len:
                name = raw[pos + 8:pos + 8 + name_len].decode("utf-8", "replace")
                if name not in (".", ".."):
                    path = f"{prefix}/{name}"
                    names.append(path)
                    child_inode = self._inode(child)
                    if struct.unpack_from("<H", child_inode, 0)[0] & 0xF000 == 0x4000:
                        names.extend(self.list_dir(child, path))
            pos += record_len
        return names

    def _find(self, path: str) -> tuple[int, bytes]:
        current = 2
        for part in [p for p in path.strip("/").split("/") if p]:
            found = None
            raw = self._read_file(self._inode(current))
            pos = 0
            while pos + 8 <= len(raw):
                child, record_len, name_len, _ = struct.unpack_from("<IHBb", raw, pos)
                name = raw[pos + 8:pos + 8 + name_len].decode("utf-8", "replace")
                if child and name == part:
                    found = child
                    break
                if record_len < 8:
                    break
                pos += record_len
            if found is None:
                raise FileNotFoundError(path)
            current = found
        return current, self._inode(current)

    def extract(self, image_path: str, destination: Path) -> int:
        _, inode = self._find(image_path)
        mode = struct.unpack_from("<H", inode, 0)[0]
        if mode & 0xF000 == 0x4000:
            raise IsADirectoryError(image_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self._read_file(inode))
        return destination.stat().st_size


def rebuild_ext4(staging: Path, output: Path, size: int, mke2fs: str = "mke2fs") -> None:
    import shutil
    import subprocess

    if not staging.is_dir():
        raise NotADirectoryError(f"Staging directory does not exist: {staging}")
    executable = shutil.which(mke2fs) or mke2fs
    if not Path(executable).exists() and shutil.which(executable) is None:
        raise FileNotFoundError("mke2fs is required to rebuild ext4 images")
    if size < 1024 * 1024:
        raise ValueError("ext4 output size must be at least 1 MiB")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        stream.truncate(size)
    command = [executable, "-t", "ext4", "-F", "-d", os.fspath(staging), os.fspath(output)]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        detail = (completed.stderr or "").strip() or (completed.stdout or "").strip()
        raise RuntimeError(f"mke2fs failed: {detail or 'unknown error'}")
