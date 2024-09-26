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
        default="Unnamed Project",
        _description = "Project to assess for sustainability impact."
    )
    metrics: List[str] = Field(
        default=list,
        _description = "List of sustainability metrics."
    )

    @validator('project')
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

    @validator('metrics', each_item=True)
    def validate_metrics(cls, v):
        if not isinstance(v, str):
            raise TypeError("Each metric must be a string.")
        if not v.strip():
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

class SustainabilityImpactInput(BaseModel):
:
    @property
    def description(self):
        return self._description

    @property
    def description(self):
        return self._description
