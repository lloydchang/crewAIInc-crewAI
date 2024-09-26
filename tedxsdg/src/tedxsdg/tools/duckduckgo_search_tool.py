# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGoSearchTool which performs web searches using DuckDuckGo.
"""

import logging
from typing import Any, Dict, Type
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class DuckDuckGoSearchToolArgs(BaseModel):
    """Arguments for DuckDuckGoSearchTool."""
    search_query: str = Field(..., description="The search query for DuckDuckGo")


class DuckDuckGoSearchTool(StructuredTool):
    """Tool for performing DuckDuckGo web searches."""

    # Class-level attributes, completely removed from Pydantic and using class properties
    _name: str = "duckduckgo_search"
    _description: str = "Performs web searches using DuckDuckGo."
    _args_schema = DuckDuckGoSearchToolArgs

    # Instance-level fields
    api_key: str = Field(..., description="API key for DuckDuckGo if required")
    base_url: str = Field(..., description="Base URL for DuckDuckGo API")
    search_results: Dict[str, Any] = Field(default_factory=dict, description="Search results")

    @validator('base_url')
    def check_base_url(cls, base_url: str) -> str:
        """Validates that the base_url starts with 'http' or 'https'."""
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http or https")
        return base_url

    @validator('search_results', pre=True, always=True)
    def load_search_results(cls, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder validator for loading search results if necessary."""
        return search_results

    def run(self, search_query: str) -> str:
        """Executes the DuckDuckGo search based on the search query."""
        logger.debug("Running DuckDuckGo search for query: %s", search_query)

        try:
            # Mock response for demonstration purposes
            results = {"results": ["Result 1", "Result 2", "Result 3"]}
            self.search_results = results
            logger.debug("Search results: %s", self.search_results)
            return f"Final Answer: DuckDuckGo Search Results:\n{self.search_results}"

        except Exception as e:
            logger.error("An error occurred during DuckDuckGo search: %s", e)
            return f"An error occurred while performing the search: {e}"

    # Use simple class properties
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> Type[BaseModel]:
        return self._args_schema

    # Prevent deep copy of specific class fields
    def __getstate__(self):
        """Customize what gets pickled or deepcopied."""
        state = self.__dict__.copy()
        # Remove any classmethods or non-pickleable objects from state
        if '_name' in state:
            del state['_name']
        if '_description' in state:
            del state['_description']
        if '_args_schema' in state:
            del state['_args_schema']
        return state

    def __setstate__(self, state):
        """Restore state from deep copy or pickle."""
        self.__dict__.update(state)

    class Config:
        arbitrary_types_allowed = True
