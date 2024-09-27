# tools/duckduckgo_search_tool.py

"""
Module for DuckDuckGoSearchTool which performs web searches using DuckDuckGo.
"""

import logging
from duckduckgo_search import ddg

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool(BaseModel):
    """Tool for performing DuckDuckGo web searches."""

    _name: str = "duckduckgo_search"
    _description: str = "Performs web searches using DuckDuckGo."
    _args_schema = None  # Define the argument schema if necessary

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Executes a search query using DuckDuckGo.

        Args:
            input (dict): Dictionary containing 'query' for the search.

        Returns:
            str: Search results formatted as a string.
        """
        query = input.get('query', '')
        logger.debug("Running DuckDuckGo search for query: %s", query)

        if not query:
            return "Query cannot be empty."

        try:
            results = ddg(query)
            if not results:
                return "No results found."
            
            # Format results for better readability
            formatted_results = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['href']}\nSnippet: {result['body']}"
                for result in results[:3]  # Limit to top 3 results
            ])
            
            logger.debug("DuckDuckGo search results: %s", formatted_results)
            return f"Final Answer: DuckDuckGo Search Results:\n{formatted_results}"
        except Exception as e:
            logger.error("Error running DuckDuckGo search: %s", e, exc_info=True)
            return "An error occurred while performing the search."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    class Config:
        arbitrary_types_allowed = True
