
# model_router.py — MULTI-PROVIDER, ROBUST, PRODUCTION-SAFE

import os
import json
import requests
from typing import List, Dict, Any, Optional, Literal

from dotenv import load_dotenv
from json_repair import repair_json

# -------------------------
# Providers SDKs
# -------------------------
import openai
import anthropic
from google import genai

# Optional token estimation
try:
    import tiktoken  # type: ignore
except ImportError:
    tiktoken = None

# User config
try:
    from model_config import MODEL_CONFIG
except Exception:
    MODEL_CONFIG = {}

load_dotenv()

# ==========================================================
# ENV
# ==========================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS missing or invalid")

if not GOOGLE_CLOUD_PROJECT:
    raise RuntimeError("GOOGLE_CLOUD_PROJECT missing")

# ==========================================================
# OPENAI CLIENT
# ==========================================================
from openai import OpenAI as OpenAIClient
openai_client = OpenAIClient(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ==========================================================
# TOKEN ESTIMATION
# ==========================================================
def _estimate_tokens_text(text: str, model_hint: str = "gpt-4.1") -> int:
    if not text:
        return 0
    if tiktoken:
        try:
            enc = tiktoken.encoding_for_model(model_hint)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    return max(1, len(text) // 4)


def _estimate_tokens_messages(messages: List[Dict[str, str]], model_hint: str = "gpt-4.1") -> int:
    joined = "\n".join(m.get("content", "") for m in messages)
    return _estimate_tokens_text(joined, model_hint)

# ==========================================================
# VERTEX GEMINI
# ==========================================================
def make_vertex_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )

def _call_gemini_json(messages: List[Dict[str, str]], model: str, max_tokens: int) -> str:
    client = make_vertex_client()

    prompt = "\n\n".join(
        f"[{m.get('role','user')}]\n{m.get('content','')}" for m in messages
    )

    est = _estimate_tokens_messages(messages)
    print(f"[gemini] approx prompt tokens ≈ {est}")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text and getattr(response, "candidates", None):
        text = "\n".join(
            p.text
            for c in response.candidates
            for p in getattr(c.content, "parts", [])
            if getattr(p, "text", None)
        )

    if not text:
        raise RuntimeError("Gemini returned empty response")

    usage = getattr(response, "usage_metadata", None)
    if usage:
        print(
            f"[gemini usage] prompt={usage.prompt_token_count} "
            f"completion={usage.candidates_token_count} total={usage.total_token_count}"
        )

    return text

# ==========================================================
# OPENAI
# ==========================================================
def _call_openai_json(messages: List[Dict[str, str]], model: str, max_tokens: int) -> str:
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY not set")

    est = _estimate_tokens_messages(messages, model)
    completion = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        max_completion_tokens=max_tokens,
    )

    usage = getattr(completion, "usage", None)
    if usage:
        print(f"[openai usage] prompt={usage.prompt_tokens} completion={usage.completion_tokens} total={usage.total_tokens}")
    else:
        print(f"[openai est] prompt≈{est}")

    return completion.choices[0].message.content

# ==========================================================
# ANTHROPIC CLAUDE
# ==========================================================
def _call_anthropic_json(messages: List[Dict[str, str]], model: str, max_tokens: int) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system = ""
    user_text = []

    for m in messages:
        if m["role"] == "system":
            system += m["content"] + "\n"
        else:
            user_text.append(m["content"])

    response = client.messages.create(
        model=model,
        system=system.strip() or None,
        messages=[{"role": "user", "content": "\n\n".join(user_text)}],
        max_tokens=max_tokens,
        temperature=0.2,
    )

    return response.content[0].text

# ==========================================================
# HUGGINGFACE (OPEN SOURCE)
# ==========================================================
def _call_huggingface_json(messages: List[Dict[str, str]], model: str, max_tokens: int) -> str:
    if not HUGGINGFACE_API_TOKEN:
        raise RuntimeError("HUGGINGFACE_API_TOKEN not set")

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    prompt = "\n\n".join(
        f"[{m.get('role','user').upper()}]\n{m.get('content','')}" for m in messages
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.2,
            "return_full_text": False,
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    raise RuntimeError(f"HuggingFace invalid response: {data}")

# ==========================================================
# MODEL CONFIG MERGE
# ==========================================================
_FALLBACK = {
    "default_provider": "gemini",
    "providers": {
        "gemini": {"orchestrator": "gemini-3-pro-preview", "agent_default": "gemini-2.5-flash"},
        "openai": {"orchestrator": "gpt-4.1", "agent_default": "gpt-4.1-mini"},
        "anthropic": {"orchestrator": "claude-3-5-sonnet-20240620", "agent_default": "claude-3-haiku-20240307"},
        "huggingface": {"orchestrator": "mistralai/Mixtral-8x7B-Instruct-v0.1", "agent_default": "Qwen/Qwen2.5-7B-Instruct"},
    },
    "by_agent": {},
}

def _merge_config():
    cfg = json.loads(json.dumps(_FALLBACK))
    if isinstance(MODEL_CONFIG, dict):
        cfg.update({k: MODEL_CONFIG.get(k, v) for k, v in cfg.items()})
    return cfg

_CONFIG = _merge_config()

# ==========================================================
# OVERRIDE NORMALIZATION
# ==========================================================
def normalize_override(user_override: Optional[str]) -> Optional[str]:
    if not user_override:
        return None
    t = user_override.lower()
    if "gemini" in t:
        return "gemini"
    if "gpt" in t or "openai" in t:
        return "openai"
    if "claude" in t or "anthropic" in t:
        return "anthropic"
    if "hf" in t or "huggingface" in t or "open source" in t:
        return "huggingface"
    return None

# ==========================================================
# PROVIDER SELECTION
# ==========================================================
def choose_provider_and_model(is_orchestrator: bool, user_override: Optional[str], agent_name: str):
    override = normalize_override(user_override)
    providers = _CONFIG["providers"]

    if override:
        return {
            "provider": override,
            "model": providers[override]["orchestrator"] if is_orchestrator else providers[override]["agent_default"],
        }

    by_agent = _CONFIG.get("by_agent", {})
    if agent_name in by_agent:
        entry = by_agent[agent_name]
        return {
            "provider": entry["provider"],
            "model": entry.get("model") or providers[entry["provider"]]["agent_default"],
        }

    provider = _CONFIG["default_provider"]
    return {
        "provider": provider,
        "model": providers[provider]["orchestrator"] if is_orchestrator else providers[provider]["agent_default"],
    }

# ==========================================================
# MAIN ENTRY
# ==========================================================
def call_llm_json(
    messages: List[Dict[str, str]],
    is_orchestrator: bool,
    agent_name: str,
    user_override: Optional[str] = None,
    max_tokens: int = 2000,
    repair: bool = True,
) -> Dict[str, Any]:

    choice = choose_provider_and_model(is_orchestrator, user_override, agent_name)
    provider = choice["provider"]
    model = choice["model"]

    print(f"[call_llm_json] agent={agent_name} provider={provider} model={model}")

    if provider == "gemini":
        raw = _call_gemini_json(messages, model, max_tokens)
    elif provider == "openai":
        raw = _call_openai_json(messages, model, max_tokens)
    elif provider == "anthropic":
        raw = _call_anthropic_json(messages, model, max_tokens)
    elif provider == "huggingface":
        raw = _call_huggingface_json(messages, model, max_tokens)
    else:
        raise RuntimeError(f"Unknown provider {provider}")

    text = raw.strip()
    if text.startswith("```"):
        text = text[text.find("{"):]

    try:
        return json.loads(text)
    except Exception:
        if not repair:
            raise
        fixed = repair_json(text)
        return json.loads(fixed) if isinstance(fixed, str) else fixed