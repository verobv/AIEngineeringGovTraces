from pathlib import Path
import json

LOG_FILE = Path("governance_results.jsonl")


def log_result(state):
    record = {
        "trace_id": state["trace_id"],
        "governance_action": state["governance_action"],
        "risk_level": state["risk_level"],
        "risk_score": state["risk_score"],
        "critic_agreement": state["critic_agreement"],
        "findings": [
            {
                "critic": f.critic,
                "severity": f.severity,
                "score": f.score,
                "finding": f.finding,
            }
            for f in state["findings"]
        ],
        "execution_time": state["execution_time"]
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")