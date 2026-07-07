from analysis.safety_analysis import analyze_safety
import time 

def safety_critic(state):

    start = time.perf_counter()

    trace = state["trace_steps"]

    finding = analyze_safety(trace)

    state["safety_score"] = finding.score

    state["safety_violation"] = (
        finding.severity in ("HIGH", "CRITICAL")
    )

    state["findings"] = [finding]

    print(f"Safety critic: {time.perf_counter() - start:.2f}s")

    return {
        "findings": [finding]
    }