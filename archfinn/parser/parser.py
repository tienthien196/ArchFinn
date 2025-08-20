# archfinn/parser/parser.py
from lark import Lark, Transformer
from .ast import Node, Edge, Control, ScenarioStep, Scenario
from .grammar import GRAMMAR


def parse_file(file_path):
    """Parse .afinn file và trả về AST."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parser.parse(content)


class AfinnTransformer(Transformer):
    def STRING(self, tok):
        return str(tok)[1:-1]  # bỏ dấu ngoặc kép

    def IDENT(self, tok):
        return str(tok)

    def NUMBER(self, tok):
        val = str(tok)
        return int(val) if '.' not in val else float(val)

    # --- META ---
    def meta_pair(self, args):
        key = args[0]
        value = args[1]
        return (key, value)

    def meta(self, args):
        return dict(args)

    # --- ATTRS ---
    def attr_pair(self, args):
        key = args[0]
        value = args[1]
        return (key, value)

    def value(self, args):
        if len(args) == 1:
            return args[0]
        return list(args)

    # --- NODE ---
    def node_def(self, args):
        name = args[0]
        props = {
            'id': name,
            'type': 'unknown',
            'state': 'secure',
            'controls': [],
            'attrs': {}
        }
        for item in args[1:]:
            if isinstance(item, tuple) and len(item) == 2:
                k, v = item
                props[k] = v
        return Node(**props)

    # --- EDGE ---
    def edge_def(self, args):
        src, dst = args[0], args[1]
        return Edge(from_id=src, to_id=dst)

    # --- CONTROL ---
    def control_def(self, args):
        name = args[0]
        effectiveness = {}
        bypass_conditions = []
        for child in args[1:]:
            if isinstance(child, dict):
                effectiveness = child
            elif isinstance(child, list):
                bypass_conditions = child
        return Control(id=name, effectiveness=effectiveness, bypass_conditions=bypass_conditions)

    # --- SCENARIO/SIMULATION PROPERTIES ---
    def action_prop(self, args):
        return ("action", args[0])

    def attacker_prop(self, args):
        return ("attacker", args[0])

    def target_prop(self, args):
        return ("target", args[0])

    def type_prop(self, args):
        return ("type", args[0])

    def base_success_prop(self, args):
        return ("base_success", args[0])

    def on_success_prop(self, args):
        return ("on_success", args[0])

    def on_fail_prop(self, args):
        return ("on_fail", args[0])

    def from_prop(self, args):
        return ("from", args[0])

    def to_prop(self, args):
        return ("to", args[0])

    def method_prop(self, args):
        return ("method", args[0])

    def rate_prop(self, args):
        return ("rate", args[0])

    def detect_prob_prop(self, args):
        return ("detect_prob", args[0])

    def on_detect_prop(self, args):
        return ("on_detect", args[0])

    def next_prop(self, args):
        return ("next", args[0])

    def data_volume_prop(self, args):
        return ("data_volume", args[0])

    def make_goto(self, args):
        # args là [IDENT] - label sau "goto:"
        return ("goto", str(args[0]))

    def make_end(self, args):
        # args là [IDENT] - label sau "end:"
        return ("end", str(args[0]))

    # --- TIMELINE ---
    def timeline_pairs(self, args):
        result = {}
        i = 0
        while i < len(args) - 1:
            result[args[i]] = args[i + 1]
            i += 2
        return result

    def timeline(self, args):
        return args[0] if args else {}

    # --- STEP ---
    def step(self, args):
        step_id = args[0]
        params = {}
        action = None
        
        for item in args[1:]:
            if isinstance(item, tuple) and len(item) == 2:
                k, v = item
                if k == 'action':
                    action = v
                else:
                    params[k] = v
        
        if action is None:
            raise ValueError(f"Step {step_id} missing 'action' property")
        
        return ScenarioStep(id=step_id, action=action, params=params)

    # --- SCENARIO BODY ---
    def scenario_body(self, args):
        timeline = {}
        steps = []
        
        for item in args:
            if isinstance(item, dict):
                timeline.update(item)
            elif isinstance(item, ScenarioStep):
                steps.append(item)
        
        return (timeline, steps)

    # --- SCENARIO/SIMULATION ---
    def scenario(self, args):
        name = args[0]
        timeline, steps = args[1]
        return Scenario(name=name, steps=steps, timeline=timeline)

    def simulation(self, args):
        name = args[0]
        timeline, steps = args[1]
        # Simulation cũng được xử lý như Scenario
        return Scenario(name=name, steps=steps, timeline=timeline)

    def start(self, args):
        scenarios = []
        for item in args:
            if isinstance(item, Scenario):
                scenarios.append(item)
        return scenarios if len(scenarios) > 1 else (scenarios[0] if scenarios else None)


# ✅ Khởi tạo parser với error handling tốt hơn
parser = Lark(GRAMMAR, parser='lalr', transformer=AfinnTransformer(), keep_all_tokens=False)