"""
Uses an LLM to check compliance with governance policies.
"""

from traces.schemas import GovernanceFinding
from utils import get_llm, invoke_structured
from config import POLICY_CRITIC_MODEL
from prompts import POLICY_PROMPT
from policies import GOVERNANCE_RULES

LLM = (
    get_llm(POLICY_CRITIC_MODEL)
    #.with_structured_output(GovernanceFinding)
)

def analyze_policy(trace) -> GovernanceFinding:

    """
    Analyze a reasoning trace for policy issues. 
    Returns a structured GovernanceFinding.
    """

    rules = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(GOVERNANCE_RULES))

    prompt = POLICY_PROMPT.format(
        trace=trace,
        rules=rules
    )

    finding = invoke_structured(LLM, prompt,  GovernanceFinding)

    print(finding)

    return finding
    