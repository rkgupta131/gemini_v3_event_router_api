# router/model_router.py
"""
Model Router - Routes to appropriate models based on model_name
"""

from .router_config import (
    get_router_model,
    get_main_model,
    get_modification_model,
    get_provider,
    is_valid_model_name
)


def select_model(prompt: str, tokens_est: int, model_name: str = "gemini") -> str:
    """
    Select model based on prompt and model_name.
    For backward compatibility, defaults to main model.
    """
    return get_main_model(model_name)


def get_router_model_for_operations(model_name: str = "gemini") -> str:
    """Get router model for intent, page_type, query, chat operations"""
    return get_router_model(model_name)


def get_main_model_for_generation(model_name: str = "gemini") -> str:
    """Get main model for project generation"""
    return get_main_model(model_name)


def get_model_for_modification(model_name: str, complexity: str) -> str:
    """Get model for modification based on complexity"""
    return get_modification_model(model_name, complexity)