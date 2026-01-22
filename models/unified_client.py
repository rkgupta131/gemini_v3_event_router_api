"""
Unified Model Client - Routes to appropriate provider based on model_name
"""

from typing import Optional, Tuple
from router.router_config import get_provider, get_router_model, get_main_model, get_modification_model


def generate_text_unified(
    prompt: str,
    model_name: str = "gemini",
    operation_type: str = "main",
    complexity: Optional[str] = None
) -> str:
    """
    Unified text generation that routes to appropriate provider.
    
    Args:
        prompt: Input prompt
        model_name: Model family (gemini, claude, gpt)
        operation_type: "router" for classification tasks, "main" for generation, "modification" for modifications
        complexity: For modifications, the complexity level (small, medium, complex)
    
    Returns:
        Generated text
    """
    provider = get_provider(model_name)
    
    if operation_type == "router":
        model = get_router_model(model_name)
    elif operation_type == "modification" and complexity:
        model = get_modification_model(model_name, complexity)
    else:
        model = get_main_model(model_name)
    
    # Route to appropriate client
    if provider == "gemini":
        from models.gemini_client import generate_text
        return generate_text(prompt, model=model)
    elif provider == "anthropic":
        from models.claude_client import generate_text
        return generate_text(prompt, model=model)
    elif provider == "openai":
        from models.gpt_client import generate_text
        return generate_text(prompt, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def classify_intent_unified(user_text: str, model_name: str = "gemini") -> Tuple[str, dict]:
    """
    Unified intent classification that routes to appropriate provider.
    
    Args:
        user_text: User input text
        model_name: Model family (gemini, claude, gpt)
    
    Returns:
        (label, metadata)
    """
    provider = get_provider(model_name)
    
    if provider == "gemini":
        from models.gemini_client import classify_intent
        model = get_router_model(model_name)
        return classify_intent(user_text, model=model)
    elif provider == "anthropic":
        from models.claude_client import classify_intent
        model = get_router_model(model_name)
        return classify_intent(user_text, model=model)
    elif provider == "openai":
        from models.gpt_client import classify_intent
        model = get_router_model(model_name)
        return classify_intent(user_text, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def classify_page_type_unified(user_text: str, model_name: str = "gemini") -> Tuple[str, dict]:
    """Unified page type classification"""
    provider = get_provider(model_name)
    
    if provider == "gemini":
        from models.gemini_client import classify_page_type
        model = get_router_model(model_name)
        return classify_page_type(user_text, model=model)
    elif provider == "anthropic":
        from models.claude_client import classify_page_type
        model = get_router_model(model_name)
        return classify_page_type(user_text, model=model)
    elif provider == "openai":
        from models.gpt_client import classify_page_type
        model = get_router_model(model_name)
        return classify_page_type(user_text, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def analyze_query_detail_unified(user_text: str, model_name: str = "gemini") -> Tuple[bool, float]:
    """Unified query analysis"""
    provider = get_provider(model_name)
    
    if provider == "gemini":
        from models.gemini_client import analyze_query_detail
        model = get_router_model(model_name)
        return analyze_query_detail(user_text, model=model)
    elif provider == "anthropic":
        from models.claude_client import analyze_query_detail
        model = get_router_model(model_name)
        return analyze_query_detail(user_text, model=model)
    elif provider == "openai":
        from models.gpt_client import analyze_query_detail
        model = get_router_model(model_name)
        return analyze_query_detail(user_text, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def chat_response_unified(user_text: str, model_name: str = "gemini") -> str:
    """Unified chat response"""
    provider = get_provider(model_name)
    
    if provider == "gemini":
        from models.gemini_client import chat_response
        model = get_router_model(model_name)
        return chat_response(user_text, model=model)
    elif provider == "anthropic":
        from models.claude_client import chat_response
        model = get_router_model(model_name)
        return chat_response(user_text, model=model)
    elif provider == "openai":
        from models.gpt_client import chat_response
        model = get_router_model(model_name)
        return chat_response(user_text, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def classify_modification_complexity_unified(instruction: str, model_name: str = "gemini") -> Tuple[str, dict]:
    """Unified modification complexity classification"""
    provider = get_provider(model_name)
    
    if provider == "gemini":
        from models.gemini_client import classify_modification_complexity
        model = get_router_model(model_name)
        return classify_modification_complexity(instruction, model=model)
    elif provider == "anthropic":
        from models.claude_client import classify_modification_complexity
        model = get_router_model(model_name)
        return classify_modification_complexity(instruction, model=model)
    elif provider == "openai":
        from models.gpt_client import classify_modification_complexity
        model = get_router_model(model_name)
        return classify_modification_complexity(instruction, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")

