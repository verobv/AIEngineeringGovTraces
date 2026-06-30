from sklearn.ensemble import IsolationForest
from pathlib import Path
import joblib

class TraceAnomalyDetector:
    """
    Wrapper around anomaly detection models.

    Supported models:
        - Isolation Forest (implemented)
        - LADLE (placeholder)
    """

    def __init__(
        self,
        detector_type: str = "iforest",
        contamination: float = 0.05,
        random_state: int = 42,
    ):
        self.detector_type = detector_type.lower()

        if self.detector_type == "iforest":
            self.model = IsolationForest(
                contamination=contamination,
                random_state=random_state,
            )

        elif self.detector_type == "ladle":
            # TODO: Replace with LADLE implementation
            self.model = None

        else:
            raise ValueError(
                f"Unsupported detector '{detector_type}'. "
                "Choose 'iforest' or 'ladle'."
            )

    def fit(self, X):
        """Train the anomaly detector."""

        if self.detector_type == "iforest":
            self.model.fit(X)

        elif self.detector_type == "ladle":
            raise NotImplementedError(
                "LADLE training not implemented yet."
            )

    def score(self, x):
        """
        Returns an anomaly score.
        Higher values indicate more anomalous traces.
        """

        if self.detector_type == "iforest":
            # Isolation Forest:
            # decision_function -> higher = more normal
            raw = self.model.decision_function([x])[0]

            # Invert so larger means more anomalous
            return -raw

        elif self.detector_type == "ladle":
            raise NotImplementedError(
                "LADLE scoring not implemented yet."
            )

    def predict(self, x):
        """
        Returns True if the trace is anomalous.
        """

        if self.detector_type == "iforest":
            return self.model.predict([x])[0] == -1

        elif self.detector_type == "ladle":
            raise NotImplementedError

    def save(self, path: str):
        """
        Save the trained detector to disk.
        """

        if self.detector_type != "iforest":
            raise NotImplementedError(
                "Saving not implemented for LADLE."
            )

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.model, path)

    def load(self, path: str):
        """
        Load a trained detector from disk.
        """

        if self.detector_type != "iforest":
            raise NotImplementedError(
                "Loading not implemented for LADLE."
            )

        self.model = joblib.load(path)