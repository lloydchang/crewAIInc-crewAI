# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content using CrewAI's CSVSearchTool with custom configurations.
"""

import logging
import os
import requests
from typing import Dict, Any  # <-- Added the missing Any import
from pydantic import BaseModel, Field
from tools.utils import extract_query_string
from crewai_tools import CSVSearchTool  # CrewAI's CSV Search Tool

logger = logging.getLogger(__name__)

# Local CSV file location and remote URL for fallback download
LOCAL_CSV_FILE = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'


class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")


class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content using CrewAI's CSVSearchTool with custom configuration."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content using CrewAI's CSVSearchTool with custom configuration."
    _args_schema = TEDxSearchToolArgs  # Define the argument schema

    def __init__(self, data_path: str = LOCAL_CSV_FILE, llm: Any = None, embedder: Any = None, **kwargs):
        super().__init__(**kwargs)

        # Ensure the CSV file is downloaded or use the cache location
        self.data_path = data_path or LOCAL_CSV_FILE
        self.download_csv_if_not_exists()

        # Configure and initialize the CSVSearchTool with a custom LLM and embedder configuration
        self.csv_search_tool = CSVSearchTool(
            csv=self.data_path,
            config=dict(
                llm=llm,
                embedder=embedder,
            )
        )

    def download_csv_if_not_exists(self):
        """Ensure that the CSV file exists locally, or download it."""
        if not os.path.exists(self.data_path):
            # If the file is not present in the cache, download it
            logger.info(f"Local file not found. Downloading CSV file from {REMOTE_CSV_URL} to cache: {self.data_path}")
            self._download_and_cache_csv()
        else:
            logger.info(f"Using cached CSV file at {self.data_path}")

    def _download_and_cache_csv(self):
        """Helper method to download the CSV file and cache it locally."""
        try:
            response = requests.get(REMOTE_CSV_URL)
            if response.status_code == 200:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

                # Write the content to the local cache file
                with open(self.data_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"CSV file successfully downloaded and cached at {self.data_path}")
            else:
                logger.error(f"Failed to download CSV file. Status code: {response.status_code}")
                raise Exception(f"Failed to download CSV file. HTTP Status: {response.status_code}")
        except Exception as e:
            logger.error("Error downloading CSV file: %s", e)
            raise Exception("Failed to download and cache CSV file.") from e

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Executes the semantic search on the TEDx dataset using CrewAI's CSVSearchTool.

        Args:
            input (dict): The input dictionary containing the search query.

        Returns:
            str: Formatted search results.
        """
        # Extract the search query from the input
        search_query = extract_query_string(input)
        logger.debug("Running TEDx search for query: %s", search_query)

        try:
            # Run the CSV search with the configured tool
            results = self.csv_search_tool._run(search_query=search_query)
            return f"TEDx Search Results:\n{results}"
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
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
