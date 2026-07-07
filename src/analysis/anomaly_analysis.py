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

MODEL_PATH = Path("models/iforest.joblib")

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

def analyze_anomaly(trace) -> GovernanceFinding:
    """
    Analyze a reasoning trace using a statistical anomaly detector.
    If an anomaly is detected, an LLM explains why.
    """

    # 1. Extract features
    features = extract_trace_features(trace)

    # Convert dict -> ordered feature vector
    feature_vector = [
        features[name]
        for name in FEATURE_ORDER
    ]

    # 2. Score trace
    anomaly_score = DETECTOR.score(feature_vector)

    print(anomaly_score)
    is_anomaly = DETECTOR.predict(feature_vector)

    # 3. No anomaly -> no LLM call needed
    if not is_anomaly:
        return GovernanceFinding(
            critic="Anomaly",
            severity="Low",
            score=0.10,
            finding="No anomalous execution pattern detected.",
            evidence="Isolation Forest classified the trace as normal."
        )

    # 4. Anomaly detected -> explain with LLM
    prompt = ANOMALY_PROMPT.format(
        trace=trace,
        anomaly_score=anomaly_score
    )

    finding = invoke_structured(LLM, prompt,  GovernanceFinding)

    if finding is None:
        finding = GovernanceFinding(
            critic="Anomaly",
            severity="Medium",
            score=0.5,
            finding="Anomaly evaluation unavailable.",
            evidence="LLM failed after retries."
        )

    return finding
    