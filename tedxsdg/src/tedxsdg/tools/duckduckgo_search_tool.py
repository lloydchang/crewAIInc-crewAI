# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGoSearchTool which performs web searches using DuckDuckGo.
"""

import logging
from typing import Any, Dict, Optional
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, validator

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
    args_schema: type[BaseModel] = DuckDuckGoSearchToolArgs

    # Define required fields
    api_key: Optional[str] = Field(None, description="API key for DuckDuckGo if required")
    base_url: str = Field(..., description="Base URL for DuckDuckGo API")

    # Initialize any additional attributes
    search_results: Dict[str, Any] = Field(default_factory=dict)

    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith("http"):
            raise ValueError("base_url must be a valid URL starting with http or https")
        return v

    @validator('search_results', pre=True, always=True)
    def initialize_search_results(cls, v):
        return {}

    def run(self, search_query: str) -> str:
        """
        Executes the DuckDuckGo search based on the search query.
        
        Args:
            search_query (str): The search query string.
        
        Returns:
            str: Formatted search results.
        """
        logger.debug("Running DuckDuckGo search for query: %s", search_query)
        try:
            # Example implementation using DuckDuckGo Instant Answer API
            params = {
                'q': search_query,
                'format': 'json',
                'no_redirect': 1,
                'no_html': 1,
                'skip_disambig': 1,
            }
            response = requests.get(self.base_url, params=params, headers={'Authorization': f"Bearer {self.api_key}"} if self.api_key else {})
            response.raise_for_status()
            data = response.json()
            # Process the JSON response to extract relevant information
            results = data.get('RelatedTopics', [])[:3]  # Limiting to top 3 results
            formatted_results = [topic.get('Text', 'No Title') for topic in results]
            self.search_results = formatted_results
            logger.debug("Search results: %s", self.search_results)
            return f"Final Answer: DuckDuckGo Search Results:\n{formatted_results}"
        except requests.RequestException as e:
            logger.error("HTTP request failed: %s", e, exc_info=True)
            return f"Error: Failed to perform search due to an HTTP error: {e}"
        except Exception as e:
            logger.error("An unexpected error occurred during search: %s", e, exc_info=True)
            return f"Error: An unexpected error occurred during search: {e}"
