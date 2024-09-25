# tools/tool_registry.py

import logging
import yaml
from typing import Dict, Any, Type
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
    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, tools_config_path: str = "config/tools.yaml"):
        if not isinstance(llm_config, LLMConfig):
            raise TypeError("Invalid LLMConfig provided.")
        if not isinstance(embedder_config, EmbedderConfig):
            raise TypeError("Invalid EmbedderConfig provided.")
        
        logger.info("ToolRegistry initialized with valid LLMConfig and EmbedderConfig.")
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.tools: Dict[str, StructuredTool] = {}

        # Load tool-specific configurations
        self.tool_configs = self._load_tool_configs(tools_config_path)

    def _load_tool_configs(self, tools_config_path: str) -> Dict[str, Dict[str, Any]]:
        """Loads tool-specific configurations from the tools.yaml file."""
        try:
            with open(tools_config_path, 'r') as f:
                tool_configs = yaml.safe_load(f)
            logger.info(f"Loaded tool configurations from '{tools_config_path}'.")
            return tool_configs
        except Exception as e:
            logger.error(f"Error loading tool configurations from '{tools_config_path}': {e}", exc_info=True)
            raise

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        tool_config = self.tool_configs.get(tool_name, {})
        embedder_conf = tool_config.get('embedder_config', {})
        data_path = tool_config.get('data_path', None)
        
        if not isinstance(embedder_conf, EmbedderConfig):
            embedder_conf = EmbedderConfig(**embedder_conf)

        if tool_name in ["tedx_search", "tedx_slug", "tedx_transcript"] and not data_path:
            raise ValueError(f"Missing data path for tool '{tool_name}'")
    
        llm_config_dict = {
            "provider": self.llm_config.provider,
            "config": {
                "model": self.llm_config.config.model,
                "temperature": self.llm_config.config.temperature,
                "top_p": self.llm_config.config.top_p,
                "stream": self.llm_config.config.stream
            }
        }

        tool_kwargs = {
            "llm_config": llm_config_dict,
            "embedder_config": embedder_conf.dict(),
            "data_path": data_path
        }

        logger.debug(f"Initialize with the provided configurations: llm_config={llm_config_dict}, embedder_config={embedder_conf.dict()}, data_path={data_path}")
        return tool_class(**tool_kwargs)

    def get_tool(self, tool_name: str) -> StructuredTool:
        if tool_name in self.tools:
            logger.debug(f"Tool '{tool_name}' fetched from registry.")
            return self.tools[tool_name]

        logger.info(f"Creating tool '{tool_name}'.")

        try:
            if tool_name == "tedx_search":
                tool = self._create_tool(tool_name, TEDxSearchTool)
            elif tool_name == "tedx_slug":
                tool = self._create_tool(tool_name, TEDxSlugTool)
            elif tool_name == "tedx_transcript":
                tool = self._create_tool(tool_name, TEDxTranscriptTool)
            elif tool_name == "sdg_align":
                tool = self._create_tool(tool_name, SDGAlignTool)
            elif tool_name == "sustainability_impact":
                tool = self._create_tool(tool_name, SustainabilityImpactTool)
            elif tool_name == "duckduckgo_search":
                tool = self._create_tool(tool_name, DuckDuckGoSearchTool)
            else:
                logger.warning(f"Tool '{tool_name}' not recognized.")
                raise ValueError(f"Unknown tool: {tool_name}")

            self.tools[tool_name] = tool
            logger.info(f"Tool '{tool_name}' created and added to registry.")
            return tool

        except Exception as e:
            logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
            raise
