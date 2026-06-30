"""
Uses an LLM to check compliance with governance policies.
"""

from src.traces.schemas import GovernanceFinding
from src.utils import get_llm
from src.config import POLICY_CRITIC_MODEL
from src.prompts import POLICY_PROMPT
from src.policies import GOVERNANCE_RULES

def analyze_policy(trace) -> GovernanceFinding:

    """
    Analyze a reasoning trace for policy issues. 
    Returns a structured GovernanceFinding.
    """

    llm = (
        get_llm(POLICY_CRITIC_MODEL)
        .with_structured_output(GovernanceFinding)
    )

    rules = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(GOVERNANCE_RULES))

    prompt = POLICY_PROMPT.format(
        trace=trace,
        rules=rules
    )

    finding = llm.invoke(prompt)

    return finding