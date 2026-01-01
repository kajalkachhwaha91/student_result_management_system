from app.utils.intent_parser import detect_intent
from backend.app.db.connection import result_collection


def process_chat(message: str, user=None):
    print("📩 MESSAGE RECEIVED:", repr(message))

    intent = detect_intent(message)
    print("🧠 DETECTED INTENT:", intent)

def process_chat(message: str, user=None):
    intent = detect_intent(message)

    if intent == "MY_PERFORMANCE":
        if not user:
            return "Please login to view your performance 🔐"

        result = result_collection.find_one(
            {"student_id": user["id"]},
            {"_id": 0}
        )

        if not result:
            return "No result found for you ❌"

        return (
            f"📊 Your Performance:\n"
            f"Total Marks: {result.get('Total Marks')}\n"
            f"Percentage: {result.get('Percentage')}%\n"
            f"Grade: {result.get('Grade')}"
        )

    if intent == "CLASS_AVERAGE":
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": "$Percentage"}}}
        ]

        data = list(result_collection.aggregate(pipeline))
        if not data:
            return "No data available for class average"

        return f"📈 Class Average Percentage: {round(data[0]['avg'], 2)}%"

    return "Sorry, I didn’t understand that. Try asking about performance."
