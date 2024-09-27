# __init__.py

"""
This module initializes the TEDxSDG package by importing necessary tools
and managers.
"""

from .manager import CrewAIManager

from .tools.tool_registry import (
    ToolRegistry,
    TEDxSearchTool,
    TEDxSlugTool,
    TEDxTranscriptTool,
)

__all__ = [
    "CrewAIManager",
    "ToolRegistry",
    "TEDxSearchTool",
    "TEDxSlugTool",
    "TEDxTranscriptTool",
]
