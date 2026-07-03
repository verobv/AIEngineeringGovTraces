from langgraph.graph import StateGraph, END
from src.governance_state import GovernanceState
from src.nodes import (
    trace_collector_node, chairman_node, policy_engine_node
)
from src.critics.anomaly_critic import anomaly_critic
from src.critics.safety_critic import safety_critic
from src.critics.policy_critic import policy_critic

def build_graph():

    """
    Builds the governance execution graph. 

    Trace -> Governance Critics (parallel) -> Chairman -> Policy Engine -> END 
    """

    workflow = StateGraph(GovernanceState)
    
    # --- Add Nodes ---

    workflow.add_node("collector", trace_collector_node)

    # Complex Modes: Add Council

    workflow.add_node("anomaly_critic", anomaly_critic)
    workflow.add_node("safety_critic", safety_critic)
    workflow.add_node("policy_critic", policy_critic)

    workflow.add_node("chairman", chairman_node)
    workflow.add_node("policy_engine", policy_engine_node)

    # --- Define Edges ---

    workflow.set_entry_point("collector")

     # Fan-out (Parallel Critics)
    workflow.add_edge("collector", "anomaly_critic")
    workflow.add_edge("collector", "safety_critic")
    workflow.add_edge("collector", "policy_critic")

    # Fan-in (Aggregation)
    workflow.add_edge("anomaly_critic", "chairman")
    workflow.add_edge("safety_critic", "chairman")
    workflow.add_edge("policy_critic", "chairman")

    # --- Final decision: no conditional routing as we want DETERMINISTIC actions ---
    # NOT based on chairman's
    workflow.add_edge("chairman", "policy_engine")
    workflow.add_edge("policy_engine", END)

    return workflow.compile()