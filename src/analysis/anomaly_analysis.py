"""
Extracts engineered features and uses an anomaly detection model.
"""

from pathlib import Path

from src.analysis.feature_extraction import extract_trace_features
from src.analysis.anomaly_detector import TraceAnomalyDetector
from src.traces.schemas import GovernanceFinding
from src.prompts import ANOMALY_PROMPT
from src.utils import get_llm
from src.config import (
    ANOMALY_CRITIC_MODEL,
    ANOMALY_DETECTOR
)

MODEL_PATH = Path("models/isolation_forest.joblib")


def analyze_anomaly(trace) -> GovernanceFinding:
    """
    Analyze a reasoning trace using a statistical anomaly detector.
    If an anomaly is detected, an LLM explains why.
    """

    # 1. Extract features
    features = extract_trace_features(trace)

    # Convert dict -> ordered feature vector
    feature_vector = list(features.values())

    # 2. Load detector
    detector = TraceAnomalyDetector(detector_type=ANOMALY_DETECTOR)
    detector.load(MODEL_PATH)

    # 3. Score trace
    raw_score = detector.score(feature_vector)

    # Map to [0, 1] (simple clipping example)
    anomaly_score = max(0.0, min(1.0, (raw_score + 1.0) / 2.0))

    is_anomaly = detector.predict(feature_vector)

    # 4. No anomaly -> no LLM call needed
    if not is_anomaly:
        return GovernanceFinding(
            critic="Anomaly",
            severity="LOW",
            score=max(0.0, anomaly_score),
            finding="No anomalous execution pattern detected.",
            evidence="Isolation Forest classified the trace as normal."
        )

    # 5. Anomaly detected -> explain with LLM
    llm = (
        get_llm(ANOMALY_CRITIC_MODEL)
        .with_structured_output(GovernanceFinding)
    )

    prompt = ANOMALY_PROMPT.format(
        trace=trace,
        anomaly_score=anomaly_score
    )

    finding = llm.invoke(prompt)

    return finding