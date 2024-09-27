# manager/manager.py

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

        # Log the loaded tools configuration
        logger.debug("Loaded tools configuration: %s", self.tools_config)

        # Initialize empty agents and tasks
        self.agents: Dict[str, Agent] = {}
        self.tasks: List[Task] = []

        # Initialize tool registry with the path to the YAML configuration file
        logger.debug("Initializing tool registry with config path: %s", tools_config_path)
        self.tool_registry = ToolRegistry(tools_config_path)  # <-- Use the path instead of self.tools_config

        # Log LLM use (Assuming all tools use the same LLM)
        self._log_llm_use()

        # Log Embedder use
        self._log_embedder_use()
