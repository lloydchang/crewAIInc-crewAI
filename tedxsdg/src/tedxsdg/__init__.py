"""
This module initializes the TEDxSDG package by importing necessary tools
and managers.
"""

from .crewai_manager import CrewAIManager, load_config
from .tools.tool_registry import (
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
