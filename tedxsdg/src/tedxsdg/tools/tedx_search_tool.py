# tools/tedx_search_tool.py

import os
import logging
import sys
import csv
from typing import Union, Dict, Any, Type, Optional
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from schemas.tedx_search_schema import TEDxSearchInput
from schemas.config_schemas import LLMConfig, EmbedderConfig
from crewai_tools import CSVSearchTool
from .utils import extract_query_string

logger = logging.getLogger(__name__)

# logging.getLogger().setLevel(logging.INFO)

logger.debug("Debug logging is working at the top of the script.")

# Local CSV file location is now managed via data_path

class TEDxSearchTool(StructuredTool):
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."
    args_schema: Type[BaseModel] = TEDxSearchInput

    llm_config: LLMConfig = Field(exclude=True)
    embedder_config: EmbedderConfig = Field(exclude=True)
    data_path: str = Field(default='data/github-mauropelucchi-tedx_dataset-update_2024-details.csv', description="Path to the TEDx dataset CSV.")

    def _invalidate_cache(self):
        # Invalidate the cache
        logger.info(f"Invalidating the cache via rm -rf db")
        os.system("rm -rf db")

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: str = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'):
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path

        # Force the creation of embeddings by invalidating the cache
        #
        # Uncomment to invalidate the cache
        self._invalidate_cache()

        print(f"Initialize CSVSearchTool with the provided configurations")
        self.csv_search_tool = CSVSearchTool(
            csv=self.data_path,
            config={
                "llm": self.llm_config,
                "embedder": self.embedder_config,
            }
        )

        # Load the entire CSV data into memory for quick lookup
        self.csv_data = self._load_csv_data()

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """Loads the CSV data into a dictionary keyed by slug."""
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
        """Finds a row in the CSV data by slug using the slug index."""
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
