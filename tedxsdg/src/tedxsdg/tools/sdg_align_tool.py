# tools/sdg_align_tool.py

import logging
from typing import Any, Dict, List, Type, Union
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from schemas.sdg_align_schema import SDGAlignInput
from schemas.config_schemas import LLMConfig, EmbedderConfig

logger = logging.getLogger(__name__)

class SDGAlignTool(StructuredTool):
    name: str = "sdg_align"
    description: str = "Analyzes ideas and aligns them with UN SDGs."
    args_schema: Type[BaseModel] = SDGAlignInput

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: Optional[str] = 'data/sdg_data.csv'):
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path

        try:
            self.sdg_data = self._load_sdg_data()
        except Exception as e:
            logger.error(f"Failed to initialize SDG Align tool: {e}")
            raise

    def _load_sdg_data(self) -> Dict[str, Any]:
        """Loads SDG-related data from a CSV file."""
        sdg_index = {}
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    sdg_id = row.get('sdg_id', '').strip()
                    if sdg_id:
                        sdg_index[sdg_id] = row
            logger.debug(f"Loaded {len(sdg_index)} SDGs from '{self.data_path}'.")
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise FileNotFoundError(f"File not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading SDG data: {e}", exc_info=True)
            raise Exception("Failed to load SDG data.")
        return sdg_index

    def _analyze(self, idea: str, sdgs: List[str]) -> Dict[str, float]:
        """Analyzes the SDG alignment of an idea based on selected SDGs."""
        results = {}
        for sdg_id, sdg_details in self.sdg_data.items():
            if sdgs and sdg_id not in sdgs:
                continue

            relevant_metrics = sdg_details.get('metrics', '').split(';')
            score = self._calculate_sdg_score(sdg_details, relevant_metrics)
            if score > 0:
                results[sdg_details['sdg_name']] = score

        return results

    def _calculate_sdg_score(self, sdg_details: Dict[str, Any], relevant_metrics: List[str]) -> float:
        """Calculates the SDG alignment score based on relevant metrics."""
        try:
            score_weight = float(sdg_details.get('score_weight', 0))
            score = score_weight * len(relevant_metrics)
            return score
        except Exception as e:
            logger.error(f"Error calculating score for SDG '{sdg_details.get('sdg_name')}': {e}", exc_info=True)
            return 0.0

    def _run(self, idea: Union[str, Dict[str, Any]], sdgs: List[str] = []) -> str:
        """Executes the SDG alignment analysis."""
        if isinstance(idea, dict):
            idea_str = idea.get('idea', "")
        else:
            idea_str = str(idea)

        if not idea_str:
            logger.error("No valid idea provided for SDG alignment analysis.")
            return "Error: No valid idea provided for SDG alignment analysis."

        sdgs = [str(sdg).strip() for sdg in sdgs if sdg]
        logger.debug(f"Running SDG alignment analysis for idea: '{idea_str}'")

        alignment_results = self._analyze(idea_str, sdgs)
        if not alignment_results:
            return "No relevant SDG alignments found."

        formatted_results = "\n".join([f"{sdg}: {score}" for sdg, score in alignment_results.items()])
        return f"Final Answer:\n{formatted_results}"
