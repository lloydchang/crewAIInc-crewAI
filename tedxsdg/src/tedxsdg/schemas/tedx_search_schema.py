# schemas/tedx_search_schema.py

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Type, Union

class TEDxSearchInput(BaseModel):
    search_query: Union[str, Dict[str, Any]] = Field(..., description="Search query for TEDx content.")
