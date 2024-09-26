"""
Module for TEDxSlugInput schema.
"""

from pydantic import BaseModel, Field


class TEDxSlugInput(BaseModel):
    """
    Schema for TEDx slug input.
    """
    slug: str = Field(..., description="The slug to retrieve data for.")
