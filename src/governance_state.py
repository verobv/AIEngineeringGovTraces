from typing import TypedDict, List, Annotated, Union
from src.traces.schemas import GovernanceFinding
from typing import NotRequired

def reduce_findings(left: List[GovernanceFinding], right: Union[List[GovernanceFinding], str]) -> List[GovernanceFinding]:
    """
    Custom reduction function:
    1. If the "DELETE" command is received, clear the list (used for Generator to reset state).
    2. Otherwise, perform list appending (used for parallel aggregation of Critics).
    """
    if right == "DELETE":
        return []
    if isinstance(right, list):
        return left + right
    return left

class GovernanceState(TypedDict):

    trace_id: str
    trace_steps: list

    safety_score: NotRequired[float]
    policy_score: NotRequired[float]
    anomaly_score: NotRequired[float]
    
    findings: Annotated[
        List[GovernanceFinding],
        reduce_findings
    ]

    safety_violation: NotRequired[bool]
    policy_violation: NotRequired[bool]
    trace_corrupted: NotRequired[bool]

    governance_action: NotRequired[str]
    governance_summary: NotRequired[str]
    risk_level: NotRequired[str]