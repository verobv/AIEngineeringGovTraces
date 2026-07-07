from analysis.policy_analysis import analyze_policy
import time

def policy_critic(state):

    start = time.perf_counter()

    trace = state["trace_steps"]

    finding = analyze_policy(trace)

    state["policy_score"] = finding.score

    state["policy_violation"] = (
        finding.severity in ("HIGH", "CRITICAL")
    )

    state["findings"] = [finding]

    print(f"Policy critic: {time.perf_counter() - start:.2f}s")

    return {
        "findings": [finding]
    }