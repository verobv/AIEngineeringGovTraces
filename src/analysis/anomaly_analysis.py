"""
Extracts engineered features and uses an anomaly detection model.
"""

from pathlib import Path

from analysis.feature_extraction import extract_trace_features
from analysis.anomaly_detector import TraceAnomalyDetector
from traces.schemas import GovernanceFinding
from prompts import ANOMALY_PROMPT
from utils import get_llm, invoke_structured
from config import ANOMALY_CRITIC_MODEL, ANOMALY_DETECTOR, FEATURE_ORDER

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / f"{ANOMALY_DETECTOR}.joblib"

# Load detector
DETECTOR = TraceAnomalyDetector(detector_type=ANOMALY_DETECTOR)

if MODEL_PATH.exists():
    DETECTOR.load(MODEL_PATH)
else:
    raise FileNotFoundError(
        f"Anomaly detector not found: {MODEL_PATH}. "
        "Train the detector before running governance."
    )

LLM = (
    get_llm(ANOMALY_CRITIC_MODEL)
    #.with_structured_output(GovernanceFinding)
)

def normalize_anomaly_score(score, threshold, max_score):
    """
    Convert the Isolation Forest anomaly score
    into a calibrated 0-1 anomaly risk.

    Scores at or below the calibrated threshold
    receive 0 anomaly risk.

    Scores above the threshold increase linearly
    toward 1.0.
    """

    if max_score is None:
        raise ValueError(
            "Detector max_score has not been calibrated. "
            "Run tune_thresholds.py first."
        )

    if max_score <= threshold:
        raise ValueError(
            "Invalid calibration: max_score must be "
            "greater than threshold."
        )

    if score <= threshold:
        return 0.0

    normalized = (
        (score - threshold)
        / (max_score - threshold)
    )

    return float(
        min(normalized, 1.0)
    )

def analyze_anomaly(trace) -> GovernanceFinding:
    """
    Analyze a reasoning trace using a statistical anomaly detector.
    If an anomaly is detected, an LLM explains why.
    """

    # 1. Extract features
    features = extract_trace_features(trace)

    # Convert dict -> ordered feature vector
    feature_vector = [ features[name] for name in FEATURE_ORDER ]

    # 2. Score trace
    anomaly_score = DETECTOR.score(feature_vector)

    # print(f"{ANOMALY_DETECTOR} score: {anomaly_score:.4f}")

    is_anomaly = DETECTOR.predict(feature_vector)

    print("\n========== ANOMALY DEBUG ==========")
    print("IF score:", anomaly_score)
    print("IF threshold:", DETECTOR.threshold)
    print("IF anomaly:", is_anomaly)

    # 3. No anomaly -> no LLM call needed
    if not is_anomaly:
        return GovernanceFinding(
            critic="Anomaly",
            severity="Low",
            score=0.10,
            finding="No anomalous execution pattern detected.",
            evidence=(
                f"Isolation Forest classified the trace as normal "
                f"(detector score={anomaly_score:.4f})."
                f"threshold="
                f"{DETECTOR.threshold:.4f})."
            )
        )

    calibrated_score = normalize_anomaly_score(anomaly_score, DETECTOR.threshold, DETECTOR.max_score)

    print(
        f"Calibrated anomaly risk: "
        f"{calibrated_score:.4f}"
    )

    # 4. Anomaly detected -> explain with LLM
    prompt = ANOMALY_PROMPT.format(trace=trace, anomaly_score=anomaly_score, calibrated_anomaly_score=calibrated_score)

    finding = invoke_structured(LLM, prompt,  GovernanceFinding)

    if finding is None:
        finding = GovernanceFinding(
            critic="Anomaly",
            severity="Medium",
            score=0.5,
            finding="Anomaly evaluation unavailable.",
            evidence=(
                f"Isolation Forest detected an anomaly "
                f"(detector score={anomaly_score:.4f}), "
                f"but LLM evaluation failed."
                f"threshold="
                f"{DETECTOR.threshold:.4f}, "
                f"calibrated anomaly risk="
                f"{calibrated_score:.4f})."
            )
        )

    print("Anomaly Critic score:", finding.score)
    print("Anomaly Critic severity:", finding.severity)
    print("Anomaly Critic finding:", finding.finding)
    print("==================================\n")

    return finding
    