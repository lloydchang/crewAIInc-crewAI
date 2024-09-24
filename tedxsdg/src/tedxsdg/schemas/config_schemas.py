# schemas/config_schemas.py

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional

class LLMInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the language model to use.")
    temperature: Optional[float] = Field(1.0, description="Temperature setting for the language model.")
    top_p: Optional[float] = Field(1.0, description="Top-p (nucleus) sampling parameter.")
    stream: Optional[bool] = Field(False, description="Whether to stream responses.")

    @field_validator('temperature')
    def temperature_non_negative(cls, v):
        if v < 0.0:
            raise ValueError('Temperature must be non-negative')
        return v

class LLMConfig(BaseModel):
    provider: str = Field(..., description="Provider of the language model.")
    config: LLMInnerConfig

class EmbedderInnerConfig(BaseModel):
    model: str = Field(..., description="Name of the embedding model.")
    task_type: Optional[str] = Field("retrieval_document", description="Type of task for embeddings.")
    title: Optional[str] = Field(None, description="Title for embeddings.")

class EmbedderConfig(BaseModel):
    provider: str = Field(..., description="Provider of the embedding model.")
    config: EmbedderInnerConfig

class ToolConfig(BaseModel):
    llm: LLMConfig
    embedder: EmbedderConfig
