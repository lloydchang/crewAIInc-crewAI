# tools/sustainability_impact_tool.py

import logging
import csv
from typing import Any, Dict, List
from langchain.tools import StructuredTool

logger = logging.getLogger(__name__)

class SustainabilityImpactTool(StructuredTool):
    name: str = "sustainability_impact"
    description: str = "Assesses the potential sustainability impact of ideas and projects."

    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any], data_path: str = 'data/impact_data.csv'):
        # Validate required fields
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")

        super().__init__()  # Call to the parent class initializer
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path

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
                    key = row.get('key', '').strip()  # Replace with your relevant key
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
