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
from crewai_manager.config_loader import load_config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any], tools_config_path: str = "config/tools.yaml"):
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")

        logger.info("ToolRegistry initialized with valid LLMConfig and EmbedderConfig.")
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.tools: Dict[str, StructuredTool] = {}

        # Load tool-specific configurations
        self.tool_configs = load_config(tools_config_path, "tools")

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        logger.debug(f"_create_tool [Line 1] Entering _create_tool for {tool_name}")

        tool_config = self.tool_configs.get(tool_name, {})
        logger.debug(f"_create_tool [Line 2] tool_config: {tool_config}")

        if not tool_config:
            logger.error(f"_create_tool [Line 3] No configuration found for tool '{tool_name}'.")
            raise ValueError(f"Tool configuration for '{tool_name}' not found in tools.yaml.")

        try:
            logger.debug("_create_tool [Line 4] Entering try block")

            embedder_conf = tool_config.get('embedder_config')
            logger.debug(f"_create_tool [Line 5] embedder_conf: {embedder_conf}")

            llm_conf = tool_config.get('llm_config')
            logger.debug(f"_create_tool [Line 6] llm_conf: {llm_conf}")

            if embedder_conf is None:
                logger.error("_create_tool [Line 8] Missing embedder_config")
                raise ValueError(f"Missing required 'embedder_config' for tool '{tool_name}'.")
            if llm_conf is None:
                logger.error("_create_tool [Line 9] Missing llm_config")
                raise ValueError(f"Missing required 'llm_config' for tool '{tool_name}'.")

            data_path = tool_config.get('data_path')
            logger.debug(f"_create_tool [Line 10] data_path: {data_path}")

            tool_kwargs = {
                "llm_config": llm_conf,
                "embedder_config": embedder_conf,
                "data_path": data_path
            }
            logger.debug(f"_create_tool [Line 12] tool_kwargs: {tool_kwargs}")

            logger.debug(f"_create_tool [Line 13] Initializing tool '{tool_name}' with provided configurations: {tool_kwargs}")
            tool_instance = tool_class(**tool_kwargs)
            logger.debug("_create_tool [Line 14] Tool instance created successfully")
            return tool_instance

        except ValueError as ve:
            logger.error(f"_create_tool [Line 15] Configuration error for tool '{tool_name}': {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"_create_tool [Line 16] Error creating tool '{tool_name}': {e}", exc_info=True)
            raise

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
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_in
