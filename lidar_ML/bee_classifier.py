# bee_classifier.py

import joblib
import os
from feature_extractor import extract_features

class BeeClassifier:
    def __init__(self, model_path, threshold=0.4):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")
        # load trained model
        self.model = joblib.load(model_path)
        self.threshold = threshold

    def predict(self, event):
        # extract features from event
        features = extract_features(event)

        # remove event_id and label
        # numeric_features = features[1:-1]
        numeric_features = features[1:14] 

        # model expects 2D input
        lidar_conf = self.model.predict_proba([numeric_features])[0][1]

        if lidar_conf > self.threshold:
            label = "bee"
        else:
            label = "not_bee"

        return label, lidar_conf