# archfinn_studio/main.py
"""
ArchFinn Studio v3.1 – Desktop IDE for ArchFinn Script
"""
import sys
from PySide6.QtWidgets import QApplication
from archfinn_studio.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ArchFinn Studio")
    app.setOrganizationName("ArchFinn Team")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()