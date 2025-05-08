from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from services.chatbot_service import generate_chat_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        return {"error": "No message provided."}
    return generate_chat_response(request.message)
