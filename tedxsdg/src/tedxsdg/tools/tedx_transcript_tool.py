# tools/tedx_transcript_tool.py

"""
Module for TEDxTranscriptTool which retrieves the transcript of a TEDx talk.
"""

import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class TEDxTranscriptToolArgs(BaseModel):
    """Arguments for TEDxTranscriptTool."""
    slug: str = Field(..., description="The slug of the TEDx talk to retrieve the transcript for.")


class TEDxTranscriptTool(BaseModel):  # Removed StructuredTool inheritance
    """
    Tool to retrieve the transcript of a TEDx talk based on the provided slug.
    """
    
    # Class-level attributes
    _name: str = "tedx_transcript"
    _description: str = (
        "Retrieves the transcript of a TEDx talk based on the provided slug."
    )
    _args_schema = TEDxTranscriptToolArgs

    # Instance-level attributes
    llm_config: Dict[str, Any]
    embedder_config: Dict[str, Any]
    data_path: Optional[str] = "data/github-mauropelucchi-tedx_dataset-update_2024-details.csv"

    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any], data_path: Optional[str] = None):
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        if data_path:
            self.data_path = data_path
        logger.info("TEDxTranscriptTool initialized")

    def run(self, slug: str) -> str:
        """
        Retrieve data for the given slug.
        """
        if not slug:
            logger.error("No slug provided.")
            return "Error: No slug provided."

        logger.debug("Retrieving transcript for slug: %s", slug)

        # Construct the transcript URL
        transcript_url = f"https://www.ted.com/talks/{slug}/transcript?subtitle=en"
        logger.debug("Constructed Transcript URL: %s", transcript_url)

        # Mock-up for website fetching logic (as the actual fetching tool is not implemented here)
        # Example response or logic to fetch transcript content should go here
        transcript_content = "This is a mocked transcript content for TEDx talk."

        if not transcript_content:
            logger.error("No transcript found at %s.", transcript_url)
            return f"Error: No transcript found at {transcript_url}."

        logger.debug("Retrieved Transcript Content: %s...", transcript_content[:200])  # Log first 200 chars

        return f"Final Answer: Transcript for '{slug}':\n{transcript_content}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
