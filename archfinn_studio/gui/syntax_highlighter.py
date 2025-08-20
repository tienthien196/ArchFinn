# gui/syntax_highlighter.py
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt

class AfinnHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formats = {}

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "SCENARIO", "SIMULATION", "STEP", "action", "target", "on_success",
            "on_fail", "on_detect", "next", "end", "goto", "timeline", "max_steps",
            "tick_delay", "ARCHFINN", "META", "STRUCTURE", "BEHAVIOR"
        ]
        for kw in keywords:
            self.formats[kw] = keyword_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.formats["string"] = string_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF8000"))
        self.formats["number"] = number_format

    def highlightBlock(self, text):
        for word, fmt in self.formats.items():
            if word in ["string"]:
                continue
            start = text.find(word)
            while start != -1:
                length = len(word)
                self.setFormat(start, length, fmt)
                start = text.find(word, start + length)

        # Highlight strings
        import re
        for match in re.finditer(r'"[^"]*"', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats["string"])

        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats["number"])