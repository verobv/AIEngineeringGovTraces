from collections import Counter
from math import log2
import re


def entropy(counter):
    total = sum(counter.values())

    if total == 0:
        return 0.0

    e = 0.0

    for c in counter.values():
        p = c / total
        e -= p * log2(p)

    return e


def average(values):
    if len(values) == 0:
        return 0.0
    return sum(values) / len(values)


def extract_trace_features(trace):

    tool_calls = []

    thought_lengths = []
    observation_lengths = []

    thought_word_lengths = []
    observation_word_lengths = []

    thought_count = 0
    observation_count = 0

    consecutive_tools = 0
    consecutive_thoughts = 0

    max_tools = 0
    max_thoughts = 0

    repeated_tool_sequences = 0

    previous_tool = None

    step_types = []

    for step in trace:

        step_type = step["type"]

        step_types.append(step_type)

        content = step.get("content", "")

        if step_type == "tool_call":

            tool = step.get("tool", "")

            tool_calls.append(tool)

            if tool == previous_tool:
                repeated_tool_sequences += 1

            previous_tool = tool

            consecutive_tools += 1
            consecutive_thoughts = 0

            max_tools = max(max_tools, consecutive_tools)

        elif step_type == "thought":

            thought_count += 1

            thought_lengths.append(len(content))
            thought_word_lengths.append(len(content.split()))

            consecutive_thoughts += 1
            consecutive_tools = 0

            max_thoughts = max(max_thoughts, consecutive_thoughts)

            previous_tool = None

        elif step_type == "observation":

            observation_count += 1

            observation_lengths.append(len(content))
            observation_word_lengths.append(len(content.split()))

            consecutive_tools = 0
            consecutive_thoughts = 0

            previous_tool = None

    tool_counts = Counter(tool_calls)

    step_counter = Counter(step_types)

    n_steps = len(trace)

    unique_tools = len(tool_counts)

    features = {

        # ----------------------------
        # Basic counts
        # ----------------------------

        "n_steps": n_steps,
        "n_tool_calls": len(tool_calls),
        "n_unique_tools": unique_tools,
        "n_thoughts": thought_count,
        "n_observations": observation_count,

        # ----------------------------
        # Ratios
        # ----------------------------

        "tool_call_ratio":
            len(tool_calls) / n_steps if n_steps else 0,

        "thought_ratio":
            thought_count / n_steps if n_steps else 0,

        "observation_ratio":
            observation_count / n_steps if n_steps else 0,

        # ----------------------------
        # Length statistics
        # ----------------------------

        "avg_thought_length":
            average(thought_lengths),

        "avg_observation_length":
            average(observation_lengths),

        "avg_thought_words":
            average(thought_word_lengths),

        "avg_observation_words":
            average(observation_word_lengths),

        # ----------------------------
        # Tool behaviour
        # ----------------------------

        "max_tool_repetition":
            max(tool_counts.values(), default=0),

        "tool_entropy":
            entropy(tool_counts),

        "repeated_tool_sequences":
            repeated_tool_sequences,

        # ----------------------------
        # Execution structure
        # ----------------------------

        "max_consecutive_tool_calls":
            max_tools,

        "max_consecutive_thoughts":
            max_thoughts,

        # ----------------------------
        # Diversity
        # ----------------------------

        "step_type_entropy":
            entropy(step_counter),

        "tool_diversity":
            unique_tools / len(tool_calls)
            if tool_calls else 0,

        # ----------------------------
        # Density
        # ----------------------------

        "steps_per_tool":
            n_steps / len(tool_calls)
            if tool_calls else 0,

        "thoughts_per_tool":
            thought_count / len(tool_calls)
            if tool_calls else 0,

        "observations_per_tool":
            observation_count / len(tool_calls)
            if tool_calls else 0,
    }

    return features