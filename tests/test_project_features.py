from pathlib import Path

from android_image_tool.compare import binary_diff
from android_image_tool.crash import analyze_log
from android_image_tool.project import load_project, save_project
from android_image_tool.romtools import build_ota


def test_project_diff_crash_and_ota(tmp_path: Path) -> None:
    root = tmp_path / "rom"
    root.mkdir()
    (root / "system.img").write_bytes(b"abc")
    manifest = tmp_path / "project.json"
    save_project(root, manifest)
    assert load_project(manifest)["images"][0]["path"] == "system.img"
    other = tmp_path / "other.img"
    other.write_bytes(b"abd")
    assert binary_diff(root / "system.img", other).changed_bytes == 1
    assert "SELinux" in str(analyze_log("avb verification failed; selinux denied"))
    build_ota(root, tmp_path / "update.zip")
    assert (tmp_path / "update.zip").is_file()
