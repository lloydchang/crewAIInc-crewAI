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
from schemas.config_schemas import LLMConfig, EmbedderConfig
from pydantic import ValidationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

class ToolRegistry:
    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, tools_config_path: str = "config/tools.yaml"):
        # Validate required fields
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")
        # Validate types
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
        logger.debug(f"_load_tool_configs [Line 1] Starting to load tool configurations from '{tools_config_path}'")
        
        try:
            logger.debug(f"_load_tool_configs [Line 2] Attempting to open the tools configuration file at '{tools_config_path}'")
            
            with open(tools_config_path, 'r') as f:
                logger.debug(f"_load_tool_configs [Line 3] Successfully opened the configuration file at '{tools_config_path}'")
                
                tool_configs = yaml.safe_load(f)
                logger.debug(f"_load_tool_configs [Line 4] Parsed the YAML configuration file successfully")
            
            logger.info(f"_load_tool_configs [Line 5] Loaded tool configurations from '{tools_config_path}'")
            logger.debug(f"_load_tool_configs [Line 6] Full tool configurations: {tool_configs}")
            
            return tool_configs

        except FileNotFoundError:
            logger.error(f"_load_tool_configs [Line 7] The configuration file '{tools_config_path}' was not found.")
            raise

        except yaml.YAMLError as yaml_error:
            logger.error(f"_load_tool_configs [Line 8] Error parsing YAML from '{tools_config_path}': {yaml_error}", exc_info=True)
            raise

        except Exception as e:
            logger.error(f"_load_tool_configs [Line 9] An unexpected error occurred while loading tool configurations from '{tools_config_path}': {e}", exc_info=True)
            raise

    def _create_tool(self, tool_name: str, tool_class: Type[StructuredTool]) -> StructuredTool:
        """Create a tool with the provided tool name and class, using the loaded config."""
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

            logger.debug(f"_create_tool [Line 7] Extracted embedder_config: {embedder_conf}, llm_config: {llm_conf}")

            if embedder_conf is None:
                logger.error("_create_tool [Line 8] Missing embedder_config")
                raise ValueError(f"Missing required 'embedder_config' for tool '{tool_name}'.")
            if llm_conf is None:
                logger.error("_create_tool [Line 9] Missing llm_config")
                raise ValueError(f"Missing required 'llm_config' for tool '{tool_name}'.")

            # Validate configuration using Pydantic 2 model_validate
            logger.debug("_create_tool [Line 10] Validating embedder_conf")
            embedder_conf = EmbedderConfig.model_validate(embedder_conf)
            logger.debug("_create_tool [Line 11] embedder_conf validation passed")
            
            logger.debug("_create_tool [Line 12] Validating llm_conf")
            llm_conf = LLMConfig.model_validate(llm_conf)
            logger.debug("_create_tool [Line 13] llm_conf validation passed")

            data_path = tool_config.get('data_path')
            logger.debug(f"_create_tool [Line 14] data_path: {data_path}")
            
            if tool_name in ["tedx_search", "tedx_slug", "tedx_transcript", "sdg_align", "sustainability_impact"] and not data_path:
                logger.error("_create_tool [Line 15] Missing data_path for specific tool")
                raise ValueError(f"Missing data path for tool '{tool_name}'")

            tool_kwargs = {
                "llm_config": llm_conf,
                "embedder_config": embedder_conf,
                "data_path": data_path
            }
            logger.debug(f"_create_tool [Line 16] tool_kwargs: {tool_kwargs}")

            logger.debug(f"_create_tool [Line 17] Initializing tool '{tool_name}' with provided configurations: {tool_kwargs}")
            logger.debug(f"_create_tool [Line 18] tool_class: {tool_class}")
            tool_instance = tool_class(**tool_kwargs)
            logger.debug("_create_tool [Line 19] Tool instance created successfully")
            return tool_instance

        except ValueError as ve:
            logger.error(f"_create_tool [Line 20] Configuration error for tool '{tool_name}': {ve}", exc_info=True)
            raise
        except ValidationError as ve:
            logger.error(f"_create_tool [Line 21] Validation error for tool '{tool_name}': {ve.errors()}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"_create_tool [Line 22] Error creating tool '{tool_name}': {e}", exc_info=True)
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
