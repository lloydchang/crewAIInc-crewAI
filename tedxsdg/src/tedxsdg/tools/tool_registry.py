# tools/tool_registry.py

import logging
from typing import Dict, Type, Any
from crewai import LLM  # Assuming LLM class is imported from crewai
from langchain.tools import StructuredTool
from .config_loader import load_config
from .duckduckgo_search_tool import DuckDuckGoSearchTool
from .sdg_align_tool import SDGAlignTool
from .sustainability_impact_tool import SustainabilityImpactTool
from .tedx_search_tool import TEDxSearchTool
from .tedx_slug_tool import TEDxSlugTool
from .tedx_transcript_tool import TEDxTranscriptTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing and creating tools.
    """

    def __init__(self, config_path: str = 'config/tools.yaml'):
        # Load the entire configuration from the specified YAML file
        self.tool_configs = load_config(config_path)
        logger.debug("Loaded tool configurations from '%s': %s", config_path, self.tool_configs)
        self.tools: Dict[str, StructuredTool] = {}

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        logger.debug("Creating tool '%s'", tool_name)
        
        if tool_name not in self.tool_configs:
            logger.error("No configuration found for tool '%s'.", tool_name)
            raise ValueError(f"Tool configuration for '{tool_name}' not found.")

        try:
            # Extract the configuration for the given tool
            tool_config = self.tool_configs[tool_name]

            # Pass the entire tool configuration to the tool during instantiation
            tool_instance = tool_class(**tool_config)
            logger.debug("Tool '%s' created successfully.", tool_name)
            
            # Cache the created tool in the registry
            self.tools[tool_name] = tool_instance
            return tool_instance

        except Exception as e:
            logger.error("Error creating tool '%s': %s", tool_name, str(e), exc_info=True)
            raise

    def get_tool(self, tool_name: str) -> StructuredTool:
        """
        Retrieve a tool by its name from the registry, or create it if not 
        already initialized.
        """
        if tool_name in self.tools:
            return self.tools[tool_name]

        logger.info("Creating tool '%s'.", tool_name)

        # Mapping tool_name to the corresponding tool class
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
            logger.warning("Tool '%s' not recognized.", tool_name)
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            # Create and return the tool instance
            return self._create_tool(tool_name, tool_class)
        except Exception as e:
            logger.error("Failed to create tool '%s': %s", tool_name, e, exc_info=True)
            raise

    def list_tools(self) -> Dict[str, StructuredTool]:
        """
        List all registered tools.
        """
        return self.tools
