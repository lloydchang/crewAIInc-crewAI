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
from pydantic import BaseModel, Field, validator

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

    # Define 'data_path' as a Pydantic field
    data_path: str = Field(..., description="Path to the data directory")
    
    # Initialize 'csv_data' with a default empty dictionary
    csv_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    # Validator to load CSV data after initialization
    @validator('csv_data', pre=True, always=True)
    def load_csv_data(cls, v, values):
        data_path = values.get('data_path')
        if not data_path:
            raise ValueError("`data_path` must be provided in the configuration")
        logger.info("Initializing TEDxSearchTool with data_path: %s", data_path)
        try:
            slug_index = {}
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug("Loaded %d slugs from CSV file.", len(slug_index))
            return slug_index
        except FileNotFoundError as exc:
            logger.error("File not found: %s", data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {data_path}") from exc
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise Exception("Failed to load CSV data.") from e

    def run(self, search_query: str) -> str:
        """Executes the search on the TEDx dataset based on the search query."""
        logger.debug("Running TEDx search for query: %s", search_query)
        results = [
            data for key, data in self.csv_data.items()
            if search_query.lower() in key.lower()
        ]
        
        if not results:
            return "No results found."

        return f"Final Answer: TEDx Search Results:\n{results}"

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
