from pathlib import Path
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


class TraceAnomalyDetector:
    """
    Generic anomaly detector wrapper.

    Supported detectors

    - Isolation Forest
    - Local Outlier Factor
    """

    def __init__(
        self,
        detector_type="iforest",
        contamination=0.05,
        random_state=42,
    ):

        self.detector_type = detector_type.lower()

        self.threshold = 0.0
        self.best_f1 = None

        if self.detector_type == "iforest":

            self.model = IsolationForest(
                contamination=contamination,
                random_state=random_state,
            )

        elif self.detector_type == "lof":

            self.model = LocalOutlierFactor(
                contamination=contamination,
                novelty=True,
            )

        else:

            raise ValueError(
                f"Unsupported detector '{detector_type}'"
            )

    def fit(self, X):

        self.model.fit(X)

    def score(self, x):
        """
        Higher = more anomalous.
        """

        raw = self.model.decision_function([x])[0]

        return -raw

    def predict(self, x, threshold=None):

        if threshold is None:
            threshold = self.threshold

        return self.score(x) >= threshold

    def save(self, path):

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            {
                "model": self.model,
                "threshold": self.threshold,
                "best_f1": self.best_f1,
                "detector_type": self.detector_type,
            },
            path,
        )

    def load(self, path):

        data = joblib.load(path)

        self.model = data["model"]

        self.threshold = data.get("threshold", 0.0)

        self.best_f1  = data.get("best_f1")

        self.detector_type = data.get(
            "detector_type",
            self.detector_type,
        )