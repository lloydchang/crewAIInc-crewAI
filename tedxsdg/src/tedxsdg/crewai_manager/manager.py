# crewai_manager/manager.py

import logging
import os
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from tools.tool_registry import ToolRegistry
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        logger.debug("[Line 1] Initializing CrewAIManager")
        
        # Validate configuration paths
        self._validate_config_path(agents_config_path, "agents")
        self._validate_config_path(tasks_config_path, "tasks")
        self._validate_config_path(model_config_path, "model")
        self._validate_config_path(tools_config_path, "tools")

        # Load configurations
        self.agents_config = load_config(agents_config_path, "agents")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        self.model_config = load_config(model_config_path, "model")
        self.tools_config = load_config(tools_config_path, "tools")

        # Initialize empty agents and tasks
        self.agents = {}
        self.tasks = []

        # Initialize tool registry
        self.tool_registry = ToolRegistry()

        # Set memory flag
        self.memory = True

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        if not os.path.exists(config_path):
            logger.error(f"{config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def create_task(self, task_name: str) -> None:
        if task_name not in self.tasks_config:
            logger.error(f"Task '{task_name}' not found in tasks configuration.")
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        agent_name = task_config.get("agent")

        if agent_name not in self.agents:
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        priority = task_config.get("priority", 2)

        task = Task(
            description=task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        try:
            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.tool_registry
            )
        except Exception as e:
            logger.error(f"Error creating agent '{agent_name}': {e}", exc_info=True)
            raise

    def initialize_crew(self) -> Crew:
        for task_name in self.tasks_config:
            try:
                self.create_task(task_name)
            except Exception as e:
                logger.error(f"Error creating task '{task_name}': {e}", exc_info=True)

        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        return Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            memory=self.memory,
            max_rpm=None,
            share_crew=False,
            verbose=True,
        )
