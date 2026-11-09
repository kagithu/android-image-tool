# Android Image Tool

<p align="center">
  <img src="assets/logo.png" alt="Android Image Tool app icon" width="220">
</p>

<p align="center"><strong>Android Image Tool app icon</strong> / <strong>アプリのアイコン</strong></p>

Cross-platform (Windows, Linux, macOS) Android partition image manager.

## Features / 機能

### English

- Detect and expand raw and Android sparse images.
- Inspect `super.img` metadata and dynamic-partition tooling.
- Inspect and extract `payload.bin` through an official/upstream tool.
- Browse, extract, and rebuild ext4 images.
- Inspect/extract Android boot images and edit gzip/cpio ramdisks.
- Inspect and sign AVB/vbmeta through `avbtool`.
- Validate image boundaries, metadata, formats, and SHA-256 hashes.
- Create ROM project manifests, safe workspaces, binary/text diffs, and OTA ZIPs.
- Analyze boot/crash logs and collect ADB/Fastboot device profiles.
- Warning-gated raw editing with backup and output hashing.
- Japanese and English UI strings stored in editable JSON files.

### 日本語

- raw / Android sparseイメージの判定・展開
- `super.img`のメタデータ解析とdynamic partition向けツール連携
- `payload.bin`の解析・展開
- ext4イメージの閲覧・抽出・再構築
- Android boot imageの解析・抽出、gzip/cpio ramdisk編集
- `avbtool`によるAVB/vbmeta解析・署名連携
- イメージ境界・メタデータ・形式・SHA-256検証
- ROMプロジェクト管理、作業コピー、差分比較、OTA ZIP作成
- boot/crashログ解析、ADB/Fastboot端末プロファイル取得
- 警告・バックアップ付きraw編集
- JSONファイルで変更できる日本語/英語UI

The application never writes to the source image. Rebuild operations produce a new output file.

本ソフトは元イメージを直接変更しません。再構築操作では常に新しい出力ファイルを作成します。

## Run / 起動方法

### English

```powershell
python -m pip install -e .
python -m android_image_tool
```

The GUI is also available with:

```powershell
android-image-tool-gui
```

Use the **Open image** button to inspect an image. For ext4 editing, choose **Extract all**, modify the extracted staging directory, then choose **Rebuild ext4**.

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

「イメージを開く」で解析対象を選択します。ext4を編集する場合は「すべて展開」で作業フォルダーへ展開し、ファイルを変更してから「ext4を再構築」を実行してください。

### English: Raw editing and CLI

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

### 日本語: raw編集とCLI

logoなどのvendor固有rawイメージは、GUIの**rawバイトを編集**を使用してください。元ファイルは直接変更せず、新しい出力イメージを作成し、`<元ファイル>.bak`を一度だけ作成します。バイト範囲を検証し、出力SHA-256を表示します。raw編集は危険なため必ず確認ダイアログが表示されます。flash前に端末メーカーや開発環境のツールで検証してください。

ROM開発向けCLIコマンドは、上記の英語セクションと同じです。ADB/FastbootはAndroid SDK Platform-Toolsの導入が必要です。partitionバックアップはroot化済み端末が必要で、`adb exec-out`を使用します。flashコマンドは実行しません。

ramdisk編集では現在、ramdiskの内容とパスを保持して展開・再梱包しますが、boot image全体のheaderやchecksumを自動再構築する処理は別途必要です。対応するboot imageツールで置き換え、flash前にAVBを検証してください。

## Notes / 注意事項

### English

EROFS can be detected and inspected at the filesystem signature level, but writing EROFS is intentionally not enabled. `mke2fs` is required for ext4 rebuild; the app searches `PATH` and common Android platform-tool locations.

The GUI log is written to `%USERPROFILE%\\.android-image-tool.log` on Windows and `~/.android-image-tool.log` on Linux/macOS. Never flash an image without a verified backup and a matching AVB/signing workflow.

### 日本語

EROFSはファイルシステム署名の検出・基本確認に対応していますが、EROFSへの書き込みは安全のため無効化しています。ext4再構築には`mke2fs`が必要で、アプリは`PATH`と一般的なPlatform-Tools配置を検索します。

GUIログはWindowsでは`%USERPROFILE%\\.android-image-tool.log`、Linux/macOSでは`~/.android-image-tool.log`に保存されます。flash前には必ずバックアップとAVB/署名手順を確認してください。

![Android Image Tool](assets/logo.png)

## Documentation / ドキュメント

- [English guide](docs/README-en.md)
- [日本語ガイド](docs/README-ja.md)
- [English FAQ](docs/FAQ-en.md)
- [よくある質問（日本語）](docs/FAQ-ja.md)

## Disclaimer / 免責事項

### English

This software is provided for research, education, and custom-ROM development. Image modification, AVB changes, bootloader operations, and device recovery may permanently damage a device, erase data, void a warranty, or make software unable to boot. You are responsible for backups, licenses, signing keys, device compatibility, and every command you execute. The authors and contributors provide no warranty and accept no liability for data loss, device damage, security issues, or legal consequences.

### 日本語

本ソフトは研究、教育、カスタムROM開発を目的として提供されます。イメージ編集、AVB変更、ブートローダー操作、端末への書き込みは、端末の破損、データ消失、保証無効化、起動不能を招く可能性があります。バックアップ、ライセンス、署名鍵、端末互換性、実行するコマンドの確認は利用者の責任です。作者および貢献者は保証を行わず、データ消失、端末破損、セキュリティ問題、法的な結果について責任を負いません。

## Tools / 使用ツール

### English

- Python and PySide6 — application runtime and GUI
- Android SDK Platform-Tools (`adb`, `fastboot`) — device inspection and backup
- `mke2fs` — ext4 image creation
- `avbtool` — AVB/vbmeta operations
- `mkbootimg` — Android boot image creation
- `lpunpack` — dynamic partition extraction
- `mkfs.erofs` / EROFS tools — EROFS image operations
- `payload-dumper-go` or compatible payload tools — OTA payload extraction

External tools are optional and are only required for the related features. Their licenses and terms remain applicable.

### 日本語

- Python / PySide6 — アプリ本体とGUI
- Android SDK Platform-Tools（`adb`、`fastboot`） — 端末情報取得・バックアップ
- `mke2fs` — ext4イメージ作成
- `avbtool` — AVB/vbmeta処理
- `mkbootimg` — Android boot image作成
- `lpunpack` — dynamic partition展開
- `mkfs.erofs` / EROFS tools — EROFSイメージ処理
- `payload-dumper-go`など — OTA payload展開

外部ツールは該当機能を使う場合だけ必要です。各ツールのライセンスと利用規約が優先されます。

## Credits / クレジット

### English

Android Image Tool is maintained by **kagithu** with assistance from **GitHub Copilot**. It builds on the Android Open Source Project ecosystem, Android SDK Platform-Tools, Linux filesystem tooling, PySide6/Qt, and the upstream projects listed above. The app icon is the user-provided artwork stored at [`assets/logo.png`](assets/logo.png).

### 日本語

Android Image Toolは**kagithu**が開発・管理し、**GitHub Copilot**の支援を受けています。Android Open Source Project、Android SDK Platform-Tools、Linux filesystem tools、PySide6/Qt、および上記の各上流プロジェクトを活用しています。アプリアイコンは利用者提供の画像を[`assets/logo.png`](assets/logo.png)として使用しています。

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
