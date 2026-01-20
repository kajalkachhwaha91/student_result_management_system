from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.app.services.chatbot_service import process_chat
from backend.app.utils.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    reply = process_chat(req.message, user)
    return {"reply": reply}
