# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content from a local CSV dataset using a RAG approach.
"""

import logging
import csv
from typing import Any, Dict
from pydantic import BaseModel, Field, validator
from crewai_tools import CSVSearchTool

# Setup basic logging configuration
logger = logging.getLogger(__name__)

class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")

class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content from a local CSV dataset using a RAG approach."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content from the local CSV dataset using a RAG approach."
    _args_schema = TEDxSearchToolArgs

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
        Executes the RAG search on the TEDx dataset based on the input.

        Args:
            input (dict): The input dictionary containing the search query.

        Returns:
            str: Formatted search results.
        """
        search_query = input.get('query', '')
        logger.debug("Running TEDx RAG search for query: %s", search_query)

        if not self.data_path:
            raise ValueError("`data_path` must be provided in the configuration.")

        try:
            # Initialize the CSVSearchTool with or without a specific CSV file
            tool = CSVSearchTool(csv=self.csv_data,
                                    config=dict(
                                        llm=dict(
                                            provider="ollama", # or google, openai, anthropic, llama2, ...
                                            config=dict(
                                                model="llama3.2",
                                                temperature=0.0,
                                                # top_p=1,
                                                # stream=true,
                                            ),
                                        ),
                                        embedder=dict(
                                            provider="ollama", # or openai, ollama, ...
                                            config=dict(
                                                model="nomic-embed-text",
#                                                task_type="retrieval_document",
                                                # title="Embeddings",
                                            ),
                                        ),
                                    )
                                )

            # Use the RAG search method of CSVSearchTool
            results = tool.search(
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
            return f"TEDx Search Results:\n{formatted_results}"
        except FileNotFoundError as exc:
            logger.error("File not found: %s", self.data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {self.data_path}") from exc
        except Exception as e:
            logger.error("Error searching CSV data: %s", e, exc_info=True)
            raise Exception("Failed to search CSV data.") from e

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
