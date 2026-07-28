from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.analysis.oneLadle_detector import OneLadleDetector
from src.analysis.feature_extraction import extract_trace_features
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.traces.loader import load_trace
from src.config import ANOMALY_DETECTOR, FEATURE_ORDER

DATA_DIR = PROJECT_ROOT / "data" / "normal"
MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

def build_training_matrix():

    X = []

    for trace_file in DATA_DIR.glob("*.json"):

        trace = load_trace(trace_file)

        features = extract_trace_features(trace["steps"])

        X.append([features[name] for name in FEATURE_ORDER])

    if len(X) == 0:
        raise RuntimeError(f"No traces found in {DATA_DIR}")

    return X

def load_trace_texts():

    traces = []

    for trace_file in DATA_DIR.glob("*.json"):

        trace = load_trace(trace_file)

        if "text" not in trace:
            raise RuntimeError(
                f"{trace_file.name} does not contain a 'text' field.\n"
                "Run convert_agenttrace.py again."
            )

        traces.append(trace["text"])

    return traces


def main():

    print("Loading training traces...")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if ANOMALY_DETECTOR == "ladle":

        traces = load_trace_texts()

        print(f"Loaded {len(traces)} traces.")

        detector = OneLadleDetector()

        print("Training ONELADLE anomaly detector...")

        detector.fit(traces)

    else:

        X = build_training_matrix()

        print(f"Loaded {len(X)} traces.")
        print(f"Feature dimension: {len(X[0])}")

        detector = TraceAnomalyDetector(detector_type=ANOMALY_DETECTOR)

        print("Training anomaly detector...")

        detector.fit(X)

    detector.save(MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()