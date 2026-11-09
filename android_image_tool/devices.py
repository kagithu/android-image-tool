from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AndroidTools:
    def __init__(self, adb: str = "adb", fastboot: str = "fastboot") -> None:
        self.adb = shutil.which(adb) or adb
        self.fastboot = shutil.which(fastboot) or fastboot

    def _run(self, command: list[str], timeout: int = 30) -> str:
        if not Path(command[0]).exists() and shutil.which(command[0]) is None:
            raise FileNotFoundError(f"Tool not found: {command[0]}")
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Android tool failed")
        return result.stdout.strip()

    def adb_devices(self) -> str:
        return self._run([self.adb, "devices", "-l"])

    def fastboot_devices(self) -> str:
        return self._run([self.fastboot, "devices"])

    def adb_shell(self, *args: str) -> str:
        return self._run([self.adb, "shell", *args])

    def getprop(self) -> dict[str, str]:
        output = self.adb_shell("getprop")
        properties: dict[str, str] = {}
        for line in output.splitlines():
            if line.startswith("[") and "]: [" in line:
                key, value = line[1:].split("]: [", 1)
                properties[key] = value.rstrip("]")
        return properties

    def partition_names(self) -> list[str]:
        output = self.adb_shell("ls", "-1", "/dev/block/by-name")
        return [line.strip() for line in output.splitlines() if line.strip()]

    def device_profile(self) -> dict[str, object]:
        properties = self.getprop()
        return {
            "model": properties.get("ro.product.model", "unknown"),
            "manufacturer": properties.get("ro.product.manufacturer", "unknown"),
            "android": properties.get("ro.build.version.release", "unknown"),
            "api": properties.get("ro.build.version.sdk", "unknown"),
            "slot": properties.get("ro.boot.slot_suffix", "unknown"),
            "ab": properties.get("ro.build.ab_update", "unknown"),
            "partitions": self.partition_names(),
        }

    def getvar(self, variable: str) -> str:
        return self._run([self.fastboot, "getvar", variable], timeout=60)

    def backup_partition(self, partition: str, output: Path) -> None:
        if not partition.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Invalid partition name")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as stream:
            result = subprocess.run(
                [self.adb, "exec-out", "su", "-c", f"dd if=/dev/block/by-name/{partition} bs=4M"],
                stdout=stream, stderr=subprocess.PIPE, text=False, check=False,
            )
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", "replace").strip() or "Partition backup failed")

    def logcat(self, output: Path | None = None) -> str:
        text = self._run([self.adb, "logcat", "-d", "-b", "all"], timeout=60)
        if output:
            output.write_text(text, encoding="utf-8")
        return text
