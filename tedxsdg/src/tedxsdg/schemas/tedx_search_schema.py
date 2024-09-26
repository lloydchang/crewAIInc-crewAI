# schemas/tedx_search_schema.py

"""
Module for TEDx search schema.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field


class TEDxSearchInput(BaseModel):
    """
    Schema for TEDx search input.
    """
    __root__: Union[str, Dict[str, Any]] = Field(
        ..., description="Search query for TEDx content."
    )
