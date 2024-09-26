# schemas/config_schemas.py

"""
Module for configuration schemas.
"""

from typing import Optional


class LLMInnerConfig:
    """
    Inner configuration for the LLM (Language Model).
    """
    def __init__(self, model: str, temperature: Optional[float] = 0):
        if temperature is None:
            raise ValueError("Missing LLM temperature.")
        if temperature < 0:
            raise ValueError(
                "LLM temperature must be equal to or greater than 0."
            )
        self.model = model
        self.temperature = temperature

    def get_model(self) -> str:
        """
        Get the model name.
    def get_temperature(self) -> float:
        """
        Get the temperature value.
        """
        return self.model

    def get_temperature(self) -> float:
        return self.temperature


class LLMConfig:
    """
    LLM Configuration.
    """
    def get_provider(self) -> str:
        """
        Get the provider name.
    def get_config(self) -> LLMInnerConfig:
        """
        Get the LLM inner configuration.
        """
        if not provider:
            raise ValueError("Missing LLM provider.")
        self.provider = provider
        self.config = config

    def get_provider(self) -> str:
        return self.provider

    def get_config(self) -> LLMInnerConfig:
        return self.config


class EmbedderInnerConfig:
    """
    Inner configuration for the Embedder.
    """
    def __init__(self, model: str, temperature: Optional[float] = 0):
        if temperature is None:
            raise ValueError("Missing Embedder temperature.")
        if temperature < 0:
            raise ValueError(
                "Embedder temperature must be equal to or greater than 0."
            )
        self.model = model
        self.temperature = temperature

    def get_model(self) -> str:
        return self.model

    def get_temperature(self) -> float:
        return self.temperature


class EmbedderConfig:
    def get_config(self) -> EmbedderInnerConfig:
        """
        Get the Embedder inner configuration.
        """
    Embedder Configuration.
    """
    def __init__(self, provider: str, config: EmbedderInnerConfig):
        if not provider:
            raise ValueError("Missing Embedder provider.")
        self.provider = provider
        self.config = config
                "Both LLM and Embedder configurations must be initialized "
                "properly."
    def get_provider(self) -> str:
        return self.provider

    def get_llm(self) -> LLMConfig:
        """
        Get the LLM configuration.
    def get_embedder(self) -> EmbedderConfig:
        """
        Get the Embedder configuration.
        """
        return self.config


class ToolConfig:
    """
    Tool configuration that encapsulates LLM and Embedder configurations.
    """
    def __init__(self, llm: LLMConfig, embedder: EmbedderConfig):
        if not llm or not embedder:
            raise ValueError(
                "Both LLM and Embedder configurations must be initialized properly."
            )
        self.llm = llm
        self.embedder = embedder

    def get_llm(self) -> LLMConfig:
        return self.llm

    def get_embedder(self) -> EmbedderConfig:
        return self.embedder
