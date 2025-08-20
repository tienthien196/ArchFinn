# ArchFinn Studio (v3.1)

    +---------------------------------------------+
    |           ArchFinn Studio (GUI)             |
    |  +------------------+  +------------------+ |
    |  |   Code Editor    |  |   Graph Viewer   | |
    |  | (Syntax Highlight|  | (Interactive     | |
    |  |   + Autocomplete)|  |   D3-like View)  | |
    |  +------------------+  +------------------+ |
    |  +------------------+  +------------------+ |
    |  |   Simulation     |  |   Log Timeline   | |
    |  | (Play/Pause/Step)|  | (Click to inspect| |
    |  +------------------+  +------------------+ |
    |                                             |
    |  ← Giao diện bằng PySide6 / DearPyGui       |
    +----------------------+----------------------+
                        ↓
            [ArchFinn Core Engine (Python)]
            ← parser, engine, model, sdk
                        ↓
            [Plugin System] ← Gọi Python module
            [networkx] ← Vẽ đồ thị, tính toán path
            [matplotlib/pyqtgraph] ← Visualize