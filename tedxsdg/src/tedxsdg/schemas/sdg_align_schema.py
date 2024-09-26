# schemas/sdg_align_schema.py

"""
Module for defining schemas related to SDG alignment.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SDGAlignInput(BaseModel):
    """
    Schema for SDG alignment input.
    """
    idea: Union[str, Dict[str, Any]] = Field(
        ..., description="Idea to analyze for SDG alignment."
    )
    sdgs: List[Union[str, int]] = Field(
        default_factory=list, description="List of SDGs to consider."
    )

    @field_validator('idea')
    def validate_idea(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Idea string cannot be empty.")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Idea dictionary cannot be empty.")
        else:
            raise TypeError("Idea must be either a string or a dictionary.")
        return v

    @field_validator('sdgs')
    def validate_sdgs(cls, v):
        if not isinstance(v, list):
            raise TypeError("SDGs must be provided as a list.")
        for sdg in v:
            if not isinstance(sdg, (str, int)):
                raise TypeError("Each SDG must be either a string or an integer.")
        return v
