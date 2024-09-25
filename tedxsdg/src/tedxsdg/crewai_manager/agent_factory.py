# crewai_manager/agent_factory.py

import logging
from crewai import Agent
from langchain.agents import AgentOutputParser
from tools.tool_registry import ToolRegistry
from schemas.config_schemas import LLMConfig, EmbedderConfig
from typing import Any, Dict, List, Optional, Type, Union

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

class CustomAgentOutputParser(AgentOutputParser):
    def parse(self, output: Any) -> dict:
        if isinstance(output, str):
            return {"final_output": output}
        elif isinstance(output, dict):
            return {
                "tool": output.get('tool'),
                "tool_input": output.get('tool_input')
            }
        else:
            raise ValueError("Invalid output format")

def create_agent(
    agent_name: str,
    agent_config: dict,
    llm_config: LLMConfig,
    embedder_config: EmbedderConfig,
    tool_registry: ToolRegistry
) -> Agent:
    """Creates an agent with the tools and configuration specified in the configuration file."""
    tool_names = agent_config.get("tools", [])
    tools = []

    # Validate LLM Configuration
    model = llm_config.config.model if llm_config and llm_config.config else None
    if not model:
        logger.error("LLMConfig does not contain a valid model.")
        raise ValueError("LLMConfig must have a valid model.")

    for tool_name in tool_names:
        try:
            logger.debug(f"Creating tool '{tool_name}'.")
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
            llm=model,
            tools=tools,
            output_parser=CustomAgentOutputParser(),
            instructions=(
                f"You have access to the following tools: {', '.join([tool.name for tool in tools])}.\n"
                "Use these tools to complete your tasks. You can provide either a string or a dictionary as input.\n"
                "For example:\n"
                '- String input: "search query"\n'
                '- Dictionary input: {"query": "search query", "additional_info": "extra details"}\n'
                "Important:\n\n"
                "- Always choose an action from the available tools when you need to perform a task.\n"
                "- Do not output 'Action: N/A', 'Action: None' or any action that is not listed in the available tools.\n"
                "- If you need to think or reason internally, use 'Thought:' followed by your reasoning.\n\n"
                "When you have a final answer or conclusion, use the 'Final Answer:' prefix to submit it."
            )
        )
        logger.info(f"Created agent '{agent_name}' with tools: {[tool.name for tool in tools]}")
        return agent
    except Exception as e:
        logger.error(f"Error creating agent '{agent_name}': {str(e)}", exc_info=True)
        raise
