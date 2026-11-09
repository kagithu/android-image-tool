from __future__ import annotations

import argparse
from pathlib import Path

from .android import parse_payload, parse_super
from .avb import avbtool_info, parse_vbmeta
from .boot import extract_boot_parts, parse_boot
from .devices import AndroidTools
from .editing import patch_binary
from .ext4 import Ext4Image, rebuild_ext4
from .formats import detect_format
from .sparse import unsparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Android image inspection and ext4 tooling")
    sub = parser.add_subparsers(dest="command", required=True)
    info = sub.add_parser("info")
    info.add_argument("image", type=Path)
    extract = sub.add_parser("extract")
    extract.add_argument("image", type=Path)
    extract.add_argument("output", type=Path)
    rebuild = sub.add_parser("rebuild-ext4")
    rebuild.add_argument("staging", type=Path)
    rebuild.add_argument("output", type=Path)
    rebuild.add_argument("--size-mib", type=int, default=2048)
    unsparse_cmd = sub.add_parser("unsparse")
    unsparse_cmd.add_argument("image", type=Path)
    unsparse_cmd.add_argument("output", type=Path)
    patch = sub.add_parser("patch-raw", help="Patch a copy of a raw image after explicit user confirmation")
    patch.add_argument("image", type=Path)
    patch.add_argument("output", type=Path)
    patch.add_argument("offset", type=lambda value: int(value, 0))
    patch.add_argument("hex_bytes", help="Replacement bytes, e.g. deadbeef")
    boot = sub.add_parser("boot-info")
    boot.add_argument("image", type=Path)
    boot_extract = sub.add_parser("boot-extract")
    boot_extract.add_argument("image", type=Path)
    boot_extract.add_argument("output", type=Path)
    vbmeta = sub.add_parser("vbmeta-info")
    vbmeta.add_argument("image", type=Path)
    vbmeta.add_argument("--avbtool", action="store_true")
    device = sub.add_parser("device-info")
    device.add_argument("--fastboot", action="store_true")
    device.add_argument("--getvar")
    logs = sub.add_parser("logcat")
    logs.add_argument("--output", type=Path)
    backup = sub.add_parser("backup-partition")
    backup.add_argument("partition")
    backup.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "info":
            value = detect_format(args.image)
            print(f"{value.format}\n{value.details}\n{value.size} bytes\neditable={value.editable}")
            if value.format == "ext4":
                with Ext4Image(args.image) as image:
                    print(f"block_size={image.block_size} label={image.label}")
                    print("\n".join(image.list_dir()[:500]))
            elif value.format == "super.img":
                print(parse_super(args.image))
            elif value.format == "payload.bin":
                print(parse_payload(args.image))
        elif args.command == "extract":
            with Ext4Image(args.image) as image:
                for entry in image.list_dir():
                    if entry.endswith("/"):
                        continue
                    try:
                        image.extract(entry, args.output / entry.lstrip("/"))
                    except (FileNotFoundError, IsADirectoryError, ValueError):
                        pass
        elif args.command == "rebuild-ext4":
            rebuild_ext4(args.staging, args.output, args.size_mib * 1024 * 1024)
        elif args.command == "patch-raw":
            result = patch_binary(args.image, args.output, args.offset, bytes.fromhex(args.hex_bytes))
            print(f"{result.output}\nbackup={result.backup}\nsha256={result.sha256}")
        elif args.command == "boot-info":
            print(parse_boot(args.image))
        elif args.command == "boot-extract":
            print(extract_boot_parts(args.image, args.output))
        elif args.command == "vbmeta-info":
            print(parse_vbmeta(args.image))
            if args.avbtool:
                print(avbtool_info(args.image))
        elif args.command == "device-info":
            tools = AndroidTools()
            print(tools.fastboot_devices() if args.fastboot else tools.adb_devices())
            if args.getvar:
                print(tools.getvar(args.getvar))
        elif args.command == "logcat":
            print(AndroidTools().logcat(args.output))
        elif args.command == "backup-partition":
            AndroidTools().backup_partition(args.partition, args.output)
            print(args.output)
        else:
            print(f"expanded {unsparse(args.image, args.output)} bytes")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
