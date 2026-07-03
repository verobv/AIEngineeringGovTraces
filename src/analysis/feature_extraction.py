from collections import Counter
from math import log2

"""
Expand it a little later with things like:
- average reasoning length
- maximum consecutive tool calls
- ratio of thoughts/tool calls
- repeated observations
- branching factor (if applicable)
- average tool latency (if available)
"""

def entropy(counter):

    total = sum(counter.values())

    if total == 0:
        return 0

    e = 0

    for c in counter.values():

        p = c / total

        e -= p * log2(p)

    return e

def extract_trace_features(trace):

    tool_calls = []

    thought_lengths = []
    observation_lengths = []

    thought_count = 0
    observation_count = 0

    consecutive_tools = 0
    consecutive_thoughts = 0

    max_tools = 0
    max_thoughts = 0

    for step in trace:

        step_type = step["type"]

        if step_type == "tool_call":

            tool_calls.append(step.get("tool", ""))

            consecutive_tools += 1
            consecutive_thoughts = 0

            max_tools = max(max_tools, consecutive_tools)

        elif step_type == "thought":

            thought_count += 1

            thought_lengths.append(
                len(step.get("content", ""))
            )

            consecutive_thoughts += 1
            consecutive_tools = 0

            max_thoughts = max(max_thoughts, consecutive_thoughts)

        elif step_type == "observation":

            observation_count += 1

            observation_lengths.append(
                len(step.get("content", ""))
            )

            consecutive_tools = 0
            consecutive_thoughts = 0

    tool_counts = Counter(tool_calls)

    n_steps = len(trace)

    features = {
        "n_steps": n_steps,
        "n_tool_calls": len(tool_calls),
        "n_unique_tools": len(tool_counts),
        "n_thoughts": thought_count,
        "n_observations": observation_count,
        "max_tool_repetition": max(tool_counts.values(), default=0),
        "avg_thought_length":
            sum(thought_lengths) / len(thought_lengths)
            if thought_lengths else 0,
        "avg_observation_length":
            sum(observation_lengths) / len(observation_lengths)
            if observation_lengths else 0,
        "tool_call_ratio":
            len(tool_calls) / n_steps
            if n_steps else 0,
        "thought_ratio":
            thought_count / n_steps
            if n_steps else 0,
        "max_consecutive_tool_calls": max_tools,
        "max_consecutive_thoughts": max_thoughts,
        "tool_entropy": entropy(tool_counts),
    }

    return features