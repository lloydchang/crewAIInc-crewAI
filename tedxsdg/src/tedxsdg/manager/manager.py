# manager/manager.py

import logging
import os
from typing import Any, Dict, List
from tools.tool_registry import ToolRegistry
from crewai import Crew, Process, Agent, Task
from tools.config_loader import load_config
from .agent_factory import create_agent

logger = logging.getLogger(__name__)

class CrewAIManager:
    """
    Manages the CrewAI operations including agents, tasks, and tools.
    """

    def __init__(
        self, 
        agents_config_path: str, 
        tasks_config_path: str, 
        tools_config_path: str = "config/tools.yaml"  # model_config_path removed
    ):
        logger.debug("Initializing CrewAIManager")

        # Validate configuration paths
        self._validate_config_path(agents_config_path, "agents")
        self._validate_config_path(tasks_config_path, "tasks")
        self._validate_config_path(tools_config_path, "tools")

        # Load configurations
        logger.debug("Loading agents configuration")
        self.agents_config = load_config(agents_config_path, "agents")

        logger.debug("Loading tasks configuration")
        self.tasks_config = load_config(tasks_config_path, "tasks")

        logger.debug("Loading tools configuration")
        self.tools_config = load_config(tools_config_path, "tools")

        # Initialize empty agents and tasks
        self.agents: Dict[str, Agent] = {}
        self.tasks: List[Task] = []

        # Initialize tool registry with preloaded configurations
        logger.debug("Initializing tool registry")
        self.tool_registry = ToolRegistry(self.tools_config)

        # Log LLM use (Assuming all tools use the same LLM)
        self._log_llm_use()

        # Log Embedder use
        self._log_embedder_use()
