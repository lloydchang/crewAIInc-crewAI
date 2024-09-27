# manager/agent_factory.py

import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from crewai import Agent, LLM
from tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class CustomAgent(Agent):
    search_query: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Default to an empty dict

    class Config:
        arbitrary_types_allowed = True

def create_agent(
    agent_name: str,
    agent_config: dict,
    tool_registry: ToolRegistry
) -> CustomAgent:
    """
    Creates an agent with the tools and LLM configuration specified in the config file.
    
    Args:
        agent_name (str): The name of the agent.
        agent_config (dict): The configuration dictionary for the agent.
        tool_registry (ToolRegistry): The registry to fetch tools from.
    
    Returns:
        CustomAgent: The created agent instance.
    
    Raises:
        ValueError: If agent creation fails.
    """
    tool_names = agent_config.get("tools", [])
    tools = []
    llms = []  # List to store the LLMs used by the tools

    # Retrieve tools from the tool registry and their respective LLMs
    for tool_name in tool_names:
        try:
            tool = tool_registry.get_tool(tool_name)
            tools.append(tool)
            logger.info("Successfully created tool '%s' for agent '%s'.", tool_name, agent_name)

            # Handle LLM if provided in agent config
            if "llm_config" in agent_config:
                llm_config = agent_config.get("llm_config", {}).get("config", {})
                llm = LLM(
                    model=llm_config.get("model"),
                    temperature=llm_config.get("temperature", 0),
                    base_url=llm_config.get("base_url", "http://localhost:11434"),
                    api_key=llm_config.get("api_key", None)
                )
                llms.append(llm)
        except ValueError as e:
            logger.warning(
                "Tool '%s' could not be created and will be skipped for agent '%s': %s", 
                tool_name, agent_name, str(e)
            )

    # Log a warning if no tools are assigned to the agent
    if not tools:
        logger.warning("No tools available for agent '%s'. The agent will have no tools assigned.", agent_name)

    # Provide default values for optional fields if not present
    required_fields = ["role", "goal", "backstory"]
    for field in required_fields:
        if field not in agent_config:
            agent_config[field] = f"Default {field} for {agent_name}"

    # Ensure search_query is present, defaulting to an empty dict
    agent_config["search_query"] = agent_config.get("search_query", {})

    try:
        # Create the agent with configuration and LLMs
        agent = CustomAgent(
            name=agent_name,
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            allow_delegation=agent_config.get("allow_delegation", True),
            verbose=True,
            tools=tools,
            search_query=agent_config["search_query"],
            llm=llms[0] if llms else None  # Use the first LLM, or None if no LLM was defined
        )
        logger.info(
            "Created agent '%s' with tools: %s",
            agent_name,
            [tool.name for tool in tools]
        )
        return agent
    except Exception as e:
        logger.error(
            "Error creating agent '%s': %s", agent_name, str(e), 
            exc_info=True
        )
        # Attempt to create the agent with minimal required fields
        try:
            agent = CustomAgent(
                name=agent_name,
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                search_query={}
            )
            logger.warning(
                "Created agent '%s' with minimal configuration due to error.", 
                agent_name
            )
            return agent
        except Exception as e2:
            logger.error(
                "Failed to create agent '%s' even with minimal configuration: %s", 
                agent_name, str(e2), 
                exc_info=True
            )
            raise ValueError(f"Failed to create agent '{agent_name}': {str(e2)}") from e2
