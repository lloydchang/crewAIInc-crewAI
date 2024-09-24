#!/usr/bin/env python

# tools/custom_tool.py

import os
import logging
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Type
from crewai_tools import CSVSearchTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# Set up logging with DEBUG level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Local CSV file location
LOCAL_CSV_FILE = 'github-mauropelucchi-tedx_dataset-update_2024-details.csv'
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'

# Function to download the CSV file if it doesn't exist
def download_csv_if_not_exists():
    if not os.path.exists(LOCAL_CSV_FILE):
        logger.info(f"Downloading CSV file from {REMOTE_CSV_URL}")
        response = requests.get(REMOTE_CSV_URL)
        if response.status_code == 200:
            with open(LOCAL_CSV_FILE, 'wb') as f:
                f.write(response.content)
            logger.info(f"CSV file saved to {LOCAL_CSV_FILE}")
        else:
            logger.error(f"Failed to download CSV file. Status code: {response.status_code}")
            raise Exception("Failed to download CSV file")

# Ensure CSV file is downloaded and ready to use
download_csv_if_not_exists()

def extract_query_string(query_input: Union[str, Dict[str, Any]]) -> str:
    """Extracts a query string from input (string, dict, or other objects)."""
    try:
        if isinstance(query_input, str):
            return query_input.strip()
        elif isinstance(query_input, dict):
            return query_input.get('search_query', query_input.get('query', query_input.get('q', ''))).strip()
        return str(query_input).strip()
    except Exception as e:
        logger.error(f"Error extracting query string: {e}")
        return ""

# Input schemas
class DuckDuckGoSearchInput(BaseModel):
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo.")

class TEDxSearchToolSchema(BaseModel):
    search_query: Union[str, Dict[str, Any]] = Field(..., description="Search query for TEDx content.")

class SDGAlignmentInput(BaseModel):
    idea: Union[str, Dict[str, Any]] = Field(..., description="Idea to analyze for SDG alignment.")
    sdgs: List[Union[str, int]] = Field(default_factory=list, description="List of SDGs to consider.")

class SustainabilityImpactInput(BaseModel):
    project: Union[str, Dict[str, Any]] = Field(default="Unnamed Project", description="Project to assess for sustainability impact.")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics.")

# Tool classes
class DuckDuckGoSearchTool(StructuredTool):
    name: str = "duckduckgo_search"
    description: str = "Searches the web using DuckDuckGo."
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    llm_config: Dict[str, Any] = Field(default_factory=dict)
    embedder_config: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, config: Dict):
        super().__init__()
        self.llm_config = config.get("llm_config", {})
        self.embedder_config = config.get("embedder_config", {})
        if not self.llm_config or not self.embedder_config:
            raise ValueError("Missing llm_config or embedder_config")  # More specific error

    def _run(self, query: Union[str, Dict[str, Any]]) -> str:
        query_str = extract_query_string(query)
        if not query_str:
            return "Error: No valid search query provided."
        try:
            logger.debug(f"Running DuckDuckGo search for query: {query_str}")
            search_api = DuckDuckGoSearchAPIWrapper()
            result = search_api.run(query_str)
            return f"Final Answer: DuckDuckGo Search Results for '{query_str}':\n{result}"
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}", exc_info=True)
            return f"Error during DuckDuckGo search: {str(e)}"

class TEDxSearchTool(StructuredTool):
    csv_search_tool: CSVSearchTool = Field(default=None)
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."
    args_schema: Type[BaseModel] = TEDxSearchToolSchema

    llm_config: Dict[str, Any] = Field(default_factory=dict)
    embedder_config: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, config: Dict):
        super().__init__()
        self.llm_config = config.get("llm_config", {})
        self.embedder_config = config.get("embedder_config", {})
        if not self.llm_config or not self.embedder_config:
            raise ValueError("Missing llm_config or embedder_config")  # More specific error
        self.csv_search_tool = CSVSearchTool(
            csv=LOCAL_CSV_FILE,
            config=dict(
                llm=config.get("llm_config", {}),
                embedder=config.get("embedder_config", {}),
            )
        )

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

class SDGAlignmentTool(StructuredTool):
    name: str = "sdg_alignment"
    description: str = "Analyzes ideas and aligns them with UN SDGs."
    args_schema: Type[BaseModel] = SDGAlignmentInput

    llm_config: Dict[str, Any] = Field(default_factory=dict)
    embedder_config: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, config: Dict):
        super().__init__()
        self.llm_config = config.get("llm_config", {})
        self.embedder_config = config.get("embedder_config", {})

        if not self.llm_config or not self.embedder_config:
            raise ValueError("Missing llm_config or embedder_config")  # More specific error

    def _run(self, idea: Union[str, Dict[str, Any]], sdgs: List[Union[str, int]] = []) -> str:
        idea_str = extract_query_string(idea)
        if not idea_str:
            return "Error: No valid idea provided for SDG alignment analysis."
        sdgs = [str(extract_query_string(sdg)) for sdg in sdgs if extract_query_string(sdg)]
        logger.debug(f"Running SDG alignment for idea: '{idea_str}' with SDGs: {', '.join(sdgs) if sdgs else 'All SDGs'}")
        return f"Final Answer: SDG Alignment analysis for idea: '{idea_str}', considering SDGs: {', '.join(sdgs) or 'All SDGs'}."

class SustainabilityImpactAssessorTool(StructuredTool):
    name: str = "sustainability_impact_assessor"
    description: str = "Assesses the potential sustainability impact of ideas and projects."
    args_schema: Type[BaseModel] = SustainabilityImpactInput

    llm_config: Dict[str, Any] = Field(default_factory=dict)
    embedder_config: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, config: Dict):
        super().__init__()
        self.llm_config = config.get("llm_config", {})
        self.embedder_config = config.get("embedder_config", {})

        if not self.llm_config or not self.embedder_config:
            raise ValueError("Missing llm_config or embedder_config") # More specific error

    def _run(self, project: Union[str, Dict[str, Any]], metrics: List[str]) -> str:
        project_str = extract_query_string(project)
        if not project_str:
            return "Error: No valid project provided for sustainability impact assessment."
        metrics = [extract_query_string(metric) for metric in metrics if extract_query_string(metric)]
        if not metrics:
            return "Error: No valid sustainability metrics provided for assessment."
        logger.debug(f"Running sustainability impact assessment for project: '{project_str}' with metrics: {', '.join(metrics)}")
        return f"Final Answer: Sustainability impact assessment for project '{project_str}', considering metrics: {', '.join(metrics)}."

# Factory function for creating tools
def create_custom_tool(tool_name: str, config: Dict = None) -> StructuredTool:
    logger.info(f"Creating custom tool: {tool_name}")

    if config is None:
        config = {}

    tools = {
        "tedx_search": TEDxSearchTool(config=config),
        "duckduckgo_search": DuckDuckGoSearchTool(config=config), 
        "sdg_alignment": SDGAlignmentTool(config=config),
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool(config=config),
    }

    tool_class = tools.get(tool_name)
    if tool_class is None:
        logger.warning(f"Tool '{tool_name}' not found. Using DuckDuckGoSearchTool as fallback.")
        return DuckDuckGoSearchTool()

    return tool_class
