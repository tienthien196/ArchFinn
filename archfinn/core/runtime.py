# archfinn/core/runtime.py
import random
from typing import Any, Dict, List
from dataclasses import dataclass, field

@dataclass
class EventBus:
    events: List[str] = field(default_factory=list)
    
    def emit(self, event: str):
        self.events.append(event)

@dataclass
class SimulationContext:
    clock: int = 0
    rng: random.Random = field(default_factory=lambda: random.Random(1337))
    event_bus: EventBus = field(default_factory=EventBus)
    facts: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

    def log(self, msg: str):
        self.logs.append(f"[t={self.clock}] {msg}")