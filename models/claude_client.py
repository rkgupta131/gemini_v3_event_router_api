"""
Claude Client - Anthropic Claude API integration
"""

import os
import json
import re
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

try:
    import anthropic
except ImportError:
    anthropic = None

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

_client = None


def _make_client():
    """Create Anthropic client"""
    global _client
    if _client is not None:
        return _client
    
    # Reload env vars to ensure we get the latest values
    load_dotenv(dotenv_path=env_path, override=True)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Please check your .env file.")
    
    if anthropic is None:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
    
    _client = anthropic.Anthropic(api_key=anthropic_api_key)
    return _client


def generate_text(prompt: str, model: str = "claude-3-haiku", fallback_models: list = None, max_tokens: int = 8192) -> str:
    """
    Generate text using Claude API.
    
    Args:
        prompt: Input prompt
        model: Model identifier
        fallback_models: Optional list of fallback models
        max_tokens: Maximum tokens to generate (default: 8192, use 16384+ for large projects)
    
    Returns:
        Generated text
    """
    client = _make_client()
    
    models_to_try = [model]
    if fallback_models:
        models_to_try.extend(fallback_models)
    
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Check if response was truncated
            if hasattr(response, 'stop_reason') and response.stop_reason == "max_tokens":
                print(f"[CLAUDE_WARNING] Response truncated due to max_tokens limit. Consider increasing max_tokens.")
            
            return response.content[0].text
        except Exception as e:
            last_error = e
            if model_name != models_to_try[-1]:
                print(f"[CLAUDE_FALLBACK] Model {model_name} failed, trying next...")
                continue
            raise last_error
    
    raise last_error if last_error else RuntimeError("No models available")


def classify_intent(user_text: str, model: str = None) -> Tuple[str, dict]:
    """
    Classify user intent using Claude.
    Returns: (label, metadata)
    """
    if model is None:
        from router.router_config import get_router_model
        model = get_router_model("claude")
    
    instructions = (
        "You are an intent classifier. Return exactly one JSON object (no extra text) in this format:\n"
        '{ "label": "<one of: webpage_build, greeting_only, chat, illegal, other>", "explanation": "<1-2 sentence>", "confidence": 0.0 }\n'
        "Definitions: webpage_build = user wants a webpage; greeting_only = simple hello; chat = general Q/A; illegal = disallowed; other = else.\n"
        "Be conservative: treat 'what is a webpage' as chat (educational)."
    )
    prompt = instructions + "\n\nUser message:\n" + json.dumps(user_text)
    
    try:
        out = generate_text(prompt, model=model)
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1 and end > start:
            cand = out[start:end+1]
            parsed = json.loads(cand)
            label = parsed.get("label", "chat")
            explanation = parsed.get("explanation", "")
            confidence = float(parsed.get("confidence", 0.0))
            result = {"explanation": explanation, "confidence": confidence, "raw": out, "model": model}
            return label, result
        result = {"explanation": "Could not parse classifier output", "confidence": 0.0, "raw": out, "model": model}
        return "chat", result
    except Exception as e:
        result = {"explanation": f"classifier error: {e}", "confidence": 0.0, "raw": "", "model": model}
        return "chat", result


def classify_page_type(user_text: str, model: str = None) -> Tuple[str, dict]:
    """Classify page type using Claude"""
    if model is None:
        from router.router_config import get_router_model
        model = get_router_model("claude")
    
    instructions = (
        "You are a page type classifier. Return exactly one JSON object (no extra text) in this format:\n"
        '{ "page_type": "<one of: landing_page, crm_dashboard, hr_portal, inventory_management, ecommerce_fashion, digital_product_store, service_marketplace, student_portfolio, hyperlocal_delivery, real_estate_listing, ai_tutor_lms, generic>", "explanation": "<1-2 sentence>", "confidence": 0.0 }\n\n'
        "Definitions:\n"
        "- landing_page: Single marketing/promotional page, lead capture, product launch, campaign\n"
        "- crm_dashboard: CRM/Customer management, lead tracking, sales pipeline\n"
        "- generic: None of the above\n"
    )
    prompt = instructions + "\n\nUser message:\n" + json.dumps(user_text)
    
    try:
        out = generate_text(prompt, model=model)
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1 and end > start:
            cand = out[start:end+1]
            parsed = json.loads(cand)
            page_type = parsed.get("page_type", "generic")
            explanation = parsed.get("explanation", "")
            confidence = float(parsed.get("confidence", 0.0))
            result = {"explanation": explanation, "confidence": confidence, "raw": out, "model": model}
            return page_type, result
        result = {"explanation": "Could not parse classifier output", "confidence": 0.0, "raw": out, "model": model}
        return "generic", result
    except Exception as e:
        result = {"explanation": f"classifier error: {e}", "confidence": 0.0, "raw": "", "model": model}
        return "generic", result


def analyze_query_detail(user_text: str, model: str = None) -> Tuple[bool, float]:
    """Analyze query detail using Claude"""
    if model is None:
        from router.router_config import get_router_model
        model = get_router_model("claude")
    
    instructions = (
        "You are a requirements analyzer. Determine if the user's request has enough detail or needs follow-up questions.\n"
        "Return exactly one JSON object (no extra text) in this format:\n"
        '{ "needs_followup": true/false, "explanation": "<1-2 sentence>", "confidence": 0.0 }\n\n'
        "Guidelines:\n"
        "- needs_followup=true if request is vague\n"
        "- needs_followup=false if request has specific details\n"
    )
    prompt = instructions + "\n\nUser request:\n" + json.dumps(user_text)
    
    try:
        out = generate_text(prompt, model=model)
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1 and end > start:
            cand = out[start:end+1]
            parsed = json.loads(cand)
            needs_followup = parsed.get("needs_followup", True)
            confidence = float(parsed.get("confidence", 0.0))
            return needs_followup, confidence
        return True, 0.0
    except Exception as e:
        return True, 0.0


def chat_response(user_text: str, model: str = None) -> str:
    """Generate chat response using Claude"""
    if model is None:
        from router.router_config import get_router_model
        model = get_router_model("claude")
    
    prompt = f"Reply in max 4 sentences.\nUser: {user_text}"
    out = generate_text(prompt, model=model)
    parts = re.split(r'(?<=[.!?])\s+', out.strip())
    result = " ".join(parts[:4])
    return result


def classify_modification_complexity(instruction: str, model: str = None) -> Tuple[str, dict]:
    """Classify modification complexity using Claude"""
    if model is None:
        from router.router_config import get_router_model
        model = get_router_model("claude")
    
    instructions = (
        "You are a task complexity classifier. Return exactly one JSON object (no extra text) in this format:\n"
        '{ "complexity": "<one of: small, medium, complex>", "explanation": "<1-2 sentence>", "confidence": 0.0 }\n\n'
        "Guidelines:\n"
        "- small: Simple text/content changes, color/theme updates, minor CSS tweaks\n"
        "- medium: Adding a component, modifying layout structure, updating multiple files\n"
        "- complex: Major restructuring, adding multiple new features, complex logic changes\n"
    )
    prompt = instructions + "\n\nModification instruction:\n" + json.dumps(instruction)
    
    try:
        out = generate_text(prompt, model=model)
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1 and end > start:
            cand = out[start:end+1]
            parsed = json.loads(cand)
            complexity = parsed.get("complexity", "medium")
            if complexity not in ["small", "medium", "complex"]:
                complexity = "medium"
            explanation = parsed.get("explanation", "")
            confidence = float(parsed.get("confidence", 0.0))
            result = {"explanation": explanation, "confidence": confidence, "raw": out, "model": model}
            return complexity, result
        result = {"explanation": "Could not parse classifier output", "confidence": 0.0, "raw": out, "model": model}
        return "medium", result
    except Exception as e:
        result = {"explanation": f"classifier error: {e}", "confidence": 0.0, "raw": "", "model": model}
        return "medium", result

