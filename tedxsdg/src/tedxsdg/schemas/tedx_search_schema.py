"""
schemas/tedx_search_schema.py

Module for TEDx search schema.
"""

from typing import Union, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class TEDxSearchInput(BaseModel):
    """Schema for TEDx search input."""

    search_query: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None, description="Search query for TEDx content."
    )

    @validator('search_query')
    def check_search_query(cls, v):
        """Validate the search_query field."""
        if v is not None and not isinstance(v, (str, dict)):
            raise ValueError("search_query must be either a string or a dictionary.")
        return v
