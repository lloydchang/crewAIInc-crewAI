# schemas/config_schemas.py

from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Any, Dict, List, Optional, Type, Union

class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0.7, description="Temperature setting for the language model.")
    
    @model_validator(mode='before')
    def validate_temperature(cls, values):
        temperature = values.get('temperature', 0.7)
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return values

class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

    @model_validator(mode='before')
    def validate_provider(cls, values):
        provider = values.get('provider')
        valid_providers = ['ollama']
        if provider not in valid_providers:
            raise ValueError(f"Invalid LLM provider '{provider}'. Must be one of: {', '.join(valid_providers)}")
        return values

class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")

class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

    @model_validator(mode='before')
    def validate_provider(cls, values):
        provider = values.get('provider')
        valid_providers = ['ollama']
        if provider not in valid_providers:
            raise ValueError(f"Invalid embedder provider '{provider}'. Must be one of: {', '.join(valid_providers)}")
        return values

class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig

    @model_validator(mode='after')
    def validate_configs(cls, values):
        llm_config = values.llm
        embedder_config = values.embedder
        
        if not llm_config or not embedder_config:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return values