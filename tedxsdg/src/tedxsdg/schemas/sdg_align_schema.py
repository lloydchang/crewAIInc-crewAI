# schemas/sdg_align_schema.py

"""
Module for defining schemas related to SDG alignment.
"""

from typing import List, Union, Dict, Any
from pydantic import BaseModel, Field


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
