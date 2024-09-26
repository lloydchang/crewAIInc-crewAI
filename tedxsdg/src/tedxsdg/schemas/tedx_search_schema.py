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

    @validator('search_query')
    def validate_search_query(cls, v):
        """Ensure that the search_query is either a non-empty string or a dictionary with relevant keys."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Search query string cannot be empty.")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Search query dictionary cannot be empty.")
            # Add more specific validations if needed
        else:
            raise ValueError("Search query must be either a string or a dictionary.")
        return v
