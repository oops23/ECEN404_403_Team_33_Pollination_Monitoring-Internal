# bee_classifier.py

import numpy as np

class BeeClassifier:
    """
    Basic placeholder classifier.
    Later you can load a trained ML model here.
    """

    def __init__(self):
        # Later you can load model weights here
        pass

    def extract_features(self, event):
        """
        Convert raw event JSON into feature vector.
        For now we compute simple stats.
        """
        distance_series = np.array(event["distance_series"])

        mean_dist = np.mean(distance_series)
        std_dist = np.std(distance_series)
        duration = event["end_time"] - event["start_time"]
        num_scans = event["num_scans"]

        return np.array([mean_dist, std_dist, duration, num_scans])

    def predict(self, event):
        """
        Return True if event is bee.
        For now always True.
        Replace with real ML later.
        """
        features = self.extract_features(event)

        # Placeholder rule
        return True