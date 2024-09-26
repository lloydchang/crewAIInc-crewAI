# schemas/config_schemas.py

"""
Module for configuration schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class LLMInnerConfig(BaseModel):
    """
    Inner configuration for the LLM (Language Model).
    """
    model: str = Field(..., description="The model name for the LLM.")
    temperature: float = Field(..., ge=0, description="Temperature for LLM generation.")

    @model_validator(mode='before')
    def check_temperature(cls, values):
        temperature = values.get('temperature')
        if temperature is None:
            raise ValueError("Missing LLM temperature.")
        if temperature < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return values


class LLMConfig(BaseModel):
    """
    LLM Configuration.
    """
    provider: str = Field(..., description="Provider name for the LLM.")
    config: LLMInnerConfig

    @model_validator(mode='before')
    def check_provider(cls, values):
        provider = values.get('provider')
        if not provider:
            raise ValueError("Missing LLM provider.")
        return values


class EmbedderInnerConfig(BaseModel):
    """
    Inner configuration for the Embedder.
    """
    model: str = Field(..., description="The model name for the Embedder.")
    temperature: float = Field(..., ge=0, description="Temperature for Embedder generation.")

    @model_validator(mode='before')
    def check_temperature(cls, values):
        temperature = values.get('temperature')
        if temperature is None:
            raise ValueError("Missing Embedder temperature.")
        if temperature < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return values


class EmbedderConfig(BaseModel):
    """
    Embedder Configuration.
    """
    provider: str = Field(..., description="Provider name for the Embedder.")
    config: EmbedderInnerConfig

    @model_validator(mode='before')
    def check_provider(cls, values):
        provider = values.get('provider')
        if not provider:
            raise ValueError("Missing Embedder provider.")
        return values


class ToolConfig(BaseModel):
    """
    Tool configuration that encapsulates LLM and Embedder configurations.
    """
    llm: LLMConfig
    embedder: EmbedderConfig

    @model_validator(mode='before')
    def check_configs(cls, values):
        llm = values.get('llm')
        embedder = values.get('embedder')
        if not llm or not embedder:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return values
