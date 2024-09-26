# schemas/sustainability_impact_schema.py

"""
Module for defining schemas related to sustainability impact.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode='before')
    def check_project(cls, values):
        """Validate the project field."""
        project = values.get('project')
        if not isinstance(project, (str, dict)):
            raise ValueError("project must be either a string or a dictionary.")
        return values

    @model_validator(mode='before')
    def check_metrics(cls, values):
        """Validate the metrics field."""
        metrics = values.get('metrics')
        if not isinstance(metrics, list):
            raise ValueError("metrics must be a list.")
        for metric in metrics:
            if not isinstance(metric, str):
                raise ValueError("Each metric must be a string.")
        return values

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
