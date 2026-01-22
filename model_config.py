# model_config.py

MODEL_CONFIG = {
    # --------------------------------------------------
    # default provider when there is NO user override
    # --------------------------------------------------
    "default_provider": "gemini",   # gemini | openai | anthropic

    # --------------------------------------------------
    # per-provider, per-role defaults
    # --------------------------------------------------
    "providers": {
        "gemini": {
            "orchestrator": "gemini-3-pro-preview",
            "agent_default": "gemini-3-pro-preview",
        },

        "openai": {
            "orchestrator": "gpt-5.2",
            "agent_default": "gpt-5.2",
        },
        "anthropic": {
            "orchestrator": "claude-sonnet-4-5-20250929",
            "agent_default": "claude-sonnet-4-5-20250929",
        },
    },

    # --------------------------------------------------
    # optional: override per AGENT name
    # --------------------------------------------------
    "by_agent": {
        # Example:
        # "code_agent": {
        #     "provider": "anthropic",
        #     "model": "claude-3-5-sonnet-20240620"
        # }
    },
}