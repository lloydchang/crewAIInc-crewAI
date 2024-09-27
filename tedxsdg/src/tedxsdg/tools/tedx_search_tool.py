# tools/tedx_search_tool.py

"""
Module for TEDxSearchTool which searches TEDx content using CrewAI's CSVSearchTool with custom configurations.
"""

import logging
import os
import yaml
import requests
from typing import Dict
from pydantic import BaseModel, Field
from tools.utils import extract_query_string
from crewai_tools import CSVSearchTool  # CrewAI's CSV Search Tool

logger = logging.getLogger(__name__)

# Local CSV file location and remote URL for fallback download
LOCAL_CSV_FILE = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'


def load_tool_config(tool_name: str, config_file: str = 'config/tools.yaml') -> dict:
    """Load the configuration for a specific tool from the YAML file."""
    with open(config_file, 'r') as file:
        tools_config = yaml.safe_load(file)
    return tools_config.get(tool_name, {})


class TEDxSearchToolArgs(BaseModel):
    """Arguments for TEDxSearchTool."""
    search_query: str = Field(default=None, description="The search query for TEDx talks")


class TEDxSearchTool(BaseModel):
    """Tool for searching TEDx content using CrewAI's CSVSearchTool with custom configuration."""
    
    _name: str = "tedx_search"
    _description: str = "Searches TEDx content using CrewAI's CSVSearchTool with custom configuration."
    _args_schema = TEDxSearchToolArgs  # Define the argument schema

    data_path: str = Field(default=LOCAL_CSV_FILE, description="Path to the TEDx dataset CSV")

    # CrewAI CSVSearchTool instance
    csv_search_tool: CSVSearchTool = None

    def __init__(self, **data):
        super().__init__(**data)
        
        # Load configurations from tools.yaml
        config = load_tool_config(self._name)

        # Set data path based on configuration or default to local CSV path
        self.data_path = config.get('data_path', LOCAL_CSV_FILE)

        # Ensure the CSV file is downloaded
        self.download_csv_if_not_exists()

        # Configure and initialize the CSVSearchTool with dynamic LLM and embedder configurations
        llm_config = config.get("llm_config", {})
        embedder_config = config.get("embedder_config", {})

        self.csv_search_tool = CSVSearchTool(
            csv=self.data_path,
            config=dict(
                llm=llm_config,
                embedder=embedder_config,
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
        Executes the semantic search on the TEDx dataset using CrewAI's CSVSearchTool with the custom configuration.

        Args:
            input (dict): The input dictionary containing the search query.

        Returns:
            str: Formatted search results.
        """
        # Extract the search query from the input
        search_query = extract_query_string(input)
        logger.debug("Running TEDx search for query: %s", search_query)

        # Perform the semantic search using CrewAI's CSVSearchTool
        try:
            results = self.csv_search_tool._run(search_query=search_query)
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
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
