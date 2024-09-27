# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content from a local CSV dataset.
"""

import logging
import csv
import os
import requests
from typing import Any, Dict, Union
from pydantic import BaseModel, Field, validator
from tools.utils import extract_query_string  # Import the utility function
from crewai_tools import CSVSearchTool  # Assuming this is available in your environment

logger = logging.getLogger(__name__)

# Local CSV file location and remote URL for fallback download
LOCAL_CSV_FILE = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'

class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")


class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content from a local CSV dataset."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content from the local CSV dataset."
    _args_schema = TEDxSearchToolArgs  # Define the argument schema

    data_path: str = Field(default=LOCAL_CSV_FILE, description="Path to the TEDx dataset CSV")
    csv_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Loaded CSV data")

    # Download CSV file if it doesn't exist
    def download_csv_if_not_exists(self):
        if not os.path.exists(self.data_path):
            logger.info(f"Downloading CSV file from {REMOTE_CSV_URL}")
            response = requests.get(REMOTE_CSV_URL)
            if response.status_code == 200:
                with open(self.data_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"CSV file saved to {self.data_path}")
            else:
                logger.error(f"Failed to download CSV file. Status code: {response.status_code}")
                raise Exception("Failed to download CSV file")

    @validator('csv_data', pre=True, always=True)
    def load_csv_data(cls, v, values):
        """
        Validator to load the CSV data when the tool is initialized.
        """
        data_path = values.get('data_path')
        if not data_path:
            raise ValueError("`data_path` must be provided in the configuration.")
        logger.info("Loading TEDxSearchTool with data_path: %s", data_path)
        
        # Ensure the CSV file exists or is downloaded
        cls.download_csv_if_not_exists(cls)

        try:
            search_index = {}
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip().lower()
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
        # Use the utility function to extract the search query
        search_query = extract_query_string(input)
        logger.debug("Running TEDx search for query: %s", search_query)
        
        if not self.data_path:
            raise ValueError("`data_path` must be provided in the configuration.")

        try:
            # Ensure the CSV file exists or is downloaded
            self.download_csv_if_not_exists()

            # Initialize CSVSearchTool for TEDx search
            results = CSVSearchTool(csv=self.data_path,
                                    config=dict(
                                        llm=dict(
                                            provider="ollama",
                                            config=dict(
                                                model="llama3.2",
                                                temperature=0.0,
                                            ),
                                        ),
                                        embedder=dict(
                                            provider="ollama",
                                            config=dict(
                                                model="nomic-embed-text",
                                            ),
                                        ),
                                    )
                                )

            logger.debug("Search results: %s", results)
            return f"TEDx Search Results:\n{results}"
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

    @property
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
