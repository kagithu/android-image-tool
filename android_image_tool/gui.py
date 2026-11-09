from __future__ import annotations

import tempfile
import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPlainTextEdit, QPushButton, QComboBox, QVBoxLayout, QWidget, QInputDialog,
)

from .android import parse_payload, parse_super
from .avb import parse_vbmeta
from .boot import parse_boot
from .devices import AndroidTools
from .editing import patch_binary
from .ext4 import Ext4Image, rebuild_ext4
from .formats import detect_format
from .i18n import LANG
from .sparse import is_sparse, unsparse

logging.basicConfig(
    filename=Path.home() / ".android-image-tool.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.image: Path | None = None
        self.lang = "ja"
        self.temp_dir = Path(tempfile.mkdtemp(prefix="android-image-tool-"))
        self.open_button = QPushButton()
        self.extract_button = QPushButton()
        self.rebuild_button = QPushButton()
        self.raw_edit_button = QPushButton()
        self.device_button = QPushButton()
        self.logcat_button = QPushButton()
        self.language = QComboBox()
        self.language.addItem("日本語", "ja")
        self.language.addItem("English", "en")
        self.language.currentIndexChanged.connect(self.change_language)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        row = QHBoxLayout()
        row.addWidget(self.open_button)
        row.addWidget(self.extract_button)
        row.addWidget(self.rebuild_button)
        row.addWidget(self.raw_edit_button)
        row.addWidget(self.device_button)
        row.addWidget(self.logcat_button)
        row.addWidget(QLabel("Language / 言語"))
        row.addWidget(self.language)
        layout = QVBoxLayout()
        layout.addLayout(row)
        layout.addWidget(self.details)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)
        self.open_button.clicked.connect(self.open_image)
        self.extract_button.clicked.connect(self.extract_all)
        self.rebuild_button.clicked.connect(self.rebuild)
        self.raw_edit_button.clicked.connect(self.edit_raw)
        self.device_button.clicked.connect(self.show_devices)
        self.logcat_button.clicked.connect(self.capture_logcat)
        self.refresh_text()

    def tr(self, key: str, **values: object) -> str:
        return LANG[self.lang][key].format(**values)

    def refresh_text(self) -> None:
        self.setWindowTitle(self.tr("title"))
        self.open_button.setText(self.tr("open"))
        self.extract_button.setText(self.tr("extract"))
        self.rebuild_button.setText(self.tr("rebuild"))
        self.raw_edit_button.setText(self.tr("raw_edit"))
        self.device_button.setText(self.tr("devices"))
        self.logcat_button.setText(self.tr("logcat"))

    def change_language(self) -> None:
        self.lang = self.language.currentData()
        self.refresh_text()

    def open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("open"), "", "Images (*.img *.bin);;All files (*)")
        if not filename:
            return
        path = Path(filename)
        try:
            info = detect_format(path)
            lines = [f"{info.format}\n{info.details}\nSize: {info.size:,} bytes"]
            if is_sparse(path):
                raw_path = self.temp_dir / f"{path.stem}.raw"
                unsparse(path, raw_path)
                lines.append(f"Sparse expanded size: {raw_path.stat().st_size:,} bytes")
            elif info.format == "ext4":
                with Ext4Image(path) as image:
                    lines.extend([f"Block size: {image.block_size}", f"Label: {image.label}"])
                    lines.extend(image.list_dir()[:500])
            elif info.format == "super.img":
                value = parse_super(path)
                lines.append(f"LP metadata: {value.major}.{value.minor}, size={value.metadata_size}")
            elif info.format == "payload.bin":
                value = parse_payload(path)
                lines.append(f"Payload version: {value.version}, manifest={value.manifest_size}")
            elif info.format == "Android boot image":
                lines.append(str(parse_boot(path)))
            elif info.format == "AVB vbmeta":
                lines.append(str(parse_vbmeta(path)))
            self.image = path
            self.details.setPlainText("\n".join(lines))
        except Exception as error:
            self.show_error(error)

    def extract_all(self) -> None:
        if not self.image:
            QMessageBox.warning(self, self.tr("title"), self.tr("choose"))
            return
        output = QFileDialog.getExistingDirectory(self, self.tr("extract"))
        if not output:
            return
        try:
            with Ext4Image(self.image) as image:
                count = 0
                for entry in image.list_dir():
                    if not entry.endswith("/"):
                        try:
                            image.extract(entry, Path(output) / entry.lstrip("/"))
                            count += 1
                        except (FileNotFoundError, IsADirectoryError, ValueError):
                            continue
            self.details.appendPlainText(f"\nExtracted files: {count}")
        except Exception as error:
            self.show_error(error)

    def rebuild(self) -> None:
        staging = QFileDialog.getExistingDirectory(self, self.tr("rebuild"))
        if not staging:
            return
        output, _ = QFileDialog.getSaveFileName(self, self.tr("rebuild"), "", "Image (*.img)")
        if not output:
            return
        size_text, ok = self._size_dialog()
        if not ok:
            return
        try:
            rebuild_ext4(Path(staging), Path(output), int(size_text) * 1024 * 1024)
            self.details.appendPlainText("\n" + self.tr("saved", path=output))
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.critical(self, self.tr("title"), str(error))

    def _size_dialog(self) -> tuple[str, bool]:
        return QInputDialog.getText(self, self.tr("rebuild"), "Output size (MiB):", text="2048")

    def edit_raw(self) -> None:
        if not self.image:
            QMessageBox.warning(self, self.tr("title"), self.tr("choose"))
            return
        warning = QMessageBox.warning(
            self,
            self.tr("warning"),
            self.tr("warning_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if warning != QMessageBox.StandardButton.Yes:
            return
        offset_text, ok = QInputDialog.getText(self, self.tr("raw_edit"), self.tr("offset"), text="0x0")
        if not ok:
            return
        hex_text, ok = QInputDialog.getText(self, self.tr("raw_edit"), self.tr("hex"))
        if not ok:
            return
        output, _ = QFileDialog.getSaveFileName(
            self, self.tr("output"), str(self.image.with_name(self.image.stem + "-edited" + self.image.suffix)),
            "Images (*.img *.bin);;All files (*)",
        )
        if not output:
            return
        try:
            offset = int(offset_text.strip(), 0)
            replacement = bytes.fromhex(hex_text)
            result = patch_binary(self.image, Path(output), offset, replacement)
            backup = self.tr("backup", path=result.backup)
            self.details.appendPlainText("\n" + self.tr(
                "patched", offset=result.offset, length=result.length, sha256=result.sha256, backup=backup,
            ))
        except (OSError, ValueError) as error:
            self.show_error(error)

    def show_error(self, error: Exception) -> None:
        logging.error(
            "Operation failed: %s",
            error,
            exc_info=(type(error), error, error.__traceback__),
        )
        QMessageBox.critical(self, self.tr("title"), str(error) or self.tr("unexpected"))

    def show_devices(self) -> None:
        try:
            tools = AndroidTools()
            self.details.appendPlainText(
                "\nADB:\n" + tools.adb_devices() + "\nFastboot:\n" + tools.fastboot_devices(),
            )
        except Exception as error:
            self.show_error(error)

    def capture_logcat(self) -> None:
        output, _ = QFileDialog.getSaveFileName(self, "Save logcat", "logcat.txt", "Text (*.txt)")
        if not output:
            return
        try:
            text = AndroidTools().logcat(Path(output))
            self.details.appendPlainText(f"\nSaved logcat: {output}\nLines: {len(text.splitlines())}")
        except Exception as error:
            self.show_error(error)


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(900, 600)
    window.show()
    app.exec()
