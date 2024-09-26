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
    search_query: str = Field(
        ..., description="The search query for DuckDuckGo"
    )


class DuckDuckGoSearchTool(StructuredTool, BaseModel):
    """Tool for performing DuckDuckGo web searches."""

    # Define class-level attributes without type annotations
    name = "duckduckgo_search"
    description = "Performs web searches using DuckDuckGo."
    args_schema = DuckDuckGoSearchToolArgs

    # Define instance-level fields
    api_key: str = Field(..., description="API key for DuckDuckGo if required")
    base_url: str = Field(..., description="Base URL for DuckDuckGo API")

    # Initialize any additional attributes
    search_results: Dict[str, Any] = Field(default_factory=dict)

    @validator('base_url')
    def check_base_url(cls, base_url: str) -> str:
        """
        Validates that the base_url starts with 'http' or 'https'.
        """
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http or https")
        return base_url

    @validator('search_results', pre=True, always=True)
    def load_search_results(cls, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder validator for loading search results if necessary.
        Currently, it simply returns the existing search_results.
        """
        # Implement additional logic here if needed
        return search_results

    def run(self, search_query: str) -> str:
        """
        Executes the DuckDuckGo search based on the search query.
        """
        logger.debug("Running DuckDuckGo search for query: %s", search_query)

        try:
            # Implement the actual search logic here
            # For demonstration, returning a mock response
            # Example: Make an API call to DuckDuckGo (pseudo-code)
            # response = requests.get(f"{self.base_url}/search", params={"q": search_query, "api_key": self.api_key})
            # response.raise_for_status()
            # results = response.json()

            # Mock response for demonstration purposes
            results = {"results": ["Result 1", "Result 2", "Result 3"]}

            self.search_results = results
            logger.debug("Search results: %s", self.search_results)
            return f"Final Answer: DuckDuckGo Search Results:\n{self.search_results}"

        except Exception as e:
            logger.error("An error occurred during DuckDuckGo search: %s", e)
            return f"An error occurred while performing the search: {e}"
