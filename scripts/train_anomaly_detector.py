from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.analysis.feature_extraction import extract_trace_features
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.traces.loader import load_trace
from src.config import ANOMALY_DETECTOR, FEATURE_ORDER

import src.config as config

DATA_DIR = PROJECT_ROOT / "data" / "normal"
MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

def build_training_matrix():

    X = []

    for trace_file in DATA_DIR.glob("*.json"):

        trace = load_trace(trace_file)

        features = extract_trace_features(trace["steps"])

        X.append(
            [features[name] for name in FEATURE_ORDER]
        )

    if len(X) == 0:
        raise RuntimeError(
            f"No traces found in {DATA_DIR}"
        )

    return X


def main():

    print("Loading training traces...")

    X = build_training_matrix()

    print(f"Loaded {len(X)} traces.")
    print(f"Feature dimension: {len(X[0])}")

    detector = TraceAnomalyDetector(
        detector_type=ANOMALY_DETECTOR
    )

    print("Training anomaly detector...")

    detector.fit(X)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    detector.save(MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()