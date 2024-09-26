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

    def _calculate_sdg_score(self, impact_details: Dict[str, str], relevant_metrics: list) -> float:
        """Calculates the sustainability impact score based on relevant metrics."""
        try:
            score_weight = float(impact_details.get('score_weight', 0))
            score = score_weight * len(relevant_metrics)
            return score
        except Exception as e:
            logger.error(f"Error calculating score for impact '{impact_details.get('name')}': {e}", exc_info=True)
            return 0.0

    def _analyze(self, project: str, metrics: list) -> Dict[str, float]:
        """Analyzes the sustainability impact of a project based on selected metrics."""
        results = {}
        for impact_key, impact_details in self.impact_data.items():
            relevant_metrics = [metric for metric in metrics if metric in impact_details.get('metrics', '').split(';')]
            score = self._calculate_sdg_score(impact_details, relevant_metrics)
            if score > 0:
                results[impact_details['name']] = score

        return results

    def _run(self, project: str, metrics: list = []) -> str:
        """Executes the sustainability impact analysis."""
        if not project:
            logger.error("No valid project provided for sustainability impact analysis.")
            return "Error: No valid project provided for sustainability impact analysis."

        metrics = [metric.strip() for metric in metrics if metric]
        logger.debug(f"Running sustainability impact analysis for project: '{project}'")

        impact_results = self._analyze(project, metrics)
        if not impact_results:
            return "No relevant sustainability impacts found."

        formatted_results = "\n".join([f"{impact}: {score}" for impact, score in impact_results.items()])
        return f"Final Answer:\n{formatted_results}"
