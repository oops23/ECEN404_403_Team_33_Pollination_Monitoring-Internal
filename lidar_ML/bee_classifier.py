# bee_classifier.py

import joblib
import os
from feature_extractor import extract_features

class BeeClassifier:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")
        # load trained model
        self.model = joblib.load(model_path)

    def predict(self, event):
        # extract features from event
        features = extract_features(event)

        # remove event_id and label
        # numeric_features = features[1:-1]
        numeric_features = features[1:14] 

        # model expects 2D input
        prediction = self.model.predict([numeric_features])[0]
        probability = self.model.predict_proba([numeric_features])[0]

        lidar_conf = probability[1]

        if prediction == 1:
            label = "bee"
        else:
            label = "not_bee"

        return label, lidar_conf