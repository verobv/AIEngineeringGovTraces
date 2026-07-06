from governance_graph import build_graph
from traces.loader import load_dataset
from pathlib import Path


graph = build_graph()

normal = load_dataset("data/normal")
anomalous = load_dataset("data/anomalous")

dataset = normal + anomalous

for trace in dataset:
    
    result = graph.invoke({
        "trace_id": trace["trace_id"],
        "trace_steps": trace["steps"]
    })

    print(trace["trace_id"], result["governance_action"]) # print maybe something more informative