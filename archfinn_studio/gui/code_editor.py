# gui/code_editor.py
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont
from .syntax_highlighter import AfinnHighlighter

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 10))
        self.highlighter = AfinnHighlighter(self.document())