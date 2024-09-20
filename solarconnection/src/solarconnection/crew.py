# crew.py

import os
from crewai import Agent, Task, Crew
from crewai.process import Process
from langchain_community.tools import Tool as LangchainTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import embedchain
import yaml
import sys
import traceback

# -----------------------------------------
# Environment Variable Configuration
# -----------------------------------------

# Set verbose logging for litellm via environment variable
os.environ['LITELLM_LOG'] = 'DEBUG'  # Enables verbose mode for litellm

# -----------------------------------------
# Ollama Configuration
# -----------------------------------------

# Configure Ollama to use Llama 3 model
ollama_model = "ollama/llama3"

# Define the Ollama LLM Configuration
ollama_llm_config = {
    "model": ollama_model,  # Use the defined model
    "temperature": 0.7,     # Optional: Customize other parameters like temperature
}

# -----------------------------------------
# Helper Function
# -----------------------------------------

def sanitize_tool_input(input_data):
    if isinstance(input_data, dict):
        return str(input_data.get('tool_input', input_data))
    return str(input_data)

# -----------------------------------------
# Tool Creation Functions
# -----------------------------------------

def create_tool(tool_name: str) -> LangchainTool:
    if tool_name == "web_search":
        search = DuckDuckGoSearchAPIWrapper()
        return LangchainTool(
            name="web_search",
            func=lambda x: search.run(sanitize_tool_input(x)),
            description="Useful for searching the web for current information."
        )
    elif tool_name == "data_analysis":
        return LangchainTool(
            name="data_analysis",
            func=lambda x: f"Analyzing data: {sanitize_tool_input(x)}",
            description="Analyzes data"
        )
    elif tool_name == "web_development":
        return LangchainTool(
            name="web_development",
            func=lambda x: f"Developing web: {sanitize_tool_input(x)}",
            description="Develops web applications"
        )
    elif tool_name == "database_management":
        return LangchainTool(
            name="database_management",
            func=lambda x: f"Managing database: {sanitize_tool_input(x)}",
            description="Manages databases"
        )
    elif tool_name == "task_management":
        return LangchainTool(
            name="task_management",
            func=lambda x: f"Managing tasks: {sanitize_tool_input(x)}",
            description="Manages tasks"
        )
    elif tool_name == "communication":
        return LangchainTool(
            name="communication",
            func=lambda x: f"Communicating: {sanitize_tool_input(x)}",
            description="Handles communication"
        )
    elif tool_name == "financial_modeling":
        return LangchainTool(
            name="financial_modeling",
            func=lambda x: f"Modeling finances: {sanitize_tool_input(x)}",
            description="Creates financial models"
        )
    elif tool_name == "cost_benefit_analysis":
        return LangchainTool(
            name="cost_benefit_analysis",
            func=lambda x: f"Analyzing cost-benefit: {sanitize_tool_input(x)}",
            description="Performs cost-benefit analysis"
        )
    else:
        return LangchainTool(
            name=tool_name,
            func=lambda x: f"Generic tool: {sanitize_tool_input(x)}",
            description=f"Generic tool for {tool_name}"
        )

# -----------------------------------------
# CrewAIManager Class Definition
# -----------------------------------------

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str):
        """
        Initializes the CrewAIManager by loading agent and task configurations.

        Args:
            agents_config_path (str): Path to the agents YAML configuration file.
            tasks_config_path (str): Path to the tasks YAML configuration file.
        """
        # Load the YAML files for agents and tasks
        try:
            with open(agents_config_path, 'r') as file:
                self.agents_config = yaml.safe_load(file)
                print(f"Loaded agents configuration from '{agents_config_path}'.")
        except Exception as e:
            print(f"Error loading agents configuration: {str(e)}")
            sys.exit(1)

        try:
            with open(tasks_config_path, 'r') as file:
                self.tasks_config = yaml.safe_load(file)
                print(f"Loaded tasks configuration from '{tasks_config_path}'.")
        except Exception as e:
            print(f"Error loading tasks configuration: {str(e)}")
            sys.exit(1)

        self.agents = {}  # Dictionary to store created agents
        self.tasks = []   # List to store created tasks

    def create_agent(self, agent_name: str) -> Agent:
        """
        Creates an Agent instance based on the configuration.

        Args:
            agent_name (str): The unique identifier for the agent.

        Returns:
            Agent: An instance of the Agent class or None if creation fails.
        """
        if agent_name not in self.agents_config:
            print(f"Agent '{agent_name}' not found in agents configuration.")
            return None

        agent_config = self.agents_config[agent_name]

        # Retrieve tools if available and convert to Tool objects
        tool_names = agent_config.get("tools", [])
        tools = [create_tool(tool_name) for tool_name in tool_names]

        # Create the agent using the Ollama model
        try:
            agent = Agent(
                name=agent_name,
                role=agent_config.get("role"),
                goal=agent_config.get("goal"),
                backstory=agent_config.get("backstory"),
                allow_delegation=agent_config.get("allow_delegation", False),
                verbose=True,
                llm=ollama_model,
                tools=tools
            )
            print(f"Created agent '{agent_name}' with tools: {[tool.name for tool in tools]}")
            self.agents[agent_name] = agent  # Store agent in dictionary
            return agent
        except Exception as e:
            print(f"Error creating agent '{agent_name}': {str(e)}")
            print("Detailed error information:")
            traceback.print_exc()
            return None

    def create_task(self, task_name: str) -> Task:
        """
        Creates a Task instance based on the configuration.

        Args:
            task_name (str): The unique identifier for the task.

        Returns:
            Task: An instance of the Task class or None if creation fails.
        """
        if task_name not in self.tasks_config:
            print(f"Task '{task_name}' not found in tasks configuration.")
            return None

        task_config = self.tasks_config[task_name]
        agent_identifier = task_config.get("agent")

        if agent_identifier not in self.agents:
            agent = self.create_agent(agent_identifier)
            if agent is None:
                print(f"Failed to create agent '{agent_identifier}' for task '{task_name}'")
                return None
        else:
            agent = self.agents[agent_identifier]

        # Retrieve and process priority
        priority = task_config.get("priority", 2)  # Default to 2 (medium) if not specified
        if isinstance(priority, str):
            priority_mapping = {
                "high": 1,
                "medium": 2,
                "low": 3
            }
            priority = priority_mapping.get(priority.lower(), 2)  # Default to 2 (medium) if unknown string
        elif isinstance(priority, (int, float)):
            priority = max(0, int(priority))  # Ensure priority is a non-negative integer
        else:
            print(f"Warning: Invalid priority type for task '{task_name}'. Using default priority 2.")
            priority = 2

        # Create the task with the agent and expected output
        try:
            task = Task(
                description=str(task_config.get("description", "")),  # Convert to string
                agent=agent,
                priority=priority,
                expected_output=str(task_config.get("expected_output", "No output specified."))
            )
            print(f"Created task '{task_name}' assigned to agent '{agent_identifier}' with priority {priority}.")
            return task
        except Exception as e:
            print(f"Error creating task '{task_name}': {str(e)}")
            traceback.print_exc()
            return None

    def initialize_crew(self) -> Crew:
        """
        Initializes the Crew with all agents and tasks.

        Returns:
            Crew: An instance of the Crew class ready to execute tasks.
        """
        # Initialize tasks (agents will be created as needed)
        for task_name in self.tasks_config.keys():
            task = self.create_task(task_name)
            if task:
                self.tasks.append(task)

        # Ensure we have at least one agent and one task
        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        print("embedchain version:", embedchain.__version__)

        # Create the crew with sequential processing
        try:
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=True,
                embedder=dict(
                    provider="ollama",
                    config=dict(
                        model="nomic-embed-text",
                    ),
                ),
                manager_llm=ollama_llm_config,  # Use the LLM configuration dictionary
                max_rpm=100,
                share_crew=False,  # Disable telemetry
                verbose=True
            )
            print("Initialized the crew with all agents and tasks for concurrent execution.")
            return crew
        except Exception as e:
            print(f"Error initializing Crew: {str(e)}")
            traceback.print_exc()
            raise

# -----------------------------------------
# Run Crew Function Definition
# -----------------------------------------

def run_crew():
    """
    Initializes and runs the CrewAI process.

    Returns:
        Any: The result of the crew's kickoff process or an error message.
    """
    # Define paths to configuration files
    agents_config_path = 'config/agents.yaml'
    tasks_config_path = 'config/tasks.yaml'

    try:
        # Initialize the manager with config paths
        manager = CrewAIManager(agents_config_path, tasks_config_path)

        # Initialize the crew with configurations
        crew = manager.initialize_crew()

        # Kick off the crew and execute tasks
        print("Kicking off the crew...")
        result = crew.kickoff()
        print("Crew execution completed.")
        return result
    except Exception as e:
        error_message = f"An error occurred while running the crew: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return f"Error: {error_message}"

# -----------------------------------------
# Main Execution Block
# -----------------------------------------

if __name__ == "__main__":
    # Run the crew and capture the result
    result = run_crew()

    # Print the result
    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
