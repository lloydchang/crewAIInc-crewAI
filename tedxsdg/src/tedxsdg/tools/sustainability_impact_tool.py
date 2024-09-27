# tools/sustainability_impact_tool.py

"""
Module for SustainabilityImpactTool which evaluates the sustainability impact of a given project.
"""

import logging
from pydantic import BaseModel, Field
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SustainabilityImpactToolArgs(BaseModel):
    """Arguments for SustainabilityImpactTool."""
    project_description: str = Field(default=None, description="Description of the project to evaluate its sustainability impact.")


class SustainabilityImpactTool(BaseModel):
    """Tool for evaluating the sustainability impact of a project."""

    _name: str = "sustainability_impact"
    _description: str = "Evaluates the sustainability impact of a given project."
    _args_schema = SustainabilityImpactToolArgs

    def invoke(self, input: Dict[str, Any]) -> str:
        """Evaluate the sustainability impact based on the provided project description."""
        project_description = input.get("project_description")
        if not project_description:
            return "Error: 'project_description' is required in the input."

        logger.debug("Evaluating sustainability impact for project: %s", project_description)

        # Implement the evaluation logic here
        impact_assessment = "High impact"  # Example output

        logger.debug("Impact assessment result: %s", impact_assessment)
        return f"Final Answer: Sustainability impact assessment for the project:\n{impact_assessment}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    @property
    def args(self) -> BaseModel:
        """Return the arguments schema for the tool."""
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
