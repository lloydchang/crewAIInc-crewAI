# tools/sustainability_impact_tool.py

import logging
import csv
from typing import Dict, Any
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class SustainabilityImpactToolArgs(BaseModel):
    """Arguments for SustainabilityImpactTool."""
    project: str = Field(..., description="The project to assess for sustainability impact")

class SustainabilityImpactTool(StructuredTool):
    name: str = "sustainability_impact"
    description: str = "Assesses the potential sustainability impact of ideas and projects."
    args_schema: type[BaseModel] = SustainabilityImpactToolArgs

    # Define required fields
    data_path: str = Field(..., description="Path to the sustainability impact data CSV")
    assessment_model: str = Field(..., description="Model used for assessment")

    # Initialize any additional attributes
    impact_data: Dict[str, Any] = Field(default_factory=dict)

    @validator('impact_data', pre=True, always=True)
    def load_impact_data(cls, value, values):
        """Loads impact data from a CSV file after model initialization."""
        data_path = values.get('data_path')
        if not data_path:
            logger.error("data_path must be provided.")
            raise ValueError("data_path must be provided.")

        try:
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                impact_data = {}
                for row in reader:
                    key = row.get('key', '').strip()
                    if key:
                        impact_data[key.lower()] = row
            logger.debug(f"Loaded {len(impact_data)} impacts from '{data_path}'.")
            return impact_data
        except FileNotFoundError:
            logger.error(f"File not found: {data_path}")
            raise FileNotFoundError(f"File not found: {data_path}")
        except Exception as e:
            logger.error(f"Error loading impact data: {e}", exc_info=True)
            raise Exception("Failed to load impact data.") from e

    def run(self, project: str) -> str:
        """Assesses the sustainability impact of the given project."""
        logger.debug("Assessing sustainability impact for project: %s", project)
        impact = self.impact_data.get(project.lower())
        if not impact:
            return f"No sustainability impact data found for project '{project}'."
        return f"Final Answer: Sustainability Impact for '{project}':\n{impact}"

    class Config:
        arbitrary_types_allowed = True
