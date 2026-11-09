from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def inspect_erofs(path: Path) -> str:
    tool = shutil.which("dump.erofs") or shutil.which("fsck.erofs")
    if not tool:
        raise FileNotFoundError("dump.erofs or fsck.erofs is required for EROFS inspection")
    result = subprocess.run(
        [tool, "--help"] if Path(tool).name.startswith("dump") else [tool, "-V"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    return result.stdout.strip() or result.stderr.strip()
