# crewai_manager/manager.py

import logging
import os
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from tools.tool_registry import ToolRegistry
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
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

        # Initialize tool registry
        logger.debug("Initializing tool registry")
        self.tool_registry = ToolRegistry()

        # Set memory flag
        self.memory = True

        # Log LLM use
        self._log_llm_use(self.tool_config['llm'])

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        logger.debug(f"Validating {config_name} config path: {config_path}")
        if not os.path.exists(config_path):
            logger.error(f"{config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def _log_llm_use(self, llm_config: Dict[str, Any]) -> None:
        logger.debug(f"Logging LLM use: {llm_config}")
        if not llm_config or not isinstance(llm_config, dict) or 'model' not in llm_config:
            logger.error("Invalid LLM configuration provided.")
            return

        provider = llm_config.get('provider')
        model = llm_config.get('model')
        temperature = llm_config.get('temperature', 'N/A')
        logger.info(f"Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def _initialize_tool_config(self) -> Dict[str, Any]:
        try:
            logger.debug(f"Model config being passed: {self.model_config}")

            llm_config = self.model_config.get('llm', {}).get('config', {})
            embedder_config = self.model_config.get('embedder', {}).get('config', {})

            if not llm_config or 'model' not in llm_config:
                logger.error("LLM configuration is missing or does not contain a valid model.")
                raise ValueError("LLM configuration must contain a valid 'model'.")

            tool_config_data = {
                "llm": llm_config,
                "embedder": embedder_config
            }

            logger.debug(f"Tool config data: {tool_config_data}")
            return tool_config_data
        except Exception as e:
            logger.error(f"Unexpected error during ToolConfig initialization: {e}", exc_info=True)
            raise

    def create_task(self, task_name: str) -> None:
        logger.debug(f"Creating task: {task_name}")
        if task_name not in self.tasks_config:
            logger.error(f"Task '{task_name}' not found in tasks configuration.")
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        logger.debug(f"Task config: {task_config}")
        agent_name = task_config.get("agent")

        if agent_name not in self.agents:
            logger.debug(f"Agent '{agent_name}' not found, creating new agent.")
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        logger.debug(f"Agent '{agent_name}' found or created")

        priority = task_config.get("priority", 2)
        logger.debug(f"Task priority: {priority}")

        task = Task(
            description=task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        logger.info(f"Created task '{task_name}' assigned to agent '{agent_name}' with priority {priority}.")
        self.tasks.append(task)

    def _create_agent(self, agent_name: str) -> Agent:
        logger.debug(f"Creating agent: {agent_name}")
        try:
            if not self.tool_config['llm'] or not self.tool_config['embedder']:
                logger.error("LLMConfig or EmbedderConfig not properly initialized.")
                raise ValueError("LLMConfig or EmbedderConfig not properly initialized.")

            logger.debug(f"Calling create_agent with agent_name={agent_name}, agent_config={self.agents_config[agent_name]}")
            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.tool_registry
            )
        except Exception as e:
            logger.error(f"Error creating agent '{agent_name}': {e}", exc_info=True)
            raise

    def initialize_crew(self) -> Crew:
        logger.debug("Initializing crew")
        for task_name in self.tasks_config:
            try:
                logger.debug(f"Creating task '{task_name}'")
                self.create_task(task_name)
            except Exception as e:
                logger.error(f"Error creating task '{task_name}': {str(e)}", exc_info=True)

        if not self.agents or not self.tasks:
            logger.error("At least one agent and one task must be successfully created to initialize the crew.")
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        try:
            logger.debug(f"Initializing Crew with {len(self.agents)} agents and {len(self.tasks)} tasks")
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
            logger.info(f"Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"Error initializing Crew: {str(e)}", exc_info=True)
            raise
