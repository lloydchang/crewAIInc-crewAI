# tools/sdg_align_tool.py

"""
Module for SDGAlignTool which aligns query with Sustainable Development Goals (SDGs).
"""

import logging
from pydantic import BaseModel, Field
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SDGAlignToolArgs(BaseModel):
    """Arguments for SDGAlignTool."""
    query: str = Field(default=None, description="query to be aligned with SDGs.")

class SDGAlignTool(BaseModel):
    """Tool for aligning query with SDGs."""

    _name: str = "sdg_align"
    _description: str = "Aligns query with Sustainable Development Goals."
    _args_schema = SDGAlignToolArgs

    def invoke(self, input: Dict[str, Any]) -> str:
        """Align the given query with SDGs."""
        query = input.get("query")
        if not query:
            return "Error: 'query' is required in the input."

        logger.debug("Aligning query with SDGs: %s", query)

        # Implement the alignment logic here
        aligned_sdgs = ["SDG 4", "SDG 13"]  # Example output

        logger.debug("Aligned SDGs: %s", aligned_sdgs)
        return f"Final Answer: query aligned with: {', '.join(aligned_sdgs)}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    @property
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
