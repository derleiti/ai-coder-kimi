"""Hauptfenster fuer ai-coder GUI — Tabs: Chat + Settings."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut

from .chat_widget import ChatWidget
from .settings_widget import SettingsWidget
from .theme import APP_STYLESHEET


def _ensure_kimi_model_silently() -> None:
    """Modell auf Kimi K3 pinnen, falls noch keins gewählt ist.

    Best-effort: ohne gültige Session (z.B. vor dem ersten Login) oder bei
    Netzwerkfehlern einfach überspringen — die Chat-Tab zeigt in dem Fall
    ohnehin den normalen Verbindungsfehler an, nur eben nicht mehr mit
    model=None ("[chat/default]") gegen einen unbekannten Backend-Default.
    """
    try:
        from ..config import load_session
        from ..kimi import ensure_kimi_model
        session = load_session()
        ensure_kimi_model(session)
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        _ensure_kimi_model_silently()
        self.tray = None  # wird von app.py gesetzt
        self.setWindowTitle("ai-coder-kimi")
        self.setMinimumSize(QSize(720, 540))
        self.resize(940, 720)

        self._apply_style()

        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 12, 14, 14)
        root_layout.setSpacing(10)

        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(14, 8, 14, 8)
        mark = QLabel(">_")
        mark.setObjectName("BrandMark")
        brand = QLabel("ai-coder-kimi")
        brand.setObjectName("Brand")
        caption = QLabel("AILinux coding agent · Kimi K3")
        caption.setObjectName("Caption")
        shortcut_hint = QLabel("Ctrl+1 Chat   Ctrl+2 Settings   Ctrl+K Prompt")
        shortcut_hint.setObjectName("Caption")
        top_layout.addWidget(mark)
        top_layout.addWidget(brand)
        top_layout.addWidget(caption)
        top_layout.addStretch()
        top_layout.addWidget(shortcut_hint)
        root_layout.addWidget(top_bar)

        self.tabs = QTabWidget()
        self.settings_tab = SettingsWidget()
        self.chat_tab = ChatWidget(settings_ref=self.settings_tab)

        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.settings_tab, "Settings")
        root_layout.addWidget(self.tabs, stretch=1)
        self.setCentralWidget(root)

        self._shortcuts = [
            QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.tabs.setCurrentIndex(0)),
            QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.tabs.setCurrentIndex(1)),
            QShortcut(QKeySequence("Ctrl+,"), self, activated=lambda: self.tabs.setCurrentIndex(1)),
        ]

    def _apply_style(self):
        self.setStyleSheet(APP_STYLESHEET)

    def closeEvent(self, event):
        """Minimize to tray statt schliessen."""
        if self.tray and self.tray.isVisible():
            self.hide()
            self.tray.showMessage(
                "ai-coder-kimi",
                "Minimiert in die Taskleiste. Klick zum Oeffnen.",
                self.tray.MessageIcon.Information,
                2000,
            )
            event.ignore()
        else:
            event.accept()

    def show_and_raise(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
