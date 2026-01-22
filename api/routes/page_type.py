"""
Page Type Classification Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import (
    PageTypeClassificationRequest,
    PageTypeClassificationResponse,
    PageTypeReferenceResponse,
    PageTypeInfo,
    ModelInfo
)
from api.utils import get_model_info
from models.gemini_client import classify_page_type
from data.page_types_reference import get_page_type_by_key, PAGE_TYPES

router = APIRouter()


@router.post("/page-type/classify", response_model=PageTypeClassificationResponse)
async def classify_page_type_endpoint(request: PageTypeClassificationRequest):
    """
    Classify the page type from user input.
    
    Returns one of the supported page types:
    - `landing_page`: Marketing/promotional page
    - `crm_dashboard`: CRM/Customer management
    - `hr_portal`: HR/Employee management
    - `inventory_management`: Stock/warehouse management
    - `ecommerce_fashion`: Online fashion store
    - `digital_product_store`: Digital downloads store
    - `service_marketplace`: Two-sided marketplace
    - `student_portfolio`: Personal portfolio
    - `hyperlocal_delivery`: Food/grocery delivery
    - `real_estate_listing`: Property listings
    - `ai_tutor_lms`: Learning management system
    - `generic`: Generic webpage (fallback)
    """
    try:
        page_type_key, metadata = classify_page_type(
            request.user_text,
            model=request.model
        )
        
        model_name = metadata.get("model", "unknown")
        model_info_dict = get_model_info(model_name)
        
        return PageTypeClassificationResponse(
            page_type=page_type_key,
            explanation=metadata.get("explanation", ""),
            confidence=metadata.get("confidence", 0.0),
            model=model_name,  # Keep for backward compatibility
            model_info=ModelInfo(**model_info_dict),
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Page type classification failed: {str(e)}")


@router.get("/page-type/{page_type_key}", response_model=PageTypeReferenceResponse)
async def get_page_type_reference(page_type_key: str):
    """
    Get page type reference information including core pages and components.
    """
    try:
        page_type_info = get_page_type_by_key(page_type_key)
        
        if page_type_info:
            return PageTypeReferenceResponse(
                page_type=PageTypeInfo(**page_type_info),
                available_types=list(PAGE_TYPES.keys())
            )
        else:
            return PageTypeReferenceResponse(
                page_type=None,
                available_types=list(PAGE_TYPES.keys())
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get page type reference: {str(e)}")


@router.get("/page-types", response_model=PageTypeReferenceResponse)
async def list_page_types():
    """
    List all available page types.
    """
    try:
        return PageTypeReferenceResponse(
            page_type=None,
            available_types=list(PAGE_TYPES.keys())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list page types: {str(e)}")

