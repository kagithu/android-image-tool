from __future__ import annotations

import struct
from pathlib import Path

MAGIC = 0xED26FF3A
CHUNK_RAW = 0xCAC1
CHUNK_FILL = 0xCAC2
CHUNK_DONT_CARE = 0xCAC3
CHUNK_CRC32 = 0xCAC4


def is_sparse(path: Path) -> bool:
    with path.open("rb") as stream:
        data = stream.read(4)
    return len(data) == 4 and struct.unpack("<I", data)[0] == MAGIC


def unsparse(source: Path, destination: Path) -> int:
    with source.open("rb") as inp:
        header = inp.read(28)
        if len(header) != 28:
            raise ValueError("Truncated sparse header")
        magic, major, minor, file_hdr, chunk_hdr, block_size, blocks, chunks, _ = struct.unpack(
            "<IHHHHIIII", header
        )
        if magic != MAGIC or major != 1 or file_hdr != 28 or chunk_hdr != 12:
            raise ValueError("Unsupported Android sparse header")
        if block_size == 0:
            raise ValueError("Invalid sparse block size")
        written = 0
        with destination.open("wb") as out:
            for _ in range(chunks):
                raw = inp.read(12)
                if len(raw) != 12:
                    raise ValueError("Truncated sparse chunk header")
                kind, _, chunk_blocks, total_size = struct.unpack("<HHII", raw)
                output_size = chunk_blocks * block_size
                data_size = total_size - chunk_hdr
                if data_size < 0:
                    raise ValueError("Invalid sparse chunk size")
                if kind == CHUNK_RAW:
                    if data_size != output_size:
                        raise ValueError("Invalid raw sparse chunk")
                    remaining = data_size
                    while remaining:
                        piece = inp.read(min(1024 * 1024, remaining))
                        if not piece:
                            raise ValueError("Truncated raw sparse chunk")
                        out.write(piece)
                        remaining -= len(piece)
                elif kind == CHUNK_FILL:
                    if data_size != 4:
                        raise ValueError("Invalid fill sparse chunk")
                    fill = inp.read(4)
                    if len(fill) != 4:
                        raise ValueError("Truncated fill sparse chunk")
                    out.write(fill * (output_size // 4))
                    if output_size % 4:
                        out.write((fill * 2)[: output_size % 4])
                elif kind == CHUNK_DONT_CARE:
                    if data_size:
                        inp.seek(data_size, 1)
                    out.seek(output_size, 1)
                elif kind == CHUNK_CRC32:
                    inp.seek(data_size, 1)
                else:
                    raise ValueError(f"Unsupported sparse chunk type 0x{kind:04x}")
                written += output_size
        if written != blocks * block_size:
            raise ValueError("Sparse block count mismatch")
        return written
