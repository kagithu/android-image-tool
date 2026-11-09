import struct
from pathlib import Path

from android_image_tool.formats import detect_format
from android_image_tool.sparse import unsparse


def test_sparse_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source.img"
    output = tmp_path / "output.img"
    source.write_bytes(b"abc" * 100)
    payload = source.read_bytes()
    header = struct.pack("<IHHHHIIII", 0xED26FF3A, 1, 0, 28, 12, 4, 75, 1, 0)
    chunk = struct.pack("<HHII", 0xCAC1, 0, 75, 12 + 300)
    sparse = tmp_path / "sparse.img"
    sparse.write_bytes(header + chunk + payload + b"\0")
    unsparse(sparse, output)
    assert output.read_bytes()[:300] == payload
    assert detect_format(sparse).format == "Android sparse"
