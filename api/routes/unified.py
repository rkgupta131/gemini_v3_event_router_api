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
from models.unified_client import (
    classify_intent_unified,
    classify_page_type_unified,
    analyze_query_detail_unified,
    chat_response_unified
)
from data.page_types_reference import get_page_type_by_key, PAGE_TYPES
from data.questionnaire_config import get_questionnaire, has_questionnaire
from data.page_categories import get_all_categories
from pydantic import BaseModel, Field

router = APIRouter()


class UnifiedRequest(BaseModel):
    """Unified request model for all operations"""
    action: Optional[str] = Field(None, description="Optional action override. If not provided, action will be auto-detected from user input.")
    user_text: Optional[str] = Field(None, description="User input text")
    user_query: Optional[str] = Field(None, description="User query (for project generation). If both user_text and user_query are provided, user_query takes precedence.")
    page_type_key: Optional[str] = Field(None, description="Page type key (for project generation, questionnaire, page type reference)")
    questionnaire_answers: Optional[Dict[str, Union[str, List[str]]]] = Field(None, description="Questionnaire answers (for project generation)")
    wizard_inputs: Optional[Dict[str, str]] = Field(None, description="Wizard inputs (for project generation)")
    instruction: Optional[str] = Field(None, description="Modification instruction (for project modification)")
    project_json: Optional[Dict[str, Any]] = Field(None, description="Project JSON (for project modification)")
    project_id: Optional[str] = Field(None, description="Project ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    model: Optional[str] = Field(None, description="Optional model override (deprecated)")
    model_family: Optional[str] = Field(None, description="Model family: Gemini, Anthropic, or OpenAI (defaults to Gemini)")
    model_name: Optional[str] = Field(None, description="Specific model name (e.g., claude-opus-4-5-20251101). If provided, model_family will be inferred from this.")


class UnifiedResponse(BaseModel):
    """Unified response model"""
    action: str = Field(..., description="Action that was performed")
    success: bool = Field(..., description="Whether the action was successful")
    data: Dict[str, Any] = Field(..., description="Response data")
    error: Optional[str] = Field(None, description="Error message if action failed")


@router.post("/stream", response_model=UnifiedResponse)
async def stream_action(request: UnifiedRequest):
    """
    Unified endpoint for all API operations.
    
    Action is auto-detected from user input using LLM intent classification.
    The detected action is returned in the response.
    
    Supported actions (auto-detected):
    - generate_project: User wants to build/create a webpage/project
    - modify_project: User wants to modify/change/update an existing project
    - chat: General Q/A, greetings, or other conversations
    
    **Example Request (Action Auto-Detected):**
    ```json
    {
      "user_query": "Generate a multi-page fitness tracking web application",
      "model_family": "Anthropic"
    }
    ```
    
    **Example Response:**
    ```json
    {
      "action": "generate_project",
      "success": true,
      "data": {
        "project_id": "proj_12345",
        "project": {...},
        "model_info": {
          "model_family": "Anthropic",
          "model_name": "claude-opus-4-5-20251101"
        }
      }
    }
    ```
    
    **Action Detection Logic:**
    - If user input contains modification keywords (modify, change, update, edit) AND project_id/project_json is provided → modify_project
    - If intent classification returns "webpage_build" → generate_project
    - Otherwise → chat
    """
    try:
        # Extract model_family from request
        # Priority: model_family > model_name (infer from model_name) > default to Gemini
        from router.router_config import normalize_model_family
        from api.utils import get_model_info
        from models.unified_client import classify_intent_unified
        
        if request.model_family:
            model_family = request.model_family
        elif request.model_name:
            # Infer model_family from model_name
            model_info = get_model_info(request.model_name)
            model_family = model_info.get("model_family", "Gemini")
        else:
            model_family = "Gemini"
        
        # Normalize to internal key for routing
        model_key = normalize_model_family(model_family)
        
        # Auto-detect action if not provided
        if request.action:
            action = request.action.lower()
        else:
            # Get user input (prefer user_query, fallback to user_text)
            user_input = request.user_query or request.user_text or request.instruction
            
            if not user_input:
                raise HTTPException(
                    status_code=400, 
                    detail="Either user_query, user_text, or instruction must be provided when action is not specified"
                )
            
            # Check if it's a modification request
            modification_keywords = ["modify", "change", "update", "edit", "alter", "adjust"]
            user_input_lower = user_input.lower()
            is_modification = any(keyword in user_input_lower for keyword in modification_keywords)
            
            if is_modification and (request.project_id or request.project_json):
                action = "modify_project"
            else:
                # Classify intent to determine action
                intent_label, intent_metadata = classify_intent_unified(user_input, model_name=model_key)
                
                # Map intent label to action
                if intent_label == "webpage_build":
                    action = "generate_project"
                elif intent_label == "illegal":
                    return UnifiedResponse(
                        action="chat",
                        success=False,
                        data={},
                        error="Request contains potentially illegal content"
                    )
                elif intent_label == "greeting_only":
                    action = "chat"
                else:  # chat, other
                    action = "chat"
        
        # Route to appropriate handler
        if action == "classify_intent":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for classify_intent")
            
            label, metadata = classify_intent_unified(request.user_text, model_name=model_key)
            model_used = metadata.get("model", "unknown")
            model_info_dict = get_model_info(model_used)
            
            return UnifiedResponse(
                action="classify_intent",
                success=True,
                data={
                    "label": label,
                    "explanation": metadata.get("explanation", ""),
                    "confidence": metadata.get("confidence", 0.0),
                    "model": model_key,
                    "model_info": model_info_dict,
                    "metadata": metadata
                }
            )
        
        elif action == "classify_page_type":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for classify_page_type")
            
            page_type_key, metadata = classify_page_type_unified(request.user_text, model_name=model_key)
            model_used = metadata.get("model", "unknown")
            model_info_dict = get_model_info(model_used)
            
            return UnifiedResponse(
                action="classify_page_type",
                success=True,
                data={
                    "page_type": page_type_key,
                    "explanation": metadata.get("explanation", ""),
                    "confidence": metadata.get("confidence", 0.0),
                    "model": model_key,
                    "model_info": model_info_dict,
                    "metadata": metadata
                }
            )
        
        elif action == "analyze_query":
            if not request.user_text:
                raise HTTPException(status_code=400, detail="user_text is required for analyze_query")
            
            needs_followup, confidence = analyze_query_detail_unified(request.user_text, model_name=model_key)
            from router.router_config import get_router_model
            model_used = get_router_model(model_family)
            model_info_dict = get_model_info(model_used)
            
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
                    "model": model_key,
                    "model_info": model_info_dict
                }
            )
        
        elif action == "chat":
            # Use user_text or user_query for chat
            user_input = request.user_text or request.user_query
            if not user_input:
                raise HTTPException(status_code=400, detail="user_text or user_query is required for chat")
            
            response_text = chat_response_unified(user_input, model_name=model_key)
            from router.router_config import get_router_model
            model_used = get_router_model(model_family)
            model_info_dict = get_model_info(model_used)
            
            return UnifiedResponse(
                action="chat",
                success=True,
                data={
                    "response": response_text,
                    "model": model_key,
                    "model_info": model_info_dict
                }
            )
        
        elif action == "generate_project":
            # Import here to avoid circular imports
            from api.routes.project import generate_project
            from api.models import ProjectGenerationRequest
            
            # Use user_query if provided, otherwise use user_text
            user_query = request.user_query or request.user_text
            if not user_query:
                raise HTTPException(status_code=400, detail="user_query or user_text is required for generate_project")
            
            project_request = ProjectGenerationRequest(
                user_query=user_query,
                page_type_key=request.page_type_key,
                questionnaire_answers=request.questionnaire_answers,
                wizard_inputs=request.wizard_inputs,
                project_id=request.project_id,
                conversation_id=request.conversation_id,
                model_family=model_family
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
            
            # Use instruction if provided, otherwise use user_text or user_query
            instruction = request.instruction or request.user_text or request.user_query
            if not instruction:
                raise HTTPException(status_code=400, detail="instruction, user_text, or user_query is required for modify_project")
            
            mod_request = ProjectModificationRequest(
                instruction=instruction,
                project_json=request.project_json,
                project_id=request.project_id,
                conversation_id=request.conversation_id,
                model_family=model_family
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

