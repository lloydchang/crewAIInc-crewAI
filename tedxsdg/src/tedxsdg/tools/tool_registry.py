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
    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any], tools_config_path: str = "config/tools.yaml"):
        # Validate required fields
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")

        logger.info("ToolRegistry initialized with valid LLMConfig and EmbedderConfig.")
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.tools: Dict[str, StructuredTool] = {}

        # Load tool-specific configurations
        self.tool_configs = self._load_tool_configs(tools_config_path)

    def _load_tool_configs(self, tools_config_path: str) -> Dict[str, Dict[str, Any]]:
        """Loads tool-specific configurations from the tools.yaml file."""
        logger.debug(f"Starting to load tool configurations from '{tools_config_path}'")
        
        try:
            with open(tools_config_path, 'r') as f:
                tool_configs = yaml.safe_load(f)
                logger.info(f"Loaded tool configurations from '{tools_config_path}'")
                logger.debug(f"Full tool configurations: {tool_configs}")
                return tool_configs

        except FileNotFoundError:
            logger.error(f"The configuration file '{tools_config_path}' was not found.")
            raise FileNotFoundError(f"The configuration file '{tools_config_path}' was not found.")
        except yaml.YAMLError as yaml_error:
            logger.error(f"Error parsing YAML from '{tools_config_path}': {yaml_error}", exc_info=True)
            raise yaml_error
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading tool configurations: {e}", exc_info=True)
            raise

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        """Create a tool with the provided tool name and class, using the loaded config."""
        logger.debug(f"Entering _create_tool for '{tool_name}'")
        
        tool_config = self.tool_configs.get(tool_name, {})
        logger.debug(f"Tool config: {tool_config}")

        if not tool_config:
            logger.error(f"No configuration found for tool '{tool_name}'.")
            raise ValueError(f"Tool configuration for '{tool_name}' not found in tools.yaml.")

        try:
            embedder_conf = tool_config.get('embedder_config')
            llm_conf = tool_config.get('llm_config')

            if embedder_conf is None:
                logger.error("Missing embedder_config")
                raise ValueError(f"Missing required 'embedder_config' for tool '{tool_name}'.")
            if llm_conf is None:
                logger.error("Missing llm_config")
                raise ValueError(f"Missing required 'llm_config' for tool '{tool_name}'.")

            data_path = tool_config.get('data_path')

            if tool_name in ["tedx_search", "tedx_slug", "tedx_transcript", "sdg_align", "sustainability_impact"] and not data_path:
                logger.error("Missing data_path for specific tool")
                raise ValueError(f"Missing data path for tool '{tool_name}'")

            logger.debug(f"Initializing tool '{tool_name}'.)
            tool_instance = tool_class()
            logger.debug("Tool instance created successfully")
            return tool_instance

        except ValueError as ve:
            logger.error(f"Configuration error for tool '{tool_name}': {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error creating tool '{tool_name}': {e}", exc_info=True)
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
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
            raise
