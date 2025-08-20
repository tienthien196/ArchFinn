# archfinn/sdk/api.py
from pathlib import Path
from typing import Dict, Any
from ..parser.parser import parser
from ..core.engine import ArchState, run_scenario


def load(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = parser.parse(source)
    return {"ast": tree, "source": source, "path": path}


def run(file_path: str, scenario_name: str = None) -> Dict[str, Any]:
    data = load(file_path)
    ast = data["ast"]

    # Hỗ trợ AST là list hoặc single scenario
    scenarios = ast if isinstance(ast, list) else [ast]
    scenario = None

    for item in scenarios:
        if hasattr(item, "name") and (scenario_name is None or item.name == scenario_name):
            scenario = item
            break

    if scenario is None:
        raise ValueError(f"Không tìm thấy scenario: {scenario_name}")

    state = ArchState(nodes={}, edges=[], controls={})
    result = run_scenario(state, scenario)
    return result


def export(file_path: str, format: str = "json") -> Any:
    data = load(file_path)
    if format == "json":
        import json
        return json.dumps({"model": str(data['ast'])}, indent=2, ensure_ascii=False)
    return data