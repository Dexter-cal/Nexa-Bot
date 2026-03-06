"""
Native Desktop GUI for EPEX APEX v5.0
Built with PyQt6 for a professional, high-performance experience.
"""

import sys
import os
import json
import psutil
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QLineEdit, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem, QProgressBar, QStatusBar, QMenu,
    QApplication, QSystemTrayIcon, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QAction

class NexaNativeGUI(QMainWindow):
    """Main Native GUI Window for EPEX"""

    def __init__(self):
        super().__init__()

        # Load config path
        self.config_path = os.path.expanduser('~/.epex/config.enc')
        self.current_view = 'chat'

        self.init_ui()
        self.setup_timers()
        # Tray might fail in headless, wrap it
        try:
            self.setup_tray()
        except: pass

    def init_ui(self):
        """Initialize high-fidelity UI layout"""
        self.setWindowTitle('EPEX APEX v5.0 — Neural OS Dashboard')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 600)

        self.apply_dark_theme()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Left Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # 2. Center Content Area (Dynamic)
        content = self.create_content_area()
        main_layout.addWidget(content, stretch=1)

        # 3. Right Status Panel
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('System Optimal')
        self.create_menu_bar()

    def apply_dark_theme(self):
        """EPEX Signature Dark Theme Styling"""
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0e1a; }
            QPushButton {
                background-color: #1a2236;
                border: 1px solid #1e2d47;
                border-radius: 8px;
                padding: 10px 16px;
                color: #e2e8f0;
            }
            QPushButton:hover { border-color: #00e5ff; background-color: #1e2d47; }
            QPushButton#primary { background-color: #00e5ff; color: #0a0e1a; font-weight: bold; }
            QLineEdit, QTextEdit {
                background-color: #111827;
                border: 1px solid #1e2d47;
                border-radius: 8px;
                padding: 10px;
                color: #e2e8f0;
            }
            QProgressBar {
                border: 1px solid #1e2d47;
                border-radius: 6px;
                background-color: #111827;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #b2f24d);
                border-radius: 5px;
            }
            QListWidget { background-color: #111827; border: none; border-radius: 8px; }
            QListWidget::item { padding: 12px; border-radius: 6px; }
            QListWidget::item:selected { background-color: rgba(0, 229, 255, 0.1); border-left: 3px solid #00e5ff; }
        """)

    def create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("background-color: #0b0d14; border-right: 1px solid #1e2d47;")
        layout = QVBoxLayout(sidebar)

        logo = QLabel('EPEX')
        logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #00e5ff; letter-spacing: 2px; padding: 20px;")
        layout.addWidget(logo)

        # Nav Buttons
        self.nav_buttons = []
        nav_items = [
            ('💬', 'Neural Chat', 0),
            ('🤖', 'Swarm Manager', 1),
            ('🛡️', 'Privacy Guardian', 2),
            ('🔑', 'API Vault', 3),
            ('📋', 'Workflows', 4),
            ('📊', 'Audit Logs', 5),
            ('⚙️', 'Settings', 6),
        ]

        for icon, label, idx in nav_items:
            btn = QPushButton(f'{icon}  {label}')
            btn.setStyleSheet("text-align: left; padding: 12px 20px; border: none; font-size: 14px;")
            btn.clicked.connect(lambda checked, i=idx: self.switch_view(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()
        return sidebar

    def create_content_area(self) -> QStackedWidget:
        self.content_stack = QStackedWidget()

        # Add Views (Placeholders for now)
        self.chat_view = self.create_chat_view()
        self.content_stack.addWidget(self.chat_view)

        self.agents_view = self.create_view_header("Swarm Manager", "#b2f24d")
        self.content_stack.addWidget(self.agents_view)

        self.privacy_view = self.create_view_header("Privacy Guardian", "#ef4444")
        self.content_stack.addWidget(self.privacy_view)

        self.keys_view = self.create_view_header("API Vault", "#00e5ff")
        self.content_stack.addWidget(self.keys_view)

        self.workflow_view = self.create_view_header("Workflows", "#9b5de5")
        self.content_stack.addWidget(self.workflow_view)

        self.logs_view = self.create_view_header("Audit Logs", "#ffffff")
        self.content_stack.addWidget(self.logs_view)

        self.settings_view = self.create_view_header("System Settings", "#64748b")
        self.content_stack.addWidget(self.settings_view)

        return self.content_stack

    def create_view_header(self, title: str, color: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        h = QLabel(title)
        h.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color}; padding: 20px;")
        l.addWidget(h)
        l.addStretch()
        return w

    def create_chat_view(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(20, 20, 20, 20)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #0b0d14; border: 1px solid #1e2d47; border-radius: 12px; padding: 15px;")
        l.addWidget(self.chat_display)

        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Direct interface with Epex...")
        self.chat_input.setFixedHeight(50)
        input_row.addWidget(self.chat_input)

        send_btn = QPushButton("SEND")
        send_btn.setObjectName("primary")
        send_btn.setFixedSize(100, 50)
        input_row.addWidget(send_btn)

        l.addLayout(input_row)
        return w

    def create_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(260)
        panel.setStyleSheet("background-color: #0b0d14; border-left: 1px solid #1e2d47;")
        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("SYSTEM METRICS"))

        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0.0 GB")
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)

        layout.addSpacing(20)
        layout.addWidget(QLabel("INTELLIGENCE"))
        self.model_label = QLabel("Auto-Routing: Active")
        layout.addWidget(self.model_label)

        layout.addStretch()
        return panel

    def switch_view(self, index: int):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet("text-align: left; padding: 12px 20px; border: none; background-color: rgba(0,229,255,0.1); border-left: 3px solid #00e5ff;")
            else:
                btn.setStyleSheet("text-align: left; padding: 12px 20px; border: none;")

    def setup_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().used / (1024**3)
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram:.1f} GB")

    def create_menu_bar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        # Placeholder icon
        self.tray.setIcon(QIcon())
        self.tray.show()

def run_native_gui():
    app = QApplication(sys.argv)
    app.setApplicationName("EPEX APEX")
    window = NexaNativeGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_native_gui()
