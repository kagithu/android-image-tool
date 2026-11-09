from pathlib import Path

from android_image_tool.boot import pack_ramdisk, unpack_ramdisk


def test_ramdisk_pack_unpack(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "init").write_text("init", encoding="utf-8")
    ramdisk = tmp_path / "ramdisk"
    unpacked = tmp_path / "unpacked"
    pack_ramdisk(source, ramdisk)
    assert unpack_ramdisk(ramdisk, unpacked) == "cpio"
    assert (unpacked / "init").read_text(encoding="utf-8") == "init"
