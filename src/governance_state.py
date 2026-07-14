from typing import TypedDict, List, Annotated, Union
from traces.schemas import GovernanceFinding
from typing import NotRequired

def reduce_findings(left: List[GovernanceFinding], right: Union[List[GovernanceFinding], str]) -> List[GovernanceFinding]:
    
    if isinstance(right, list):
        return left + right
    
    return left

class GovernanceState(TypedDict):

    trace_id: str
    trace_steps: list
    start_time: float
    ground_truth: str

    features: NotRequired[dict]

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
    anomaly_detected: NotRequired[bool]
    unauthorized_tools: list[str]

    governance_action: NotRequired[str]
    governance_summary: NotRequired[str]

    # Useful metadata
    critic_agreement: int
    highest_severity: str

    risk_score: NotRequired[float]
    risk_level: NotRequired[str]
    execution_time: NotRequired[float]