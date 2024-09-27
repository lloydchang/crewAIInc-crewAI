"""
schemas/sdg_align_schema.py

Module for defining schemas related to SDG alignment.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, validator


class SDGAlignInput(BaseModel):
    """Schema for SDG alignment input."""

    idea: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None, description="Idea to analyze for SDG alignment."
    )
    sdgs: Optional[List[Union[str, int]]] = Field(
        default_factory=list, description="List of SDGs to consider."
    )

#     @validator('idea')
    def validate_idea(cls, v):
        if v is not None:  # Only validate if the value is not None
            if isinstance(v, str) and not v.strip():
                raise ValueError("Idea string cannot be empty.")
            elif isinstance(v, dict) and not v:
                raise ValueError("Idea dictionary cannot be empty.")
        return v

#     @validator('sdgs', each_item=True)
    def validate_sdgs(cls, v):
        if v is not None and not isinstance(v, (str, int)):
            raise TypeError("Each SDG must be either a string or an integer.")
        return v
