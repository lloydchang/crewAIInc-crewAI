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
            llm_config=self.tool_config['llm'],
            embedder_config=self.tool_config['embedder'],
            tools_config_path=tools_config_path
        )
        logger.debug("[Line 18] Tool registry initialized")

        # Set memory flag
        self.memory = True
        logger.debug("[Line 19] Memory flag set to True")

        # Log LLM use
        logger.debug("[Line 20] Logging LLM usage")
        self._log_llm_use(self.tool_config['llm'])
        logger.debug("[Line 21] LLM usage logged")

    def _validate_config_path(self, config_path: str, config_name: str) -> None:
        logger.debug(f"[Line 22] Validating {config_name} config path: {config_path}")
        if not os.path.exists(config_path):
            logger.error(f"[Line 23] {config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")
        logger.debug(f"[Line 24] {config_name} config path validation successful")

    def _log_llm_use(self, llm_config: Dict[str, Any]) -> None:
        logger.debug(f"[Line 25] Logging LLM use: {llm_config}")
        if not llm_config or not isinstance(llm_config, dict) or 'model' not in llm_config:
            logger.error("[Line 26] Invalid LLM configuration provided.")
            return

        provider = llm_config.get('provider')
        model = llm_config.get('model')
        temperature = llm_config.get('temperature', 'N/A')
        logger.info(f"[Line 27] Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def _initialize_tool_config(self) -> Dict[str, Any]:
        try:
            logger.debug(f"[Line 28] Model config being passed: {self.model_config}")

            # Log the actual llm and embedder configs
            logger.debug(f"[Line 29] LLM Config: {self.model_config.get('llm')}")
            logger.debug(f"[Line 30] Embedder Config: {self.model_config.get('embedder')}")

            tool_config_data = {
                "llm": self.model_config["llm"],
                "embedder": self.model_config["embedder"]
            }

            logger.debug(f"[Line 31] Tool config data before validation: {tool_config_data}")
            return tool_config_data  # Return the configuration data as a dictionary
        except Exception as e:
            logger.error(f"[Line 34] Unexpected error during ToolConfig initialization: {e}", exc_info=True)
            raise

    def create_task(self, task_name: str) -> None:
        logger.debug(f"[Line 35] Creating task: {task_name}")
        if task_name not in self.tasks_config:
            logger.error(f"[Line 36] Task '{task_name}' not found in tasks configuration.")
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        logger.debug(f"[Line 37] Task config: {task_config}")
        agent_name = task_config.get("agent")

        if agent_name not in self.agents:
            logger.debug(f"[Line 38] Agent '{agent_name}' not found, creating new agent.")
            self.agents[agent_name] = self._create_agent(agent_name)

        agent = self.agents[agent_name]
        logger.debug(f"[Line 39] Agent '{agent_name}' found or created")

        priority = task_config.get("priority", 2)
        logger.debug(f"[Line 40] Task priority: {priority}")

        task = Task(
            description=task_config.get("description", ""),
            agent=agent,
            priority=priority,
            expected_output=task_config.get("expected_output", "No output specified.")
        )
        logger.info(f"[Line 41] Created task '{task_name}' assigned to agent '{agent_name}' with priority {priority}.")
        self.tasks.append(task)
        logger.debug(f"[Line 42] Task '{task_name}' added to tasks list")

    def _create_agent(self, agent_name: str) -> Agent:
        logger.debug(f"[Line 43] Creating agent: {agent_name}")
        try:
            if not self.tool_config['llm'] or not self.tool_config['embedder']:
                logger.error("[Line 44] LLMConfig or EmbedderConfig not properly initialized.")
                raise ValueError("LLMConfig or EmbedderConfig not properly initialized.")

            logger.debug(f"[Line 45] Calling create_agent with agent_name={agent_name}, llm_config={self.tool_config['llm']}, embedder_config={self.tool_config['embedder']}")
            return create_agent(
                agent_name,
                self.agents_config[agent_name],
                self.tool_config['llm'],
                self.tool_config['embedder'],
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
                embedder=self.tool_config['embedder'],  # Pass as dictionary
                max_rpm=None,
                share_crew=False,
                verbose=True,
            )
            logger.info(f"[Line 52] Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"[Line 53] Error initializing Crew: {str(e)}", exc_info=True)
            raise
