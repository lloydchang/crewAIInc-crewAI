# manager/agent_factory.py

import logging
from typing import Optional
from pydantic import ValidationError
from crewai import Agent
from tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class CustomAgent(Agent):
    search_query: Optional[dict] = {}

def create_agent(
    agent_name: str,
    agent_config: dict,
    tool_registry: ToolRegistry
) -> CustomAgent:
    """
    Creates an agent with the tools and configuration specified in the config file.
    
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

    # Retrieve tools from the tool registry
    for tool_name in tool_names:
        try:
            tool = tool_registry.get_tool(tool_name)
            tools.append(tool)
            logger.info("Successfully created tool '%s' for agent '%s'.", tool_name, agent_name)
        except ValueError as e:
            logger.error(
                "Error creating tool '%s' for agent '%s': %s", tool_name, agent_name, str(e), 
                exc_info=True
            )
            logger.warning(
                "Tool '%s' could not be created and will be skipped for agent '%s'.", 
                tool_name, agent_name
            )

    # Log a warning if no tools are assigned to the agent
    if not tools:
        logger.warning("No tools available for agent '%s'. The agent will have no tools assigned.", agent_name)

    # Ensure all required fields are present
    required_fields = ["role", "goal", "backstory"]
    for field in required_fields:
        if field not in agent_config:
            agent_config[field] = f"Default {field} for {agent_name}"

    # Ensure search_query is present
    agent_config["search_query"] = agent_config.get("search_query", {})

    try:
        # Create the agent with configuration
        agent = CustomAgent(
            name=agent_name,
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            allow_delegation=agent_config.get("allow_delegation", True),
            verbose=True,
            tools=tools,
            search_query=agent_config["search_query"]
        )
        logger.info(
            "Created agent '%s' with tools: %s",
            agent_name,
            [tool.name for tool in tools]
        )
        return agent
    except ValidationError as e:
        logger.error(
            "Validation error creating agent '%s': %s", agent_name, str(e), 
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
                "Created agent '%s' with minimal configuration due to validation error.", 
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
    except Exception as e:
        logger.error(
            "Error creating agent '%s': %s", agent_name, str(e), 
            exc_info=True
        )
        raise ValueError(f"Failed to create agent '{agent_name}': {str(e)}") from e