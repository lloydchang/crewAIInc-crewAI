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
        tools_config_path: str = "config/tools.yaml"
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

        # Set memory flag
        self.memory = True

        # Log LLM use (Assuming all tools use the same LLM)
        self._log_llm_use()

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        logger.debug("Validating %s config path: %s", config_name, config_path)
        if not os.path.exists(config_path):
            logger.error("%s config file not found: %s", config_name.capitalize(), config_path)
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def _log_llm_use(self) -> None:
        """
        Logs the LLM configurations used by each tool.
        """
        for tool_name, tool_config in self.tools_config.items():
            llm_config = tool_config.get('llm_config', {}).get('config', {})
            if not llm_config or 'model' not in llm_config:
                logger.error("LLM configuration for tool '%s' is missing or does not contain a valid model.", tool_name)
                continue

            provider = tool_config.get('llm_config', {}).get('provider', 'Unknown')
            model = llm_config.get('model')
            temperature = llm_config.get('temperature', 'N/A')
            logger.info(
                "Tool '%s' uses LLM - Provider: %s, Model: %s, Temperature: %s", 
                tool_name, provider, model, temperature
            )

    def create_task(self, task_name: str) -> None:
        """
        Creates a task based on the provided task name.
        """
        logger.debug("Creating task: %s", task_name)
        if task_name not in self.tasks_config:
            logger.error("Task '%s' not found in tasks configuration.", task_name)
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        logger.debug("Task config: %s", task_config)
        agent__name = task_config.get("agent")

        if agent_name not in self.agents:
            logger.debug("Agent '%s' not found, creating new agent.", agent_name)
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        logger.debug("Agent '%s' found or created", agent_name)

        priority = task_config.get("priority", 2)
        logger.debug("Task priority: %s", priority)

        task = Task(
            _description = task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        logger.info(
            "Created task '%s' assigned to agent '%s' with priority %s.", 
            task_name, agent_name, priority
        )
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        """
        Creates an agent using the agent_factory.
        """
        logger.debug("Creating agent: %s", agent_name)
        try:
            agent_config = self.agents_config.get(agent_name, {})
            if not agent_config:
                logger.error("Agent configuration for '%s' is missing.", agent_name)
                raise ValueError(f"Agent configuration for '{agent_name}' is missing.")

            agent = create_agent(
                agent_name,
                agent_config,
                self.tool_registry
            )
            logger.debug("Agent '%s' created successfully.", agent_name)
            return agent
        except Exception as e:
            logger.error("Error creating agent '%s': %s", agent_name, e, exc_info=True)
            raise

    def initialize_crew(self) -> Crew:
        """
        Initializes the crew with agents and tasks.
        """
        logger.debug("Initializing crew")
        for task_name in self.tasks_config:
            try:
                logger.debug("Creating task '%s'", task_name)
                self.create_task(task_name)
            except Exception as e:
                logger.error("Error creating task '%s': %s", task_name, str(e), exc_info=True)

        if not self.agents or not self.tasks:
            logger.error("At least one agent and one task must be successfully created to initialize the crew.")
            raise ValueError(
                "At least one agent and one task must be successfully created to initialize the crew."
            )

        try:
            logger.debug(
                "Initializing Crew with %d agents and %d tasks", 
                len(self.agents), len(self.tasks)
            )
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=self.memory,
                embedder=None,  # Assuming embedder is handled within tools
                max_rpm=None,
                share_crew=False,
                verbose=True,
            )
            logger.info(
                "Initialized the crew with %d agents and %d tasks.", 
                len(self.agents), len(self.tasks)
            )
            return crew
        except Exception as e:
            logger.error("Error initializing Crew: %s", str(e), exc_info=True)
            raise
