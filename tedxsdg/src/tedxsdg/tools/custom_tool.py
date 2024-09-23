#!/usr/bin/env python

# tools/custom_tool.py

import logging
import re
from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Type, Optional
from crewai_tools import CSVSearchTool

# Set up logging with DEBUG level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    name = "duckduckgo_search"
    description = "Searches the web using DuckDuckGo."
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

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
    name: str = "tedx_search"
    description: str = "Searches TEDx content from CSV dataset."
    args_schema: Type[BaseModel] = TEDxSearchToolSchema
    csv_file: str = "https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv"
    csv_search_tool: Optional[CSVSearchTool] = None  # Declare csv_search_tool as an optional attribute

    def __init__(self, csv_file: Optional[str] = None):
        super().__init__()
        self.csv_file = csv_file or self.csv_file

        # Initialize CSVSearchTool with the provided CSV file
        try:
            self.csv_search_tool = CSVSearchTool(csv=self.csv_file)  # Set the csv_search_tool attribute
            logger.debug(f"TEDxSearchTool initialized with CSV file: {self.csv_file}")
        except Exception as e:
            logger.error(f"Failed to initialize CSVSearchTool: {str(e)}")
            self.csv_search_tool = None  # Ensure csv_search_tool is None in case of failure

    def _run(self, search_query: Union[str, Dict[str, Any]], **kwargs: Any) -> str:
        if not self.csv_search_tool:
            return "Error: CSV search tool not properly initialized."

        # Extract and prepare the search query
        try:
            query_str = extract_query_string(search_query)
            if not query_str:
                raise ValueError("No valid search query found.")

            # Perform the search in the CSV
            logger.debug(f"Running CSV search for query: {query_str}")
            search_result = self.csv_search_tool._run(search_query=query_str)
            return f"Final Answer: Search Results for '{query_str}' in CSV dataset:\n{search_result}"
    
        except ValueError as ve:
            logger.error(f"Value error: {str(ve)}")
            return f"Error: {str(ve)}"
        except Exception as e:
            logger.error(f"Error during CSV search: {str(e)}", exc_info=True)
            return f"Error during CSV search: {str(e)}"

class SDGAlignmentTool(StructuredTool):
    name = "sdg_alignment"
    description = "Analyzes ideas and aligns them with UN SDGs."
    args_schema: Type[BaseModel] = SDGAlignmentInput

    def _run(self, idea: Union[str, Dict[str, Any]], sdgs: List[Union[str, int]] = []) -> str:
        idea_str = extract_query_string(idea)
        if not idea_str:
            return "Error: No valid idea provided for SDG alignment analysis."
        sdgs = [str(extract_query_string(sdg)) for sdg in sdgs if extract_query_string(sdg)]
        logger.debug(f"Running SDG alignment for idea: '{idea_str}' with SDGs: {', '.join(sdgs) if sdgs else 'All SDGs'}")
        return f"Final Answer: SDG Alignment analysis for idea: '{idea_str}', considering SDGs: {', '.join(sdgs) or 'All SDGs'}."

class SustainabilityImpactAssessorTool(StructuredTool):
    name = "sustainability_impact_assessor"
    description = "Assesses the potential sustainability impact of ideas and projects."
    args_schema: Type[BaseModel] = SustainabilityImpactInput

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
    tools = {
        "tedx_search": TEDxSearchTool,
        "duckduckgo_search": DuckDuckGoSearchTool,
        "sdg_alignment": SDGAlignmentTool,
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool,
    }
    tool_class = tools.get(tool_name)
    if tool_class is None:
        logger.warning(f"Tool '{tool_name}' not found. Using DuckDuckGoSearchTool as fallback.")
        return DuckDuckGoSearchTool()
    return tool_class()
