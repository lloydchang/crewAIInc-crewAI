# tools/tedx_slug_tool.py

import logging
import csv
import io
from typing import Optional, Dict, Union, Any, Type
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from schemas.tedx_slug_schema import TEDxSlugInput
from schemas.config_schemas import LLMConfig, EmbedderConfig
from .tedx_search_tool import TEDxSearchTool
from .utils import extract_query_string

logger = logging.getLogger(__name__)

# logging.getLogger().setLevel(logging.DEBUG)

logger.debug("Debug logging is working at the top of the script.")

class TEDxSlugTool(StructuredTool):
    name: str = "tedx_slug"
    description: str = "Retrieves TEDx content details based on a provided slug."
    args_schema: Type[BaseModel] = TEDxSlugInput

    llm_config: LLMConfig = Field(exclude=True)
    embedder_config: EmbedderConfig = Field(exclude=True)
    data_path: str = Field(default='data/github-mauropelucchi-tedx_dataset-update_2024-details.csv', description="Path to the TEDx data CSV.")

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: str = 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'):
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path
        self.tedx_search_tool = TEDxSearchTool(llm_config=llm_config, embedder_config=embedder_config, data_path=data_path)

    def _run(self, slug: str) -> str:
        try:
            if not slug:
                logger.error("No slug provided.")
                return "Error: No slug provided."

            logger.debug(f"Retrieving data for slug: {slug}")
            row = self.tedx_search_tool._find_row_by_slug(slug)
            if not row:
                logger.warning(f"No data found for slug: '{slug}'")
                return f"No data found for slug: '{slug}'. Please ensure the slug is correct."

            # Prepare CSV output
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=row.keys())
            writer.writeheader()
            writer.writerow(row)

            csv_output = output.getvalue()
            output.close()

            logger.debug(f"Formatted CSV output for slug '{slug}':\n{csv_output}")

            return f"Final Answer: CSV Data for slug '{slug}':\n{csv_output}"

        except Exception as e:
            logger.error(f"Error retrieving data for slug '{slug}': {str(e)}", exc_info=True)
            return f"Error retrieving data for slug '{slug}': {str(e)}"
