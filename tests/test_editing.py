from pathlib import Path

import pytest

from android_image_tool.editing import patch_binary


def test_patch_binary_creates_copy_and_backup(tmp_path: Path) -> None:
    source = tmp_path / "logo.img"
    output = tmp_path / "logo-edited.img"
    source.write_bytes(b"abcdef")
    result = patch_binary(source, output, 2, b"XY")
    assert output.read_bytes() == b"abXYef"
    assert source.read_bytes() == b"abcdef"
    assert result.backup.read_bytes() == b"abcdef"


def test_patch_binary_rejects_overflow(tmp_path: Path) -> None:
    source = tmp_path / "logo.img"
    source.write_bytes(b"abc")
    with pytest.raises(ValueError):
        patch_binary(source, tmp_path / "out.img", 2, b"too long")
