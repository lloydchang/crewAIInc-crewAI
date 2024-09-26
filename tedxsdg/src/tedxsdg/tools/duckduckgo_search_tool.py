# tools/duckduckgo_search_tool.py

import logging
from langchain.tools import StructuredTool
from typing import Any, Dict, Union
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from .utils import extract_query_string

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool(StructuredTool):
    name: str = "duckduckgo_search"
    description: str = "Searches the web using DuckDuckGo."

    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any]):
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config

    def _run(self, query: Union[str, Dict[str, Any]]) -> str:
        query_str = extract_query_string(query)
        if not query_str:
            logger.error("No valid search query provided.")
            return "Error: No valid search query provided."
        
        try:
            logger.debug(f"Running DuckDuckGo search for query: {query_str}")
            search_api = DuckDuckGoSearchAPIWrapper()
            result = search_api.run(query_str)
            
            if not result:
                logger.warning(f"No results found for query: {query_str}")
                return f"No results found for '{query_str}'."
            
            return f"Final Answer: DuckDuckGo Search Results for '{query_str}':\n{result}"
        
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}", exc_info=True)
            return f"Error during DuckDuckGo search: {str(e)}"
