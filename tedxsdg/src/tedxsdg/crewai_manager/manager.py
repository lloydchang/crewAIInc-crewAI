# crewai_manager/manager.py

import logging
import os
from pydantic import ValidationError
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from schemas.config_schemas import ToolConfig, LLMConfig, EmbedderConfig
from tools.tool_registry import ToolRegistry
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        self._validate_config_path(agents_config_path, "agents")
        self._validate_config_path(tasks_config_path, "tasks")
        self._validate_config_path(model_config_path, "model")
        self._validate_config_path(tools_config_path, "tools")

        self.agents_config = load_config(agents_config_path, "agents")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        self.model_config = load_config(model_config_path, "model")
        self.tools_config = load_config(tools_config_path, "tools")

        self.agents = {}
        self.tasks = []

        self.tool_config = self._initialize_tool_config()

        self.tool_registry = ToolRegistry(
            llm_config=self.tool_config.llm,
            embedder_config=self.tool_config.embedder,
            tools_config_path=tools_config_path
        )

        self.memory = True
        self._log_llm_use(self.tool_config.llm)

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        if not os.path.exists(config_path):
            logger.error(f"{config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def _log_llm_use(self, llm_config: LLMConfig) -> None:
        if not llm_config or not hasattr(llm_config, 'config') or not hasattr(llm_config.config, 'model'):
            logger.error("Invalid LLM configuration provided.")
            return

        provider = llm_config.provider
        model = llm_config.config.model
        temperature = getattr(llm_config.config, 'temperature', 'N/A')
        logger.info(f"Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def _initialize_tool_config(self) -> ToolConfig:
        try:
            logger.debug(f"Model config being passed: {self.model_config}")

            llm_config = LLMConfig(**self.model_config["llm"])
            embedder_config = EmbedderConfig(**self.model_config["embedder"])

            tool_config = ToolConfig(llm=llm_config, embedder=embedder_config)
            logger.debug(f"ToolConfig successfully initialized: {tool_config}")
            return tool_config
        except ValidationError as ve:
            logger.error(f"Validation error in tool configuration: {ve.errors()}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during ToolConfig initialization: {e}", exc_info=True)
            raise

    def create_task(self, task_name: str) -> None:
        if task_name not in self.tasks_config:
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
        logger.info(f"Created task '{task_name}' assigned to agent '{agent_name}' with priority {priority}.")
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        try:
            if not self.tool_config.llm or not self.tool_config.embedder:
                raise ValueError("LLMConfig or EmbedderConfig not properly initialized.")

            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.tool_config.llm,
                self.tool_config.embedder,
                self.tool_registry
            )
        except Exception as e:
            logger.error(f"Error creating agent '{agent_name}': {e}", exc_info=True)
            raise

    def initialize_crew(self) -> Crew:
        logger.info("Initializing crew")
        for task_name in self.tasks_config:
            try:
                self.create_task(task_name)
            except Exception as e:
                logger.error(f"Error creating task '{task_name}': {str(e)}", exc_info=True)

        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        try:
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=self.memory,
                verbose=True,
            )
            logger.info(f"Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"Error initializing Crew: {str(e)}", exc_info=True)
            raise