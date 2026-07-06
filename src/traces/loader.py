import json
from pathlib import Path

def load_trace(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_dataset(folder):
    traces = []

    for file in sorted(Path(folder).glob("*.json")):
        traces.append(load_trace(file))

    return traces