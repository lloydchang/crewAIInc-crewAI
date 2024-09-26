# schemas/config_schemas.py

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, Dict, Any

# Inner configuration for the LLM (Language Model)
class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0, description="Temperature setting for the language model.")

    @field_validator('temperature')
    def validate_temperature(cls, value):
        if value is not None and value < 0:
            raise ValueError("Temperature must be equal to or greater than 0.")
        return value

# LLM Configuration
class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

    @field_validator('provider')
    def validate_provider(cls, value):
        valid_providers = ['ollama']
        if value not in valid_providers:
            raise ValueError(f"Invalid LLM provider '{value}'. Must be one of: {', '.join(valid_providers)}")
        return value

# Inner configuration for the Embedder
class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")

# Embedder Configuration
class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

    @field_validator('provider')
    def validate_provider(cls, value):
        valid_providers = ['ollama']
        if value not in valid_providers:
            raise ValueError(f"Invalid embedder provider '{value}'. Must be one of: {', '.join(valid_providers)}")
        return value

# Tool configuration that encapsulates LLM and Embedder configurations
class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig

    @field_validator('llm', 'embedder')
    def validate_configs(cls, value):
        if not value:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return value
