import re

"""
Uses an LLM to check compliance with governance policies.
"""

from traces.schemas import GovernanceFinding
from utils import get_llm, invoke_structured
from collections import Counter
from config import POLICY_CRITIC_MODEL
from prompts import POLICY_PROMPT
from policies import (
    GOVERNANCE_RULES,
    APPROVED_TOOLS,
    MAX_TRACE_LENGTH,
    MAX_TOOL_CALLS,
    MAX_REPEATED_TOOL_CALLS,
    SENSITIVE_KEYWORDS,
)

LLM = (
    get_llm(POLICY_CRITIC_MODEL)
    #.with_structured_output(GovernanceFinding)
)

def extract_tool_calls(trace_steps):
    """
    Extract all tool calls from a reasoning trace.
    """

    tools = []

    for step in trace_steps:

        if step.get("type") == "tool_call":
            tools.append(step["tool"])

    return tools

def contains_sensitive_information(trace):

    text = str(trace).lower()

    for keyword in SENSITIVE_KEYWORDS:

        if keyword in text:
            return keyword

    return None

def check_policy_rules(trace):

    violations = []

    tool_calls = extract_tool_calls(trace)

    #
    # Rule 1
    # Unauthorized tool
    #

    for tool in tool_calls:

        if tool not in APPROVED_TOOLS:

            violations.append({
                "rule": "UNAUTHORIZED_TOOL",
                "severity": "High",
                "message": f"Unauthorized tool '{tool}'",
                "evidence": tool,
            })

    #
    # Rule 2
    # Too many total tool calls
    #

    if len(tool_calls) > MAX_TOOL_CALLS:

        violations.append({
            "rule": "EXCESSIVE_TOOL_USAGE",
            "severity": "Medium",
            "message": f"{len(tool_calls)} tool calls",
            "evidence": str(len(tool_calls)),
        })

    #
    # Rule 3
    # Same tool repeated
    #

    counts = Counter(tool_calls)

    for tool, count in counts.items():

        if count > MAX_REPEATED_TOOL_CALLS:

            violations.append({
                "rule": "REPEATED_TOOL_CALL",
                "severity": "Medium",
                "message": f"{tool} called {count} times",
                "evidence": tool,
            })

    #
    # Rule 4
    # Trace too long
    #

    if len(trace) > MAX_TRACE_LENGTH:

        violations.append({
            "rule": "TRACE_TOO_LONG",
            "severity": "Medium",
            "message": f"{len(trace)} reasoning steps",
            "evidence": str(len(trace)),
        })

    #
    # Rule 5
    # Sensitive information
    #

    keyword = contains_sensitive_information(trace)

    if keyword:

        violations.append({
            "rule": "SENSITIVE_INFORMATION",
            "severity": "Critical",
            "message": f"Detected sensitive keyword '{keyword}'",
            "evidence": keyword,
        })

    #
    # Rule 6
    # Missing final answer
    #

    if not any(
        step.get("type") == "final_answer"
        for step in trace
    ):

        violations.append({
            "rule": "MISSING_FINAL_ANSWER",
            "severity": "Medium",
            "message": "Trace never reaches a final answer",
            "evidence": "Missing final_answer step",
        })

    #
    # Rule 7
    # Tool output without tool call
    #

    tool_called = False

    for step in trace:

        if step.get("type") == "tool_call":
            tool_called = True

        if step.get("type") == "tool_output" and not tool_called:

            violations.append({
                "rule": "ORPHAN_TOOL_OUTPUT",
                "severity": "High",
                "message": "Tool output before tool call",
                "evidence": str(step),
            })

            break

    return violations

def analyze_policy(trace) -> GovernanceFinding:

    """
    Analyze a reasoning trace for policy issues. 
    Returns a structured GovernanceFinding.
    """

    violations = check_policy_rules(trace)

    if not violations:
        return GovernanceFinding(
            critic="Policy",
            severity="Low",
            score=0.0,
            finding="No policy violations detected.",
            evidence="All deterministic governance rules passed."
        )

    rules = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(GOVERNANCE_RULES))

    violations_text = "\n".join(
        f"""
Rule: {v["rule"]}
Severity: {v["severity"]}
Message: {v["message"]}
Evidence: {v["evidence"]}
"""
        for v in violations
    )

    prompt = POLICY_PROMPT.format(
        trace=trace,
        rules=rules,
        violations=violations_text
    )

    finding = invoke_structured(LLM, prompt,  GovernanceFinding)

    if finding is None:
        finding = GovernanceFinding(
            critic="Policy",
            severity="Medium",
            score=0.5,
            finding="Policy evaluation unavailable.",
            evidence="LLM failed after retries."
        )

    return finding
    