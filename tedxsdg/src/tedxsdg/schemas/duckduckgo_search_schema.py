"""
schemas/duckduckgo_search_schema.py

This module defines the schema for DuckDuckGo search input.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field, model_validator


class DuckDuckGoSearchInput(BaseModel):
    """Schema for DuckDuckGo search input."""

    query: Union[str, Dict[str, Any]] = Field(
        ..., description="Search query for DuckDuckGo."
    )

    @model_validator(mode='before')
    def check_query(self, values):
        """Validate the query field."""
        query = values.get('query')
        if not isinstance(query, (str, dict)):
            raise ValueError("Query must be either a string or a dictionary.")
        return values
