# schemas/duckduckgo_search_schema.py

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Type, Union

class DuckDuckGoSearchInput(BaseModel):
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo.")
