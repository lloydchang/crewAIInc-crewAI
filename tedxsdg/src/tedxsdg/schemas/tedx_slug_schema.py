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
    def check_slug(cls, v):
        """Validate the slug field."""
        if not v or not isinstance(v, str):
            raise ValueError("slug must be a non-empty string.")
        return v.strip()
