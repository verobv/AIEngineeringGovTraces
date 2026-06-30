import json

def load_trace(path):

    with open(path) as f:
        trace = json.load(f)

    return trace