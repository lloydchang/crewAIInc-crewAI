# crewai_manager/manager.py

import logging
import os
from pydantic import ValidationError
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from schemas.config_schemas import ToolConfig, LLMConfig, EmbedderConfig
from tools.tool_registry import ToolRegistry

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        logger.debug("[Line 1] Initializing CrewAIManager")
        
        # Validate configuration paths
        self._validate_config_path(agents_config_path, "agents")
        logger.debug("[Line 2] Agents config path validated")

        self._validate_config_path(tasks_config_path, "tasks")
        logger.debug("[Line 3] Tasks config path validated")

        self._validate_config_path(model_config_path, "model")
        logger.debug("[Line 4] Model config path validated")

        self._validate_config_path(tools_config_path, "tools")
        logger.debug("[Line 5] Tools config path validated")

        # Load configurations
        logger.debug("[Line 6] Loading agents configuration")
        self.agents_config = load_config(agents_config_path, "agents")
        logger.debug(f"[Line 7] Agents configuration loaded: {self.agents_config}")

        logger.debug("[Line 8] Loading tasks configuration")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        logger.debug(f"[Line 9] Tasks configuration loaded: {self.tasks_config}")

        logger.debug("[Line 10] Loading model configuration")
        self.model_config = load_config(model_config_path, "model")
        logger.debug(f"[Line 11] Model configuration loaded: {self.model_config}")

        logger.debug("[Line 12] Loading tools configuration")
        self.tools_config = load_config(tools_config_path, "tools")
        logger.debug(f"[Line 13] Tools configuration loaded: {self.tools_config}")

        # Initialize empty agents and tasks
        self.agents = {}
        self.tasks = []
        logger.debug("[Line 14] Empty agents and tasks initialized")

        # Initialize tool configuration
        logger.debug("[Line 15] Initializing tool configuration")
        self.tool_config = self._initialize_tool_config()
        logger.debug(f"[Line 16] Tool configuration initialized: {self.tool_config}")

        # Initialize tool registry
        logger.debug("[Line 17] Initializing tool registry")
        self.tool_registry = ToolRegistry(
            llm_config=self.tool_config.llm,
            embedder_config=self.tool_config.embedder,
            tools_config_path=tools_config_path
        )
        logger.debug("[Line 18] Tool registry initialized")

        # Set memory flag
        self.memory = True
        logger.debug("[Line 19] Memory flag set to True")

        # Log LLM use
        logger.debug("[Line 20] Logging LLM usage")
        self._log_llm_use(self.tool_config.llm)
        logger.debug("[Line 21] LLM usage logged")

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        logger.debug(f"[Line 22] Validating {config_name} config path: {config_path}")
        if not os.path.exists(config_path):
            logger.error(f"[Line 23] {config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")
        logger.debug(f"[Line 24] {config_name} config path validation successful")

    def _log_llm_use(self, llm_config: LLMConfig) -> None:
        logger.debug(f"[Line 25] Logging LLM use: {llm_config}")
        if not llm_config or not hasattr(llm_config, 'config') or not hasattr(llm_config.config, 'model'):
            logger.error("[Line 26] Invalid LLM configuration provided.")
            return

        provider = llm_config.provider
        model = llm_config.config.model
        temperature = getattr(llm_config.config, 'temperature', 'N/A')
        logger.info(f"[Line 27] Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def _initialize_tool_config(self) -> ToolConfig:
        try:
            logger.debug(f"[Line 28] Model config being passed: {self.model_config}")

            tool_config_data = {
                "llm": self.model_config["llm"],
                "embedder": self.model_config["embedder"]
            }

            logger.debug(f"[Line 31] Tool config data before validation: {tool_config_data}")
            tool_config = ToolConfig(**tool_
