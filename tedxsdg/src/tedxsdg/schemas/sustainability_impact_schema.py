"""
schemas/sustainability_impact_schema.py

Module for defining schemas related to sustainability impact.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, validator


class SustainabilityImpactInput(BaseModel):
    """Schema for sustainability impact input."""

    project: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None,
        description="Project to assess for sustainability impact."
    )
    metrics: Optional[List[str]] = Field(
        default_factory=list,
        description="List of sustainability metrics."
    )

#     @validator('project')
    def validate_project(cls, v):
        if v is not None:  # Only validate if the value is not None
            if isinstance(v, str) and not v.strip():
                raise ValueError("Project string cannot be empty.")
            elif isinstance(v, dict) and not v:
                raise ValueError("Project dictionary cannot be empty.")
        return v

#     @validator('metrics', each_item=True)
    def validate_metrics(cls, v):
        if v is not None and not isinstance(v, str):
            raise TypeError("Each metric must be a string.")
        if v and not v.strip():
            raise ValueError("Metrics cannot contain empty strings.")
        return v
