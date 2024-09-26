# schemas/sustainability_impact_schema.py

"""
Module for defining schemas related to sustainability impact.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, validator


class SustainabilityImpactInput(BaseModel):
    """
    Schema for sustainability impact input.
    """
    project: Union[str, Dict[str, Any]] = Field(
        ..., description="Project to assess for sustainability impact."
    )
    metrics: List[str] = Field(
        ..., description="List of sustainability metrics."
    )

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

    @validator('project')
    def validate_project(cls, v):
        """Ensure that the project field is non-empty."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Project name cannot be empty.")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Project details dictionary cannot be empty.")
            # Add more specific validations if needed
        else:
            raise ValueError("Project must be either a string or a dictionary.")
        return v

    @validator('metrics', each_item=True)
    def validate_metrics(cls, v):
        """Ensure that each metric is a non-empty string."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Each metric must be a non-empty string.")
        return v.strip()
