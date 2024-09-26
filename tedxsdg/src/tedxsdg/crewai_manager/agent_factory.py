"""
Module for creating agents with specified tools and configurations.
"""

import logging
from crewai import Agent
from tedxsdg.crewai_manager.tools.tool_registry import ToolRegistry

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_agent(
    agent_name: str,
    agent_config: dict,
    tool_registry: ToolRegistry
) -> Agent:
    """Creates an agent with the tools and configuration specified in the 
    config file."""
    tool_names = agent_config.get("tools", [])
    tools = []

    for tool_name in tool_names:
        try:
            tool = tool_registry.get_tool(tool_name)
            tools.append(tool)
            logger.info("Successfully created tool '%s'.", tool_name)
        except KeyError as e:
            logger.error(
                "Error creating tool '%s': %s", tool_name, str(e), 
                exc_info=True
            )
            logger.warning(
                "Tool '%s' could not be created and will be skipped.", 
                tool_name
            )

    try:
        agent = Agent(
            name=agent_name,
            role=agent_config.get("role"),
            goal=agent_config.get("goal"),
            backstory=agent_config.get("backstory"),
            allow_delegation=agent_config.get("allow_delegation", True),
            verbose=True,
            tools=tools
        )
        logger.info(
            "Created agent '%s' with tools: %s",
            agent_name,
            [tool.name for tool in tools]
        )
        return agent
    except ValueError as e:
        logger.error(
            "Error creating agent '%s': %s", agent_name, str(e), 
            exc_info=True
        )
        raise
