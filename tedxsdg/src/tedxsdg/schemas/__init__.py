"""
schemas/__init__.py

This module initializes the schemas package.
"""

from .duckduckgo_search_schema import DuckDuckGoSearchInput
from .tedx_search_schema import TEDxSearchInput
from .tedx_slug_schema import TEDxSlugInput
from .tedx_transcript_schema import TEDxTranscriptInput
from .sdg_align_schema import SDGAlignInput
from .sustainability_impact_schema import SustainabilityImpactInput
from .config_schemas import ToolConfig, LLMConfig, EmbedderConfig

__all__ = [
    "DuckDuckGoSearchInput",
    "TEDxSearchInput",
    "TEDxSlugInput",
    "TEDxTranscriptInput",
    "SDGAlignInput",
    "SustainabilityImpactInput",
    "ToolConfig",
    "LLMConfig",
    "EmbedderConfig"
]
