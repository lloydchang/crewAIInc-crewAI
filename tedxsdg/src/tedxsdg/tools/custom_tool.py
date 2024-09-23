#!/usr/bin/env python

# tools/custom_tool.py

import logging
import re
from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Type, Optional
from crewai_tools import YoutubeChannelSearchTool as CrewAIYoutubeChannelSearchTool

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Helper functions
def is_valid_YouTube_url(url: str) -> bool:
    """
    Validates if the given URL is a valid YouTube URL using a regex pattern.
    """
    YouTube_regex = re.compile(r'(https?://)?(www\.)?(YouTube|youtu|YouTube-nocookie)\.(com|be)/.+')
    return bool(YouTube_regex.match(url))

def extract_query_string(query_input: Any) -> str:
    """
    Extracts a query string from different input types such as string, dict, or other objects.
    """
    if query_input is None or str(query_input).lower() in ['none', 'null', '']:
        return ""
    if isinstance(query_input, str):
        return query_input.strip()
    if isinstance(query_input, dict):
        return query_input.get('search_query', query_input.get('query', query_input.get('q', '')).strip())
    return str(query_input).strip()

def prepare_YouTube_search_input(input_data: Union[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Prepares the input for the YouTube search tool by extracting the search query.
    """
    logger.debug("Preparing YouTube search input.")
    if isinstance(input_data, str):
        search_query = input_data.strip()
        if not search_query:
            logger.error("Input string is empty.")
            raise ValueError("Input string is empty.")
        logger.debug(f"Extracted search_query from string: {search_query}")
        return {"search_query": search_query}
    
    elif isinstance(input_data, dict):
        search_query = input_data.get('search_query')
        if isinstance(search_query, str):
            search_query = search_query.strip()
            if search_query:
                logger.debug(f"Extracted search_query from dict: {search_query}")
                return {"search_query": search_query}
        
        # Extract first string found in the dictionary if no 'search_query' key is found
        for key, value in input_data.items():
            if isinstance(value, str):
                search_query = value.strip()
                if search_query:
                    logger.debug(f"Extracted search_query from key '{key}': {search_query}")
                    return {"search_query": search_query}
        
        logger.error("Dictionary input does not contain a valid 'search_query' string.")
        raise ValueError("Dictionary input does not contain a valid 'search_query' string.")
    
    else:
        logger.error("Invalid input type received. Expected string or dictionary.")
        raise ValueError("Input must be a string or a dictionary containing 'search_query'.")

# Input schemas
class DuckDuckGoSearchInput(BaseModel):
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo. Can be a string or a dictionary with a 'q' key.")

class YouTubeSearchToolSchema(BaseModel):
    search_query: Union[str, Dict[str, Any]] = Field(..., description="Search query for YouTube channel content.")
    YouTube_channel_handle: Optional[str] = Field(None, description="Optional YouTube channel handle")

class SDGAlignmentInput(BaseModel):
    idea: Union[str, Dict[str, Any]] = Field(..., description="Idea to analyze for SDG alignment")
    sdgs: List[Union[str, int]] = Field(default_factory=list, description="List of SDGs to consider")

class SustainabilityImpactInput(BaseModel):
    project: Union[str, Dict[str, Any]] = Field(default="Unnamed Project", description="Project to assess for sustainability impact")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics")

# Tool classes
class DuckDuckGoSearchTool(StructuredTool):
    name = "duckduckgo_search"
    description = "Searches the web using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: Union[str, Dict[str, Any]]) -> str:
        query_str = extract_query_string(query)
        logger.info(f"DuckDuckGoSearchTool._run called with query: {query_str}")
        if not query_str:
            return "Error: No valid search query provided."
        search_api = DuckDuckGoSearchAPIWrapper()
        try:
            result = search_api.run(query_str)
            logger.info(f"DuckDuckGo search completed successfully for query: {query_str}")
            return f"Final Answer: DuckDuckGo Search Results for '{query_str}':\n{result}"
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}", exc_info=True)
            return f"Error during DuckDuckGo search: {str(e)}"

class CustomYouTubeSearchTool(StructuredTool):
    name: str = "YouTube_search"
    description: str = "Searches YouTube channel content"
    args_schema: Type[BaseModel] = YouTubeSearchToolSchema
    config: Dict[str, Any] = Field(default_factory=dict)
    crewai_tool: Optional[CrewAIYoutubeChannelSearchTool] = None
    YouTube_channel_handle: Optional[str] = Field(default=None)  # Add this field

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        YouTube_channel_handle: Optional[str] = None  # Add this parameter
    ):
        super().__init__()
        self.config = config or {}
        self.YouTube_channel_handle = YouTube_channel_handle or '@TEDx'  # Default to @TEDx if no handle is provided

        # Initialize CrewAIYoutubeChannelSearchTool with the channel handle
        self.crewai_tool = CrewAIYoutubeChannelSearchTool(YouTube_channel_handle=self.YouTube_channel_handle, config=self.config)
        logger.debug(f"CustomYouTubeSearchTool initialized with channel handle: {self.YouTube_channel_handle}")

    def _run(self, search_query: Union[str, Dict[str, Any]], **kwargs: Any) -> str:
        logger.debug(f"_run called with search_query: {search_query}, kwargs: {kwargs}")

        # Ensure the YouTube channel handle from initialization is used if not explicitly provided
        channel_handle = kwargs.get('YouTube_channel_handle', self.YouTube_channel_handle)

        if channel_handle is None:
            logger.error("No valid YouTube channel handle provided.")
            return "Error: No valid YouTube channel handle provided."

        try:
            formatted_input = prepare_YouTube_search_input(search_query)
            query_str = formatted_input["search_query"]
            logger.info(f"CustomYouTubeSearchTool._run called with query_str: {query_str}")
        except ValueError as ve:
            logger.error(f"Input preparation error: {str(ve)}")
            return f"Error: {str(ve)}"

        if not query_str:
            logger.error("Error: No valid search query provided.")
            return "Error: No valid search query provided."

        # Perform the query within the YouTube channel
        try:
            result = self.crewai_tool.run(query_str)
            logger.info("YouTube channel search completed successfully")
            return f"Final Answer: YouTube Channel Search Results for '{query_str}' in channel '{channel_handle}':\n{result}"

        except Exception as e:
            logger.error(f"Error during YouTube channel search: {str(e)}", exc_info=True)
            return f"Error during YouTube channel search: {str(e)}"

class SDGAlignmentTool(StructuredTool):
    name = "sdg_alignment"
    description = "Analyzes ideas and aligns them with UN SDGs"
    args_schema: Type[BaseModel] = SDGAlignmentInput

    def _run(self, idea: Union[str, Dict[str, Any]], sdgs: List[Union[str, int]] = []) -> str:
        idea_str = extract_query_string(idea)
        logger.info(f"SDGAlignmentTool._run called with idea: {idea_str}, sdgs: {sdgs}")
        if not idea_str:
            return "Error: No valid idea provided for SDG alignment analysis."
        
        sdgs = [str(extract_query_string(sdg)) for sdg in sdgs if extract_query_string(sdg)]
        if not sdgs:
            sdgs = ["All SDGs"]
        
        logger.info(f"Performing SDG alignment analysis for idea: {idea_str}")
        return f"Final Answer: SDG Alignment analysis for idea: '{idea_str}', considering SDGs: {', '.join(sdgs)}"

class SustainabilityImpactAssessorTool(StructuredTool):
    name = "sustainability_impact_assessor"
    description = "Assesses the potential sustainability impact of ideas and projects"
    args_schema: Type[BaseModel] = SustainabilityImpactInput

    def _run(self, project: Union[str, Dict[str, Any]], metrics: List[str]) -> str:
        project_str = extract_query_string(project)
        logger.info(f"SustainabilityImpactAssessorTool._run called with project: {project_str}, metrics: {metrics}")
        if not project_str:
            return "Error: No valid project provided for sustainability impact assessment."
        
        metrics = [extract_query_string(metric) for metric in metrics if extract_query_string(metric)]
        if not metrics:
            return "Error: No valid sustainability metrics provided for assessment."

        logger.info(f"Performing sustainability impact assessment for project: {project_str}")
        return f"Final Answer: Sustainability impact assessment for project: {project_str}, considering metrics: {', '.join(metrics)}"

# Factory function for creating tools
def create_custom_tool(tool_name: str, config: Dict = None, YouTube_channel_handle: Optional[str] = None) -> StructuredTool:
    logger.info(f"Creating custom tool: {tool_name}")

    tools = {
        "youtube_search": CustomYouTubeSearchTool,  # Ensure this matches the name being passed
        "duckduckgo_search": DuckDuckGoSearchTool,
        "sdg_alignment": SDGAlignmentTool,
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool,
    }

    tool_class = tools.get(tool_name)
    if tool_class is None:
        logger.warning(f"Tool '{tool_name}' not found. Using DuckDuckGoSearchTool as fallback.")
        tool = DuckDuckGoSearchTool()
    elif tool_class == CustomYouTubeSearchTool:
        tool = CustomYouTubeSearchTool(config=config, YouTube_channel_handle=YouTube_channel_handle)
    else:
        tool = tool_class()

    logger.info(f"Created tool: {tool.name}")
    return tool
