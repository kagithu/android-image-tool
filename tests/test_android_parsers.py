import struct
from pathlib import Path

from android_image_tool.android import parse_payload
from android_image_tool.avb import parse_vbmeta
from android_image_tool.boot import parse_boot


def test_payload_header(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(struct.pack("<4sQQI", b"CrAU", 2, 100, 8))
    value = parse_payload(path)
    assert value.version == 2
    assert value.data_offset == 132


def test_vbmeta_header(tmp_path: Path) -> None:
    data = bytearray(b"AVB0" + b"\0" * 252)
    data[28:32] = (1).to_bytes(4, "big")
    data[96:104] = (42).to_bytes(8, "big")
    path = tmp_path / "vbmeta.img"
    path.write_bytes(data)
    assert parse_vbmeta(path).rollback_index == 42


def test_boot_header(tmp_path: Path) -> None:
    data = bytearray(b"ANDROID!" + b"\0" * 400)
    struct.pack_into("<III", data, 8, 10, 20, 0)
    struct.pack_into("<I", data, 36, 4096)
    path = tmp_path / "boot.img"
    path.write_bytes(data)
    assert parse_boot(path).kernel_size == 10
