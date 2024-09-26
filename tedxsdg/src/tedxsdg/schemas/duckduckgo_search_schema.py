# schemas/duckduckgo_search_schema.py

from pydantic import BaseModel, Field
from typing import Union, Dict, Any

class DuckDuckGoSearchInput(BaseModel):
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo.")
