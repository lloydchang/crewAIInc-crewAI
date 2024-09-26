# schemas/duckduckgo_search_schema.py

"""
schemas/duckduckgo_search_schema.py

This module defines the schema for DuckDuckGo search input.
"""

from typing import Union, Dict, Any
from pydantic import BaseModel, Field, validator


class DuckDuckGoSearchInput(BaseModel):
    """Schema for DuckDuckGo search input."""

    query: Union[str, Dict[str, Any]] = Field(
        ..., description="Search query for DuckDuckGo."
    )

    @validator('query')
    def validate_query(cls, v):
        """Ensure that the query is either a non-empty string or a dictionary with relevant keys."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Query string cannot be empty.")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Query dictionary cannot be empty.")
            # Add more specific validations if needed
        else:
            raise ValueError("Query must be either a string or a dictionary.")
        return v
