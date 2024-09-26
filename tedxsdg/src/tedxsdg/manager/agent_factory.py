# manager/agent_factory.py

"""
Module for creating agents with specified tools and configurations.
"""

import logging
from crewai import Agent
from tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


def create_agent(
    agent_name: str,
    agent_config: dict,
    tool_registry: ToolRegistry
) -> Agent:
    """
    Creates an agent with the tools and configuration specified in the config file.
    
    Args:
        agent_name (str): The name of the agent.
        agent_config (dict): The configuration dictionary for the agent.
        tool_registry (ToolRegistry): The registry to fetch tools from.
    
    Returns:
        Agent: The created agent instance.
    
    Raises:
        ValueError: If agent creation fails.
    """
    tool_names = agent_config.get("tools", [])
    tools = []

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

    if not tools:
        logger.warning("No tools available for agent '%s'. The agent will have no tools assigned.", agent_name)

    try:
        agent = Agent(
            _name=agent_name,
            role=agent_config.get("role"),
            goal=agent_config.get("goal"),
            backstory=agent_config.get("backstory"),
            allow_delegation=agent_config.get("allow_delegation", True),
            verbose=True,
            tools=tools,
            search_query=agent_config.get("search_query", {}),  # Ensure search_query is added
            type=agent_config.get("type")  # Ensure type is included
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
        raise ValueError(f"Failed to create agent '{agent_name}': {str(e)}") from e
