# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content from a local CSV dataset.
"""

import logging
import csv
from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")


class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content from a local CSV dataset."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content from the local CSV dataset."
    _args_schema = TEDxSearchToolArgs  # Define the argument schema

    data_path: str = Field(default=None, description="Path to the TEDx dataset CSV")
    csv_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Loaded CSV data")

    @validator('csv_data', pre=True, always=True)
    def load_csv_data(cls, v, values):
        data_path = values.get('data_path')
        if not data_path:
            raise ValueError("`data_path` must be provided in the configuration.")
        logger.info("Loading TEDxSearchTool with data_path: %s", data_path)
        try:
            search_index = {}
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip().lower()
                    title = row.get('title', '').strip().lower()
                    description = row.get('description', '').strip().lower()
                    if slug:
                        search_index[slug] = row
            logger.debug("Loaded %d entries from CSV file.", len(search_index))
            return search_index
        except FileNotFoundError as exc:
            logger.error("File not found: %s", data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {data_path}") from exc
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise Exception("Failed to load CSV data.") from e

    def run(self, search_query: str) -> str:
        """
        Executes the search on the TEDx dataset based on the search query.

        Args:
            search_query (str): The search query string.

        Returns:
            str: Formatted search results.
        """
        logger.debug("Running TEDx search for query: %s", search_query)
        search_query_lower = search_query.lower()
        results: List[Dict[str, Any]] = []

        for entry in self.csv_data.values():
            if (search_query_lower in entry.get('title', '').lower()) or \
               (search_query_lower in entry.get('description', '').lower()):
                results.append(entry)
                if len(results) >= 3:  # Limit to top 3 results
                    break

        if not results:
            return "No results found."

        # Format results for better readability
        formatted_results = "\n\n".join([
            f"Title: {entry.get('title', 'No Title')}\nDescription: {entry.get('description', 'No Description')}\nURL: {entry.get('url', 'No URL')}"
            for entry in results
        ])

        logger.debug("Search results: %s", formatted_results)
        return f"Final Answer: TEDx Search Results:\n{formatted_results}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    @property
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
