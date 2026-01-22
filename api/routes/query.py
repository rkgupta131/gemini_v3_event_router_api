"""
Query Analysis Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import QueryAnalysisRequest, QueryAnalysisResponse
from models.gemini_client import analyze_query_detail

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
        
        return QueryAnalysisResponse(
            needs_followup=needs_followup,
            explanation=explanation,
            confidence=confidence,
            model=request.model or "gemini-2.0-flash-lite"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")

