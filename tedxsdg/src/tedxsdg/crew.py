#!/usr/bin/env python

# crew.py

import os
import logging
from crewai import Agent, Task, Crew, Process
from langchain.tools import StructuredTool
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
import yaml
import sys
import traceback
import re
from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field
from tools.custom_tool import create_custom_tool

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define global LLM configurations
llm_model_name = "ollama/llama3"  # Adjust the model name to a valid Ollama model

llm_config = {
    "provider": "ollama",
    "model": llm_model_name,
    "temperature": 2.0,
}

llm_memory = False

embedder_config = {
    "provider": "ollama",
    "config": {
        "model": "nomic-embed-text",
    }
}

class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if the output is a final answer
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )

        # Parse out the action and action input
        regex = r"Action:\s*(.*?)\s*Action Input:\s*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)

        if not match:
            # Check for "thought:" or "Thought:" without an action
            thought_match = re.search(r"(thought|Thought):\s*(.*)", llm_output, re.DOTALL)
            if thought_match:
                # Handle 'thought' as internal reasoning
                return AgentAction(tool="thought", tool_input=thought_match.group(2).strip(), log=llm_output)

            # If no patterns matched, raise an error
            raise ValueError(f"Could not parse LLM output: {llm_output}")

        action = match.group(1).strip()
        action_input = match.group(2).strip()

        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip('"'), log=llm_output)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str):
        # Load agents and tasks configurations
        self.agents_config = self.load_config(agents_config_path, "agents")
        self.tasks_config = self.load_config(tasks_config_path, "tasks")
        self.agents = {}
        self.tasks = []

        self.llm_config = llm_config
        self.memory = llm_memory
        self.embedder = embedder_config

    def load_config(self, config_path: str, config_type: str) -> Dict:
        # Load configuration from YAML files
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded {config_type} configuration from '{config_path}'.")
                return config
        except Exception as e:
            logger.error(f"Error loading {config_type} configuration: {str(e)}")
            sys.exit(1)

    def create_agent(self, agent_name: str) -> Agent:
        # Create an agent based on the configuration
        if agent_name not in self.agents_config:
            raise ValueError(f"Agent '{agent_name}' not found in agents configuration.")

        agent_config = self.agents_config[agent_name]
        tool_names = agent_config.get("tools", [])
        tools = []
        for tool_name in tool_names:
            # Prepare tool configuration
            tool_config = {
                "llm": {
                    "config": self.llm_config
                },
                "embedder": self.embedder,
                "memory": self.memory
            }
            tools.append(create_custom_tool(tool_name, config=tool_config))

        try:
            agent = Agent(
                name=agent_name,
                role=agent_config.get("role"),
                goal=agent_config.get("goal"),
                backstory=agent_config.get("backstory"),
                allow_delegation=agent_config.get("allow_delegation", True),
                verbose=True,
                llm_config=self.llm_config,
                tools=tools,
                output_parser=CustomOutputParser(),
                instructions=f"""You have access to the following tools: {', '.join([tool.name for tool in tools])}.
Use these tools to complete your tasks. You can provide either a string or a dictionary as input.
For example:
- String input: "search query"
- Dictionary input: {{"query": "search query", "additional_info": "extra details"}}
Important:

- Always choose an action from the available tools when you need to perform a task.
- Do not output 'Action: None' or any action that is not listed in the available tools.
- If you need to think or reason internally, use 'Thought:' followed by your reasoning.

When you have a final answer or conclusion, use the 'Final Answer:' prefix to submit it."""
            )
            logger.info(f"Created agent '{agent_name}' with tools: {[tool.name for tool in tools]}")
            self.agents[agent_name] = agent
            return agent
        except Exception as e:
            logger.error(f"Error creating agent '{agent_name}': {str(e)}")
            raise

    def create_task(self, task_name: str) -> Task:
        # Create a task based on the configuration
        if task_name not in self.tasks_config:
            raise ValueError(f"Task '{task_name}' not found in tasks configuration.")

        task_config = self.tasks_config[task_name]
        agent_identifier = task_config.get("agent")

        if agent_identifier not in self.agents:
            self.create_agent(agent_identifier)

        agent = self.agents[agent_identifier]
        priority = task_config.get("priority", 2)

        try:
            task = Task(
                description=str(task_config.get("description", "")),
                agent=agent,
                priority=priority,
                expected_output=str(task_config.get("expected_output", "No output specified."))
            )
            logger.info(f"Created task '{task_name}' assigned to agent '{agent_identifier}' with priority {priority}.")
            return task
        except Exception as e:
            logger.error(f"Error creating task '{task_name}': {str(e)}")
            raise

    def initialize_crew(self) -> Crew:
        # Initialize the crew with agents and tasks
        logger.info("Initializing crew")
        for task_name in self.tasks_config.keys():
            try:
                task = self.create_task(task_name)
                self.tasks.append(task)
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
                embedder=self.embedder,
                manager_llm_config=self.llm_config,
                max_rpm=None,
                share_crew=False,
                verbose=True,
            )
            logger.info(f"Initialized the crew with {len(self.agents)} agents and {len(self.tasks)} tasks.")
            return crew
        except Exception as e:
            logger.error(f"Error initializing Crew: {str(e)}")
            raise

def run_crew() -> Union[str, None]:
    # Main function to run the crew
    agents_config_path = 'config/agents.yaml'
    tasks_config_path = 'config/tasks.yaml'

    manager = CrewAIManager(agents_config_path, tasks_config_path)

    try:
        crew = manager.initialize_crew()
        logger.info("Kicking off the crew...")
        result = crew.kickoff()
        logger.info("Crew execution completed.")
        return result
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = run_crew()

    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
