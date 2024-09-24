# tools/tool_registry.py

import logging
from typing import Dict
from langchain.tools import StructuredTool
from .duckduckgo_search_tool import DuckDuckGoSearchTool
from .tedx_search_tool import TEDxSearchTool
from .tedx_slug_tool import TEDxSlugTool
from .tedx_transcript_tool import TEDxTranscriptTool
from .sdg_align_tool import SDGAlignTool
from .sustainability_impact_tool import SustainabilityImpactTool
from schemas.config_schemas import LLMConfig, EmbedderConfig

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig):
        # Validate the configs
        if not isinstance(llm_config, LLMConfig):
            raise TypeError("Invalid LLMConfig provided.")
        if not isinstance(embedder_config, EmbedderConfig):
            raise TypeError("Invalid EmbedderConfig provided.")
        
        logger.info("ToolRegistry initialized with valid LLMConfig and EmbedderConfig.")
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.tools: Dict[str, StructuredTool] = {}

    def get_tool(self, tool_name: str) -> StructuredTool:
        if tool_name in self.tools:
            logger.debug(f"Tool '{tool_name}' fetched from registry.")
            return self.tools[tool_name]

        logger.info(f"Creating tool '{tool_name}'.")

        try:
            tool = None  # Initialize tool variable
            if tool_name == "tedx_search":
                tool = TEDxSearchTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            elif tool_name == "tedx_slug":
                self.get_tool("tedx_search")  # Pre-fetch to ensure it's initialized
                tool = TEDxSlugTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            elif tool_name == "tedx_transcript":
                self.get_tool("tedx_slug")  # Ensure 'tedx_slug' is created before 'tedx_transcript'
                tool = TEDxTranscriptTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            elif tool_name == "sdg_align":
                tool = SDGAlignTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            elif tool_name == "sustainability_impact":
                tool = SustainabilityImpactTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            elif tool_name == "duckduckgo_search":
                tool = DuckDuckGoSearchTool(llm_config=self.llm_config, embedder_config=self.embedder_config)
            else:
                logger.warning(f"Tool '{tool_name}' not recognized.")
                raise ValueError(f"Unknown tool: {tool_name}")

            if tool:
                self.tools[tool_name] = tool
                logger.info(f"Tool '{tool_name}' created and added to registry.")
                return tool

        except Exception as e:
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
            raise
