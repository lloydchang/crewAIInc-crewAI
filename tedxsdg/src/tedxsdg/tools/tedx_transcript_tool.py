"""
Module for TEDxTranscriptTool which retrieves the transcript of a TEDx talk.
"""

import logging
from typing import Any, Dict, Optional
from langchain.tools import StructuredTool
from crewai_tools import WebsiteSearchTool

logger = logging.getLogger(__name__)


class TEDxTranscriptTool(StructuredTool):
    """
    Tool to retrieve the transcript of a TEDx talk based on the provided slug.
    """
    name: str = "tedx_transcript"
    description: str = (
        "Retrieves the transcript of a TEDx talk based on the provided slug."
    )

    def __init__(
        self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any]
        data_path: Optional[str] = None
    ):
        if not llm_config or not embedder_config:
            raise ValueError(
                "Missing LLM configuration or Embedder configuration."
            )
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = (
            data_path or 
            'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
        )
        self.website_search_tool = WebsiteSearchTool()
    def _run(self, slug: str, *args: Any, **kwargs: Any) -> str:
    def _run(self, slug: str) -> str:
        try:
            if not slug:
                logger.error("No slug provided.")
                return "Error: No slug provided."

            logger.debug("Retrieving transcript for slug: %s", slug)

            # Construct the transcript URL
            transcript_url = (
                f"https://www.ted.com/talks/{slug}/transcript?subtitle=en"
            )
            logger.debug("Constructed Transcript URL: %s", transcript_url)

            # Use WebsiteSearchTool to fetch the transcript content
            transcript_content = self.website_search_tool.run(
                {"url": transcript_url}
            )

            if not transcript_content:
                logger.error("No transcript found at %s.", transcript_url)
                return f"Error: No transcript found at {transcript_url}."

            logger.debug(
                "Retrieved Transcript Content: %s...", transcript_content[:200]
            )  # Log first 200 chars

            return (
                f"Final Answer: Transcript for '{slug}':\n{transcript_content}"
            )
        except (ValueError, KeyError, TypeError) as e:
        except Exception as e:
                "Error retrieving transcript for slug '%s': %s", slug, str(e)
                "Error retrieving transcript for slug '%s': %s", slug, str(e), 
                exc_info=True
            )
            return f"Error retrieving transcript for slug '{slug}': {str(e)}"
