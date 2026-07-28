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
    roc_auc_score, roc_curve,
    precision_recall_curve,
    average_precision_score
)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from src.analysis.embedding import embed
from src.analysis.feature_extraction import extract_trace_features
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.analysis.oneLadle_detector import OneLadleDetector
from src.traces.loader import load_trace
from src.config import ANOMALY_DETECTOR, FEATURE_ORDER

MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

NORMAL_DIR = PROJECT_ROOT / "data" / "normal"
ANOMALOUS_DIR = PROJECT_ROOT / "data" / "anomalous"

def evaluate_directory(detector, directory, expected_label):
    """
    Evaluate every trace in one directory.
    Uses one embedding pass for all traces (much faster).
    """

    y_true = []
    y_pred = []
    scores = []

    # ---------- Non-LADLE detectors ----------
    if ANOMALY_DETECTOR != "ladle":

        """for trace_file in directory.glob("*.json"):

            trace = load_trace(trace_file)

            features = extract_trace_features(trace["steps"])

            x = [features[name] for name in FEATURE_ORDER]

            score = detector.score(x)
            prediction = detector.predict(x)

            y_true.append(expected_label)
            y_pred.append(int(prediction))
            scores.append(score)

        return y_true, y_pred, scores"""

        results = []

        for trace_file in directory.glob("*.json"):

            trace = load_trace(trace_file)

            features = extract_trace_features(trace["steps"])

            x = [features[name] for name in FEATURE_ORDER]

            score = detector.score(x)
            prediction = int(detector.predict(x))

            results.append({
                "file": trace_file.name,
                "true_label": expected_label,
                "score": float(score),
                "prediction": prediction,
                "trace": trace,
                "anomaly_type": trace.get("synthetic_anomaly", "normal")
            })

        return results

    # ---------- LADLE detector ----------

    results = []

    traces = []
    trace_files = []
    trace_objects = []
    trace_window_counts = []
    all_windows = []

    print(f"\nLoading traces from {directory.name}...")

    for trace_file in directory.glob("*.json"):

        trace = load_trace(trace_file)

        if "text" not in trace:
            raise RuntimeError(
                f"{trace_file.name} has no 'text' field."
            )

        traces.append(trace["text"])
        trace_files.append(trace_file.name)
        trace_objects.append(trace)

        windows = detector._create_windows(trace["text"])

        trace_window_counts.append(len(windows))
        all_windows.extend(windows)

    print(f"Loaded {len(traces)} traces.")
    print(f"Created {len(all_windows)} windows.")

    print("Embedding all windows...")

    embeddings = embed(all_windows)

    print("Computing nearest neighbors...")

    distances, _ = detector.nn.kneighbors(embeddings)

    window_scores = np.mean(distances, axis=1)

    start = 0

    for file_name, trace, n_windows in zip(
        trace_files,
        trace_objects,
        trace_window_counts,
    ):

        end = start + n_windows

        score = float(np.mean(window_scores[start:end]))

        prediction = int(score > detector.threshold)

        results.append(
            {
                "file": file_name,
                "true_label": expected_label,
                "score": score,
                "prediction": prediction,
                "trace": trace,
                "anomaly_type": trace.get(
                    "synthetic_anomaly",
                    "normal",
                ),
            }
        )

        start = end

    return results

def outcome(true_label, pred):
    if true_label == 1 and pred == 1:
        return "TP"  # correctly detected anomaly
    if true_label == 1 and pred == 0:
        return "FN"  # missed anomaly
    if true_label == 0 and pred == 1:
        return "FP"  # false alarm
    return "TN"      # correctly detected normal

def main():

    if ANOMALY_DETECTOR == "ladle":
        detector = OneLadleDetector()
        title = "LADLE"
    else:
        detector = TraceAnomalyDetector(detector_type=ANOMALY_DETECTOR)
        title = ANOMALY_DETECTOR.upper()

    detector.load(MODEL_PATH)

    normal_results = evaluate_directory(detector, NORMAL_DIR, expected_label=0)

    anomaly_results = evaluate_directory(detector, ANOMALOUS_DIR, expected_label=1)

    all_results = normal_results + anomaly_results

    for r in all_results:
        r["outcome"] = outcome(r["true_label"], r["prediction"])

    df = pd.DataFrame([
        {
            "file": r["file"],
            "true_label": r["true_label"],
            "score": r["score"],
            "prediction": r["prediction"],
            "outcome": r["outcome"],
        }
        for r in all_results
    ])

    df.to_csv(PROJECT_ROOT / f"evaluation_results_{title}.csv", index=False)

    print(f"Saved detailed results to evaluation_results_{title}.csv")

    tp = [r for r in all_results if r["outcome"] == "TP"]
    fn = [r for r in all_results if r["outcome"] == "FN"]
    fp = [r for r in all_results if r["outcome"] == "FP"]
    tn = [r for r in all_results if r["outcome"] == "TN"]

    print(f"TP: {len(tp)}")
    print(f"FN: {len(fn)}")
    print(f"FP: {len(fp)}")
    print(f"TN: {len(tn)}")

    print("\nMissed anomalies (FN):")
    for r in fn[:10]:
        print(f"{r['file']:30} score={r['score']:.3f}")

    print("\nCorrectly detected anomalies (TP):")
    for r in sorted(tp, key=lambda x: x["score"], reverse=True)[:10]:
        print(f"{r['file']:30} score={r['score']:.3f}")

    stats = defaultdict(lambda: {"tp": 0, "fn": 0})

    for r in anomaly_results:

        if r["prediction"] == 1:
            stats[r["anomaly_type"]]["tp"] += 1
        else:
            stats[r["anomaly_type"]]["fn"] += 1

    print("\n========== PERFORMANCE BY ANOMALY TYPE ==========\n")

    for anomaly_type, s in sorted(stats.items()):

        total = s["tp"] + s["fn"]

        recall = s["tp"] / total if total else 0

        print(f"{anomaly_type:25}"
            f" Total={total:4}"
            f" Detected={s['tp']:4}"
            f" Missed={s['fn']:4}"
            f" Recall={recall:.3f}")
    
    types = []
    recalls = []

    for anomaly_type, s in sorted(stats.items()):

        total = s["tp"] + s["fn"]

        types.append(anomaly_type)
        recalls.append(s["tp"] / total)

    plt.figure(figsize=(10,5))
    plt.bar(types, recalls)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Recall")
    plt.title(f"Recall by Synthetic Anomaly Type for {title}")
    plt.tight_layout()
    plt.show()
        

    normal_scores = np.array( [ r["score"] for r in normal_results ] )
    anomaly_scores = np.array( [ r["score"] for r in anomaly_results ] )

    pooled = np.sqrt((normal_scores.std()**2 + anomaly_scores.std()**2) / 2)

    d = (anomaly_scores.mean() - normal_scores.mean()) / pooled

    print("\nProbability statistics")
    print("----------------------")
    print(f"Normal mean : {np.mean(normal_scores):.3f}")
    print(f"Normal std  : {np.std(normal_scores):.3f}")
    print(f"Anomaly mean: {np.mean(anomaly_scores):.3f}")
    print(f"Anomaly std : {np.std(anomaly_scores):.3f}")
    print(f"Cohen's d: {d}")

    plt.figure(figsize=(8,5))
    plt.hist(normal_scores, bins=40, alpha=0.6, label="Normal")
    plt.hist(anomaly_scores, bins=40, alpha=0.6, label="Anomalous")
    plt.xlabel("Anomaly score")
    plt.ylabel("Number of traces")
    plt.title(f"{title} Score Distribution")

    plt.legend()

    plt.show()

    # ======================================================
    # ROC and Precision-Recall evaluation
    # ======================================================

    scores = np.concatenate( [normal_scores, anomaly_scores] )

    labels = np.concatenate([ np.zeros(len(normal_scores)), np.ones(len(anomaly_scores)) ])

    # ---------------- ROC ----------------

    roc_auc = roc_auc_score(labels, scores)

    print(f"\nROC-AUC: {roc_auc:.3f}")

    fpr, tpr, _ = roc_curve(labels, scores)

    plt.figure(figsize=(6,6))

    plt.plot(
        fpr,
        tpr,
        linewidth=2,
        label=f"AUC = {roc_auc:.3f}"
    )

    plt.plot(
        [0,1],
        [0,1],
        "--",
        color="gray"
    )

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"{title} ROC Curve")
    plt.legend(loc="lower right")

    plt.tight_layout()
    plt.show()

    # ---------------- Precision-Recall ----------------

    precision, recall, _ = precision_recall_curve( labels, scores )

    ap = average_precision_score( labels, scores )

    print(f"Average Precision (PR-AUC): {ap:.3f}")

    plt.figure(figsize=(6,6))

    plt.plot(
        recall,
        precision,
        linewidth=2,
        label=f"AP = {ap:.3f}"
    )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"{title} Precision-Recall Curve")
    plt.legend(loc="lower left")

    plt.tight_layout()
    plt.show()

    # ======================================================
    # Threshold sweep
    # ======================================================

    print("\n========== THRESHOLD SWEEP ==========\n")

    thresholds = np.linspace(scores.min(), scores.max(), 100)

    results = []

    best_threshold = None
    best_f1 = -1

    print( f"{'Threshold':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}" )

    for threshold in thresholds:

        predictions = (scores >= threshold).astype(int)

        precision = precision_score( labels, predictions, zero_division=0 )

        recall = recall_score( labels, predictions, zero_division=0 )

        f1 = f1_score( labels, predictions, zero_division=0 )

        results.append((threshold, precision, recall, f1))

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

        print(
            f"{threshold:10.3f}"
            f"{precision:10.3f}"
            f"{recall:10.3f}"
            f"{f1:10.3f}"
        )

    print("\nBest threshold")
    print("----------------")
    print(f"Threshold : {best_threshold:.3f}")
    print(f"Best F1   : {best_f1:.3f}")

    """
    The threshold -0.191 was selected using the evaluation labels. That makes it an oracle threshold—it's useful for analyzing the detector's potential, 
    but it should not be presented as the threshold you would deploy in practice. In a real system, the threshold would be tuned on a separate 
    validation set or chosen based on operational requirements (e.g., prioritizing high recall or limiting false positives).
    """

    threshold_values = [r[0] for r in results]
    f1_values = [r[3] for r in results]

    plt.figure(figsize=(7,4))

    plt.plot( threshold_values, f1_values, linewidth=2 )

    plt.axvline( best_threshold, color="red", linestyle="--", label=f"Best = {best_threshold:.3f}" )
    
    if ANOMALY_DETECTOR == "ladle":
        plt.axvline( detector.threshold, color="green", linestyle=":", label="Training threshold" )

    plt.xlabel("Anomaly score threshold")
    plt.ylabel("F1-score")
    plt.title(f"{title} F1-score vs Decision Threshold")

    plt.legend()

    plt.tight_layout()
    plt.show()

    precision_values = [r[1] for r in results]
    recall_values = [r[2] for r in results]

    plt.figure(figsize=(8,5))

    plt.plot( threshold_values, precision_values, label="Precision", linewidth=2 )

    plt.plot( threshold_values, recall_values, label="Recall", linewidth=2 )

    plt.plot( threshold_values, f1_values, label="F1-score", linewidth=2 )

    plt.axvline( best_threshold, color="black", linestyle="--", label="Best F1 threshold" )

    plt.xlabel("Anomaly score threshold")
    plt.ylabel("Metric value")
    plt.title(f"{title} Effect of Decision Threshold")

    plt.legend()

    plt.tight_layout()
    plt.show()

    print("\n========== RESULTS ==========\n")

    y_true = [r["true_label"] for r in all_results] 
    y_pred = [r["prediction"] for r in all_results]

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