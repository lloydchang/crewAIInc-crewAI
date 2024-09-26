# tools/tool_registry.py

import logging
import yaml
from typing import Any, Dict, Type
from langchain.tools import StructuredTool
from .duckduckgo_search_tool import DuckDuckGoSearchTool
from .tedx_search_tool import TEDxSearchTool
from .tedx_slug_tool import TEDxSlugTool
from .tedx_transcript_tool import TEDxTranscriptTool
from .sdg_align_tool import SDGAlignTool
from .sustainability_impact_tool import SustainabilityImpactTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self, config_loader):
        self.llm_config = config_loader.model_config.get('llm')
        self.embedder_config = config_loader.model_config.get('embedder')
        self.tools: Dict[str, StructuredTool] = {}
        self.tool_configs = config_loader.tools_config  # Directly use the loaded config

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        logger.debug(f"Entering _create_tool for '{tool_name}'")

        tool_config = self.tool_configs.get(tool_name, {})
        if not tool_config:
            logger.error(f"No configuration found for tool '{tool_name}'.")
            raise ValueError(f"Tool configuration for '{tool_name}' not found.")

        # Extract configurations directly from tool_config
        llm_conf = tool_config.get('llm_config')
        embedder_conf = tool_config.get('embedder_config')
        data_path = tool_config.get('data_path')

        tool_kwargs = {
            "llm_config": llm_conf,
            "embedder_config": embedder_conf,
            "data_path": data_path
        }

        logger.debug(f"Initializing tool '{tool_name}' with configurations: {tool_kwargs}")
        tool_instance = tool_class(**tool_kwargs)
        logger.debug("Tool instance created successfully")
        return tool_instance

    def get_tool(self, tool_name: str) -> StructuredTool:
        """Retrieve a tool by its name from the registry, or create it if not already initialized."""
        if tool_name in self.tools:
            logger.debug(f"Tool '{tool_name}' fetched from registry.")
            return self.tools[tool_name]

        logger.info(f"Creating tool '{tool_name}'.")

        # Mapping tool_name to corresponding tool class
        tool_mapping = {
            "tedx_search": TEDxSearchTool,
            "tedx_slug": TEDxSlugTool,
            "tedx_transcript": TEDxTranscriptTool,
            "sdg_align": SDGAlignTool,
            "sustainability_impact": SustainabilityImpactTool,
            "duckduckgo_search": DuckDuckGoSearchTool
        }

        tool_class = tool_mapping.get(tool_name)
        if not tool_class:
            logger.warning(f"Tool '{tool_name}' not recognized.")
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            tool = self._create_tool(tool_name, tool_class)
            self.tools[tool_name] = tool
            logger.info(f"Tool '{tool_name}' created and added to registry.")
            return tool
        except Exception as e:
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
            raise
