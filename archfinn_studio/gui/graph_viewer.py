# archfinn_studio/gui/graph_viewer.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QObject
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import networkx as nx
import threading
import re
from archfinn.core.engine import ArchState, run_scenario
from archfinn.parser.parser import parse_file

class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(8, 6))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.ax.axis('off')

class GraphViewer(QWidget):
    # Signals để MainWindow bắt và đổ vào LogPanel / highlight
    log_emitted = Signal(str)
    step_changed = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.canvas = GraphCanvas()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.G = nx.DiGraph()
        self.scenario = None

        # runtime flags
        self._thread = None
        self._paused = False
        self._stop = False
        self._step_token = False

    # ----------------------- LOAD & DRAW -----------------------
    def load_from_editor(self, code: str, file_path: str | None = None):
        try:
            ast = parse_file(file_path) if file_path else None
            scenario = ast[0] if isinstance(ast, list) else ast
            if scenario is None:
                raise ValueError("No scenario parsed")

            G = nx.DiGraph()
            for step in scenario.steps:
                action = step.action
                color = "#2E8B57"
                if action == "exploit": color = "#DC143C"
                elif action == "move_lateral": color = "#4169E1"
                elif action == "exfiltrate": color = "#FF8C00"

                G.add_node(step.id, label=step.id, color=color, action=action)

                for key, edge_color in zip(
                    ["on_success", "on_fail", "on_detect", "next"],
                    ["#32CD32", "#FF4500", "#FFD700", "#808080"]
                ):
                    jump = step.params.get(key)
                    if jump and isinstance(jump, tuple) and jump[0] == "goto":
                        G.add_edge(step.id, jump[1], color=edge_color, style="solid", key=key)

            self.G = G
            self.scenario = scenario
            self.draw_graph()
        except Exception as e:
            self.log_emitted.emit(f"[UI] Parse error: {e}")
            self.G = nx.DiGraph()
            self.scenario = None
            self.draw_graph()

    def draw_graph(self, highlight: str | None = None):
        ax = self.canvas.ax
        ax.clear()
        ax.axis('off')

        if not self.G.nodes:
            ax.text(0.5, 0.5, "No scenario loaded", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        pos = nx.spring_layout(self.G, k=3, iterations=50)
        edge_colors = [self.G[u][v].get('color', 'gray') for u, v in self.G.edges]
        base_colors = [self.G.nodes[n].get('color', 'gray') for n in self.G.nodes]
        node_colors = [('#FFFF00' if n == highlight else base_colors[i]) for i, n in enumerate(self.G.nodes)]

        nx.draw(self.G, pos, ax=ax, with_labels=True,
                node_color=node_colors, edge_color=edge_colors,
                node_size=900, font_size=10, font_color='white', font_weight='bold',
                alpha=0.95, edgecolors='black', linewidths=1.5)
        self.canvas.draw()

    # ----------------------- RUNTIME -----------------------
    def _on_log(self, line: str):
        self.log_emitted.emit(line)
        # tự động detect "Executing step Sx" để highlight
        m = re.search(r"Executing step\s+(S\w+)", line)
        if m:
            sid = m.group(1)
            self.step_changed.emit(sid)
            self.draw_graph(highlight=sid)

    def _should_pause(self) -> bool:
        # nếu đang paused nhưng có token step thì cho đi qua 1 step
        if self._paused and self._step_token:
            # consume token ngay trước khi thực thi step
            self._step_token = False
            return False
        return self._paused

    def _should_stop(self) -> bool:
        return self._stop

    def run_simulation(self, code: str, file_path: str | None):
        if not self.scenario:
            self.load_from_editor(code, file_path)
        if not self.scenario:
            self.log_emitted.emit("[UI] No scenario to run")
            return

        if self._thread and self._thread.is_alive():
            self.log_emitted.emit("[UI] Simulation already running")
            return

        self._paused = False
        self._stop = False
        self._step_token = False

        def worker():
            state = ArchState(nodes={}, edges=[], controls={})
            state.on_log = self._on_log
            result = run_scenario(
                state, self.scenario,
                on_step_start=lambda s, st: None,
                should_pause=self._should_pause,
                should_stop=self._should_stop,
            )
            self.finished.emit(result)

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def pause_simulation(self):
        self._paused = True
        self.log_emitted.emit("[UI] Paused")

    def step_simulation(self):
        # bật pause nếu chưa, cấp 1 token để đi 1 bước
        self._paused = True
        self._step_token = True
        self.log_emitted.emit("[UI] Step → advance one iteration")

    def reset_simulation(self):
        self._stop = True
        self._paused = False
        self._step_token = False
        self.log_emitted.emit("[UI] Reset requested. If running, it will stop soon…")
