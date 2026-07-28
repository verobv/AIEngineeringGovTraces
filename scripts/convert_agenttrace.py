import json
from pathlib import Path
from datasets import load_dataset

dataset = load_dataset("pagarsky/agent-trace")["train"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
output_dir = PROJECT_ROOT / "data" / "normal"

output_dir.mkdir(parents=True, exist_ok=True)

N = min(5000, len(dataset))

for idx, sample in enumerate(dataset.select(range(N))):

    trace = {
        "trace_id": sample["trace_id"],
        "model": sample.get("model"),
        "dataset": sample.get("dataset_name"),
        "steps": [],
        "text": ""
    }

    trace_text = []

    steps = sample["llm_steps_json"]

    if isinstance(steps, str):
        steps = json.loads(steps)

    for step in steps:

        reasoning = step.get("reasoning_content")

        if reasoning:
            trace["steps"].append({
                "type": "thought",
                "content": reasoning
            })

            trace_text.append(reasoning)

        for call in step.get("tool_calls") or []:

            tool_name = call["name"]

            trace["steps"].append({
                "type": "tool_call",
                "tool": call["name"],
                "arguments": call.get("arguments", {})
            })

            trace_text.append(tool_name)

        output = step.get("model_output")

        if output:
            trace["steps"].append({
                "type": "observation",
                "content": output
            })

            trace_text.append(output)
        
        trace["text"] = "\n".join(trace_text)

    with open(
        output_dir / f"{idx:05}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)