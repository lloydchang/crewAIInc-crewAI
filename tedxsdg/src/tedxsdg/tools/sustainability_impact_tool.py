# tools/sustainability_impact_tool.py

import logging
import csv
from typing import Dict
from langchain.tools import StructuredTool
from crewai_manager.config_loader import load_config

logger = logging.getLogger(__name__)

class SustainabilityImpactTool(StructuredTool):
    name: str = "sustainability_impact"
    description: str = "Assesses the potential sustainability impact of ideas and projects."

    def __init__(self, config: dict):
        # Ensure proper initialization with configuration
        super().__init__()
        self.data_path = config.get('data_path')
        if not self.data_path:
            logger.error("No data path provided for SustainabilityImpactTool.")
            raise ValueError("Data path is required for SustainabilityImpactTool.")

        try:
            self.impact_data = self._load_impact_data()
        except Exception as e:
            logger.error(f"Failed to initialize sustainability impact tool: {e}")
            raise

    def _load_impact_data(self):
        """Loads impact data from a CSV file."""
        impact_index = {}
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    key = row.get('key', '').strip()
                    if key:
                        impact_index[key] = row
            logger.debug(f"Loaded {len(impact_index)} impacts from '{self.data_path}'.")
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise FileNotFoundError(f"File not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading impact data: {e}", exc_info=True)
            raise Exception("Failed to load impact data.")
        return impact_index
