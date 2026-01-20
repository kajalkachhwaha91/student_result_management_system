import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "model/intent_model.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "model/vectorizer.pkl"))

def detect_intent_ml(message: str):
    message = message.lower().strip() 
    X = vectorizer.transform([message])

    intent = model.predict(X)[0]

    # decision scores
    scores = model.decision_function(X)

    # convert scores → pseudo confidence (0–1)
    if scores.ndim == 1:
        confidence = 1 / (1 + np.exp(-abs(scores[0])))
    else:
        confidence = 1 / (1 + np.exp(-np.max(scores[0])))

    return intent, float(confidence)
