# schemas/duckduckgo_search_schema.py

"""
schemas/duckduckgo_search_schema.py

This module defines the schema for DuckDuckGo search input.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field, model_validator


class DuckDuckGoSearchInput(BaseModel):
    """Schema for DuckDuckGo search input."""

    search_query: Union[str, Dict[str, Any]] = Field(
        ..., description="Search query for DuckDuckGo."
    )

    @model_validator(mode='before')
    def check_search_query(cls, values):
        """Validate the search_query field."""
        search_query = values.get('search_query')
        if not isinstance(search_query, (str, dict)):
            raise ValueError("search_query must be either a string or a dictionary.")
        return values
