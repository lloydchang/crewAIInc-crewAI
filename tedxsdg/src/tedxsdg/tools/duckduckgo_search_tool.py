# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGo search tool.
"""

import logging
from typing import Any, Dict, Union
from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from .utils import extract_query_string

logger = logging.getLogger(__name__)


class DuckDuckGoSearchTool(StructuredTool):
    """
    Tool for performing web searches using DuckDuckGo.
    """
    name: str = "duckduckgo_search"
    description: str = "Searches the web using DuckDuckGo."

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the search tool with the given configuration.
        """
        super().__init__()
        self.llm_config = config.get('llm_config')
        self.embedder_config = config.get('embedder_config')
        if not self.llm_config or not self.embedder_config:
            raise ValueError(
                "Missing LLM configuration or Embedder configuration."
            )

    def _run(self, query: Union[str, Dict[str, Any]], *args: Any, **kwargs: Any) -> str:
        """
        Run the DuckDuckGo search with the given query.
        """
        query_str = extract_query_string(query)
        if not query_str:
            logger.error("No valid search query provided.")
            return "Error: No valid search query provided."

        try:
            logger.debug("Running DuckDuckGo search for query: %s", query_str)
            search_api = DuckDuckGoSearchAPIWrapper()
            result = search_api.run(query_str)

            if not result:
                logger.warning("No results found for query: %s", query_str)
                return f"No results found for '{query_str}'."

            return (
                f"Final Answer: DuckDuckGo Search Results for '{query_str}':\n"
                f"{result}"
            )

            logger.error(
                "Error during DuckDuckGo search: %s", str(e), exc_info=True
            )
            logger.error("Error during DuckDuckGo search: %s", str(e), exc_info=True)
            return f"Error during DuckDuckGo search: {str(e)}"
