# archfinn_studio/utils/graph_builder.py
import networkx as nx
from archfinn.parser.parser import parser

# Parse trực tiếp từ source code (không ghi file tạm)

def code_to_nx_graph(code: str):
    try:
        ast = parser.parse(code)
        scenario = ast[0] if isinstance(ast, list) else ast
        if scenario is None:
            return nx.DiGraph(), None

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

        return G, scenario
    except Exception as e:
        print(f"Parse error: {e}")
        return nx.DiGraph(), None
