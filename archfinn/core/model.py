# archfinn/core/model.py
from dataclasses import dataclass, field
from typing import Dict, List, Any
from typing import Optional

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
class Vulnerability:
    id: str
    node: str
    type: str
    base_success: float
    post_actions: List[dict] = field(default_factory=list)

@dataclass
class Detector:
    id: str
    on: List[str]
    where: Dict[str, Any]
    detect_prob: float
    emit: List[str]

@dataclass
class Response:
    id: str
    when: str
    actions: List[dict]

@dataclass
class Actor:
    id: str
    role: str
    capabilities: List[str] = field(default_factory=list)