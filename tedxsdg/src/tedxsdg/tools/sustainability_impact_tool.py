# tools/sustainability_impact_tool.py

"""
Module for SustainabilityImpactTool which assesses the sustainability impact of projects.
"""

import logging
import csv
from typing import Dict, Any
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class SustainabilityImpactToolArgs(BaseModel):
    """Arguments for SustainabilityImpactTool."""
    project: str = Field(default=None, description="The project to assess for sustainability impact")


class SustainabilityImpactTool(BaseModel):
    """Tool for assessing sustainability impact of ideas and projects."""

    _name: str = "sustainability_impact"
    _description: str = "Assesses the potential sustainability impact of ideas and projects."
    _args_schema = SustainabilityImpactToolArgs

    data_path: str = Field(default=None, description="Path to the sustainability impact data CSV")
    assessment_model: str = Field(default=None, description="Model used for assessment")
    impact_data: Dict[str, Any] = Field(default_factory=dict, description="Impact data")

    @validator('data_path')
    def check_data_path(cls, v):
        """Validator to ensure the data path is provided."""
        if v is None:
            raise ValueError("data_path must be provided")
        return v

    @validator('impact_data', pre=True, always=True)
    def load_impact_data(cls, value, values):
        """Loads impact data from a CSV file."""
        data_path = values.get('data_path')
        if not data_path:
            logger.error("data_path must be provided.")
            raise ValueError("data_path must be provided.")

        try:
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                impact_data = {row['key']: row for row in reader if row.get('key')}
            logger.debug(f"Loaded {len(impact_data)} impacts from '{data_path}'.")
            return impact_data
        except FileNotFoundError:
            logger.error(f"File not found: {data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading impact data: {e}", exc_info=True)
            raise

    def run(self, project: str) -> str:
        """Assesses the sustainability impact of the given project."""
        logger.debug("Assessing sustainability impact for project: %s", project)
        impact = self.impact_data.get(project.lower())
        if not impact:
            return f"No sustainability impact data found for project '{project}'."
        return f"Final Answer: Sustainability Impact for '{project}':\n{impact}"

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
