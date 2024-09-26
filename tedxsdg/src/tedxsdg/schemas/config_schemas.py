# schemas/config_schemas.py

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, Dict, Any

# Inner configuration for the LLM (Language Model)
class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0, description="Temperature setting for the language model.")

    @field_validator('temperature')
    def validate_temperature(cls, value):
        if value is None:
            raise ValueError("Missing LLM temperature.")
        if value < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return value

# LLM Configuration
class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

    @field_validator('provider')
    def validate_provider(cls, value):
        if value is None:
            raise ValueError("Missing LLM provider.")
        return value

# Inner configuration for the Embedder
class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")
    temperature: Optional[float] = Field(0, description="Temperature setting for the embedding model.")

    @field_validator('temperature')
    def validate_temperature(cls, value):
        if value is None:
            raise ValueError("Missing Embedder temperature.")
        if value < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return value

# Embedder Configuration
class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

    @field_validator('provider')
    def validate_provider(cls, value):
        if value is None:
            raise ValueError("Missing Embedder provider.")
        return value

# Tool configuration that encapsulates LLM and Embedder configurations
class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig

    @field_validator('llm', 'embedder')
    def validate_configs(cls, value):
        if value is None:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return value
