from fastapi import APIRouter, Depends
from service.chat_service import chat, reset_chat
from schemas.chat import ChatMessage
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from core.security import get_current_user
from service.user_log import insert_user_log

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(
    message: ChatMessage, user: str = Depends(get_current_user)
) -> StreamingResponse:
    user_id = user.id
    return StreamingResponse(chat(message, user_id), media_type="text/event-stream")


@router.post("/chat/reset")
async def reset_chat_endpoint(
    user: str = Depends(get_current_user),
) -> StreamingResponse:
    user_id = user.id
    result = await reset_chat(user_id)
    return JSONResponse(content={"message": result})
