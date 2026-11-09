# Android Image Tool

<p align="center">
  <img src="assets/logo.png" alt="Android Image Tool app icon / Android Image Tool アプリアイコン" width="220">
</p>

<p align="center"><strong>Android Image Tool app icon / Android Image Tool アプリアイコン</strong></p>

Android Image Tool is a cross-platform Android partition image manager for Windows, Linux, and macOS.

Android Image Toolは、Windows・Linux・macOSで動作するAndroid partition image管理ツールです。

## Features / 機能

### English

- Detect and expand raw and Android sparse images.
- Inspect `super.img` metadata and dynamic partitions.
- Inspect and extract `payload.bin`.
- Browse, extract, and rebuild ext4 images.
- Inspect Android boot images and edit gzip/cpio ramdisks.
- Inspect and sign AVB/vbmeta through `avbtool`.
- Validate image boundaries, metadata, formats, and SHA-256 hashes.
- Create ROM project manifests, safe workspaces, binary/text diffs, and OTA ZIPs.
- Analyze boot/crash logs and collect ADB/Fastboot device profiles.
- Edit raw images with warnings, backups, range validation, and output hashes.
- Use Japanese and English UI strings stored in editable JSON files.

### 日本語

- raw / Android sparseイメージの判定・展開
- `super.img`のメタデータ解析とdynamic partition対応
- `payload.bin`の解析・展開
- ext4イメージの閲覧・抽出・再構築
- Android boot imageの解析・抽出、gzip/cpio ramdisk編集
- `avbtool`によるAVB/vbmeta解析・署名連携
- イメージ境界・メタデータ・形式・SHA-256検証
- ROMプロジェクト管理、作業コピー、差分比較、OTA ZIP作成
- boot/crashログ解析、ADB/Fastboot端末プロファイル取得
- 警告・バックアップ・範囲検証付きraw編集
- JSONファイルで変更できる日本語/英語UI

The application never edits the source image in place. Rebuild operations create a new output file.

本ソフトは元イメージを直接変更しません。再構築では常に新しい出力ファイルを作成します。

## Run / 起動方法

### English

```powershell
cd C:\Users\mnqhp\Documents\Android_tools
python -m pip install -e .
python -m android_image_tool
```

The GUI can also be started with:

```powershell
android-image-tool-gui
```

Open an image with **Open image**. For ext4 editing, choose **Extract all**, modify the staging directory, then choose **Rebuild ext4**.

### 日本語

```powershell
cd C:\Users\mnqhp\Documents\Android_tools
python -m pip install -e .
python -m android_image_tool
```

GUIは次でも起動できます。

```powershell
android-image-tool-gui
```

「イメージを開く」で対象を選択します。ext4編集では「すべて展開」で作業フォルダーへ展開し、ファイル変更後に「ext4を再構築」を実行します。

## Image editing / イメージ編集

### English

For logo and vendor-specific raw images, use **Edit raw bytes**. The tool writes a new output image, creates `<source>.bak` once, validates the byte range, and displays the output SHA-256. Raw editing is dangerous and requires explicit confirmation.

Ramdisks can be unpacked and repacked as gzip/cpio components. Rebuilding the complete boot image header and AVB metadata still requires a compatible boot-image/signing tool.

### 日本語

logoなどのvendor固有rawイメージは「rawバイトを編集」を使います。新しい出力を作成し、`<元ファイル>.bak`を一度だけ作成し、バイト範囲を検証してSHA-256を表示します。raw編集には確認が必要です。

ramdiskはgzip/cpioコンポーネントとして展開・再梱包できます。boot image全体のheaderやAVBメタデータの再構築には、対応するboot image・署名ツールが必要です。

## CLI commands / CLIコマンド

The following commands are available. / 以下のコマンドを利用できます。

```powershell
python -m android_image_tool.cli boot-info boot.img
python -m android_image_tool.cli boot-extract boot.img extracted-boot
python -m android_image_tool.cli ramdisk-unpack extracted-boot\ramdisk ramdisk
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

## External tools / 外部ツール

### English

Python and PySide6 provide the application and GUI. Optional Android tools include Android SDK Platform-Tools (`adb`, `fastboot`), `mke2fs`, `avbtool`, `mkbootimg`, `lpunpack`, `mkfs.erofs`, and `payload-dumper-go`. Each tool is required only for its related feature, and its own license and terms apply.

If a required tool is missing, the GUI asks first. Google Platform-Tools are downloaded only after confirmation from Google's official distribution. For other tools, the app opens official or upstream instructions instead of silently downloading an untrusted executable.

### 日本語

Python / PySide6がアプリ本体とGUIを提供します。任意の外部ツールとしてAndroid SDK Platform-Tools（`adb`、`fastboot`）、`mke2fs`、`avbtool`、`mkbootimg`、`lpunpack`、`mkfs.erofs`、`payload-dumper-go`などを使用します。必要な機能の実行時だけ導入が必要で、各ツールのライセンスと利用規約が適用されます。

必要なツールがない場合、GUIは先に確認します。Google Platform-Toolsは確認後にGoogle公式配布元から取得します。それ以外は、出所不明の実行ファイルを勝手に取得せず、公式または上流プロジェクトの手順を案内します。

## Notes / 注意事項

### English

EROFS can be detected and inspected, but EROFS writing is disabled for safety. `mke2fs` is required for ext4 rebuilding. ADB/Fastboot partition backup requires a rooted device and uses `adb exec-out`; the application never runs a flash command automatically. GUI logs are stored at `%USERPROFILE%\.android-image-tool.log` on Windows and `~/.android-image-tool.log` on Linux/macOS.

### 日本語

EROFSは検出・基本確認できますが、安全のため書き込みは無効です。ext4再構築には`mke2fs`が必要です。ADB/Fastbootのpartitionバックアップにはroot化済み端末が必要で、`adb exec-out`を使用します。自動flashは行いません。GUIログはWindowsでは`%USERPROFILE%\.android-image-tool.log`、Linux/macOSでは`~/.android-image-tool.log`に保存されます。

## Documentation / ドキュメント

- [English guide](docs/README-en.md)
- [日本語ガイド](docs/README-ja.md)
- [English FAQ](docs/FAQ-en.md)
- [よくある質問（日本語）](docs/FAQ-ja.md)

## Disclaimer / 免責事項

### English

This software is provided for research, education, and custom-ROM development. Image modification, AVB changes, bootloader operations, and device recovery may damage a device, erase data, void a warranty, or make software unable to boot. You are responsible for backups, licenses, signing keys, compatibility, and every command you execute. The authors and contributors provide no warranty and accept no liability.

### 日本語

本ソフトは研究、教育、カスタムROM開発を目的として提供されます。イメージ編集、AVB変更、ブートローダー操作、端末への書き込みは、端末破損、データ消失、保証無効化、起動不能を招く可能性があります。バックアップ、ライセンス、署名鍵、互換性、実行するコマンドは利用者が確認してください。作者および貢献者は保証を行わず、責任を負いません。

## Credits / クレジット

### English

Android Image Tool is maintained by **kagithu** with assistance from **GitHub Copilot**. It builds on the Android Open Source Project ecosystem, Android SDK Platform-Tools, Linux filesystem tools, PySide6/Qt, and the upstream projects listed above. The app icon is stored at [`assets/logo.png`](assets/logo.png).

### 日本語

Android Image Toolは**kagithu**が開発・管理し、**GitHub Copilot**の支援を受けています。Android Open Source Project、Android SDK Platform-Tools、Linux filesystem tools、PySide6/Qt、および上記の上流プロジェクトを活用しています。アプリアイコンは[`assets/logo.png`](assets/logo.png)に保存されています。
