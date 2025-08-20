# gui/log_panel.py
from PySide6.QtWidgets import QListWidget

class LogPanel(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("font-family: Consolas; font-size: 9pt;")