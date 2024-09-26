# schemas/sustainability_impact_schema.py

from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any

class SustainabilityImpactInput(BaseModel):
    project: Union[str, Dict[str, Any]] = Field(default="Unnamed Project", description="Project to assess for sustainability impact.")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics.")
