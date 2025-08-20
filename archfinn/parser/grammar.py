# archfinn/parser/grammar.py
"""
ArchFinn Script Grammar - FIXED TERMINALS
"""

GRAMMAR = r'''
    ?start: archfinn_header meta? structure? behavior? (scenario | simulation)+

    archfinn_header: "ARCHFINN" STRING

    meta: "META" "{" meta_pair* "}"
    meta_pair: IDENT "=" value

    structure: "STRUCTURE" "{" (node_def | edge_def)* "}"
    node_def: "NODE" IDENT "{" node_prop* "}"
    node_prop: "type" "=" IDENT
             | "state" "=" state_enum
             | "controls" "=" "[" IDENT ("," IDENT)* "]"
             | "attrs" "{" attr_pair* "}"

    attr_pair: IDENT "=" value

    edge_def: "EDGE" IDENT "->" IDENT ("[" edge_prop* "]")?
    edge_prop: IDENT "=" value

    behavior: "BEHAVIOR" "{" (control_def | vuln_def | detector_def | response_def | actor_def)* "}"

    control_def: "CONTROL" IDENT "{" "effectiveness" "=" "{" IDENT "=" NUMBER ("," IDENT "=" NUMBER)* "}" ("bypass_conditions" "=" "[" IDENT ("," IDENT)* "]")? "}"
    vuln_def: "VULN" IDENT "{" "node" "=" IDENT "," "type" "=" IDENT "," "base_success" "=" NUMBER ("post" "=" "{" action_list "}")? "}"
    detector_def: "DETECTOR" IDENT "{" "on" "=" "[" IDENT ("," IDENT)* "]" ("," "where" "=" "{" IDENT "=" value ("," IDENT "=" value)* "}")? "," "detect_prob" "=" NUMBER "," "emit" "=" "[" STRING ("," STRING)* "]" "}"
    response_def: "RESPONSE" IDENT "{" "when" "=" STRING "," "actions" "=" "{" action_list "}" "}"
    actor_def: "ACTOR" IDENT "{" "role" "=" IDENT ("," "capabilities" "=" "[" IDENT ("," IDENT)* "]")? "}"

    // Support both SCENARIO and SIMULATION
    scenario: "SCENARIO" STRING "{" scenario_body "}"
    simulation: "SIMULATION" STRING "{" scenario_body "}"
    
    scenario_body: (timeline? step*)
    timeline: "timeline" "=" "{" timeline_pairs "}"
    timeline_pairs: IDENT "=" value ("," IDENT "=" value)*

    // Fixed step definition - include ALL possible properties
    step: "STEP" IDENT "{" (action_prop | attacker_prop | target_prop | type_prop 
        | base_success_prop | on_success_prop | on_fail_prop | from_prop 
        | to_prop | method_prop | rate_prop | detect_prob_prop 
        | on_detect_prop | next_prop | data_volume_prop)* "}"
    
    # step_prop: action_prop
    #          | attacker_prop
    #          | target_prop
    #          | type_prop
    #          | base_success_prop
    #          | on_success_prop
    #          | on_fail_prop
    #          | from_prop
    #          | to_prop
    #          | method_prop
    #          | rate_prop
    #          | detect_prob_prop
    #          | on_detect_prop
    #          | next_prop
    #          | data_volume_prop

    // --- Step properties ---
    action_prop: "action" "=" value
    attacker_prop: "attacker" "=" value
    target_prop: "target" "=" value
    type_prop: "type" "=" value
    base_success_prop: "base_success" "=" NUMBER
    on_success_prop: "on_success" "=" jump_target
    on_fail_prop: "on_fail" "=" jump_target
    from_prop: "from" "=" value
    to_prop: "to" "=" value
    method_prop: "method" "=" value
    rate_prop: "rate" "=" value
    detect_prob_prop: "detect_prob" "=" NUMBER
    on_detect_prop: "on_detect" "=" jump_target
    next_prop: "next" "=" jump_target
    data_volume_prop: "data_volume" "=" NUMBER

    // Simplified jump targets
    jump_target: "goto" ":" IDENT -> make_goto
               | "end" ":" IDENT -> make_end

    state_enum: "secure" | "vulnerable" | "compromised" | "contained" | "offline"

    action_list: change_state_action | emit_action | action_list "," (change_state_action | emit_action)
    change_state_action: "change_state" "(" IDENT "," IDENT ")"
    emit_action: "emit" "(" STRING ")"

    value: STRING | NUMBER | IDENT | "[" value ("," value)* "]"

    // === TERMINALS - NO KEYWORD CONFLICTS ===
    IDENT: /[a-zA-Z_][a-zA-Z0-9_-]*/
    STRING: /"[^"]*"/
    NUMBER: /\d+\.?\d*/

    %import common.WS
    %ignore WS
    %ignore /#.*$/
'''