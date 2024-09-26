# crewai_manager/__init__.py

"""
This module initializes the crewai_manager package by importing the necessary
components.
"""

# crewai_manager/__init__.py

from .manager import CrewAIManager
from .config_loader import load_config
from .agent_factory import create_agent

__all__ = [
    "CrewAIManager",
    "load_config",
    "create_agent"
]
