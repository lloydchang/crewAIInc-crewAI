# tools/sdg_align_tool.py

"""
Module for SDGAlignTool which aligns content with Sustainable Development Goals (SDGs).
"""

import logging

logger = logging.getLogger(__name__)

class SDGAlignTool(BaseModel):
    """Tool for aligning ideas with the UN Sustainable Development Goals (SDGs)."""

    _name: str = "sdg_align"
    _description: str = "Aligns ideas or projects with the UN SDGs."
    _args_schema = None  # Define the argument schema if necessary

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Aligns the input idea with SDGs.

        Args:
            input (dict): Dictionary containing 'idea' for SDG alignment.

        Returns:
            str: The SDG alignment results.
        """
        idea = input.get('idea', '')
        logger.debug("Aligning idea with SDGs: %s", idea)

        if not idea:
            return "Idea cannot be empty."

        try:
            # Simulate the SDG alignment process (replace with actual logic)
            aligned_sdgs = ["SDG 3: Good Health and Well-being", "SDG 15: Life on Land"]
            
            logger.debug("Aligned SDGs: %s", aligned_sdgs)
            return f"Final Answer: The idea aligns with the following SDGs: {', '.join(aligned_sdgs)}"
        except Exception as e:
            logger.error("Error aligning idea with SDGs: %s", e, exc_info=True)
            return "An error occurred while aligning the idea with SDGs."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    class Config:
        arbitrary_types_allowed = True
