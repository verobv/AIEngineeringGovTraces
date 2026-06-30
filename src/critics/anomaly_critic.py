from src.analysis.anomaly_analysis import analyze_anomaly

def anomaly_critic(state):

    trace = state["trace_steps"]

    finding = analyze_anomaly(trace)

    state["anomaly_score"] = finding.score

    state["trace_corrupted"] = (
        finding.severity in ("HIGH", "CRITICAL")
    )

    state["findings"] = [finding]

    return state