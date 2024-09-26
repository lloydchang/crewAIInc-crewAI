# schemas/sustainability_impact_schema.py

"""
Module for defining schemas related to sustainability impact.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field


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

        @classmethod
        def get_schema_extra(cls):
            """
            Returns the schema extra configuration.
            """
            return cls.schema_extra

        @classmethod
        def set_schema_extra(cls, example: Dict[str, Any]):
            """
            Sets a new schema extra configuration.
            """
            cls.schema_extra = example

        def get_example(self):
            """
            Returns the example schema.
            """
            return SustainabilityImpactInput.Config.schema_extra["example"]

        def set_example(self, example: Dict[str, Any]):
            """
            Sets a new example schema.
            """
            SustainabilityImpactInput.Config.schema_extra["example"] = example
