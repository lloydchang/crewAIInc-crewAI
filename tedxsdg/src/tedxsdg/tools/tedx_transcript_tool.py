# tools/tedx_transcript_tool.py

import logging
from langchain.tools import StructuredTool
from pydantic import BaseModel
from typing import Union, Dict, Any, Type
from schemas.tedx_transcript_schema import TEDxTranscriptInput
from crewai_tools import WebsiteSearchTool
from schemas.config_schemas import LLMConfig, EmbedderConfig
from .utils import extract_query_string

logger = logging.getLogger(__name__)

class TEDxTranscriptTool(StructuredTool):
    name: str = "tedx_transcript"
    description: str = "Retrieves the transcript of a TEDx talk based on the provided slug."
    args_schema: Type[BaseModel] = TEDxTranscriptInput

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig):
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.website_search_tool = WebsiteSearchTool()

    def _run(self, slug: str) -> str:
        try:
            if not slug:
                logger.error("No slug provided.")
                return "Error: No slug provided."

            logger.debug(f"Retrieving transcript for slug: {slug}")

            # Construct the transcript URL
            transcript_url = f"https://www.ted.com/talks/{slug}/transcript?subtitle=en"
            logger.debug(f"Constructed Transcript URL: {transcript_url}")

            # Use WebsiteSearchTool to fetch the transcript content
            transcript_content = self.website_search_tool.run({"url": transcript_url})

            if not transcript_content:
                logger.error(f"No transcript found at {transcript_url}.")
                return f"Error: No transcript found at {transcript_url}."

            logger.debug(f"Retrieved Transcript Content: {transcript_content[:200]}...")  # Log first 200 chars

            return f"Final Answer: Transcript for '{slug}':\n{transcript_content}"

        except Exception as e:
            logger.error(f"Error retrieving transcript for slug '{slug}': {str(e)}", exc_info=True)
            return f"Error retrieving transcript for slug '{slug}': {str(e)}"
