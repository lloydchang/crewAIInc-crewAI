# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content from a local CSV dataset.
"""

import logging
import csv
from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator
from crewai_tools import CSVSearchTool

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

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Executes the search on the TEDx dataset based on the input.

        Args:
            input (dict): The input dictionary containing the search query.

        Returns:
            str: Formatted search results.
        """
        search_query = input.get('query', '')  # Extract 'query' from the input dictionary
        logger.debug("Running TEDx search for query: %s", search_query)
        if not self.data_path:
            raise ValueError("`data_path` must be provided in the configuration.")

        try:
            # Initialize the CSVSearchTool with configurations
            tool = CSVSearchTool(
                config=dict(
                    llm=dict(
                        provider="ollama",  # Example provider
                        config=dict(
                            model="ollama/llama3",
                            temperature=0.0
                        ),
                    ),
                    embedder=dict(
                        provider="ollama",  # Example provider
                        config=dict(
                            model="nomic-embed-text"
                        ),
                    ),
                ),
                csv=self.data_path
            )

            # Use the search method of CSVSearchTool, assuming it takes a 'csv' and a 'query' parameter
            results = tool.search(
                csv=self.csv_data,  # Assuming csv_data is compatible with the search method's expectations
                query=search_query.lower()
            )

            if not results:
                return "No results found."

            # Format results for better readability
            formatted_results = "\n\n".join([
                f"Title: {entry.get('title', 'No Title')}\nDescription: {entry.get('description', 'No Description')}\nURL: {entry.get('url', 'No URL')}"
                for entry in results
            ])

            logger.debug("Search results: %s", formatted_results)
            return f"Final Answer: TEDx Search Results:\n{formatted_results}"
        except FileNotFoundError as exc:
            logger.error("File not found: %s", self.data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {self.data_path}") from exc
        except Exception as e:
            logger.error("Error searching CSV data: %s", e, exc_info=True)
            raise Exception("Failed to search CSV data.") from e

        # Use the search method of CSVSearchTool, assuming it takes a 'csv' and a 'query' parameter
        results = tool.search(
            csv=self.csv_data,  # Assuming csv_data is compatible with the search method's expectations
            query=search_query.lower()
        )

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
