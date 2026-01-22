"""
Utility functions for API
"""

from typing import Dict, Any


def get_model_info(model_name: str) -> Dict[str, str]:
    """
    Convert model name to standardized model_family and model_name format.
    
    Args:
        model_name: Model identifier (e.g., "gemini-2.0-flash-lite", "claude-3-haiku", "gpt-4o-mini")
    
    Returns:
        Dictionary with model_family and model_name
    """
    # Detect provider from model name
    normalized_name = model_name.lower().strip()
    
    if normalized_name.startswith("gemini") or "gemini" in normalized_name:
        model_family = "Gemini"
        # Remove any prefixes like "gemini:" if present
        normalized_name = normalized_name.replace("gemini:", "").strip()
    elif normalized_name.startswith("claude") or "claude" in normalized_name:
        model_family = "Anthropic"
        normalized_name = normalized_name.replace("anthropic:", "").strip()
    elif normalized_name.startswith("gpt") or "gpt" in normalized_name or "openai" in normalized_name:
        model_family = "OpenAI"
        normalized_name = normalized_name.replace("openai:", "").strip()
    else:
        # Default to Gemini for backward compatibility
        model_family = "Gemini"
        normalized_name = normalized_name.replace("gemini:", "").strip()
    
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

