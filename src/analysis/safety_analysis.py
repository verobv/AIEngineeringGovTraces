"""
Uses an LLM to inspect the trace for unsafe behavior.
"""

from src.traces.schemas import GovernanceFinding
from src.utils import get_llm
from src.config import SAFETY_CRITIC_MODEL
from src.prompts import SAFETY_PROMPT

def analyze_safety(trace) -> GovernanceFinding:

    """
    Analyze a reasoning trace for safety issues. 
    Returns a structured GovernanceFinding.
    """

    llm = (
        get_llm(SAFETY_CRITIC_MODEL)
        .with_structured_output(GovernanceFinding)
    )

    prompt = SAFETY_PROMPT.format(trace=trace)

    finding = llm.invoke(prompt)

    return finding