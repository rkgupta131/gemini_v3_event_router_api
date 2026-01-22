"""
Chat Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import ChatRequest, ChatResponse
from models.gemini_client import chat_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate a chat response for general Q/A conversations.
    
    This endpoint is used when the user intent is classified as 'chat'.
    Returns a conversational response (max 4 sentences).
    """
    try:
        response_text = chat_response(
            request.user_text,
            model=request.model
        )
        
        return ChatResponse(
            response=response_text,
            model=request.model or "gemini-2.0-flash-lite"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat response generation failed: {str(e)}")

