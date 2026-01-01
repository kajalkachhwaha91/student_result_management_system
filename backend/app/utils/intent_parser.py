import spacy

nlp = spacy.load("en_core_web_sm")

def detect_intent(message: str):
    msg = message.lower().strip()   # ✅ normalize

    # CLASS AVERAGE
    if "average" in msg and "class" in msg:
        return "CLASS_AVERAGE"

    # ATTENDANCE (handle typo)
    if "attendance" in msg or "attendence" in msg:
        return "ATTENDANCE"

    # NLP fallback for performance
    doc = nlp(msg)
    for token in doc:
        if token.lemma_ in ["performance", "result", "mark", "score"]:
            return "MY_PERFORMANCE"

    return "UNKNOWN"
