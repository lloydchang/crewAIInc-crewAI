"""
schemas/duckduckgo_search_schema.py

This module defines the schema for DuckDuckGo search input.
"""

from typing import Union, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class DuckDuckGoSearchInput(BaseModel):
    """Schema for DuckDuckGo search input."""

    search_query: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None, description="Search query for DuckDuckGo."
    )

    @validator('search_query')
    def check_search_query(cls, v):
        """Validate the search_query field."""
        if v is not None and not isinstance(v, (str, dict)):
            raise ValueError("search_query must be either a string or a dictionary.")
        return v
