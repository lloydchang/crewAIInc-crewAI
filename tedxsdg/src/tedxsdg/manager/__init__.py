# manager/__init__.py

from .manager import CrewAIManager
from .agent_factory import create_agent

__all__ = [
    "CrewAIManager",
    "create_agent"
]
