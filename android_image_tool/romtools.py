from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path


def _tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise FileNotFoundError(f"{name} is required; install Android build tools and add it to PATH")
    return path


def run_tool(name: str, args: list[str], timeout: int = 600) -> str:
    result = subprocess.run(
        [_tool(name), *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{name} failed")
    return result.stdout.strip()


def unpack_super(image: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    return run_tool("lpunpack", [str(image), str(output)])


def unpack_payload(payload: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    for name in ("payload-dumper-go", "payload-dumper"):
        if shutil.which(name):
            return run_tool(name, [str(payload), "-o", str(output)])
    raise FileNotFoundError("payload-dumper-go or payload-dumper is required to extract payload.bin")


def rebuild_erofs(source: Path, output: Path, size: int | None = None) -> str:
    args = [str(output), str(source)]
    if size:
        args[0:0] = ["-E", f"fragments,max-extent-by-4k"]
    return run_tool("mkfs.erofs", args)


def build_ota(source: Path, output: Path) -> None:
    if not source.is_dir():
        raise NotADirectoryError(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())


def repack_boot(kernel: Path, ramdisk: Path, output: Path, extra: list[str] | None = None) -> str:
    args = ["--kernel", str(kernel), "--ramdisk", str(ramdisk), "--output", str(output)]
    if extra:
        args.extend(extra)
    return run_tool("mkbootimg", args)


def sign_vbmeta(image: Path, key: Path, algorithm: str, output: Path) -> str:
    return run_tool(
        "avbtool",
        [
            "make_vbmeta_image",
            "--output", str(output),
            "--algorithm", algorithm,
            "--key", str(key),
            "--include_descriptors_from_image", str(image),
        ],
    )
