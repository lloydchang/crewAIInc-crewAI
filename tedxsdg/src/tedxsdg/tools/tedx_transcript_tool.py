# tools/tedx_transcript_tool.py

"""
Module for TEDxTranscriptTool which retrieves the transcript of a TEDx talk.
"""

import logging

logger = logging.getLogger(__name__)

class TEDxTranscriptTool(BaseModel):
    """Tool for retrieving TEDx talk transcripts."""

    _name: str = "tedx_transcript"
    _description: str = "Retrieves TEDx talk transcripts."
    _args_schema = None  # Define the argument schema if necessary

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Retrieves the transcript of a TEDx talk based on a given talk ID or title.

        Args:
            input (dict): Dictionary containing 'talk_id' or 'title' for TEDx transcript lookup.

        Returns:
            str: The transcript of the TEDx talk.
        """
        talk_id = input.get('talk_id', '')
        title = input.get('title', '')
        logger.debug("Retrieving TEDx transcript for talk_id: %s or title: %s", talk_id, title)

        if not talk_id and not title:
            return "Either 'talk_id' or 'title' must be provided."

        try:
            # Simulate TEDx transcript lookup (replace with actual logic)
            transcript = "This is the transcript of the TEDx talk on sustainability and innovation..."

            logger.debug("Retrieved TEDx transcript: %s", transcript)
            return f"Final Answer: TEDx Transcript:\n{transcript}"
        except Exception as e:
            logger.error("Error retrieving TEDx transcript: %s", e, exc_info=True)
            return "An error occurred while retrieving the TEDx transcript."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    class Config:
        arbitrary_types_allowed = True
