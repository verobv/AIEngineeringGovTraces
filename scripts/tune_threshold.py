from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import numpy as np

from sklearn.metrics import f1_score

from src.analysis.oneLadle_detector import OneLadleDetector
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.analysis.feature_extraction import extract_trace_features
from src.traces.loader import load_trace
from src.config import FEATURE_ORDER, ANOMALY_DETECTOR


MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

NORMAL_DIR = PROJECT_ROOT / "data" / "val" / "normal"
ANOMALY_DIR = PROJECT_ROOT / "data" / "val" / "anomalous"


def score_trace(detector, trace):

    if ANOMALY_DETECTOR == "ladle":
        return detector.score(trace["text"])

    features = extract_trace_features(trace["steps"])
    x = [features[name] for name in FEATURE_ORDER]

    return detector.score(x)


def load_scores(detector, directory, label):

    scores = []
    labels = []

    for file in directory.glob("*.json"):

        trace = load_trace(file)

        scores.append(score_trace(detector, trace))
        labels.append(label)

    return scores, labels


def main():

    if ANOMALY_DETECTOR == "ladle":
        detector = OneLadleDetector()
    else:
        detector = TraceAnomalyDetector(detector_type=ANOMALY_DETECTOR)

    detector.load(MODEL_PATH)

    normal_scores, normal_labels = load_scores(detector, NORMAL_DIR, 0)
    anomaly_scores, anomaly_labels = load_scores(detector, ANOMALY_DIR, 1)

    scores = np.array(normal_scores + anomaly_scores)
    labels = np.array(normal_labels + anomaly_labels)

    min_score = float(scores.min())
    max_score = float(scores.max())

    print("\nValidation score statistics")
    print("--------------------------")

    print(
        f"Normal mean   : "
        f"{np.mean(normal_scores):.4f}"
    )

    print(
        f"Normal std    : "
        f"{np.std(normal_scores):.4f}"
    )

    print(
        f"Anomaly mean  : "
        f"{np.mean(anomaly_scores):.4f}"
    )

    print(
        f"Anomaly std   : "
        f"{np.std(anomaly_scores):.4f}"
    )

    print(
        f"Minimum score : "
        f"{min_score:.4f}"
    )

    print(
        f"Maximum score : "
        f"{max_score:.4f}"
    )

    thresholds = np.linspace(min_score, max_score, 200)

    best_threshold = None
    best_f1 = -1

    for threshold in thresholds:

        predictions = (scores >= threshold).astype(int)

        f1 = f1_score(labels, predictions)

        if f1 > best_f1:

            best_f1 = f1
            best_threshold = threshold

    detector.threshold = float(best_threshold)
    detector.best_f1 = float(best_f1)
    detector.min_score = min_score
    detector.max_score = max_score

    print("\nBest threshold")
    print("----------------")
    print(
        f"{best_threshold:.6f}"
    )

    print("\nBest validation F1")
    print("------------------")
    print(
        f"{best_f1:.6f}"
    )

    print("\nCalibration range")
    print("-----------------")
    print(
        f"{min_score:.6f} -> "
        f"{max_score:.6f}"
    )

    detector.save(MODEL_PATH)

    print("\nUpdated detector saved.")


if __name__ == "__main__":
    main()