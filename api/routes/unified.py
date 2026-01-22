"""
Unified API Endpoint - Single endpoint for all operations
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, Union, List
from api.models import (
    IntentClassificationResponse,
    PageTypeClassificationResponse,
    QueryAnalysisResponse,
    ChatResponse,
    ProjectGenerationResponse,
    ProjectModificationResponse,
    QuestionnaireResponse,
    CategoriesResponse,
    PageTypeReferenceResponse,
    ModelInfo
)
from api.utils import get_model_info
from models.gemini_client import (
    classify_intent,
    classify_page_type,
    analyze_query_detail,
    chat_response,
    get_smaller_model
)
from data.page_types_reference import get_page_type_by_key, PAGE_TYPES
from data.questionnaire_config import get_questionnaire, has_questionnaire
from data.page_categories import get_all_categories
from pydantic import BaseModel, Field

router = APIRouter()


class UnifiedRequest(BaseModel):
    """Unified request model for all operations"""
    action: str = Field(..., description="Action to perform: classify_intent, classify_page_type, analyze_query, chat, generate_project, modify_project, get_questionnaire, get_categories, get_page_type")
    user_text: Optional[str] = Field(None, description="User input text (required for most actions)")
    user_query: Optional[str] = Field(None, description="User query (for project generation)")
    page_type_key: Optional[str] = Field(None, description="Page type key (for project generation, questionnaire, page type reference)")
    questionnaire_answers: Optional[Dict[str, Union[str, List[str]]]] = Field(None, description="Questionnaire answers (for project generation)")
    wizard_inputs: Optional[Dict[str, str]] = Field(None, description="Wizard inputs (for project generation)")
    instruction: Optional[str] = Field(None, description="Modification instruction (for project modification)")
    project_json: Optional[Dict[str, Any]] = Field(None, description="Project JSON (for project modification)")
    project_id: Optional[str] = Field(None, description="Project ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    model: Optional[str] = Field(None, description="Optional model override")


class UnifiedResponse(BaseModel):
    """Unified response model"""
    action: str = Field(..., description="Action that was performed")
    success: bool = Field(..., description="Whether the action was successful")
    data: Dict[str, Any] = Field(..., description="Response data")
    error: Optional[str] = Field(None, description="Error message if action failed")


@router.post("/execute", response_model=UnifiedResponse)
async def execute_action(request: UnifiedRequest):
    """
    Unified endpoint for all API operations.
    
    This single endpoint handles all operations:
    - classify_intent: Classify user intent
    - classify_page_type: Classify page type
    - analyze_query: Analyze query detail
    - chat: Get chat response
    - generate_project: Generate a project
    - modify_project: Modify an existing project
    - get_questionnaire: Get questionnaire for page type
    - get_categories: Get all categories
    - get_page_type: Get page type reference
    
    **Example Request:**
    ```json
    {
      "action": "classify_intent",
      "user_text": "I want to build a CRM"
    }
    ```
    
    **Example Response:**
    ```json
    {
      "action": "classify_intent",
      "success": true,
      "data": {
        "label": "webpage_build",
        "explanation": "...",
        "confidence": 0.95,
        "model_info": {
          "model_family": "Gemini",
          "model_name": "gemini-2.0-flash-lite"
        }
      }
    }
    ```
    """
    try:
        action = request.action.lower()
        
        # Route to appropriate handler
        if action == "classify_intent":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for classify_intent")
            
            label, metadata = classify_intent(request.user_text, model=request.model)
            model_name = metadata.get("model", "unknown")
            model_info_dict = get_model_info(model_name)
            
            return UnifiedResponse(
                action="classify_intent",
                success=True,
                data={
                    "label": label,
                    "explanation": metadata.get("explanation", ""),
                    "confidence": metadata.get("confidence", 0.0),
                    "model": model_name,
                    "model_info": model_info_dict,
                    "metadata": metadata
                }
            )
        
        elif action == "classify_page_type":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for classify_page_type")
            
            page_type_key, metadata = classify_page_type(request.user_text, model=request.model)
            model_name = metadata.get("model", "unknown")
            model_info_dict = get_model_info(model_name)
            
            return UnifiedResponse(
                action="classify_page_type",
                success=True,
                data={
                    "page_type": page_type_key,
                    "explanation": metadata.get("explanation", ""),
                    "confidence": metadata.get("confidence", 0.0),
                    "model": model_name,
                    "model_info": model_info_dict,
                    "metadata": metadata
                }
            )
        
        elif action == "analyze_query":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for analyze_query")
            
            needs_followup, confidence = analyze_query_detail(request.user_text, model=request.model)
            model_name = request.model or get_smaller_model()
            model_info_dict = get_model_info(model_name)
            
            explanation = (
                "Query needs follow-up questions to gather more details"
                if needs_followup
                else "Query has sufficient detail to proceed"
            )
            
            return UnifiedResponse(
                action="analyze_query",
                success=True,
                data={
                    "needs_followup": needs_followup,
                    "explanation": explanation,
                    "confidence": confidence,
                    "model": model_name,
                    "model_info": model_info_dict
                }
            )
        
        elif action == "chat":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for chat")
            
            response_text = chat_response(request.user_text, model=request.model)
            model_name = request.model or get_smaller_model()
            model_info_dict = get_model_info(model_name)
            
            return UnifiedResponse(
                action="chat",
                success=True,
                data={
                    "response": response_text,
                    "model": model_name,
                    "model_info": model_info_dict
                }
            )
        
        elif action == "generate_project":
            # Import here to avoid circular imports
            from api.routes.project import generate_project
            from api.models import ProjectGenerationRequest
            
            if not request.user_query:
                raise HTTPException(status_code=400, detail="user_query is required for generate_project")
            
            project_request = ProjectGenerationRequest(
                user_query=request.user_query,
                page_type_key=request.page_type_key,
                questionnaire_answers=request.questionnaire_answers,
                wizard_inputs=request.wizard_inputs,
                project_id=request.project_id,
                conversation_id=request.conversation_id
            )
            
            project_response = await generate_project(project_request)
            
            return UnifiedResponse(
                action="generate_project",
                success=True,
                data=project_response.dict()
            )
        
        elif action == "modify_project":
            from api.routes.project import modify_project
            from api.models import ProjectModificationRequest
            
            if not request.instruction:
                raise HTTPException(status_code=400, detail="instruction is required for modify_project")
            
            mod_request = ProjectModificationRequest(
                instruction=request.instruction,
                project_json=request.project_json,
                project_id=request.project_id,
                conversation_id=request.conversation_id
            )
            
            mod_response = await modify_project(mod_request)
            
            return UnifiedResponse(
                action="modify_project",
                success=True,
                data=mod_response.dict()
            )
        
        elif action == "get_questionnaire":
            if not request.page_type_key:
                raise HTTPException(status_code=400, detail="page_type_key is required for get_questionnaire")
            
            questionnaire = get_questionnaire(request.page_type_key)
            
            if not questionnaire:
                raise HTTPException(
                    status_code=404,
                    detail=f"No questionnaire found for page type: {request.page_type_key}"
                )
            
            from api.models import Question
            questions = [Question(**q) for q in questionnaire.get("questions", [])]
            
            return UnifiedResponse(
                action="get_questionnaire",
                success=True,
                data={
                    "page_type": request.page_type_key,
                    "questions": [q.dict() for q in questions]
                }
            )
        
        elif action == "get_categories":
            categories_dict = get_all_categories()
            from api.models import CategoryInfo
            
            categories_info = {
                key: CategoryInfo(**info).dict()
                for key, info in categories_dict.items()
            }
            
            return UnifiedResponse(
                action="get_categories",
                success=True,
                data={"categories": categories_info}
            )
        
        elif action == "get_page_type":
            if not request.page_type_key:
                raise HTTPException(status_code=400, detail="page_type_key is required for get_page_type")
            
            page_type_info = get_page_type_by_key(request.page_type_key)
            
            if page_type_info:
                from api.models import PageTypeInfo
                return UnifiedResponse(
                    action="get_page_type",
                    success=True,
                    data={
                        "page_type": PageTypeInfo(**page_type_info).dict(),
                        "available_types": list(PAGE_TYPES.keys())
                    }
                )
            else:
                return UnifiedResponse(
                    action="get_page_type",
                    success=True,
                    data={
                        "page_type": None,
                        "available_types": list(PAGE_TYPES.keys())
                    }
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action: {request.action}. Supported actions: classify_intent, classify_page_type, analyze_query, chat, generate_project, modify_project, get_questionnaire, get_categories, get_page_type"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return UnifiedResponse(
            action=request.action,
            success=False,
            data={},
            error=str(e)
        )

