#!/usr/bin/env python

# tools/custom_tool.py

from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from crewai_tools import YoutubeVideoSearchTool as YoutubeSearchToolAPI
from pydantic import BaseModel, Field
from typing import List, Union
import json  # Added to handle JSON-related issues

# Sanitizing input for tools
def sanitize_tool_input(input_data):
    if isinstance(input_data, dict):
        return str(input_data.get('tool_input', input_data))
    return str(input_data)

# DuckDuckGo Search Tool Input Schema
class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query for DuckDuckGo")

# DuckDuckGo Web Search Tool
class DuckDuckGoSearchTool(StructuredTool):
    name = "web_search"
    description = "Searches the web using DuckDuckGo"
    args_schema = WebSearchInput

    def _run(self, query: str) -> str:
        # Use DuckDuckGo API to search the web and return the results
        search_api = DuckDuckGoSearchAPIWrapper()
        result = search_api.run(query)
        return f"DuckDuckGo Search Results for '{query}':\n{result}"

# YouTube Video Search Tool Input Schema
class YoutubeSearchInput(BaseModel):
    query: str = Field(..., description="Search query for YouTube content")
    youtube_video_url: str = Field(None, description="Optional YouTube video URL to target specific video")

# YouTube Video Search Tool
class YoutubeVideoSearchTool(StructuredTool):
    name = "youtube_search"
    description = "Searches YouTube videos for specific content"
    args_schema = YoutubeSearchInput

    def _run(self, query: str, youtube_video_url: str = None) -> str:
        # Initialize the YouTube video search tool
        if youtube_video_url:
            tool = YoutubeSearchToolAPI(youtube_video_url=youtube_video_url)
        else:
            tool = YoutubeSearchToolAPI()
        
        # Perform the search
        result = tool.run(query)
        return f"YouTube Search Results for '{query}' (Video URL: {youtube_video_url}):\n{result}"

# SDG Alignment Tool Input Schema with String or Dictionary Input
class SDGAlignmentInput(BaseModel):
    idea: Union[str, dict] = Field(
        ..., 
        description="The idea to analyze for SDG alignment. Can be either a string or a dictionary with fields like 'title' and 'description'."
    )
    sdgs: List[str] = Field(default_factory=list, description="List of SDGs to consider")

# SDG Alignment Tool
class SDGAlignmentTool(StructuredTool):
    name = "sdg_alignment"
    description = "Analyzes ideas and aligns them with UN Sustainable Development Goals (SDGs)"
    args_schema = SDGAlignmentInput

    def _run(self, idea: Union[str, dict], sdgs: List[str]) -> str:
        if isinstance(idea, dict):
            # If the idea is a dictionary, extract the title and description
            title = idea.get('title', 'Untitled')
            description = idea.get('description', 'No description provided')
            idea_str = f"Title: {title}, Description: {description}"
        else:
            # If the idea is a string, use it directly
            idea_str = idea

        # Simulate SDG alignment analysis
        return f"SDG Alignment analysis for idea: '{idea_str}', considering SDGs: {', '.join(sdgs)}"

# Sustainability Impact Tool Input Schema
class SustainabilityImpactInput(BaseModel):
    project: str = Field(default="Unnamed Project", description="The project to assess for sustainability impact")  # Default project name
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics to consider")

# Sustainability Impact Assessor Tool
class SustainabilityImpactAssessorTool(StructuredTool):
    name = "sustainability_impact_assessor"
    description = "Assesses the potential sustainability impact of ideas and projects"
    args_schema = SustainabilityImpactInput

    def _run(self, project: str, metrics: List[str]) -> str:
        # Simulate sustainability impact assessment
        return f"Sustainability impact assessment for project: {project}, considering metrics: {', '.join(metrics)}"

# Tool creation factory to return the appropriate tool based on the name
def create_custom_tool(tool_name: str) -> StructuredTool:
    tools = {
        "web_search": DuckDuckGoSearchTool(),
        "youtube_search": YoutubeVideoSearchTool(),
        "sdg_alignment": SDGAlignmentTool(),
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool(),
    }
    return tools.get(tool_name, None)
