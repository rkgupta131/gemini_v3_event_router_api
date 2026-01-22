"""
Chat Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import ChatRequest, ChatResponse, ModelInfo
from api.utils import get_model_info
from models.gemini_client import chat_response, get_smaller_model

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
        
        model_name = request.model or get_smaller_model()
        model_info_dict = get_model_info(model_name)
        
        return ChatResponse(
            response=response_text,
            model=model_name,  # Keep for backward compatibility
            model_info=ModelInfo(**model_info_dict)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat response generation failed: {str(e)}")

