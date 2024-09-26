# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content from a local CSV dataset.
"""

import os
import logging
import csv
import shutil
from typing import Any, Dict
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(
        ..., description="The search query for TEDx talks"
    )


class TEDxSearchTool(StructuredTool):
    """Tool for searching TEDx content from a local CSV dataset."""
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."
    args_schema: type[BaseModel] = TEDxSearchToolArgs

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.data_path = config.get('data_path')
        if not self.data_path:
            raise ValueError("data_path must be provided in the configuration")
        logger.info("Initializing TEDxSearchTool.")
        self.csv_data = self._load_csv_data()

    def _invalidate_cache(self):
        """Invalidates the cache by removing the 'db' directory or file."""
        logger.info("Invalidating the cache.")
        try:
            db_path = "db"
            if os.path.exists(db_path):
                if os.path.isfile(db_path):
                    os.remove(db_path)
                    logger.debug("Removed file: %s", db_path)
                elif os.path.isdir(db_path):
                    shutil.rmtree(db_path)
                    logger.debug("Removed directory: %s", db_path)
                logger.info("Cache invalidation completed successfully.")
            else:
                logger.info("No cache to invalidate. 'db' does not exist.")
        except Exception as e:
            logger.error(
                "Error during cache invalidation: %s", e, exc_info=True
            )
            raise

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """Load TEDx data from the CSV file."""
        slug_index = {}
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug("Loaded %d slugs from CSV file.", len(slug_index))
        except FileNotFoundError as exc:
            logger.error("File not found: %s", self.data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {self.data_path}") from exc
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise Exception("Failed to load CSV data.") from e
        return slug_index

    def _run(self, search_query: str) -> str:
        """Executes the search on the TEDx dataset based on the search query."""
        logger.debug("Running TEDx search for query: %s", search_query)
        results = [
            data for key, data in self.csv_data.items()
            if search_query.lower() in key.lower()
        ]
        
        if not results:
            return "No results found."

        return f"Final Answer: TEDx Search Results:\n{results}"

    def _run(self, search_query: str) -> str:
        """Executes the search on the TEDx dataset based on the search query."""
        logger.debug("Running TEDx search for query: %s", search_query)
        results = [
            data for key, data in self.csv_data.items()
            if search_query.lower() in key.lower()
        ]
        
        if not results:
            return "No results found."

        return f"Final Answer: TEDx Search Results:\n{results}"
