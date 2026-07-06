"""
Uses an LLM to inspect the trace for unsafe behavior.
"""

from traces.schemas import GovernanceFinding
from utils import get_llm, invoke_structured
from config import SAFETY_CRITIC_MODEL
from prompts import SAFETY_PROMPT

LLM = (
    get_llm(SAFETY_CRITIC_MODEL)
    #.with_structured_output(GovernanceFinding)
)

def analyze_safety(trace) -> GovernanceFinding:

    """
    Analyze a reasoning trace for safety issues. 
    Returns a structured GovernanceFinding.
    """

    prompt = SAFETY_PROMPT.format(trace=trace)

    # finding = LLM.invoke(prompt)

    # return finding

    finding = invoke_structured(LLM, prompt,  GovernanceFinding)

    print(finding)

    return finding