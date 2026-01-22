"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# ============================================================================
# Model Information Models
# ============================================================================

class ModelInfo(BaseModel):
    """Standardized model information for frontend compatibility"""
    model_family: str = Field(..., description="Model family (e.g., 'Gemini', 'Anthropic')")
    model_name: str = Field(..., description="Specific model name (e.g., 'gemini-2.0-flash-lite', 'gemini-3-pro-preview')")


# ============================================================================
# Intent Classification Models
# ============================================================================

class IntentClassificationRequest(BaseModel):
    """Request model for intent classification"""
    user_text: str = Field(..., description="User input text to classify")
    model: Optional[str] = Field(None, description="Optional model override")


class IntentClassificationResponse(BaseModel):
    """Response model for intent classification"""
    label: str = Field(..., description="Intent label: webpage_build, chat, greeting_only, illegal, other")
    explanation: str = Field(..., description="Explanation of the classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    model: str = Field(..., description="Model used for classification (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# ============================================================================
# Page Type Classification Models
# ============================================================================

class PageTypeClassificationRequest(BaseModel):
    """Request model for page type classification"""
    user_text: str = Field(..., description="User input text to classify")
    model: Optional[str] = Field(None, description="Optional model override")


class PageTypeClassificationResponse(BaseModel):
    """Response model for page type classification"""
    page_type: str = Field(..., description="Page type key")
    explanation: str = Field(..., description="Explanation of the classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    model: str = Field(..., description="Model used for classification (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# ============================================================================
# Query Analysis Models
# ============================================================================

class QueryAnalysisRequest(BaseModel):
    """Request model for query detail analysis"""
    user_text: str = Field(..., description="User query to analyze")
    model: Optional[str] = Field(None, description="Optional model override")


class QueryAnalysisResponse(BaseModel):
    """Response model for query analysis"""
    needs_followup: bool = Field(..., description="Whether follow-up questions are needed")
    explanation: str = Field(..., description="Explanation of the analysis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    model: str = Field(..., description="Model used for analysis (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")


# ============================================================================
# Chat Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat response"""
    user_text: str = Field(..., description="User message")
    model: Optional[str] = Field(None, description="Optional model override")


class ChatResponse(BaseModel):
    """Response model for chat"""
    response: str = Field(..., description="Chat response text")
    model: str = Field(..., description="Model used for generation (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")


# ============================================================================
# Project Generation Models
# ============================================================================

class ProjectGenerationRequest(BaseModel):
    """Request model for project generation"""
    user_query: str = Field(..., description="User's webpage building request")
    page_type_key: Optional[str] = Field(None, description="Optional page type override")
    questionnaire_answers: Optional[Dict[str, Union[str, List[str]]]] = Field(
        None, 
        description="Answers from questionnaire (if applicable)"
    )
    wizard_inputs: Optional[Dict[str, str]] = Field(
        None,
        description="Wizard inputs (hero_text, subtext, cta, theme)"
    )
    project_id: Optional[str] = Field(None, description="Optional project ID")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")


class ProjectGenerationResponse(BaseModel):
    """Response model for project generation"""
    project_id: str = Field(..., description="Generated project ID")
    conversation_id: str = Field(..., description="Conversation ID")
    project: Dict[str, Any] = Field(..., description="Generated project JSON")
    files_count: int = Field(..., description="Number of files in the project")
    page_type: Optional[str] = Field(None, description="Detected page type")
    model_used: str = Field(..., description="Model used for generation (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")
    models_used: Optional[List[ModelInfo]] = Field(None, description="All models used in the pipeline (intent, page_type, generation, etc.)")
    generation_time_seconds: Optional[float] = Field(None, description="Time taken for generation")


# ============================================================================
# Project Modification Models
# ============================================================================

class ProjectModificationRequest(BaseModel):
    """Request model for project modification"""
    instruction: str = Field(..., description="Modification instruction")
    project_json: Optional[Dict[str, Any]] = Field(None, description="Base project JSON (if not using project_id)")
    project_id: Optional[str] = Field(None, description="Project ID to modify (if project_json not provided)")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")


class ProjectModificationResponse(BaseModel):
    """Response model for project modification"""
    project_id: str = Field(..., description="Project ID")
    modified_project: Dict[str, Any] = Field(..., description="Modified project JSON")
    complexity: str = Field(..., description="Modification complexity: small, medium, complex")
    model_used: str = Field(..., description="Model used for modification (deprecated, use model_info)")
    model_info: ModelInfo = Field(..., description="Model information with family and name")
    modification_time_seconds: Optional[float] = Field(None, description="Time taken for modification")


# ============================================================================
# Project Retrieval Models
# ============================================================================

class ProjectResponse(BaseModel):
    """Response model for project retrieval"""
    project_id: str = Field(..., description="Project ID")
    project: Dict[str, Any] = Field(..., description="Project JSON")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    modified_at: Optional[datetime] = Field(None, description="Last modification timestamp")


# ============================================================================
# Page Type Reference Models
# ============================================================================

class PageTypeInfo(BaseModel):
    """Page type information"""
    name: str = Field(..., description="Display name")
    category: str = Field(..., description="Category")
    end_user: str = Field(..., description="Target user description")
    core_pages: List[str] = Field(..., description="List of core pages")
    components: List[Dict[str, str]] = Field(..., description="List of components")
    keywords: List[str] = Field(..., description="Keywords for matching")


class PageTypeReferenceResponse(BaseModel):
    """Response model for page type reference"""
    page_type: Optional[PageTypeInfo] = Field(None, description="Page type information")
    available_types: List[str] = Field(..., description="List of all available page types")


# ============================================================================
# Questionnaire Models
# ============================================================================

class QuestionOption(BaseModel):
    """Question option"""
    id: Optional[str] = None
    label: Optional[str] = None
    value: str = Field(..., description="Option value")


class Question(BaseModel):
    """Question model"""
    id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    type: str = Field(..., description="Question type: radio, multiselect, open_ended")
    options: List[str] = Field(..., description="Available options")


class QuestionnaireResponse(BaseModel):
    """Response model for questionnaire"""
    page_type: str = Field(..., description="Page type key")
    questions: List[Question] = Field(..., description="List of questions")


# ============================================================================
# Category Models
# ============================================================================

class CategoryInfo(BaseModel):
    """Category information"""
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Description")
    icon: str = Field(..., description="Icon emoji")
    examples: str = Field(..., description="Example use cases")


class CategoriesResponse(BaseModel):
    """Response model for categories"""
    categories: Dict[str, CategoryInfo] = Field(..., description="Map of category key to info")


# ============================================================================
# Event Models
# ============================================================================

class EventEnvelopeModel(BaseModel):
    """Event envelope model"""
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    project_id: Optional[str] = Field(None, description="Project ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    payload: Dict[str, Any] = Field(..., description="Event payload")


class EventStreamRequest(BaseModel):
    """Request model for event stream"""
    project_id: Optional[str] = Field(None, description="Project ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    event_types: Optional[List[str]] = Field(None, description="Filter by event types")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

