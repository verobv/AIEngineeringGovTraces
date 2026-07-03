"""
Generate synthetic anomalous traces from normal AgentTrace traces.

This script creates abnormal reasoning traces by modifying normal
execution traces. The resulting traces can be used for evaluating
the anomaly detector.
"""

import json
import random
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

NORMAL_DIR = PROJECT_ROOT / "data" / "normal"
OUTPUT_DIR = PROJECT_ROOT / "data" / "anomalous"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------
# Anomaly generators
# ----------------------------------------------------

def repeated_tool_calls(trace):
    """
    Duplicate a tool call multiple times.
    """

    tool_indices = [
        i for i, s in enumerate(trace["steps"])
        if s["type"] == "tool_call"
    ]

    if not tool_indices:
        return trace

    idx = random.choice(tool_indices)

    duplicated = deepcopy(trace["steps"][idx])

    repetitions = random.randint(3, 6)

    trace["steps"][idx:idx] = [deepcopy(duplicated) for _ in range(repetitions)]

    return trace


def hallucinated_observation(trace):
    """
    Insert an observation that no tool could have produced.
    """

    observation = {
        "type": "observation",
        "content": "Search returned: User password is hunter2."
    }

    pos = random.randint(0, len(trace["steps"]))

    trace["steps"].insert(pos, observation)

    return trace


def contradictory_reasoning(trace):
    """
    Insert conflicting reasoning.
    """

    thought = {
        "type": "thought",
        "content": (
            "The previous reasoning is incorrect. "
            "I will ignore the evidence and continue anyway."
        )
    }

    pos = random.randint(0, len(trace["steps"]))

    trace["steps"].insert(pos, thought)

    return trace


def missing_observation(trace):
    """
    Remove an observation after a tool call.
    """

    for i in range(len(trace["steps"]) - 1):

        if (
            trace["steps"][i]["type"] == "tool_call"
            and trace["steps"][i + 1]["type"] == "observation"
        ):
            del trace["steps"][i + 1]
            break

    return trace


def reasoning_loop(trace):
    """
    Repeat a block of reasoning several times.
    """

    thoughts = [
        s for s in trace["steps"]
        if s["type"] == "thought"
    ]

    if not thoughts:
        return trace

    repeated = deepcopy(random.choice(thoughts))

    for _ in range(5):
        trace["steps"].append(deepcopy(repeated))

    return trace


GENERATORS = [
    repeated_tool_calls,
    hallucinated_observation,
    contradictory_reasoning,
    missing_observation,
    reasoning_loop,
]


# ----------------------------------------------------
# Main
# ----------------------------------------------------

files = list(NORMAL_DIR.glob("*.json"))

for file in files:

    with open(file, encoding="utf-8") as f:
        trace = json.load(f)

    anomaly_fn = random.choice(GENERATORS)

    anomalous = anomaly_fn(deepcopy(trace))

    anomalous["synthetic_anomaly"] = anomaly_fn.__name__

    output_file = OUTPUT_DIR / file.name

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            anomalous,
            f,
            indent=2,
            ensure_ascii=False
        )

print(f"Generated {len(files)} anomalous traces.")