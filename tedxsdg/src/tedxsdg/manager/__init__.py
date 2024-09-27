# manager/__init__.py

"""
This module initializes the manager package by importing necessary classes and functions.
"""

from .manager import CrewAIManager
from .agent_factory import create_agent

__all__ = [
    "CrewAIManager",
    "create_agent"
]
