# crewai_manager/manager.py

import logging
import os
from pydantic import ValidationError
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from schemas.config_schemas import ToolConfig, LLMConfig, EmbedderConfig  # Ensure these are updated in config_schemas.py
from tools.tool_registry import ToolRegistry
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug logging is working at the top of the script.")

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        # Ensure config paths are valid
        self._validate_config_path(agents_config_path, "agents")
        self._validate_config_path(tasks_config_path, "tasks")
        self._validate_config_path(model_config_path, "model")
        self._validate_config_path(tools_config_path, "tools")

        # Load configurations
        self.agents_config = load_config(agents_config_path, "agents")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        self.model_config = load_config(model_config_path, "model")
        self.tools_config = load_config(tools_config_path, "tools")

        self.agents = {}
        self.tasks = []

        # Validate and load model configuration
        self.tool_config = self._initialize_tool_config()

        # Initialize ToolRegistry
        self.tool_registry = ToolRegistry(
            llm_config=self.tool_config.llm,
            embedder_config=self.tool_config.embedder,
            tools_config_path=tools_config_path
        )

        self.memory = True  # Enable memory by default
        self._log_llm_use(self.tool_config.llm)

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        if not os.path.exists(config_path):
            logger.error(f"{config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def _log_llm_use(self, llm_config: LLMConfig) -> None:
        if not llm_config or not llm_config.config.get('model', None):
            logger.error("Invalid LLM configuration provided.")
            return

        provider = llm_config.provider
        model = llm_config.config['model']
        temperature = llm_config.config.get('temperature', 'N/A')
        logger.info(f"Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def _initialize_tool_config(self) -> ToolConfig:
        try:
            logger.debug(f"Model config being passed: {self.model_config}")

            tool_config_data = {
                "llm": self.model_config["llm"],
                "embedder": self.model_config["embedder"]
            }

            # Add data_paths to embedder config
            tool_config_data["embedder"]["data_paths"] = [
                tool_config["data_path"] for tool_config in self.tools_config.values()
            ]

            tool_config = ToolConfig(**tool_config_data)
            logger.debug(f"ToolConfig successfully initialized: {tool_config}")
            return tool_config
        except ValidationError as ve:
            logger.error(f"Validation error in tool configuration: {ve.errors