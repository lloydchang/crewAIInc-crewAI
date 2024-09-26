# manager/manager.py

import logging
import os
from typing import Any, Dict
from tools.tool_registry import ToolRegistry
from crewai import Crew, Process, Agent, Task
from tools.config_loader import load_config
from manager.agent_factory import create_agent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CrewAIManager:
    """
    Manages the CrewAI operations including agents, tasks, and tools.
    """

    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str,
                 tools_config_path: str = "config/tools.yaml"):
        logger.debug("Initializing CrewAIManager")

        # Validate configuration paths
        self._validate_config_path(agents_config_path, "agents")
        self._validate_config_path(tasks_config_path, "tasks")
        self._validate_config_path(model_config_path, "model")
        self._validate_config_path(tools_config_path, "tools")

        # Load configurations
        logger.debug("Loading agents configuration")
        self.agents_config = load_config(agents_config_path, "agents")

        logger.debug("Loading tasks configuration")
        self.tasks_config = load_config(tasks_config_path, "tasks")

        logger.debug("Loading model configuration")
        self.model_config = load_config(model_config_path, "model")

        logger.debug("Loading tools configuration")
        self.tools_config = load_config(tools_config_path, "tools")

        # Initialize empty agents and tasks
        self.agents = {}
        self.tasks = []

        # Initialize tool configuration
        logger.debug("Initializing tool configuration")
        self.tool_config = self._initialize_tool_config()

        # Initialize tool registry with preloaded configurations
        logger.debug("Initializing tool registry")
        self.tool_registry = ToolRegistry(self.tools_config)

        # Set memory flag
        self.memory = True

        # Log LLM use
        self._log_llm_use(self.tool_config['llm'])

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        logger.debug("Validating %s config path: %s", config_name, config_path)
        if not os.path.exists(config_path):
            logger.error("%s config file not found: %s", config_name.capitalize(), config_path)
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def _log_llm_use(self, llm_config: Dict[str, Any]) -> None:
        logger.debug("Logging LLM use: %s", llm_config)
        if not llm_config or not isinstance(llm_config, dict) or 'model' not in llm_config:
            logger.error("Invalid LLM configuration provided.")
            return

        provider = llm_config.get('provider')
        model = llm_config.get('model')
        temperature = llm_config.get('temperature', 'N/A')
        logger.info("Using LLM - Provider: %s, Model: %s, Temperature: %s", provider, model, temperature)

    def _initialize_tool_config(self) -> Dict[str, Any]:
        try:
            logger.debug("Model config being passed: %s", self.model_config)

            llm_config = self.model_config.get('llm', {}).get('config', {})
            embedder_config = self.model_config.get('embedder', {}).get('config', {})

            if not llm_config or 'model' not in llm_config:
                logger.error("LLM configuration is missing or does not contain a valid model.")
                raise ValueError("LLM configuration must contain a valid 'model'.")

            tool_config_data = {
                "llm": llm_config,
                "embedder": embedder_config
            }

            logger.debug("Tool config data: %s", tool_config_data)
            return tool_config_data
        except Exception as e:
            logger.error("Unexpected error during ToolConfig initialization: %s", e, exc_info=True)
            raise

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
        agent_name = task_config.get("agent")

        if agent_name not in self.agents:
            logger.debug("Agent '%s' not found, creating new agent.", agent_name)
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        logger.debug("Agent '%s' found or created", agent_name)

        priority = task_config.get("priority", 2)
        logger.debug("Task priority: %s", priority)

        task = Task(
            description=task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        logger.info("Created task '%s' assigned to agent '%s' with priority %s.", task_name, agent_name, priority)
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        logger.debug("Creating agent: %s", agent_name)
        try:
            if not self.tool_config['llm'] or not self.tool_config['embedder']:
                logger.error("LLMConfig or EmbedderConfig not properly initialized.")
                raise ValueError("LLMConfig or EmbedderConfig not properly initialized.")

            logger.debug("Calling create_agent with agent_name=%s, agent_config=%s", agent_name, self.agents_config[agent_name])
            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.tool_registry
            )
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
            logger.debug("Initializing Crew with %d agents and %d tasks", len(self.agents), len(self.tasks))
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=self.memory,
                embedder=self.tool_config['embedder'],
                max_rpm=None,
                share_crew=False,
                verbose=True,
            )
            logger.info("Initialized the crew with %d agents and %d tasks.", len(self.agents), len(self.tasks))
            return crew
        except Exception as e:
            logger.error("Error initializing Crew: %s", str(e), exc_info=True)
            raise
