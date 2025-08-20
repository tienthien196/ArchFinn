# gui/simulation_control.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal

class SimulationControl(QWidget):
    run_clicked = Signal()
    pause_clicked = Signal()
    step_clicked = Signal()
    reset_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        self.btn_run = QPushButton("▶️ Run")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_step = QPushButton("⏭ Step")
        self.btn_reset = QPushButton("⏮ Reset")

        self.btn_run.clicked.connect(self.run_clicked.emit)
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        self.btn_step.clicked.connect(self.step_clicked.emit)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)

        layout.addWidget(self.btn_run)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_step)
        layout.addWidget(self.btn_reset)
        self.setLayout(layout)