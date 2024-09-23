#!/usr/bin/env python

# tools/custom_tool.py

import logging
import re
from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Type, Optional
from embedchain import App as EmbedChainApp
from embedchain.config import AppConfig
import litellm

litellm.set_verbose = True

use_rag = True

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper functions
def is_valid_youtube_url(url: str) -> bool:
    """
    Validates if the given URL is a valid YouTube URL using a regex pattern.
    """
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    return bool(youtube_regex.match(url))

def extract_query_string(query_input: Any) -> str:
    """
    Extracts a query string from different input types such as string, dict, or other objects.
    """
    if query_input is None or str(query_input).lower() in ['none', 'null', '']:
        return ""
    if isinstance(query_input, str):
        return query_input.strip()
    if isinstance(query_input, dict):
        return query_input.get('q', '').strip()
    return str(query_input).strip()

# Input schemas
class DuckDuckGoSearchInput(BaseModel):
    """
    Input schema for DuckDuckGoSearchTool.
    """
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo. Can be a string or a dictionary with a 'q' key.")

class YoutubeVideoSearchToolSchema(BaseModel):
    """
    Input schema for CustomYoutubeVideoSearchTool.
    """
    search_query: Union[str, Dict[str, Any]] = Field(..., description="Search query for YouTube content.")
    youtube_video_url: Optional[str] = Field(None, description="Optional YouTube video URL")

class SDGAlignmentInput(BaseModel):
    """
    Input schema for SDGAlignmentTool.
    """
    idea: Union[str, Dict[str, Any]] = Field(..., description="Idea to analyze for SDG alignment")
    sdgs: List[Union[str, int]] = Field(default_factory=list, description="List of SDGs to consider")

class SustainabilityImpactInput(BaseModel):
    """
    Input schema for SustainabilityImpactAssessorTool.
    """
    project: Union[str, Dict[str, Any]] = Field(default="Unnamed Project", description="Project to assess for sustainability impact")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics")


class CustomLlm:
    """
    A custom LLM class that wraps litellm and uses dynamic configuration passed from crew.py.
    """
    def __init__(self, config):
        self.config = config  # Accept the configuration passed from crew.py

    def generate(self, prompt: str) -> str:
        """
        Generates a response using litellm with dynamic configuration.
        """
        response = litellm.completion(
            model=self.config.get('model'),
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.get('temperature'),
            api_base=self.config.get('api_base', 'http://localhost:11434'),  # Default to localhost:11434
        )
        return response

# Tool classes
class DuckDuckGoSearchTool(StructuredTool):
    """
    A tool that uses DuckDuckGo to search the web.
    """
    name = "duckduckgo_search"
    description = "Searches the web using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: Union[str, Dict[str, Any]]) -> str:
        """
        Runs a DuckDuckGo search and returns the results.
        """
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

class CustomYoutubeVideoSearchTool(StructuredTool):
    """
    A custom YouTube video search tool that performs semantic searches on YouTube videos using embedchain.
    """
    name: str = "youtube_search"
    description: str = "Searches YouTube videos for specific content using RAG techniques"
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolSchema
    embedchain_app: Any = None
    config: Dict[str, Any] = Field(default_factory=dict)
    llm: Any = None
    embedding_fn: Any = None

    def __init__(self, youtube_video_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None, use_rag: bool = False):
        super().__init__()
        self.config = config or {}

        # Initialize custom LLM and embedder based on config to avoid OpenAI API usage
        llm_provider = self.config.get('llm', {}).get('provider')
        llm_provider_config = self.config.get('llm', {}).get('config', {})

        embedder_provider = self.config.get('embedder', {}).get('provider')
        embedder_provider_config = self.config.get('embedder', {}).get('config', {})

        self.llm = CustomLlm(config=llm_provider_config)  # Pass config as a single argument

        if use_rag:
            # Initialize embedchain with custom LLM and embedding function
            app_config = AppConfig(collect_metrics=False)
            self.embedchain_app = EmbedChainApp(config=app_config)
            self.embedchain_app.embedding_fn = self.embedding_fn
            self.embedchain_app.llm = self.llm

            if youtube_video_url and youtube_video_url.lower() != "none":
                self.embedchain_app.add("youtube_video", youtube_video_url)
                self.description = f"A tool that can be used to semantic search a query in the {youtube_video_url} YouTube video content."

    def _run(self, search_query: Union[str, Dict[str, Any]], youtube_video_url: Optional[str] = None, **kwargs: Any) -> str:
        query_str = extract_query_string(search_query)
        logger.info(f"CustomYoutubeVideoSearchTool._run called with search_query: {query_str}, youtube_video_url: {youtube_video_url}")

        if not query_str:
            return "Error: No valid search query provided."

        if youtube_video_url and youtube_video_url.lower() == "none":
            youtube_video_url = None

        try:
            # Only perform RAG if the flag is set
            if youtube_video_url:
                if not is_valid_youtube_url(youtube_video_url):
                    logger.warning(f"Invalid YouTube URL provided: {youtube_video_url}")
                    return f"Error: Invalid YouTube URL provided: {youtube_video_url}"
                logger.info(f"Adding YouTube video URL: {youtube_video_url}")
                if self.embedchain_app:
                    self.embedchain_app.add("youtube_video", youtube_video_url)
            else:
                logger.info("No valid YouTube video URL provided, proceeding with general search.")

            if self.embedchain_app:
                result = self.embedchain_app.query(query_str)
                logger.info("YouTube search completed successfully")
                return f"Final Answer: YouTube Search Results for '{query_str}':\n{result}"
            else:
                return "RAG service disabled."

        except Exception as e:
            logger.error(f"Error during YouTube video search: {str(e)}", exc_info=True)
            return f"Error during YouTube video search: {str(e)}"

class SDGAlignmentTool(StructuredTool):
    """
    A tool that analyzes ideas and aligns them with the United Nations Sustainable Development Goals (SDGs).
    """
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
    """
    A tool that assesses the potential sustainability impact of ideas and projects based on certain metrics.
    """
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

def create_custom_tool(tool_name: str, config: Dict = None, use_rag: bool = False) -> StructuredTool:
    logger.info(f"Creating custom tool: {tool_name}")
    tools = {
        "youtube_search": CustomYoutubeVideoSearchTool,
        "duckduckgo_search": DuckDuckGoSearchTool,
        "sdg_alignment": SDGAlignmentTool,
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool,
    }
    tool_class = tools.get(tool_name)
    if tool_class is None:
        logger.warning(f"Tool '{tool_name}' not found. Using DuckDuckGoSearchTool as fallback.")
        tool = DuckDuckGoSearchTool()
    elif tool_class == CustomYoutubeVideoSearchTool:
        tool = CustomYoutubeVideoSearchTool(config=config, use_rag=use_rag)
    else:
        tool = tool_class()
    logger.info(f"Created tool: {tool.name}")
    return tool
