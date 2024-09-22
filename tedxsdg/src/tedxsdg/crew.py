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
import json

# Set the LLaMA 3 model for use with Ollama
ollama_model = "ollama/llama3"

# Helper Functions
def sanitize_tool_input(input_data):
    if isinstance(input_data, dict) and 'tool_input' in input_data:
        return input_data['tool_input']
    return str(input_data)

def load_json_with_extra_data(data):
    try:
        obj, end = json.JSONDecoder().raw_decode(data)
        extra_data = data[end:].strip()
        if extra_data:
            print(f"Extra data found: {extra_data}")
            obj['extra_data'] = extra_data
        return obj
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return {"error": "Invalid JSON"}

# Import Custom Tools
from tools.custom_tool import (
    DuckDuckGoSearchTool, YoutubeVideoSearchTool, SDGAlignmentTool, SustainabilityImpactAssessorTool
)

# Tool Input Schemas
class WebSearchInputSchema(BaseModel):
    query: str = Field(..., description="Search query for DuckDuckGo")

class YoutubeSearchInputSchema(BaseModel):
    query: str = Field(..., description="Search query for YouTube content")
    youtube_video_url: str = Field(None, description="Optional YouTube video URL to target specific video")

class SDGAlignmentInputSchema(BaseModel):
    idea: Union[str, dict] = Field(..., description="The idea to analyze for SDG alignment. Can be either a string or a dictionary.")
    sdgs: List[str] = Field(default_factory=list, description="List of SDGs to consider for the analysis.")

class SustainabilityImpactInputSchema(BaseModel):
    project: str = Field(default="Unnamed Project", description="The project to assess for sustainability impact")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics to consider")

def create_custom_tool(tool_name: str) -> StructuredTool:
    tools = {
        "web_search": DuckDuckGoSearchTool(args_schema=WebSearchInputSchema),
        "youtube_search": YoutubeVideoSearchTool(args_schema=YoutubeSearchInputSchema),
        "sdg_alignment": SDGAlignmentTool(args_schema=SDGAlignmentInputSchema),
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool(args_schema=SustainabilityImpactInputSchema),
    }
    return tools.get(tool_name, None)

class CrewAIManager:
    def __init__(self, agents_config_path: str, tasks_config_path: str):
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

        self.agents = {}
        self.tasks = []

    def create_agent(self, agent_name: str) -> Agent:
        if agent_name not in self.agents_config:
            raise ValueError(f"Agent '{agent_name}' not found in agents configuration.")

        agent_config = self.agents_config[agent_name]
        tool_names = agent_config.get("tools", [])
        tools = [create_custom_tool(tool_name) for tool_name in tool_names]

        try:
            agent = Agent(
                name=agent_name,
                role=agent_config.get("role"),
                goal=agent_config.get("goal"),
                backstory=agent_config.get("backstory"),
                allow_delegation=agent_config.get("allow_delegation", True),
                verbose=True,
                llm=ollama_model,
                llm_config={"temperature": 2.0},
                tools=tools
            )
            print(f"Created agent '{agent_name}' with tools: {[tool.name for tool in tools]}")
            self.agents[agent_name] = agent
            return agent
        except Exception as e:
            print(f"Error creating agent '{agent_name}': {str(e)}")
            traceback.print_exc()
            raise

    def create_task(self, task_name: str) -> Task:
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
            print(f"Created task '{task_name}' assigned to agent '{agent_identifier}' with priority {priority}.")
            return task
        except Exception as e:
            print(f"Error creating task '{task_name}': {str(e)}")
            traceback.print_exc()
            raise

    def initialize_crew(self) -> Crew:
        for task_name in self.tasks_config.keys():
            try:
                task = self.create_task(task_name)
                self.tasks.append(task)
            except Exception as e:
                print(f"Error creating task '{task_name}': {str(e)}")
                traceback.print_exc()

        if not self.agents or not self.tasks:
            raise ValueError("At least one agent and one task must be successfully created to initialize the crew.")

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
                manager_llm=ollama_model,
                manager_llm_config={"temperature": 2.0},
                max_rpm=100,
                share_crew=False,
                verbose=True,
            )
            print(f"Initialized the crew with all agents and tasks.")
            return crew
        except Exception as e:
            print(f"Error initializing Crew: {str(e)}")
            traceback.print_exc()
            raise

def run_crew():
    agents_config_path = 'config/agents.yaml'
    tasks_config_path = 'config/tasks.yaml'

    manager = CrewAIManager(agents_config_path, tasks_config_path)

    crew = manager.initialize_crew()

    try:
        print("Kicking off the crew...")
        result = crew.kickoff()
        print("Crew execution completed.")
        return result
    except Exception as e:
        print(f"An error occurred while running the crew: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = run_crew()

    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
