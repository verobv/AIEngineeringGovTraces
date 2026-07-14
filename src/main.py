from governance_graph import build_graph
from traces.loader import load_dataset
from pathlib import Path
import time 
import random

start = time.perf_counter()

graph = build_graph()

normal = load_dataset("data/normal")
anomalous = load_dataset("data/anomalous")

for t in normal:
    t["ground_truth"] = "normal"

anomalous = load_dataset("data/anomalous")
for t in anomalous:
    t["ground_truth"] = "anomalous"

dataset = normal + anomalous

# print(len(dataset))

rng = random.Random(42)
rng.shuffle(dataset)

N = 250

for i, trace in enumerate(normal [:N]):

    print(i,"", trace["trace_id"])

    start_trace = time.perf_counter()
    
    result = graph.invoke({
        "trace_id": trace["trace_id"],
        "trace_steps": trace["steps"],
        "start_time": start_trace,
        "ground_truth": trace["ground_truth"]
    })

    print(f"Trace {trace["trace_id"]} execution time: {result["execution_time"]:.2f} seconds")

    print(trace["trace_id"], result["governance_action"]) # print maybe something more informative

end = time.perf_counter()

print(f"Total execution time: {end - start:.2f} seconds")

"""
TO DO:
- improve anomaly detector, ladle
- improve policy critic
"""