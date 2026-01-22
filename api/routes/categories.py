"""
Category Routes
"""

from fastapi import APIRouter, HTTPException
from api.models import CategoriesResponse, CategoryInfo
from data.page_categories import get_all_categories

router = APIRouter()


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """
    Get all page type categories for user selection.
    
    Returns a map of category keys to their display information.
    """
    try:
        categories_dict = get_all_categories()
        
        categories_info = {
            key: CategoryInfo(**info)
            for key, info in categories_dict.items()
        }
        
        return CategoriesResponse(categories=categories_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

