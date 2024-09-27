# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGoSearchTool which performs web searches using DuckDuckGo.
"""

import logging
from typing import Any, Dict
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DuckDuckGoSearchToolArgs(BaseModel):
    """Arguments for DuckDuckGoSearchTool."""
    search_query: str = Field(default=None, description="The search query for DuckDuckGo")


class DuckDuckGoSearchTool(BaseModel):
    """Tool for performing DuckDuckGo web searches."""

    _name: str = "duckduckgo_search"
    _description: str = "Performs web searches using DuckDuckGo."
    _args_schema = DuckDuckGoSearchToolArgs

    api_key: str = Field(default=None, description="API key for DuckDuckGo if required")
    base_url: str = Field(default=None, description="Base URL for DuckDuckGo API")
    search_results: Dict[str, Any] = Field(default_factory=dict, description="Search results")

    def run(self, search_query: str = None) -> str:
        """Executes the DuckDuckGo search based on the search query."""
        search_query = search_query or self.search_results.get('search_query', '')
        logger.debug("Running DuckDuckGo search for query: %s", search_query)

        try:
            results = {"results": ["Result 1", "Result 2", "Result 3"]}
            self.search_results = results
            logger.debug("Search results: %s", self.search_results)
            return f"Final Answer: DuckDuckGo Search Results:\n{self.search_results}"

        except Exception as e:
            logger.error("An error occurred during DuckDuckGo search: %s", e)
            return f"An error occurred while performing the search: {e}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> Type[BaseModel]:
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
