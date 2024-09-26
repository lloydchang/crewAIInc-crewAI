# schemas/config_schemas.py

"""
Module for configuration schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class LLMInnerConfig(BaseModel):
    """
    Inner configuration for the LLM (Language Model).
    """
    model: str = Field(..., description="The model name for the LLM.")
    temperature: float = Field(0, ge=0, description="The temperature setting for the LLM.")

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return v


class LLMConfig(BaseModel):
    """
    LLM Configuration.
    """
    provider: str = Field(..., description="The provider for the LLM.")
    config: LLMInnerConfig = Field(..., description="Inner configuration for the LLM.")


class EmbedderInnerConfig(BaseModel):
    """
    Inner configuration for the Embedder.
    """
    model: str = Field(..., description="The model name for the Embedder.")
    temperature: float = Field(0, ge=0, description="The temperature setting for the Embedder.")

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return v


class EmbedderConfig(BaseModel):
    """
    Embedder Configuration.
    """
    provider: str = Field(..., description="The provider for the Embedder.")
    config: EmbedderInnerConfig = Field(..., description="Inner configuration for the Embedder.")


class ToolConfig(BaseModel):
    """
    Tool configuration that encapsulates LLM and Embedder configurations.
    """
    llm: LLMConfig = Field(..., description="LLM configuration.")
    embedder: EmbedderConfig = Field(..., description="Embedder configuration.")
