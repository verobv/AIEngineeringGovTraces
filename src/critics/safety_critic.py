from analysis.safety_analysis import analyze_safety

def safety_critic(state):

    trace = state["trace_steps"]

    finding = analyze_safety(trace)

    state["safety_score"] = finding.score

    state["safety_violation"] = (
        finding.severity in ("HIGH", "CRITICAL")
    )

    state["findings"] = [finding]

    return {
        "findings": [finding]
    }