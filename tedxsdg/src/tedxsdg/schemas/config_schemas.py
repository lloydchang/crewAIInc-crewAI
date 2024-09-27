"""
schemas/config_schemas.py

Module for configuration schemas using Pydantic.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class LLMInnerConfig(BaseModel):
    """Inner configuration for the LLM (Language Model)."""
    
    model: Optional[str] = Field(default=None, description="The model name for the LLM.")
    temperature: Optional[float] = Field(default=0, ge=0, description="Temperature for the LLM.")

#     @validator('model')
    def validate_model(cls, v):
        if v is not None and not v.strip():
            raise ValueError("LLM model name cannot be empty.")
        return v

#     @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and v < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return v


class LLMConfig(BaseModel):
    """LLM Configuration."""
    
    provider: Optional[str] = Field(default=None, description="Provider name for the LLM.")
    config: Optional[LLMInnerConfig] = None

#     @validator('provider')
    def validate_provider(cls, v):
        if v is not None and not v.strip():
            raise ValueError("LLM provider cannot be empty.")
        return v


class EmbedderInnerConfig(BaseModel):
    """Inner configuration for the Embedder."""
    
    model: Optional[str] = Field(default=None, description="The model name for the Embedder.")
    temperature: Optional[float] = Field(default=0, ge=0, description="Temperature for the Embedder.")

#     @validator('model')
    def validate_model(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Embedder model name cannot be empty.")
        return v

#     @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and v < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return v


class EmbedderConfig(BaseModel):
    """Embedder Configuration."""
    
    provider: Optional[str] = Field(default=None, description="Provider name for the Embedder.")
    config: Optional[EmbedderInnerConfig] = None

#     @validator('provider')
    def validate_provider(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Embedder provider cannot be empty.")
        return v


class ToolConfig(BaseModel):
    """Tool configuration that encapsulates LLM and Embedder configurations."""
    
    llm: Optional[LLMConfig] = None
    embedder: Optional[EmbedderConfig] = None

#     @validator('llm', 'embedder', pre=True, always=True)
    def validate_configs(cls, v, field):
        if v is None:  # Accept None for optional fields
            return v
        return v
