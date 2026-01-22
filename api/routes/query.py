"""
Query Analysis Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import QueryAnalysisRequest, QueryAnalysisResponse, ModelInfo
from api.utils import get_model_info
from models.gemini_client import analyze_query_detail, get_smaller_model

router = APIRouter()


@router.post("/query/analyze", response_model=QueryAnalysisResponse)
async def analyze_query(request: QueryAnalysisRequest):
    """
    Analyze if a user query has enough detail or needs follow-up questions.
    
    Returns:
    - `needs_followup`: True if the query is vague and needs questionnaire
    - `confidence`: Confidence score of the analysis
    """
    try:
        needs_followup, confidence = analyze_query_detail(
            request.user_text,
            model=request.model
        )
        
        # Get explanation from a more detailed analysis if needed
        explanation = (
            "Query needs follow-up questions to gather more details"
            if needs_followup
            else "Query has sufficient detail to proceed"
        )
        
        model_name = request.model or get_smaller_model()
        model_info_dict = get_model_info(model_name)
        
        return QueryAnalysisResponse(
            needs_followup=needs_followup,
            explanation=explanation,
            confidence=confidence,
            model=model_name,  # Keep for backward compatibility
            model_info=ModelInfo(**model_info_dict)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")

