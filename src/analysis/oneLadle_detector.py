import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib
from .embedding import embed


class OneLadleDetector:

    def __init__(
        self,
        k=5,
        window_size=5,
        threshold_percentile=95,
        top_fraction=0.10,
    ):
        self.k = k
        self.window_size = window_size
        self.threshold_percentile = threshold_percentile
        self.top_fraction = top_fraction

        self.nn = NearestNeighbors(
            n_neighbors=k,
            metric="cosine"
        )

        self.threshold = None
        self.best_f1 = None

    def _create_windows(self, trace):

        lines = [
            line.strip()
            for line in trace.split("\n")
            if line.strip()
        ]

        if len(lines) <= self.window_size:
            return ["\n".join(lines)]

        windows = []

        for i in range(len(lines) - self.window_size + 1):
            windows.append(
                "\n".join(lines[i:i + self.window_size])
            )

        return windows

    def _aggregate_window_scores(self, window_scores):

        """
        Convert window-level anomaly scores into one trace-level score.

        Instead of taking only the single most anomalous window,
        average the highest-scoring fraction of windows.

        This makes the detector sensitive to sustained anomalous
        behaviour rather than one unusual semantic window.
        """

        if len(window_scores) == 0:
            return 0.0

        window_scores = np.asarray(window_scores)

        # Number of windows to keep
        n_top = max(
            1,
            int(np.ceil(len(window_scores) * self.top_fraction))
        )

        # Highest-scoring windows
        top_scores = np.sort(window_scores)[-n_top:]

        return float(np.mean(top_scores))

    def fit(self, traces):

        lengths = [len(t) for t in traces]
        line_counts = [len(t.splitlines()) for t in traces]

        print(f"Loaded {len(traces)} traces.")
        print(f"Average characters: {np.mean(lengths):.0f}")
        print(f"Maximum characters: {max(lengths)}")
        print(f"Average lines: {np.mean(line_counts):.1f}")
        print(f"Maximum lines: {max(line_counts)}")

        reference_windows = []
        trace_window_counts = []

        for trace in traces:

            windows = self._create_windows(trace)

            trace_window_counts.append(len(windows))
            reference_windows.extend(windows)

        print(f"Created {len(reference_windows)} windows.")
        print("Embedding all windows...")

        embeddings = embed(reference_windows)

        print("Embeddings computed.")
        print("Building nearest-neighbor index...")

        self.nn.fit(embeddings)

        print("Nearest-neighbor index built.")
        print("Computing training scores...")

        scores = []

        start = 0

        for n_windows in trace_window_counts:

            end = start + n_windows

            trace_embeddings = embeddings[start:end]

            distances, _ = self.nn.kneighbors(
                trace_embeddings
            )

            # Distance of each window from its k nearest
            # reference windows
            window_scores = np.mean(distances, axis=1)

            # NEW: aggregate the worst 10% rather than max
            score = self._aggregate_window_scores(
                window_scores
            )

            scores.append(score)

            start = end

        self.threshold = np.percentile(
            scores,
            self.threshold_percentile
        )

        print(
            f"Trace score mean = {np.mean(scores):.4f}"
        )

        print(
            f"Trace score std = {np.std(scores):.4f}"
        )

        print(
            f"Trace score min = {np.min(scores):.4f}"
        )

        print(
            f"Trace score max = {np.max(scores):.4f}"
        )

        print(
            f"Threshold = {self.threshold:.4f}"
        )

    def score(self, trace):

        windows = self._create_windows(trace)

        embeddings = embed(windows)

        distances, _ = self.nn.kneighbors(
            embeddings
        )

        window_scores = np.mean(distances, axis=1)

        return self._aggregate_window_scores(
            window_scores
        )

    def predict(self, trace, threshold=None):

        if threshold is None:
            threshold = self.threshold

        return self.score(trace) > threshold

    def save(self, path):

        joblib.dump(
            {
                "nn": self.nn,
                "threshold": self.threshold,
                "k": self.k,
                "window_size": self.window_size,
                "threshold_percentile": self.threshold_percentile,
                "top_fraction": self.top_fraction,
                "threshold_source": "validation",
                "best_f1": self.best_f1,
            },
            path
        )

    def load(self, path):

        data = joblib.load(path)

        self.nn = data["nn"]
        self.threshold = data["threshold"]
        self.k = data["k"]
        self.window_size = data["window_size"]

        self.threshold_percentile = data.get(
            "threshold_percentile",
            95
        )

        self.top_fraction = data.get(
            "top_fraction",
            0.10
        )

        self.best_f1 = data.get(
            "best_f1",
            None
        )