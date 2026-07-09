from analysis.anomaly_analysis import analyze_anomaly
import time

def anomaly_critic(state):

    start = time.perf_counter()

    trace = state["trace_steps"]

    finding = analyze_anomaly(trace)

    state["anomaly_score"] = finding.score

    state["trace_corrupted"] = (
        finding.severity in ("High", "Critical")
    )

    state["findings"] = [finding]

    print(f"Anomaly critic: {time.perf_counter() - start:.2f}s")

    return {
        "findings": [finding]
    }