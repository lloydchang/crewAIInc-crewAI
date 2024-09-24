# schemas/tedx_slug_schema.py

from pydantic import BaseModel, Field

class TEDxSlugInput(BaseModel):
    slug: str = Field(..., description="The slug to retrieve data for.")
