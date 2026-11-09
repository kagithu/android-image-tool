from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CrashSummary:
    kind: str
    process: str
    signal: str
    suspected: tuple[str, ...]


def analyze_log(text: str) -> CrashSummary:
    lower = text.lower()
    kind = "bootloop" if any(word in lower for word in ("bootloop", "watchdog", "fatal exception")) else "log"
    process_match = re.search(r"(?:process|pid)\s*[:=]\s*([A-Za-z0-9._:-]+)", text, re.I)
    signal_match = re.search(r"(?:signal|fatal signal)\s*[:=]?\s*([A-Z0-9]+)", text, re.I)
    suspects: list[str] = []
    for marker, reason in (
        ("avb", "AVB/vbmeta verification"),
        ("verity", "dm-verity"),
        ("selinux", "SELinux denial"),
        ("mount", "filesystem mount"),
        ("fstab", "fstab configuration"),
        ("permission denied", "file permission"),
    ):
        if marker in lower:
            suspects.append(reason)
    return CrashSummary(
        kind, process_match.group(1) if process_match else "unknown",
        signal_match.group(1) if signal_match else "unknown", tuple(suspects),
    )


def analyze_file(path: Path) -> CrashSummary:
    return analyze_log(path.read_text(encoding="utf-8", errors="replace"))
