# crewai_manager/manager.py

import logging
import os
from pydantic import ValidationError
from crewai import Crew, Process, Agent, Task
from crewai_manager.config_loader import load_config
from crewai_manager.agent_factory import create_agent
from schemas.config_schemas import ToolConfig
from tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

# logging.getLogger().setLevel(logging.DEBUG)

logger.debug("Debug logging is working at the top of the script.")

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str, model_config_path: str, tools_config_path: str = "config/tools.yaml"):
        # Ensure config paths are valid
        self.validate_config_path(agents_config_path, "agents")
        self.validate_config_path(tasks_config_path, "tasks")
        self.validate_config_path(model_config_path, "model")
        self.validate_config_path(tools_config_path, "tools")

        # Load configurations for agents, tasks, model, and tools
        self.agents_config = load_config(agents_config_path, "agents")
        self.tasks_config = load_config(tasks_config_path, "tasks")
        self.model_config = load_config(model_config_path, "model")
        self.tools_config = load_config(tools_config_path, "tools")

        self.agents = {}  # To store created agents
        self.tasks = []  # To store created tasks

        # Validate and load the model configuration
        try:
            # Initialize ToolConfig based on the model configuration
            self.tool_config = ToolConfig(**self.model_config)
            self.llm_config = self.tool_config.llm
            self.embedder_config = self.tool_config.embedder
            logger.debug(f"LLM Configuration: {self.llm_config}")
            logger.debug(f"Embedder Configuration: {self.embedder_config}")
            logger.debug(f"ToolConfig successfully initialized: {self.tool_config}")
        except ValidationError as ve:
            logger.error(f"Validation error in model configuration: {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during ToolConfig initialization: {e}", exc_info=True)
            raise

        # Initialize ToolRegistry with tool-specific configurations
        self.tool_registry = ToolRegistry(
            llm_config=self.llm_config, 
            embedder_config=self.embedder_config, 
            tools_config_path=tools_config_path
        )

        # Memory flag assumption
        self.memory = True  # Enable memory by default
        # Log the LLM configuration for debugging purposes
        self.log_llm_use(self.llm_config)

    def validate_config_path(self, config_path: str, config_name: str):
        """
        Validate that a given config path exists.
        Raise an error if the file does not exist.
        """
        if not os.path.exists(config_path):
            logger.error(f"{config_name.capitalize()} config file not found: {config_path}")
            raise FileNotFoundError(f"{config_name.capitalize()} config file not found: {config_path}")

    def log_llm_use(self, llm_config):
        """
        Log the LLM configuration details.
        """
        if not llm_config or not llm_config.config:
            logger.error("Invalid LLM configuration provided.")
            return

        # Log the provider, model, and temperature of the LLM
        provider = llm_config.provider
        model = llm_config.config.model
        temperature = llm_config.config.temperature
        logger.info(f"Using LLM - Provider: {provider}, Model: {model}, Temperature: {temperature}")

    def create_task(self, task_name: str):
        """
        Create a task based on the provided task_name.
        """
        if task_name not in self.tasks_config:
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        agent_name = task_config.get("agent")

        # Check if the agent is already created, if not create one
        if agent_name not in self.agents:
            try:
                # Validate that LLMConfig and EmbedderConfig are initialized before creating the agent
                if not self.llm_config or not self.embedder_config:
                    raise ValueError("LLMConfig or EmbedderConfig not properly initialized.")
                
                # Create the agent using the agent configuration, LLM/Embedder configurations, and ToolRegistry
                self.agents[agent_name] = create_agent(
                    agent_name, 
                    self.agents_config[agent_name], 
                    self.llm_config, 
                    self.embedder_config, 
                    self.tool_registry  # Pass ToolRegistry instance
                )
            except Exception as e:
                logger.error(f"Error creating agent '{agent_name}': {e}", exc_info=True)
                raise

        # Retrieve the created agent and create the task
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

    def initialize_crew(self) -> Crew:
        """
        Initialize the Crew by creating tasks and agents.
        """
        logger.info("Initializing crew")
        for task_name in self.tasks_config:
            try:
                self.create_task(task_name)
            except Exception as e:
                logger.error(f"Error creating task '{task_name}': {str(e)}", exc_info=True)

        # Ensure at least one agent and one task exist before initializing the crew
        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        try:
            # Initialize the Crew with the created agents, tasks, and configurations
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,  # Sequential processing of tasks
                memory=self.memory,
                embedder=self.embedder_config.dict(),  # Embedder configuration used in Crew
                max_rpm=None,  # RPM not limited
                share_crew=False,  # Crew sharing is disabled
                verbose=True,  # Enable verbose logging
            )
            logger.info(f"Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"Error initializing Crew: {str(e)}", exc_info=True)
            raise
