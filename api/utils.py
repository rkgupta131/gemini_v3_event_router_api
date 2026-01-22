"""
Utility functions for API
"""

from typing import Dict, Any


def get_model_info(model_name: str) -> Dict[str, str]:
    """
    Convert model name to standardized model_family and model_name format.
    
    Args:
        model_name: Model identifier (e.g., "gemini-2.0-flash-lite", "gemini-3-pro-preview")
    
    Returns:
        Dictionary with model_family and model_name
    """
    # All models in this system are Gemini models
    model_family = "Gemini"
    
    # Normalize model name
    # Remove any prefixes like "gemini:" if present
    normalized_name = model_name.replace("gemini:", "").strip()
    
    return {
        "model_family": model_family,
        "model_name": normalized_name
    }


def format_model_response(model_name: str, include_family: bool = True) -> Dict[str, Any]:
    """
    Format model information for API responses.
    
    Args:
        model_name: Model identifier
        include_family: Whether to include model_family (default: True)
    
    Returns:
        Dictionary with model information
    """
    if include_family:
        return get_model_info(model_name)
    else:
        return {"model_name": model_name.replace("gemini:", "").strip()}

