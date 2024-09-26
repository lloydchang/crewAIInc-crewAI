# schemas/config_schemas.py

from typing import Dict, Any, Optional

# Inner configuration for the LLM (Language Model)
class LLMInnerConfig:
    def __init__(self, model: str, temperature: Optional[float] = 0):
        if temperature is None:
            raise ValueError("Missing LLM temperature.")
        if temperature < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        self.model = model
        self.temperature = temperature

# LLM Configuration
class LLMConfig:
    def __init__(self, provider: str, config: LLMInnerConfig):
        if not provider:
            raise ValueError("Missing LLM provider.")
        self.provider = provider
        self.config = config

# Inner configuration for the Embedder
class EmbedderInnerConfig:
    def __init__(self, model: str, temperature: Optional[float] = 0):
        if temperature is None:
            raise ValueError("Missing Embedder temperature.")
        if temperature < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        self.model = model
        self.temperature = temperature

# Embedder Configuration
class EmbedderConfig:
    def __init__(self, provider: str, config: EmbedderInnerConfig):
        if not provider:
            raise ValueError("Missing Embedder provider.")
        self.provider = provider
        self.config = config

# Tool configuration that encapsulates LLM and Embedder configurations
class ToolConfig:
    def __init__(self, llm: LLMConfig, embedder: EmbedderConfig):
        if not llm or not embedder:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        self.llm = llm
        self.embedder = embedder
