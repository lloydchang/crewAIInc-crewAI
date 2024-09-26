# schemas/duckduckgo_search_schema.py

"""
schemas/duckduckgo_search_schema.py

This module defines the schema for DuckDuckGo search input.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field, validator


class DuckDuckGoSearchInput(BaseModel):
    """Schema for DuckDuckGo search input."""

    search_query: Union[str, Dict[str, Any]] = Field(
        ..., _description = "Search query for DuckDuckGo."
    )

    @validator('search_query', pre=True, always=True)
    def check_search_query(cls, v):
        """Validate the search_query field."""
        if not isinstance(v, (str, dict)):
            raise ValueError("search_query must be either a string or a dictionary.")
        return v

class DuckDuckGoSearchInput(BaseModel):
:
    @property
    def description(self):
        return self._description
