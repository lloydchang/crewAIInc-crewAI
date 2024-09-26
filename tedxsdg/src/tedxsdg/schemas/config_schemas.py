# schemas/config_schemas.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional

# Inner configuration for the LLM (Language Model)
class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0, description="Temperature setting for the language model.")

    @model_validator(mode='before')
    def validate_temperature(cls, values):
        temp = values.get("temperature")
        if temp is None:
            raise ValueError("Missing LLM temperature.")
        if temp < 0:
            raise ValueError("LLM temperature must be equal to or greater than 0.")
        return values

# LLM Configuration
class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

    @model_validator(mode='before')
    def validate_provider(cls, values):
        if not values.get("provider"):
            raise ValueError("Missing LLM provider.")
        return values

# Inner configuration for the Embedder
class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")
    temperature: Optional[float] = Field(0, description="Temperature setting for the embedding model.")

    @model_validator(mode='before')
    def validate_temperature(cls, values):
        temp = values.get("temperature")
        if temp is None:
            raise ValueError("Missing Embedder temperature.")
        if temp < 0:
            raise ValueError("Embedder temperature must be equal to or greater than 0.")
        return values

# Embedder Configuration
class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

    @model_validator(mode='before')
    def validate_provider(cls, values):
        if not values.get("provider"):
            raise ValueError("Missing Embedder provider.")
        return values

# Tool configuration that encapsulates LLM and Embedder configurations
class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig

    @model_validator(mode='before')
    def validate_configs(cls, values):
        if not values.get("llm") or not values.get("embedder"):
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return values
