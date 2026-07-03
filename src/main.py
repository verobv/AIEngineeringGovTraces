from src.governance_graph import build_graph
from src.traces.loader import load_trace
from pathlib import Path


graph = build_graph()

for file in Path("data/traces").glob("*.json"):
    trace = load_trace(file)

    result = graph.invoke({
        "trace_id": trace["trace_id"],
        "trace_steps": trace["steps"]
    })

    print(trace["trace_id"], result["governance_action"]) # print maybe something more informative