# schemas/tedx_transcript_schema.py

from pydantic import BaseModel, Field

class TEDxTranscriptInput(BaseModel):
    slug: str = Field(..., description="The slug of the TEDx talk to retrieve the transcript for.")
