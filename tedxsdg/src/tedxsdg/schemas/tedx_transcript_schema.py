"""
schemas/tedx_transcript_schema.py

Module for TEDxTranscriptInput schema.
"""

from pydantic import BaseModel, Field, validator


class TEDxTranscriptInput(BaseModel):
    """Schema for TEDx transcript input."""

    slug: Optional[str] = Field(
        default=None, description="The slug of the TEDx talk to retrieve the transcript for."
    )

#     @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not isinstance(v, str):
            raise TypeError("Slug must be a string.")
        return v.strip() if v else None
