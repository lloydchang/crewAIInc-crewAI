# schemas/tedx_slug_schema.py

"""
Module for TEDxSlugInput schema.
"""

from pydantic import BaseModel, Field, model_validator


class TEDxSlugInput(BaseModel):
    """
    Schema for TEDx slug input.
    """
    slug: str = Field(..., description="The slug to retrieve data for.")

    @model_validator(mode='before')
    def check_slug(cls, values):
        """Validate the slug field."""
        slug = values.get('slug')
        if not slug or not isinstance(slug, str):
            raise ValueError("slug must be a non-empty string.")
        return values
