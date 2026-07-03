from src.policy_engine import decide_action
from src.governance_state import GovernanceState
from src.traces.schemas import GovernanceFinding, GovernanceAssessment
from src.utils import get_llm
from src.analysis.feature_extraction import extract_trace_features
from src.config import CHAIRMAN_MODEL_NAME

def trace_collector_node(state: GovernanceState):

    """
    Inital preprocessing stage.

    TODO Future responsibilities:
        - validate traces
        - normalize trace formats
        - attach metadata
    """

    state.setdefault("findings", [])

    state["features"] = extract_trace_features(state["trace_steps"])

    return state

def chairman_node(state: GovernanceState):

    """
    Aggregates findings from all critics.

    The Chairman does not decide the final governance action. 
    It only synthesizes the critics' outputs into an overall risk assessment. 
    """

    findings: list[GovernanceFinding] = state.get("findings", [])

    if not findings: 
        state["risk_level"] = "LOW"
        state["governance_summary"] = "No governance issues detected."
        return state

    llm = get_llm(CHAIRMAN_MODEL_NAME).with_structured_output(
        GovernanceAssessment
    )

    findings_text = "\n\n".join(
        [
            f"""
Critic: {f.critic}
Severity: {f.severity}
Score: {f.score}
Finding: {f.finding}
Evidence: {f.evidence}
"""     
            for f in findings
        ]
    )

    prompt = f"""
You are the Chairman of a governace council.

Your task is ONLY to synthesize the critic's findings. 

Do NOT decide whether to block, review or allow.
Do not invent new issues.

Do not recommend actions.

Return GovernanceAssessment.

Critic findings:

{findings_text}
"""
    
    assessment = llm.invoke(prompt)

    state["risk_level"] = assessment.risk_level
    state["governance_summary"] = assessment.summary

    return state

def policy_engine_node(state: GovernanceState):

    """
    Deterministic governance decision. 

    This node delegates the decidion to the policy engine.
    """

    state["governance_action"] = decide_action(state)

    return state