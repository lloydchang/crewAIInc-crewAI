# schemas/tedx_transcript_schema.py

"""
Module for TEDxTranscriptInput schema.
"""

from pydantic import BaseModel, Field, field_validator


class TEDxTranscriptInput(BaseModel):
    """
    Schema for TEDx transcript input.
    """
    slug: str = Field(
        ...,
        description="The slug of the TEDx talk to retrieve the transcript for."
    )

    @field_validator('slug')
    def validate_slug(cls, v):
        if not v:
            raise ValueError("Slug cannot be empty.")
        if not isinstance(v, str):
            raise TypeError("Slug must be a string.")
        return v.strip()
