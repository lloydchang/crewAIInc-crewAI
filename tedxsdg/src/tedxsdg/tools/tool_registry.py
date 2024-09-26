# tools/tool_registry.py

import logging
from typing import Dict, Type
from langchain.tools import StructuredTool
from crewai_manager.config_loader import load_config
from .sustainability_impact_tool import SustainabilityImpactTool
from .sdg_align_tool import SDGAlignTool
from .tedx_search_tool import TEDxSearchTool

logger = logging.getLogger(__name__)

# In tool_registry.py

class ToolRegistry:
    def __init__(self):
        self.tool_configs = load_config('config/tools.yaml', 'tools')
        self.tools: Dict[str, StructuredTool] = {}

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        logger.debug(f"Creating tool '{tool_name}'")
        
        if tool_name not in self.tool_configs:
            logger.error(f"No configuration found for tool '{tool_name}'.")
            raise ValueError(f"Tool configuration for '{tool_name}' not found.")

        try:
            tool_config = self.tool_configs[tool_name]
            tool_instance = tool_class(config=tool_config)
            logger.debug(f"Tool '{tool_name}' created successfully")
            return tool_instance
        except Exception as e:
            logger.error(f"Error creating tool '{tool_name}': {str(e)}", exc_info=True)
            raise

    def get_tool(self, tool_name: str) -> StructuredTool:
        """Retrieve a tool by its name from the registry, or create it if not already initialized."""
        if tool_name in self.tools:
            return self.tools[tool_name]

        logger.info(f"Creating tool '{tool_name}'.")

        # Mapping tool_name to corresponding tool class
        tool_mapping = {
            "tedx_search": TEDxSearchTool,
            "sdg_align": SDGAlignTool,
            "sustainability_impact": SustainabilityImpactTool,
        }

        tool_class = tool_mapping.get(tool_name)
        if not tool_class:
            logger.warning(f"Tool '{tool_name}' not recognized.")
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            tool = self._create_tool(tool_name, tool_class)
            self.tools[tool_name] = tool
            return tool
        except Exception as e:
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
            raise
