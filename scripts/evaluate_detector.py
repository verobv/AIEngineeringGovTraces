from pathlib import Path
import sys 

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from src.analysis.feature_extraction import extract_trace_features
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.traces.loader import load_trace
from src.config import ANOMALY_DETECTOR, FEATURE_ORDER

MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

NORMAL_DIR = PROJECT_ROOT / "data" / "normal"
ANOMALOUS_DIR = PROJECT_ROOT / "data" / "anomalous"


def evaluate_directory(detector, directory, expected_label):
    """
    Evaluate every trace in one directory.

    expected_label:
        0 = normal
        1 = anomaly
    """

    y_true = []
    y_pred = []

    for trace_file in directory.glob("*.json"):

        trace = load_trace(trace_file)

        features = extract_trace_features(trace["steps"])

        x = [features[name] for name in FEATURE_ORDER]

        prediction = detector.predict(x)

        y_true.append(expected_label)
        y_pred.append(int(prediction))

    return y_true, y_pred


def main():

    detector = TraceAnomalyDetector(
        detector_type=ANOMALY_DETECTOR
    )

    detector.load(MODEL_PATH)

    normal_true, normal_pred = evaluate_directory(
        detector,
        NORMAL_DIR,
        expected_label=0,
    )

    anomaly_true, anomaly_pred = evaluate_directory(
        detector,
        ANOMALOUS_DIR,
        expected_label=1,
    )

    y_true = normal_true + anomaly_true
    y_pred = normal_pred + anomaly_pred

    print("\n========== RESULTS ==========\n")

    print(f"Accuracy : {accuracy_score(y_true, y_pred):.3f}")
    print(f"Precision: {precision_score(y_true, y_pred):.3f}")
    print(f"Recall   : {recall_score(y_true, y_pred):.3f}")
    print(f"F1-score : {f1_score(y_true, y_pred):.3f}")

    print("\nConfusion Matrix")
    print(confusion_matrix(y_true, y_pred))

    print("\nClassification Report")
    print(classification_report(y_true, y_pred))

    print()

    print("Predicted anomalies:", sum(y_pred))
    print("Predicted normal:", len(y_pred) - sum(y_pred))


if __name__ == "__main__":
    main()