# tools/sustainability_impact_tool.py

"""
Module for SustainabilityImpactTool which evaluates the sustainability impact of a given project.
"""

import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SustainabilityImpactToolArgs(BaseModel):
    """Arguments for SustainabilityImpactTool."""
    project_description: str = Field(default=None, description="Description of the project to evaluate its sustainability impact.")


class SustainabilityImpactTool(BaseModel):
    """Tool for evaluating the sustainability impact of a project."""

    _name: str = "sustainability_impact"
    _description: str = "Evaluates the sustainability impact of a given project."
    _args_schema = SustainabilityImpactToolArgs

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

    def evaluate(self, project_description: str) -> str:
        """Evaluate the sustainability impact of the given project description."""
        logger.debug("Evaluating sustainability impact for project: %s", project_description)

        # Implement the evaluation logic here
        impact_assessment = "High impact"  # Example output

        logger.debug("Impact assessment result: %s", impact_assessment)
        return impact_assessment

    class Config:
        arbitrary_types_allowed = True
