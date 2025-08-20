# archfinn/parser/ast.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Node:
    id: str
    type: str
    state: str
    controls: List[str] = field(default_factory=list)
    attrs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    from_id: str
    to_id: str
    protocol: Optional[str] = None
    attrs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Control:
    id: str
    effectiveness: Dict[str, float]
    bypass_conditions: List[str] = field(default_factory=list)

@dataclass
class ScenarioStep:
    id: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Scenario:
    name: str
    steps: List[ScenarioStep]
    timeline: Dict[str, Any] = field(default_factory=dict)