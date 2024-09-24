# schemas/sdg_align_schema.py

from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any

class SDGAlignInput(BaseModel):
    idea: Union[str, Dict[str, Any]] = Field(..., description="Idea to analyze for SDG alignment.")
    sdgs: List[Union[str, int]] = Field(default_factory=list, description="List of SDGs to consider.")
