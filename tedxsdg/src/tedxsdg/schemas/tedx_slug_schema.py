# schemas/tedx_slug_schema.py

"""
Module for TEDxSlugInput schema.
"""

from pydantic import BaseModel, Field, validator


class TEDxSlugInput(BaseModel):
    """
    Schema for TEDx slug input.
    """
    slug: str = Field(..., description="The slug to retrieve data for.")

    @validator('slug')
    def validate_slug(cls, v):
        """Ensure that the slug is a non-empty string and follows expected format."""
        if not v.strip():
            raise ValueError("Slug cannot be empty.")
        # Add more specific slug format validations if necessary
        return v.strip().lower()
