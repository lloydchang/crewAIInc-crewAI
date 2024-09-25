# schemas/config_schemas.py

from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Any, Dict, List, Optional, Type, Union

class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(0.7, description="Temperature setting for the language model.")
    top_p: Optional[float] = Field(1.0, description="Top-p (nucleus) sampling parameter.")
    stream: Optional[bool] = Field(False, description="Whether to stream responses.")

    @model_validator(mode='before')
    def validate_temperature(cls, values):
        temperature = values.get('temperature', 0.7)
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return values

    @model_validator(mode='before')
    def validate_model(cls, values):
        model = values.get('model')
        valid_models = ['ollama/llama3']  # Add valid models as needed
        if model not in valid_models:
            raise ValueError(f"Invalid LLM model '{model}'. Must be one of: {', '.join(valid_models)}")
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

    @model_validator(mode='before')
    def validate_model(cls, values):
        model = values.get('model')
        valid_models = ['nomic-embed-text']  # Add as needed
        if model not in valid_models:
            raise ValueError(f"Invalid embedder model '{model}'. Must be one of: {', '.join(valid_models)}")
        return values

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
        llm_config = values.get('llm')
        embedder_config = values.get('embedder')
        
        if not llm_config or not embedder_config:
            raise ValueError("Both LLM and Embedder configurations must be initialized properly.")
        return values

# Example usage:
if __name__ == "__main__":
    try:
        # Correct initialization
        llm_conf = LLMConfig(
            provider="ollama",
            config=LLMInnerConfig(model="ollama/llama3", temperature=0.7)  # Use the valid model
        )
        
        embedder_conf = EmbedderConfig(
            provider="ollama",
            config=EmbedderInnerConfig(model="nomic-embed-text")
        )
        
        tool_conf = ToolConfig(llm=llm_conf, embedder=embedder_conf)
        print("Configuration successful:", tool_conf)

    except ValidationError as e:
        print(f"Validation error: {e}")
