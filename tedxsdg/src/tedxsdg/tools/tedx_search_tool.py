# tools/tedx_search_tool.py

import os
import logging
import csv
from typing import Any, Dict, Optional, Union
from langchain.tools import StructuredTool
from pydantic import ValidationError
from schemas.tedx_search_schema import TEDxSearchInput
from schemas.config_schemas import LLMConfig, EmbedderConfig
from crewai_tools import CSVSearchTool
from .utils import extract_query_string

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TEDxSearchTool(StructuredTool):
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."
    args_schema = TEDxSearchInput

    # Define attributes without underscore
    llm_config: LLMConfig
    embedder_config: EmbedderConfig
    data_path: str

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: Optional[str] = None):
        # Directly assign values without underscore
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path if data_path else 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'

        logger.info("Initializing CSVSearchTool with the provided configurations")
        
        # Initialize the CSV search tool
        self.csv_search_tool = self._initialize_csv_search_tool()

    def _initialize_csv_search_tool(self) -> Optional[CSVSearchTool]:
        try:
            self.csv_search_tool = CSVSearchTool(
                csv=self.data_path,
                config={
                    "llm": self.llm_config,
                    "embedder": self.embedder_config,
                }
            )
            logger.info("CSVSearchTool initialized successfully.")
            self.csv_data = self._load_csv_data()
        except ValueError as e:
            logger.warning(f"Failed to initialize CSVSearchTool: {e}")
            self.csv_search_tool = None
        
        # Retry initialization if necessary
        if self.csv_search_tool is None:
            logger.info("Invalidating cache and attempting to reinitialize CSVSearchTool.")
            self._invalidate_cache()
            self.csv_search_tool = self._initialize_csv_search_tool()

        return self.csv_search_tool

    def _invalidate_cache(self):
        logger.info("Invalidating the cache via rm -rf db")
        try:
            os.system("rm -rf db")  # Caution: This will delete the db directory
        except Exception as e:
            logger.error(f"Error during cache invalidation: {str(e)}")

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """Load TEDx data from the CSV file."""
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
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise FileNotFoundError(f"File not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}", exc_info=True)
            raise Exception("Failed to load CSV data.")

    def _run(self, search_query: Union[str, Dict[str, Any]], **kwargs: Any) -> str:
        """Executes the search on the TEDx dataset based on the search query."""
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
