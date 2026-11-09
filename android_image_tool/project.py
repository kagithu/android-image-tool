from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from .editing import sha256


@dataclass(frozen=True)
class ProjectImage:
    path: str
    format: str
    size: int
    sha256: str
    modified: str


def scan_project(root: Path) -> list[ProjectImage]:
    if not root.is_dir():
        raise NotADirectoryError(root)
    images: list[ProjectImage] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".img", ".bin", ".zip", ".dat"}:
            continue
        stat = path.stat()
        images.append(ProjectImage(
            str(path.relative_to(root)), "unknown", stat.st_size, sha256(path),
            datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        ))
    return images


def save_project(root: Path, output: Path) -> None:
    data = {"version": 1, "root": str(root), "images": [asdict(item) for item in scan_project(root)]}
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_project(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("images"), list):
        raise ValueError("Unsupported project file")
    return data


def create_workspace(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise NotADirectoryError(source)
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Workspace is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
