from pathlib import Path

import pytest

from android_image_tool.android import parse_payload
from android_image_tool.boot import unpack_ramdisk
from android_image_tool.editing import patch_binary
from android_image_tool.project import load_project


def test_malformed_payload_is_rejected(tmp_path: Path) -> None:
    image = tmp_path / "payload.bin"
    image.write_bytes(b"bad")
    with pytest.raises(ValueError):
        parse_payload(image)


def test_unsafe_ramdisk_path_is_rejected(tmp_path: Path) -> None:
    ramdisk = tmp_path / "ramdisk"
    ramdisk.write_bytes(
        b"070701" + b"00000001" + b"000081a4" + b"00000000" * 4
        + b"00000004" + b"00000000" * 5 + b"../x\0" + b"\0\0\0\0"
    )
    with pytest.raises(ValueError):
        unpack_ramdisk(ramdisk, tmp_path / "out")


def test_project_schema_is_checked(tmp_path: Path) -> None:
    project = tmp_path / "project.json"
    project.write_text('{"version": 99, "images": []}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_project(project)


def test_in_place_patch_is_rejected(tmp_path: Path) -> None:
    image = tmp_path / "image.img"
    image.write_bytes(b"abc")
    with pytest.raises(ValueError):
        patch_binary(image, image, 0, b"x")
