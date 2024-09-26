"""
Module for TEDx transcript schema.
"""

from pydantic import BaseModel, Field


class TEDxTranscriptInput(BaseModel):
    """
    Schema for TEDx transcript input.
    """
    slug: str = Field(
        ...,
        description="The slug of the TEDx talk to retrieve the transcript for."
    )
