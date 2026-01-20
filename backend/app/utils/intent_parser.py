from backend.ml.intent_classifier import detect_intent_ml

CONFIDENCE_THRESHOLD = 0.6

def detect_intent(message: str):
    intent, confidence = detect_intent_ml(message)

    if confidence < CONFIDENCE_THRESHOLD:
        return "UNKNOWN"

    return intent
