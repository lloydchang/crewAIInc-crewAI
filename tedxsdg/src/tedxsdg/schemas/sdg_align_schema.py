# schemas/sdg_align_schema.py

"""
Module for defining schemas related to SDG alignment.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode='before')
    def check_idea(cls, values):
        """Validate the idea field."""
        idea = values.get('idea')
        if not isinstance(idea, (str, dict)):
            raise ValueError("idea must be either a string or a dictionary.")
        return values

    @model_validator(mode='before')
    def check_sdgs(cls, values):
        """Validate the sdgs field."""
        sdgs = values.get('sdgs')
        if not isinstance(sdgs, list):
            raise ValueError("sdgs must be a list.")
        for sdg in sdgs:
            if not isinstance(sdg, (str, int)):
                raise ValueError("Each SDG must be a string or integer.")
        return values
