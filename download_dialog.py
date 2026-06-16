import os
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QMessageBox
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import QObject, Signal, QThread, Qt
from i18n import t
from update_manager import download_update


class DownloadWorker(QObject):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            def report(downloaded, total):
                if self._cancelled:
                    raise Exception("cancelled")
                pct = int(downloaded * 100 / total) if total > 0 else 0
                self.progress.emit(pct)
            download_update(self.url, self.dest, report)
            if not self._cancelled:
                self.finished.emit(self.dest)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))


class DownloadDialog(QDialog):
    def __init__(self, url, dest, version, lang, parent=None):
        super().__init__(parent)
        self.url = url
        self.dest = dest
        self.version = version
        self.lang = lang
        self.worker = None
        self.thread = None
        self._finished = False
        self._setup_ui()
        self._start_download()

    def _setup_ui(self):
        self.setWindowTitle(t("dl_title", self.lang))
        self.setFixedSize(400, 140)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.label = QLabel(t("dl_status", self.lang).format(latest=self.version))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton(t("cancel", self.lang))
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _start_download(self):
        self.thread = QThread()
        self.worker = DownloadWorker(self.url, self.dest)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.thread.start()

    def _cleanup(self):
        try:
            if os.path.exists(self.dest):
                os.remove(self.dest)
        except Exception:
            pass

    def _on_cancel(self):
        reply = QMessageBox.question(
            self,
            t("dl_title", self.lang),
            t("dl_cancel_confirm", self.lang),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if self.worker:
            self.worker.cancel()
        self._cleanup()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)
        self.reject()

    def _on_finished(self, path):
        self._finished = True
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)
        self.accept()

    def _on_error(self, msg):
        self._finished = True
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)
        self._cleanup()
        QMessageBox.critical(
            self,
            t("settings_title", self.lang),
            t("dl_error", self.lang).format(error=msg)
        )
        self.reject()

    def closeEvent(self, event):
        if not self._finished:
            event.ignore()
            self._on_cancel()
        else:
            event.accept()
