"""
Router Configuration - Maps model_family to router and main models
"""

# Map model_family (from API) to internal model keys
MODEL_FAMILY_MAP = {
    "gemini": "gemini",
    "anthropic": "claude",
    "claude": "claude",
    "openai": "gpt",
    "gpt": "gpt"
}

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


def normalize_model_family(model_family: str) -> str:
    """
    Normalize model_family from API (e.g., "Anthropic", "Gemini", "OpenAI") to internal key.
    
    Args:
        model_family: Model family name from API (case-insensitive)
    
    Returns:
        Internal model key (gemini, claude, gpt)
    """
    if not model_family:
        return "gemini"
    
    model_family_lower = model_family.lower().strip()
    return MODEL_FAMILY_MAP.get(model_family_lower, "gemini")


def get_router_model(model_family: str = "gemini") -> str:
    """
    Get the router model for classification tasks (intent, page_type, query, chat, modification complexity).
    
    Args:
        model_family: Model family name (Gemini, Anthropic, OpenAI) or internal key (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Model identifier for router operations
    """
    internal_key = normalize_model_family(model_family)
    config = ROUTER_CONFIG.get(internal_key, ROUTER_CONFIG["gemini"])
    return config["router_model"]


def get_main_model(model_family: str = "gemini") -> str:
    """
    Get the main model for generation tasks (project generation, complex modifications).
    
    Args:
        model_family: Model family name (Gemini, Anthropic, OpenAI) or internal key (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Model identifier for main operations
    """
    internal_key = normalize_model_family(model_family)
    config = ROUTER_CONFIG.get(internal_key, ROUTER_CONFIG["gemini"])
    return config["main_model"]


def get_modification_model(model_family: str, complexity: str) -> str:
    """
    Get the appropriate model for modifications based on complexity.
    
    Args:
        model_family: Model family name (Gemini, Anthropic, OpenAI) or internal key (gemini, claude, gpt). Case-insensitive.
        complexity: Modification complexity (small, medium, complex)
    
    Returns:
        Model identifier for modification
    """
    complexity_lower = complexity.lower() if complexity else "medium"
    
    # Small/Medium use router_model, Complex uses main_model
    if complexity_lower == "complex":
        return get_main_model(model_family)
    else:
        return get_router_model(model_family)


def get_provider(model_family: str = "gemini") -> str:
    """
    Get the provider name for the given model_family.
    
    Args:
        model_family: Model family name (Gemini, Anthropic, OpenAI) or internal key (gemini, claude, gpt). Case-insensitive.
    
    Returns:
        Provider name (gemini, anthropic, openai)
    """
    internal_key = normalize_model_family(model_family)
    config = ROUTER_CONFIG.get(internal_key, ROUTER_CONFIG["gemini"])
    return config["provider"]


def is_valid_model_family(model_family: str) -> bool:
    """
    Check if model_family is valid.
    
    Args:
        model_family: Model family name to check (Gemini, Anthropic, OpenAI, or internal keys)
    
    Returns:
        True if valid, False otherwise
    """
    if not model_family:
        return False
    internal_key = normalize_model_family(model_family)
    return internal_key in ROUTER_CONFIG

