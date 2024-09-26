# tools/sustainability_impact_tool.py

"""
Module for assessing the potential sustainability impact of ideas and projects.
"""

import logging
import csv
from langchain.tools import StructuredTool

logger = logging.getLogger(__name__)


class SustainabilityImpactTool(StructuredTool):
    """
    Tool to assess the potential sustainability impact of ideas and projects.
    """
    name: str = "sustainability_impact"
    description: str = (
        "Assesses the potential sustainability impact of ideas and projects."
    )

    def __init__(self, config: dict):
        """
        Initialize the tool with the given configuration.
        """
        super().__init__(**config)
        self.data_path = config.get('data_path')
        if not self.data_path:
            logger.error("No data path provided for SustainabilityImpactTool.")
            raise ValueError(
                "Data path is required for SustainabilityImpactTool."
            )

        try:
            self.impact_data = self._load_impact_data()
        except Exception as e:
            logger.error(
                "Failed to initialize sustainability impact tool: %s", e
            )
            raise RuntimeError("Failed to load impact data.") from e

    def _load_impact_data(self):
        """
        Loads impact data from a CSV file.
        """
        impact_index = {}
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    key = row.get('key', '').strip()
                    if key:
                        impact_index[key] = row
            logger.debug(
                "Loaded %d impacts from '%s'.",
                len(impact_index),
                self.data_path
            )
            except FileNotFoundError as e:
                logger.error("File not found: %s", self.data_path, exc_info=True)
                raise FileNotFoundError(f"File not found: {self.data_path}") from e
            except Exception as e:
                logger.error("Error loading impact data: %s", e, exc_info=True)
                raise RuntimeError("Failed to load impact data.") from e
            return impact_index
