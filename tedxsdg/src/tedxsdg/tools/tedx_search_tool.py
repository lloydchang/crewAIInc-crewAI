# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content using CrewAI's CSVSearchTool with custom configurations.
"""

import logging
import os
import requests
from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.utils import extract_query_string
from crewai_tools import CSVSearchTool  # CrewAI's CSV Search Tool

logger = logging.getLogger(__name__)

# Remote URL for fallback download
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'


class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")


class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content using CrewAI's CSVSearchTool with custom configuration."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content using CrewAI's CSVSearchTool with custom configuration."
    _args_schema = TEDxSearchToolArgs  # Define the argument schema

    def __init__(self, data_path: str, llm: Any = None, embedder: Any = None, **kwargs):
        super().__init__(**kwargs)

        # Ensure the CSV file is downloaded
        self.data_path = data_path
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
            logger.info(f"Downloading CSV file from {REMOTE_CSV_URL}")
            response = requests.get(REMOTE_CSV_URL)
            if response.status_code == 200:
                with open(self.data_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"CSV file saved to {self.data_path}")
            else:
                logger.error(f"Failed to download CSV file. Status code: {response.status_code}")
                raise Exception("Failed to download CSV file")

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
            results = self.csv_search_tool._run(search_query=search_query)
            return f"TEDx Search Results:\n{results}"
        except Exception as e:
            logger.error("Error searching CSV data: %s", e, exc_info=True)
            raise Exception("Failed to search CSV data.") from e
