from governance_graph import build_graph
from traces.loader import load_dataset
from pathlib import Path
import time 

start = time.perf_counter()

graph = build_graph()

normal = load_dataset("data/normal")
anomalous = load_dataset("data/anomalous")

dataset = normal + anomalous

print(len(dataset))

counter = 0

for trace in anomalous:

    print(counter, ". ", trace["trace_id"])

    counter += 1

    start_trace = time.perf_counter()
    
    result = graph.invoke({
        "trace_id": trace["trace_id"],
        "trace_steps": trace["steps"]
    })

    end_trace = time.perf_counter()

    print(f"Trace {trace["trace_id"]} execution time: {end_trace - start_trace:.2f} seconds")

    print(trace["trace_id"], result["governance_action"]) # print maybe something more informative

end = time.perf_counter()

print(f"Total execution time: {end - start:.2f} seconds")