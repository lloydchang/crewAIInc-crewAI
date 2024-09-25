# schemas/config_schemas.py

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Any, Dict, List, Optional, Type, Union

class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0.7, description="Temperature setting for the language model.")
    top_p: Optional[float] = Field(1.0, description="Top-p (nucleus) sampling parameter.")
    stream: Optional[bool] = Field(False, description="Whether to stream responses.")

    @field_validator('temperature')
    def temperature_must_be_non_negative(cls, v):
        """Ensure temperature is between 0.0 and 2.0."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @field_validator('model')
    def valid_llm_model(cls, v):
        """Ensure that the model is valid based on provider constraints."""
        valid_models = ['ollama/llama3']  # Add valid models as needed
        if v not in valid_models:
            raise ValueError(f"Invalid LLM model '{v}'. Must be one of: {', '.join(valid_models)}")
        return v

class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

    @field_validator('provider')
    def valid_llm_provider(cls, v):
        """Ensure provider is recognized."""
        valid_providers = ['ollama']
        if v not in valid_providers:
            raise ValueError(f"Invalid LLM provider '{v}'. Must be one of: {', '.join(valid_providers)}")
        return v

class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")

    @field_validator('model')
    def valid_embedder_model(cls, v):
        """Ensure that the model is valid."""
        valid_models = ['nomic-embed-text']  # Add as needed
        if v not in valid_models:
            raise ValueError(f"Invalid embedder model '{v}'. Must be one of: {', '.join(valid_models)}")
        return v

class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

    @field_validator('provider')
    def valid_embedder_provider(cls, v):
        """Ensure provider is recognized."""
        valid_providers = ['ollama']
        if v not in valid_providers:
            raise ValueError(f"Invalid embedder provider '{v}'. Must be one of: {', '.join(valid_providers)}")
        return v

class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig

    @field_validator('llm', 'embedder')
    def validate_configs(cls, v):
        """Ensure both LLM and Embedder configurations are initialized correctly."""
        if not v:
            raise ValueError(f"{v} configuration is not initialized properly")
        return v

# Example usage:
if __name__ == "__main__":
    try:
        # Correct initialization
        llm_conf = LLMConfig(
            provider="ollama",
            config=LLMInnerConfig(model="llama3", temperature=0.7)
        )
        
        embedder_conf = EmbedderConfig(
            provider="nomic",
            config=EmbedderInnerConfig(model="nomic-embed-text")
        )
        
        tool_conf = ToolConfig(llm=llm_conf, embedder=embedder_conf)
        print("Configuration successful:", tool_conf)

    except ValidationError as e:
        print(f"Validation error: {e}")
