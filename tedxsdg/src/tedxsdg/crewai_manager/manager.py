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

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        logger.debug("[Line 1] Initializing CrewAIManager")
        
        # Load configurations
        self.agents_config = load_config(agents_config_path, "agents")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        self.model_config = load_config(model_config_path, "model")
        self.tools_config = load_config(tools_config_path, "tools")

        # Initialize empty agents and tasks
        self.agents = {}
        self.tasks = []

        # Initialize tool registry
        self.tool_registry = ToolRegistry(
            llm_config=self.model_config.get("llm"),
            embedder_config=self.model_config.get("embedder"),
            tools_config_path=tools_config_path
        )

        # Set memory flag
        self.memory = True

    def create_task(self, task_name: str) -> None:
        logger.debug(f"[Line 35] Creating task: {task_name}")
        if task_name not in self.tasks_config:
            logger.error(f"[Line 36] Task '{task_name}' not found in tasks configuration.")
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        agent_name = task_config.get("agent")

        if agent_name not in self.agents:
            logger.debug(f"[Line 38] Agent '{agent_name}' not found, creating new agent.")
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        priority = task_config.get("priority", 2)

        task = Task(
            description=task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        logger.info(f"[Line 41] Created task '{task_name}' assigned to agent '{agent_name}' with priority {priority}.")
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        logger.debug(f"[Line 43] Creating agent: {agent_name}")
        try:
            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.model_config.get("llm"),
                self.model_config.get("embedder"),
                self.tool_registry
            )
        except Exception as e:
            logger.error(f"[Line 46] Error creating agent '{agent_name}': {e}", exc_info=True)
            raise

    def initialize_crew(self) -> Crew:
        logger.debug("[Line 47] Initializing crew")
        for task_name in self.tasks_config:
            try:
                logger.debug(f"[Line 48] Creating task '{task_name}'")
                self.create_task(task_name)
            except Exception as e:
                logger.error(f"[Line 49] Error creating task '{task_name}': {str(e)}", exc_info=True)

        if not self.agents or not self.tasks:
            logger.error("[Line 50] At least one agent and one task must be successfully created to initialize the crew.")
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        try:
            logger.debug(f"[Line 51] Initializing Crew with {len(self.agents)} agents and {len(self.tasks)} tasks")
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=self.memory,
                verbose=True,
            )
            logger.info(f"[Line 52] Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"[Line 53] Error initializing Crew: {str(e)}", exc_info=True)
            raise
