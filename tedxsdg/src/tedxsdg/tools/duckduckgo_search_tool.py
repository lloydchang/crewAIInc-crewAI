# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGoSearchTool which performs web searches using DuckDuckGo.
"""

import logging
from typing import Any, Dict, Type
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class DuckDuckGoSearchToolArgs(BaseModel):
    """Arguments for DuckDuckGoSearchTool."""
    search_query: str = Field(
        ..., description="The search query for DuckDuckGo"
    )


class DuckDuckGoSearchTool(StructuredTool):
    """Tool for performing DuckDuckGo web searches."""
    name: str = "duckduckgo_search"
    description: str = "Performs web searches using DuckDuckGo."
    args_schema: Type[BaseModel] = DuckDuckGoSearchToolArgs

    # Define any required fields
    api_key: str = Field(..., description="API key for DuckDuckGo if required")
    base_url: str = Field(..., description="Base URL for DuckDuckGo API")

    # Initialize any additional attributes
    search_results: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    def check_fields(cls, values):
        base_url = values.get('base_url')
        if not base_url.startswith("http"):
            raise ValueError("base_url must be a valid URL starting with http or https")
        return values

    @model_validator(mode='after')
    def load_search_results(cls, model):
        # Placeholder for loading search results if necessary
        return model

    def run(self, search_query: str) -> str:
        """Executes the DuckDuckGo search based on the search query."""
        logger.debug("Running DuckDuckGo search for query: %s", search_query)
        # Implement the actual search logic here
        # For demonstration, returning a mock response
        results = {"results": ["Result 1", "Result 2", "Result 3"]}
        self.search_results = results
        logger.debug("Search results: %s", self.search_results)
        return f"Final Answer: DuckDuckGo Search Results:\n{self.search_results}"
