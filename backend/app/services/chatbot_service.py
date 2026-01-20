# backend/app/services/chatbot_service.py

from app.utils.intent_parser import detect_intent
from backend.app.db.connection import result_collection

def process_chat(message: str, user=None):
    intent = detect_intent(message)

    if intent == "GREETING":
        return "Hello!!😊 How can I help you, today?"

    if intent == "MY_PERFORMANCE":
        if not user:
            return "Please login to view your performance 🔐"

        if user["role"] != "Student":
            return "Only students can view performance 📚"

        result = result_collection.find_one(
            {"student_email": user["email"]},
            {"_id": 0}
        )

        if not result:
            return "No result found for you ❌"

        return (
            f"📊 Your Performance:\n"
            f"Math: {result.get('math')}\n"
            f"Science: {result.get('science')}\n"
            f"English: {result.get('english')}\n"
            f"Total: {result.get('total')}\n"
            f"Percentage: {round(result.get('percentage', 0), 2)}%\n"
            f"Grade: {result.get('grade')}"
        )

    if intent == "CLASS_AVERAGE":
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$percentage"}}}]
        data = list(result_collection.aggregate(pipeline))
        return f"📈 Class Average: {round(data[0]['avg'], 2)}%" if data else "No data available"

    return "Sorry, I didn’t understand that 🤔"
