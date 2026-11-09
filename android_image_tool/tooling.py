from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"


class MissingToolError(FileNotFoundError):
    def __init__(self, tool: str, purpose: str) -> None:
        super().__init__(f"{tool} is required for {purpose}")
        self.tool = tool
        self.purpose = purpose


def find_tool(name: str, purpose: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    filename = f"{name}.exe" if os.name == "nt" else name
    for local in (TOOLS_DIR / filename, TOOLS_DIR / "platform-tools" / filename):
        if local.is_file():
            return str(local)
    raise MissingToolError(name, purpose)


def platform_tools_url() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    if system == "darwin":
        return "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    return "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"


def download_platform_tools(progress: callable | None = None) -> Path:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    archive = TOOLS_DIR / "platform-tools.zip"
    urllib.request.urlretrieve(platform_tools_url(), archive, progress)
    extract = TOOLS_DIR / "platform-tools"
    shutil.unpack_archive(archive, TOOLS_DIR)
    archive.unlink(missing_ok=True)
    return extract


def open_tool_instructions(tool: str) -> None:
    urls = {
        "avbtool": "https://android.googlesource.com/platform/external/avb/",
        "mkbootimg": "https://android.googlesource.com/platform/system/tools/mkbootimg/",
        "lpunpack": "https://android.googlesource.com/platform/system/core/+/main/fs_mgr/",
        "mkfs.erofs": "https://erofs.docs.kernel.org/en/latest/tools.html",
        "payload-dumper-go": "https://github.com/ssut/payload-dumper-go/releases",
    }
    webbrowser.open(urls.get(tool, "https://developer.android.com/tools/releases/platform-tools"))
