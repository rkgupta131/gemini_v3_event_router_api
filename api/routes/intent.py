"""
Intent Classification Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import IntentClassificationRequest, IntentClassificationResponse, ModelInfo
from api.utils import get_model_info
from models.gemini_client import classify_intent

router = APIRouter()


@router.post("/intent/classify", response_model=IntentClassificationResponse)
async def classify_user_intent(request: IntentClassificationRequest):
    """
    Classify user intent from input text.
    
    Returns one of:
    - `webpage_build`: User wants to build a webpage
    - `chat`: General Q/A conversation
    - `greeting_only`: Simple greeting
    - `illegal`: Disallowed request
    - `other`: Other intent
    """
    try:
        label, metadata = classify_intent(
            request.user_text,
            model=request.model
        )
        
        model_name = metadata.get("model", "unknown")
        model_info_dict = get_model_info(model_name)
        
        return IntentClassificationResponse(
            label=label,
            explanation=metadata.get("explanation", ""),
            confidence=metadata.get("confidence", 0.0),
            model=model_name,  # Keep for backward compatibility
            model_info=ModelInfo(**model_info_dict),
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {str(e)}")

