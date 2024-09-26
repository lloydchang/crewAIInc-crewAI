# tools/sustainability_impact_tool.py

import logging
import csv
from typing import Dict, Any
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class SustainabilityImpactToolArgs(BaseModel):
    """Arguments for SustainabilityImpactTool."""
    project: str = Field(..., description="The project to assess for sustainability impact")


class SustainabilityImpactTool(StructuredTool, BaseModel):
    name: str = "sustainability_impact"
    description: str = "Assesses the potential sustainability impact of ideas and projects."
    args_schema: type[BaseModel] = SustainabilityImpactToolArgs

    # Define required fields
    data_path: str = Field(..., description="Path to the sustainability impact data CSV")
    assessment_model: str = Field(..., description="Model used for assessment")

    # Initialize any additional attributes
    impact_data: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def load_impact_data(cls, model):
        """Loads impact data from a CSV file after model initialization."""
        try:
            with open(model.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    key = row.get('key', '').strip()
                    if key:
                        model.impact_data[key.lower()] = row
            logger.debug(f"Loaded {len(model.impact_data)} impacts from '{model.data_path}'.")
        except FileNotFoundError:
            logger.error(f"File not found: {model.data_path}")
            raise FileNotFoundError(f"File not found: {model.data_path}")
        except Exception as e:
            logger.error(f"Error loading impact data: {e}", exc_info=True)
            raise Exception("Failed to load impact data.") from e
        return model

    def run(self, project: str) -> str:
        """Assesses the sustainability impact of the given project."""
        logger.debug("Assessing sustainability impact for project: %s", project)
        impact = self.impact_data.get(project.lower())
        if not impact:
            return f"No sustainability impact data found for project '{project}'."
        return f"Final Answer: Sustainability Impact for '{project}':\n{impact}"
