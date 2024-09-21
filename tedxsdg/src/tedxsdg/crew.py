#!/usr/bin/env python

# crew.py

import os
from crewai import Agent, Task, Crew, Process
from langchain.tools import StructuredTool
from langchain_community.tools import Tool as LangchainTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import yaml
import sys
import traceback
from typing import Union, List
from pydantic import BaseModel, Field

# -----------------------------------------
# Environment Variable Configuration
# -----------------------------------------

import os
os.environ['OTEL_SDK_DISABLED'] = 'true' # Disable telemetry

# Set verbose logging for litellm via environment variable
os.environ['LITELLM_LOG'] = 'DEBUG'  # Enables verbose mode for litellm

# -----------------------------------------
# Ollama Configuration
# -----------------------------------------

# Configure Ollama to use Llama 3
ollama_model = "ollama/llama3"

# -----------------------------------------
# Helper Function
# -----------------------------------------

def sanitize_tool_input(input_data):
    if isinstance(input_data, dict) and 'tool_input' in input_data:
        return input_data['tool_input']
    return str(input_data)

# -----------------------------------------
# Tool Input Schemas
# -----------------------------------------

class SDGAlignmentInput(BaseModel):
    idea: str = Field(..., description="The idea to analyze for SDG alignment")
    sdgs: List[str] = Field(default_factory=list, description="List of SDGs to consider")

class SustainabilityImpactInput(BaseModel):
    project: str = Field(..., description="The project to assess for sustainability impact")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics to consider")

# -----------------------------------------
# Tool Functions
# -----------------------------------------

def analyze_sdg_alignment(idea: str, sdgs: List[str]) -> str:
    # Implement the SDG alignment analysis logic here
    return f"Analyzing SDG alignment for idea: {idea}\nConsidering SDGs: {', '.join(sdgs)}"

def assess_sustainability_impact(project: str, metrics: List[str]) -> str:
    # Implement the sustainability impact assessment logic here
    return f"Assessing sustainability impact for project: {project}\nConsidering metrics: {', '.join(metrics)}"

# -----------------------------------------
# Tool Creation Functions
# -----------------------------------------

def create_tool(tool_name: str) -> Union[LangchainTool, StructuredTool]:
    if tool_name == "sdg_alignment":
        return StructuredTool.from_function(
            func=analyze_sdg_alignment,
            name="sdg_alignment",
            description="Analyzes the alignment of an idea with Sustainable Development Goals (SDGs)",
            args_schema=SDGAlignmentInput
        )
    elif tool_name == "sustainability_impact_assessor":
        return StructuredTool.from_function(
            func=assess_sustainability_impact,
            name="sustainability_impact_assessor",
            description="Assesses the sustainability impact of a given solution",
            args_schema=SustainabilityImpactInput
        )
    elif tool_name == "web_search":
        search = DuckDuckGoSearchAPIWrapper()
        return LangchainTool(
            name="web_search",
            func=lambda x: search.run(sanitize_tool_input(x)),
            description="Useful for searching the web for current information."
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
            Agent: An instance of the Agent class.
        """
        if agent_name not in self.agents_config:
            raise ValueError(f"Agent '{agent_name}' not found in agents configuration.")

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
            raise

    def create_task(self, task_name: str) -> Task:
        """
        Creates a Task instance based on the configuration.

        Args:
            task_name (str): The unique identifier for the task.

        Returns:
            Task: An instance of the Task class.
        """
        if task_name not in self.tasks_config:
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        agent_identifier = task_config.get("agent")

        if agent_identifier not in self.agents:
            self.create_agent(agent_identifier)

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
            raise

    def initialize_crew(self) -> Crew:
        """
        Initializes the Crew with all agents and tasks.

        Returns:
            Crew: An instance of the Crew class ready to execute tasks.
        """
        # Initialize tasks (agents will be created as needed)
        for task_name in self.tasks_config.keys():
            try:
                task = self.create_task(task_name)
                self.tasks.append(task)
            except Exception as e:
                print(f"Error creating task '{task_name}': {str(e)}")
                traceback.print_exc()

        # Ensure we have at least one agent and one task
        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

        # Create the crew with sequential processing
        try:
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                memory=False,  # Avoids dependency on OpenAI's Memory
                max_rpm=100,
                share_crew=True,
                verbose=True
            )
            print("Initialized the crew with all agents and tasks.")
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
        Any: The result of the crew's kickoff process.
    """
    # Define paths to configuration files
    agents_config_path = 'config/agents.yaml'
    tasks_config_path = 'config/tasks.yaml'

    # Initialize the manager with config paths
    manager = CrewAIManager(agents_config_path, tasks_config_path)

    # Initialize the crew with configurations
    crew = manager.initialize_crew()

    try:
        # Kick off the crew and execute tasks
        print("Kicking off the crew...")
        result = crew.kickoff()
        print("Crew execution completed.")
        return result
    except Exception as e:
        print(f"An error occurred while running the crew: {str(e)}")
        traceback.print_exc()
        return None

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
