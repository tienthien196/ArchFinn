# archfinn_studio/gui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from archfinn_studio.gui.code_editor import CodeEditor
from archfinn_studio.gui.graph_viewer import GraphViewer
from archfinn_studio.gui.log_panel import LogPanel
from archfinn_studio.gui.simulation_control import SimulationControl
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchFinn Studio v3.1")
        self.resize(1400, 900)

        self.current_file = None

        # Components
        self.editor = CodeEditor()
        self.graph_viewer = GraphViewer()
        self.log_panel = LogPanel()
        self.control_panel = SimulationControl()

        # Layout left/right
        left_side = QWidget(); left_layout = QVBoxLayout(left_side)
        left_layout.addWidget(self.editor)
        left_layout.addWidget(self.control_panel)

        right_side = QWidget(); right_layout = QVBoxLayout(right_side)
        right_layout.addWidget(self.graph_viewer)
        right_layout.addWidget(self.log_panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_side)
        splitter.addWidget(right_side)
        splitter.setSizes([600, 800])
        self.setCentralWidget(splitter)

        # Signals từ control panel
        self.control_panel.run_clicked.connect(self.on_run)
        self.control_panel.pause_clicked.connect(self.on_pause)
        self.control_panel.step_clicked.connect(self.on_step)
        self.control_panel.reset_clicked.connect(self.on_reset)

        # Signals từ graph viewer → log panel & UI
        self.graph_viewer.log_emitted.connect(self.log_panel.addItem)
        self.graph_viewer.step_changed.connect(self.graph_viewer.draw_graph)
        self.graph_viewer.finished.connect(self.on_finished)

        self.setup_menu()

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        open_action = file_menu.addAction("Open .afinn")
        open_action.triggered.connect(self.open_file)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open ArchFinn Script", "", "ArchFinn Files (*.afinn)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file = path
            self.setWindowTitle(f"ArchFinn Studio – {Path(path).name}")
            self.graph_viewer.load_from_editor(content, path)
            self.log_panel.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open file: {e}")

    # -------- Controls
    def on_run(self):
        code = self.editor.toPlainText()
        self.graph_viewer.run_simulation(code, self.current_file)

    def on_pause(self):
        self.graph_viewer.pause_simulation()

    def on_step(self):
        self.graph_viewer.step_simulation()

    def on_reset(self):
        self.graph_viewer.reset_simulation()

    def on_finished(self, result: dict):
        self.log_panel.addItem(f"[UI] Finished: result={result.get('result')}")
