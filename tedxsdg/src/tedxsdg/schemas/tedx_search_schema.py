# schemas/tedx_search_schema.py

from pydantic import BaseModel, Field
from typing import Union, Dict, Any

class TEDxSearchInput(BaseModel):
    search_query: Union[str, Dict[str, Any]] = Field(..., description="Search query for TEDx content.")
