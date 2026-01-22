"""
Router Configuration - Maps model_name to router and main models
"""

ROUTER_CONFIG = {
    "gemini": {
        "router_model": "gemini-2.0-flash-lite",  # For intent, page_type, query, chat, modification complexity
        "main_model": "gemini-3-pro-preview",  # For project generation, complex modifications
        "provider": "gemini"
    },
    "claude": {
        "router_model": "claude-haiku-4-5-20251001",  # For intent, page_type, query, chat, modification complexity
        "main_model": "claude-opus-4-5-20251101",  # For project generation, complex modifications
        "provider": "anthropic"
    },
    "gpt": {
        "router_model": "gpt-4o-mini",  # For intent, page_type, query, chat, modification complexity
        "main_model": "gpt-5.2",  # For project generation, complex modifications
        "provider": "openai"
    }
}


def get_router_model(model_name: str = "gemini") -> str:
    """
    Get the router model for classification tasks (intent, page_type, query, chat, modification complexity).
    
    Args:
        model_name: Model family name (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Model identifier for router operations
    """
    model_name_lower = model_name.lower() if model_name else "gemini"
    config = ROUTER_CONFIG.get(model_name_lower, ROUTER_CONFIG["gemini"])
    return config["router_model"]


def get_main_model(model_name: str = "gemini") -> str:
    """
    Get the main model for generation tasks (project generation, complex modifications).
    
    Args:
        model_name: Model family name (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Model identifier for main operations
    """
    model_name_lower = model_name.lower() if model_name else "gemini"
    config = ROUTER_CONFIG.get(model_name_lower, ROUTER_CONFIG["gemini"])
    return config["main_model"]


def get_modification_model(model_name: str, complexity: str) -> str:
    """
    Get the appropriate model for modifications based on complexity.
    
    Args:
        model_name: Model family name (gemini, claude, gpt). Case-insensitive.
        complexity: Modification complexity (small, medium, complex)
    
    Returns:
        Model identifier for modification
    """
    complexity_lower = complexity.lower() if complexity else "medium"
    
    # Small/Medium use router_model, Complex uses main_model
    if complexity_lower == "complex":
        return get_main_model(model_name)
    else:
        return get_router_model(model_name)


def get_provider(model_name: str = "gemini") -> str:
    """
    Get the provider name for the given model_name.
    
    Args:
        model_name: Model family name (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Provider name (gemini, anthropic, openai)
    """
    model_name_lower = model_name.lower() if model_name else "gemini"
    config = ROUTER_CONFIG.get(model_name_lower, ROUTER_CONFIG["gemini"])
    return config["provider"]


def is_valid_model_name(model_name: str) -> bool:
    """
    Check if model_name is valid.
    
    Args:
        model_name: Model family name to check
    
    Returns:
        True if valid, False otherwise
    """
    if not model_name:
        return False
    return model_name.lower() in ROUTER_CONFIG

