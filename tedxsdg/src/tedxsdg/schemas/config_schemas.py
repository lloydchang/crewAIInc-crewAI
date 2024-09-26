# schemas/config_schemas.py

"""
Module for configuration schemas using Pydantic v1.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class LLMInnerConfig(BaseModel):
    """
    Inner configuration for the LLM (Language Model).
    """
    model: str = Field(..., description="The model name for the LLM.")
    temperature: float = Field(0, ge=0, description="Temperature for the LLM.")

    @validator('model')
    def validate_model(cls, v):
        if not v.strip():
            raise ValueError("LLM model name cannot be empty.")
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return v


class LLMConfig(BaseModel):
    """
    LLM Configuration.
    """
    provider: str = Field(..., description="Provider name for the LLM.")
    config: LLMInnerConfig

    @validator('provider')
    def validate_provider(cls, v):
        if not v.strip():
            raise ValueError("LLM provider cannot be empty.")
        return v


class EmbedderInnerConfig(BaseModel):
    """
    Inner configuration for the Embedder.
    """
    model: str = Field(..., description="The model name for the Embedder.")
    temperature: float = Field(0, ge=0, description="Temperature for the Embedder.")

    @validator('model')
    def validate_model(cls, v):
        if not v.strip():
            raise ValueError("Embedder model name cannot be empty.")
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return v


class EmbedderConfig(BaseModel):
    """
    Embedder Configuration.
    """
    provider: str = Field(..., description="Provider name for the Embedder.")
    config: EmbedderInnerConfig

    @validator('provider')
    def validate_provider(cls, v):
        if not v.strip():
            raise ValueError("Embedder provider cannot be empty.")
        return v


class ToolConfig(BaseModel):
    """
    Tool configuration that encapsulates LLM and Embedder configurations.
    """
    llm: LLMConfig
    embedder: EmbedderConfig

    @validator('llm', 'embedder', pre=True, always=True)
    def validate_configs(cls, v, field):
        if not v:
            raise ValueError(f"{field.name.upper()} configuration must be provided.")
        return v
