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

---

## 日本語

Androidのsystem/vendor/recovery/logoなどを扱う、Windows・Linux・macOS対応のカスタムROM開発支援ツールです。

### 未導入ツールの扱い

機能に必要な外部ツールが見つからない場合、GUIはその機能を実行する前に確認を表示します。承諾すると、ADB/FastbootはGoogle公式のPlatform-Toolsを`tools/`へ取得します。その他の`avbtool`、`mkbootimg`、`lpunpack`、`mkfs.erofs`などは、対応する公式または上流プロジェクトの案内を開きます。無断で実行ファイルを取得・実行することはありません。

### ファイルで変更できる言語

画面文言は[locales/ja.json](locales/ja.json)と[locales/en.json](locales/en.json)に分離しています。JSONを編集して再起動すれば、独自の翻訳へ変更できます。

### 安全性

元イメージは直接変更しません。raw編集では警告、出力コピー、バックアップ、SHA-256を使用します。flash操作は実装しておらず、ADB/Fastbootは情報取得、logcat、バックアップを中心にしています。

---

## English

Android Image Tool is a cross-platform custom-ROM development utility for system, vendor, recovery, logo, boot, and related images.

### Missing tools

When a required external tool is missing, the GUI asks before taking action. With confirmation, ADB/Fastboot Platform-Tools are downloaded from Google's official distribution into `tools/`. For `avbtool`, `mkbootimg`, `lpunpack`, and `mkfs.erofs`, the app opens the official or upstream instructions instead of silently downloading and executing untrusted binaries.

### File-based localization

UI strings live in [locales/ja.json](locales/ja.json) and [locales/en.json](locales/en.json). Edit a JSON file and restart the application to customize the translation.

### Safety

Source images are never edited in place. Raw editing requires a warning confirmation and creates an output copy, backup, and SHA-256 report. Flashing is intentionally not automated; ADB/Fastboot features focus on inspection, logcat capture, and backups.
