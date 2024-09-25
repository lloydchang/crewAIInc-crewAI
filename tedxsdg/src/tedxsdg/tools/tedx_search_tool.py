# tools/tedx_search_tool.py

import os
import logging
import csv
from typing import Union, Dict, Any, Type, Optional
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from schemas.tedx_search_schema import TEDxSearchInput
from schemas.config_schemas import LLMConfig, EmbedderConfig
from crewai_tools import CSVSearchTool
from .utils import extract_query_string

logger = logging.getLogger(__name__)

# logging.getLogger().setLevel(logging.DEBUG)

logger.debug("Debug logging is working at the top of the script.")

class TEDxSearchTool(StructuredTool):
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."
    args_schema: Type[BaseModel] = TEDxSearchInput

    llm_config: LLMConfig = Field(exclude=True)
    embedder_config: EmbedderConfig = Field(exclude=True)
    data_path: str = Field(default='data/github-mauropelucchi-tedx_dataset-update_2024-details.csv', description="Path to the TEDx dataset CSV.")
    csv_search_tool: Optional[CSVSearchTool] = None  # Declare as a field
    csv_data: Optional[Dict[str, Dict[str, Any]]] = None  # Declare as a field

    def _invalidate_cache(self):
        logger.info("Invalidating the cache via rm -rf db")
        os.system("rm -rf db")

    def _initialize_csv_search_tool(self) -> Optional[CSVSearchTool]:
        try:
            return CSVSearchTool(
                csv=self.data_path,
                config={
                    "llm": self.llm_config,
                    "embedder": self.embedder_config,
                }
            )
        except ValueError as e:
            logger.warning(f"Failed to initialize CSVSearchTool: {e}")
            return None

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: str = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'):
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path

        print("Initialize CSVSearchTool with the provided configurations")

        # First attempt to initialize CSVSearchTool
        try:
            self.csv_search_tool = self._initialize_csv_search_tool()
        except Exception as e:
            logger.error(f"Error during initial initialization: {str(e)}", exc_info=True)
            self.csv_search_tool = None

        # If the first initialization fails, invalidate the cache and try again
        if self.csv_search_tool is None:
            logger.info("Attempting to invalidate cache and reinitialize CSVSearchTool.")
            self._invalidate_cache()

            try:
                self.csv_search_tool = self._initialize_csv_search_tool()
                if self.csv_search_tool is None:
                    logger.error("Failed to initialize CSVSearchTool after cache invalidation.")
                    raise RuntimeError("CSVSearchTool could not be initialized.")
            except Exception as e:
                logger.error(f"Error during reinitialization: {str(e)}", exc_info=True)
                raise RuntimeError("CSVSearchTool could not be initialized after cache invalidation.")

        self.csv_data = self._load_csv_data()

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        try:
            slug_index = {}
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug(f"Loaded {len(slug_index)} slugs from CSV file.")
            return slug_index
        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}", exc_info=True)
            raise Exception("Failed to load CSV data.")

    def _find_row_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        return self.csv_data.get(slug)

    def _run(self, search_query: Union[str, Dict[str, Any]], **kwargs: Any) -> str:
        try:
            query_str = extract_query_string(search_query)
            if not query_str:
                raise ValueError("No valid search query found.")

            logger.debug(f"Running CSV search for query: {query_str}")
            search_result = self.csv_search_tool._run(search_query=query_str)

            if not search_result:
                return "No results found in the CSV."

            logger.debug(f"CSV search result: {search_result}")

            return f"Final Answer: CSV Search Results for '{query_str}':\n{search_result}"

        except ValueError as ve:
            logger.error(f"Value error: {str(ve)}")
            return f"Error: {str(ve)}"
        except Exception as e:
            logger.error(f"Error during CSV search: {str(e)}", exc_info=True)
            return f"Error during CSV search: {str(e)}"
