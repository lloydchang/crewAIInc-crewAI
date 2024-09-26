# schemas/tedx_search_schema.py

"""
Module for TEDx search schema.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field, validator


class TEDxSearchInput(BaseModel):
    """
    Schema for TEDx search input.
    """
    search_query: Union[str, Dict[str, Any]] = Field(
        ..., description="Search query for TEDx content."
    )

    @validator('search_query', pre=True, always=True)
    def check_search_query(cls, v):
        """Validate the search_query field."""
        if not isinstance(v, (str, dict)):
            raise ValueError("search_query must be either a string or a dictionary.")
        return v
