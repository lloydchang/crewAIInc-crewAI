# __init__.py

"""
This module initializes the TEDxSDG package by importing necessary tools
and managers.
"""

from .manager import CrewAIManager

from .tools.tool_registry import (
    load_config,
    ToolRegistry,
    DuckDuckGoSearchTool,
    TEDxSearchTool,
    TEDxSlugTool,
    TEDxTranscriptTool,
    SDGAlignTool,
    SustainabilityImpactTool
)

__all__ = [
    "CrewAIManager",
    "load_config",
    "ToolRegistry",
    "DuckDuckGoSearchTool",
    "TEDxSearchTool",
    "TEDxSlugTool",
    "TEDxTranscriptTool",
    "SDGAlignTool",
    "SustainabilityImpactTool"
]
