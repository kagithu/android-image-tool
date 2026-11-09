# Android Image Tool

Cross-platform (Windows, Linux, macOS) Android partition image manager.

## Features

- Raw and Android sparse image detection and conversion.
- `super.img` metadata inspection (LP metadata header and partition table).
- `payload.bin` header and operation inspection.
- ext4 superblock, inode, extent, directory listing, and file extraction.
- ext4 image rebuilding from a staging directory using `mke2fs`.
- Japanese and English GUI/CLI messages.
- Warning-gated raw binary patching for logo/boot/vendor-specific images.
- Automatic source backup (`.bak`), SHA-256 reporting, and error logging.
- Android boot image and vbmeta inspection/extraction.
- Ramdisk gzip/cpio unpacking and repacking for `init`, `fstab`, and early-boot changes.
- Image validation and SHA-256 integrity reporting.
- ROM project manifests, safe workspace copies, binary/text diffs, and crash-log summaries.
- `super.img`, payload, EROFS, and OTA ZIP tool integrations with explicit missing-tool errors.
- Boot repacking, AVB signing wrappers, and ADB device profiles with partition inventories.
- ADB/Fastboot device information, logcat capture, and partition backup helpers.

The application never writes to the source image. Rebuild operations produce a new output file.

## Run

```powershell
python -m pip install -e .
python -m android_image_tool
```

The GUI is also available with:

```powershell
android-image-tool-gui
```

Use the **Open image** button to inspect an image. For ext4 editing, choose **Extract all**, modify the extracted staging directory, then choose **Rebuild ext4**.

For logo and other vendor-specific raw images, use **Edit raw bytes**. The tool always writes a new output image, creates `<source>.bak` once, validates the byte range, and displays the output SHA-256. Raw edits are dangerous and require explicit confirmation; verify the image with the device/vendor tooling before flashing.

Useful ROM-development CLI commands:

```powershell
python -m android_image_tool.cli boot-info boot.img
python -m android_image_tool.cli boot-extract boot.img extracted-boot
python -m android_image_tool.cli ramdisk-unpack extracted-boot/ramdisk ramdisk
python -m android_image_tool.cli ramdisk-pack ramdisk ramdisk-new
python -m android_image_tool.cli vbmeta-info vbmeta.img
python -m android_image_tool.cli validate boot.img
python -m android_image_tool.cli project-scan rom-project rom-project.json
python -m android_image_tool.cli diff stock.img modified.img
python -m android_image_tool.cli analyze-crash boot.log
python -m android_image_tool.cli super-unpack super.img partitions
python -m android_image_tool.cli payload-unpack payload.bin partitions
python -m android_image_tool.cli erofs-rebuild system-tree system-new.img
python -m android_image_tool.cli ota-zip ota-staging update.zip
python -m android_image_tool.cli boot-pack kernel ramdisk-new boot-new.img
python -m android_image_tool.cli vbmeta-sign vbmeta.img key.pem SHA256_RSA2048 vbmeta-signed.img
python -m android_image_tool.cli device-profile
python -m android_image_tool.cli device-info
python -m android_image_tool.cli logcat --output boot.log
python -m android_image_tool.cli backup-partition system system-backup.img
```

ADB/Fastboot tools must be installed separately (Android SDK platform-tools). Partition backup requires a rooted device and uses `adb exec-out`; it never runs a flash command.

Ramdisk editing currently preserves file contents and paths but does not yet rebuild the complete boot image header/checksums. Replace the ramdisk through a boot-image-aware tool and verify AVB before flashing.

## Notes

EROFS can be detected and inspected at the filesystem signature level, but writing EROFS is intentionally not enabled. `mke2fs` is required for ext4 rebuild; the app searches `PATH` and common Android platform-tool locations.

The GUI log is written to `%USERPROFILE%\\.android-image-tool.log` on Windows and `~/.android-image-tool.log` on Linux/macOS. Never flash an image without a verified backup and a matching AVB/signing workflow.

![Android Image Tool](assets/logo.png)
