# crewai_manager/agent_factory.py

import logging
from crewai import Agent
from tools.tool_registry import ToolRegistry

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_agent(
    agent_name: str,
    agent_config: dict,
    tool_registry: ToolRegistry
) -> Agent:
    """Creates an agent with the tools and configuration specified in the configuration file."""
    tool_names = agent_config.get("tools", [])
    tools = []

    for tool_name in tool_names:
        try:
            tool = tool_registry.get_tool(tool_name)
            tools.append(tool)
            logger.info(f"Successfully created tool '{tool_name}'.")
        except Exception as e:
            logger.error(f"Error creating tool '{tool_name}': {str(e)}", exc_info=True)
            logger.warning(f"Tool '{tool_name}' could not be created and will be skipped.")

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
        logger.info(f"Created agent '{agent_name}' with tools: {[tool.name for tool in tools]}")
        return agent
    except Exception as e:
        logger.error(f"Error creating agent '{agent_name}': {str(e)}", exc_info=True)
        raise
