"""
Questionnaire Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import QuestionnaireResponse, Question
from data.questionnaire_config import get_questionnaire, has_questionnaire

router = APIRouter()


@router.get("/questionnaire/{page_type_key}", response_model=QuestionnaireResponse)
async def get_questionnaire_for_page_type(page_type_key: str):
    """
    Get questionnaire for a specific page type.
    
    Returns a list of questions that help gather requirements when user input is vague.
    """
    try:
        questionnaire = get_questionnaire(page_type_key)
        
        if not questionnaire:
            raise HTTPException(
                status_code=404,
                detail=f"No questionnaire found for page type: {page_type_key}"
            )
        
        questions = [
            Question(**q) for q in questionnaire.get("questions", [])
        ]
        
        return QuestionnaireResponse(
            page_type=page_type_key,
            questions=questions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get questionnaire: {str(e)}")


@router.get("/questionnaire/{page_type_key}/exists")
async def check_questionnaire_exists(page_type_key: str):
    """
    Check if a questionnaire exists for a page type.
    """
    try:
        exists = has_questionnaire(page_type_key)
        return {"page_type": page_type_key, "has_questionnaire": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check questionnaire: {str(e)}")

