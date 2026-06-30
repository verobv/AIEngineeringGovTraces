from src.analysis.policy_analysis import analyze_policy

def policy_critic(state):

    trace = state["trace_steps"]

    finding = analyze_policy(trace)

    state["policy_score"] = finding.score

    state["policy_violation"] = (
        finding.severity in ("HIGH", "CRITICAL")
    )

    state["findings"] = [finding]

    return state