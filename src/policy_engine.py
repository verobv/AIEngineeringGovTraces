def decide_action(state):
    
    """
    Applies deterministic rules to produce the final governance action.

    The Chairman provides an overall assessment, but the Policy Engine is the only
    component allowed to decide the final action.
    """

    # hard constraints first
    if state.get("safety_violation", False):
        return "BLOCK"

    if state.get("policy_violation", False):
        return "INTERVENE"

    if state.get("trace_corrupted", False):
        return "REVIEW"
    
    # otherwise, overall risk estimated by Chairman
    risk = state.get("risk_level", "LOW")

    if risk == "CRITICAL":
        return "BLOCK"

    if risk == "HIGH":
        return "INTERVENE"

    if risk == "MEDIUM":
        return "REVIEW"

    return "ALLOW"