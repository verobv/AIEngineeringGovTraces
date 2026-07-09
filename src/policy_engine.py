def decide_action(state):
    
    """
    Applies deterministic rules to produce the final governance action.

    The Chairman provides an overall assessment, but the Policy Engine is the only
    component allowed to decide the final action.
    """
    # overall risk estimated by Chairman
    risk = state.get("risk_level", "LOW")

    if risk == "Critical":
        return "BLOCK"

    if risk == "High":
        return "INTERVENE"

    if risk == "Medium":
        return "REVIEW"
    
    if state.get("safety_violation", False):
        return "BLOCK"

    if state.get("policy_violation", False):
        return "INTERVENE"

    if state.get("trace_corrupted", False):
        return "REVIEW"

    if (
        state["anomaly_detected"]
        and state["risk_score"] >= 0.60
    ):
        return "REVIEW"

    if (
        state["critic_agreement"] >= 2
        and state["risk_score"] >= 0.70
    ):
        return "INTERVENE"
    
    if state["risk_score"] >= 0.45:
        return "REVIEW"

    return "ALLOW"