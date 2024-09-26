# schemas/sustainability_impact_schema.py

"""
Module for defining schemas related to sustainability impact.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SustainabilityImpactInput(BaseModel):
    """
    Schema for sustainability impact input.
    """
    project: Union[str, Dict[str, Any]] = Field(
        default="Unnamed Project",
        description="Project to assess for sustainability impact."
    )
    metrics: List[str] = Field(
        default_factory=list,
        description="List of sustainability metrics."
    )

    @field_validator('project')
    def validate_project(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Project string cannot be empty.")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Project dictionary cannot be empty.")
        else:
            raise TypeError("Project must be either a string or a dictionary.")
        return v

    @field_validator('metrics')
    def validate_metrics(cls, v):
        if not isinstance(v, list):
            raise TypeError("Metrics must be provided as a list.")
        for metric in v:
            if not isinstance(metric, str):
                raise TypeError("Each metric must be a string.")
            if not metric.strip():
                raise ValueError("Metrics cannot contain empty strings.")
        return v

    class Config:
        """
        Configuration for the SustainabilityImpactInput schema.
        """
        schema_extra = {
            "example": {
                "project": "Green Energy Initiative",
                "metrics": ["carbon footprint", "energy efficiency"]
            }
        }
