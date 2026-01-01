from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.chatbot_service import process_chat

router = APIRouter(prefix="/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat(req: ChatRequest):
    reply = process_chat(req.message)
    return {"reply": reply}
