# tools/tedx_transcript_tool.py

"""
Module for TEDxTranscriptTool which retrieves the transcript of a TEDx talk.
"""

import logging
import csv
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class TEDxTranscriptToolArgs(BaseModel):
    """Arguments for TEDxTranscriptTool."""
    slug: str = Field(..., description="The slug of the TEDx talk to retrieve the transcript for.")


class TEDxTranscriptTool(BaseModel):
    """
    Tool to retrieve the transcript of a TEDx talk based on the provided slug.
    """
    
    _name: str = "tedx_transcript"
    _description: str = "Retrieves the transcript of a TEDx talk based on the provided slug."
    _args_schema = TEDxTranscriptToolArgs

    data_path: str = Field(..., description="Path to the TEDx dataset CSV")
    csv_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Loaded CSV data")

    @validator('csv_data', pre=True, always=True)
    def load_csv_data(cls, v, values):
        data_path = values.get('data_path')
        if not data_path:
            raise ValueError("`data_path` must be provided in the configuration.")
        logger.info("Loading TEDxTranscriptTool with data_path: %s", data_path)
        try:
            transcript_index = {}
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip().lower()
                    transcript = row.get('transcript', '').strip()
                    if slug:
                        transcript_index[slug] = row
            logger.debug("Loaded %d entries from CSV file.", len(transcript_index))
            return transcript_index
        except FileNotFoundError as exc:
            logger.error("File not found: %s", data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {data_path}") from exc
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise Exception("Failed to load CSV data.") from e

    def run(self, slug: str) -> str:
        """
        Retrieve transcript for the given slug.

        Args:
            slug (str): The TEDx talk slug.

        Returns:
            str: The transcript for the TEDx talk.
        """
        logger.debug("Running TEDxTranscriptTool for slug: %s", slug)
        slug_lower = slug.lower()

        if slug_lower not in self.csv_data:
            return f"No transcript found for slug '{slug}'. Please ensure the slug is correct."

        entry = self.csv_data[slug_lower]
        transcript = entry.get('transcript', 'No transcript available.')

        formatted_result = (
            f"Title: {entry.get('title', 'No Title')}\n"
            f"Transcript: {transcript}"
        )
        
        logger.debug("Result for slug '%s': %s", slug, formatted_result)
        return f"Final Answer: Transcript for TEDx talk '{slug}':\n{formatted_result}"

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
