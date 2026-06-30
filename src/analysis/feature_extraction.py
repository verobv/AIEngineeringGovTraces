from collections import Counter

"""
Expand it a little later with things like:
- average reasoning length
- maximum consecutive tool calls
- ratio of thoughts/tool calls
- repeated observations
- branching factor (if applicable)
- average tool latency (if available)
"""


def extract_trace_features(trace):

    tool_calls = []
    thought_count = 0
    observation_count = 0

    for step in trace:

        if step["type"] == "tool_call":
            tool_calls.append(step.get("tool"))

        elif step["type"] == "thought":
            thought_count += 1

        elif step["type"] == "observation":
            observation_count += 1

    tool_counts = Counter(tool_calls)

    features = {
        "n_steps": len(trace),
        "n_tool_calls": len(tool_calls),
        "n_unique_tools": len(set(tool_calls)),
        "n_thoughts": thought_count,
        "n_observations": observation_count,
        "max_tool_repetition": max(tool_counts.values(), default=0)
    }

    return features