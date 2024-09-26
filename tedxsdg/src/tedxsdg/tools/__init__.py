# tools/__init__.py

"""
Tool Registry Module

This module imports various tools for searching TEDx content,
aligning with SDGs, and assessing sustainability impacts.
"""

from .tool_registry import ToolRegistry
from .duckduckgo_search_tool import DuckDuckGoSearchTool
from .tedx_search_tool import TEDxSearchTool
from .tedx_slug_tool import TEDxSlugTool
from .tedx_transcript_tool import TEDxTranscriptTool
from .sdg_align_tool import SDGAlignTool
from .sustainability_impact_tool import SustainabilityImpactTool

import logging
logger = logging.getLogger(__name__)
logger.info("Tool registry module loaded successfully.")
