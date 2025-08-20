# archfinn/core/engine.py
import random
import time
from typing import Dict, Any, Optional, List
from ..parser.ast import Scenario, ScenarioStep
from dataclasses import dataclass, field

@dataclass
class ArchState:
    nodes: Dict[str, Any]
    edges: list
    controls: Dict[str, Any]
    events: list = field(default_factory=list)
    logs: list = field(default_factory=list)
    tick: int = 0
    rng: random.Random = field(default_factory=lambda: random.Random(1337))

    def log(self, msg: str):
        timestamp = f"[t={self.tick:02d}]"
        self.logs.append(f"{timestamp} {msg}")
        print(f"{timestamp} {msg}")  # Real-time output

    def eff_node(self, node_id: str, kind: str) -> float:
        """Calculate control effectiveness for a node"""
        node = self.nodes.get(node_id)
        if not node or not hasattr(node, 'controls'):
            return 0.0
        prod = 1.0
        for ctrl in node.controls:
            eff = self.controls.get(ctrl, {}).get("effectiveness", {}).get(kind, 0.0)
            prod *= (1.0 - eff)
        return 1.0 - prod

def eval_prob(state: ArchState, kind: str, *, target=None, path=None, base_p=0.5, context=1.0) -> float:
    """Evaluate success probability based on controls and context"""
    if path:
        p_block = 1.0
        for nid in path:
            p_block *= (1.0 - state.eff_node(nid, kind))
    elif target:
        p_block = state.eff_node(target, kind)
    else:
        p_block = 0.0
    return max(0.0, min(1.0, base_p * (1.0 - p_block) * context))

def run_scenario(state: ArchState, scenario: Scenario) -> Dict[str, Any]:
    """Run a scenario simulation with improved logging and error handling"""
    if not scenario.steps:
        return {"result": "no_steps", "logs": ["❌ No steps found in scenario"], "events": []}
    
    steps = {s.id: s for s in scenario.steps}
    current = scenario.steps[0].id
    max_steps = scenario.timeline.get("max_steps", 20)
    tick_delay = scenario.timeline.get("tick_delay", 0.5)
    
    state.log(f"🚀 Running scenario: {scenario.name}")
    state.log(f"📊 Timeline: max_steps={max_steps}, tick_delay={tick_delay}s")
    state.log(f"🎯 Starting from step: {current}")

    for iteration in range(max_steps):
        step = steps.get(current)
        if not step:
            state.log(f"❌ Step not found: {current}")
            break

        state.tick += 1
        action = step.action
        params = step.params
        
        state.log(f"⚡ Executing step {step.id}: {action}")
        
        # Add realistic delay
        if tick_delay > 0:
            time.sleep(tick_delay)

        # Handle different actions
        if action == "exploit":
            target = params.get("target", "unknown")
            exploit_type = params.get("type", "generic")
            base_success = params.get("base_success", 0.5)
            
            p = eval_prob(state, exploit_type, target=target, base_p=base_success)
            success = state.rng.random() < p
            
            emoji = "✅" if success else "❌"
            state.log(f"🎯 Exploit {target} via {exploit_type}: p={p:.2f} → {emoji}")
            
            next_key = "on_success" if success else "on_fail"
            next_val = params.get(next_key)
            
            if next_val and isinstance(next_val, tuple):
                jump_type, label = next_val
                if jump_type == "goto":
                    current = label
                    continue
                elif jump_type == "end":
                    state.log(f"🏁 END: {label.upper()}")
                    return {"result": label, "logs": state.logs, "events": state.events}

        elif action == "move_lateral":
            from_node = params.get("from", "unknown")
            to_node = params.get("to", "unknown")
            move_type = params.get("type", "generic")
            base_success = params.get("base_success", 0.5)
            
            path = [from_node, to_node]
            p = eval_prob(state, move_type, path=path, base_p=base_success)
            success = state.rng.random() < p
            
            emoji = "✅" if success else "❌"
            state.log(f"➡️  Lateral {from_node}→{to_node} via {move_type}: p={p:.2f} → {emoji}")
            
            next_key = "on_success" if success else "on_fail"
            next_val = params.get(next_key)
            
            if next_val and isinstance(next_val, tuple):
                jump_type, label = next_val
                if jump_type == "goto":
                    current = label
                    continue
                elif jump_type == "end":
                    state.log(f"🏁 END: {label.upper()}")
                    return {"result": label, "logs": state.logs, "events": state.events}

        elif action == "exfiltrate":
            detect_prob = params.get("detect_prob", 0.0)
            data_volume = params.get("data_volume", 0)
            
            detected = state.rng.random() < detect_prob
            
            if detected:
                state.events.append("ALERT.EXFIL")
                state.log(f"🚨 Exfiltration detected! ({data_volume} MB)")
                next_val = params.get("on_detect")
                if next_val and isinstance(next_val, tuple):
                    jump_type, label = next_val
                    if jump_type == "end":
                        state.log(f"🏁 END: {label.upper()}")
                        return {"result": label, "logs": state.logs, "events": state.events}
            else:
                state.log(f"💾 Exfiltrating {data_volume} MB... undetected")
                next_val = params.get("on_success")
                if next_val and isinstance(next_val, tuple):
                    jump_type, label = next_val
                    if jump_type == "goto":
                        current = label
                        continue
                    elif jump_type == "end":
                        state.log(f"🏁 END: {label.upper()}")
                        return {"result": label, "logs": state.logs, "events": state.events}

        else:
            state.log(f"⚠️  Unknown action: {action}")
            return {"result": "unknown_action", "logs": state.logs, "events": state.events}

        # Nếu không có jump hợp lệ, kết thúc
        state.log("❌ No valid transition found, ending scenario")
        break

    state.log(f"⏰ Maximum steps ({max_steps}) reached")
    return {"result": "max_steps", "logs": state.logs, "events": state.events}