# tools/custom_tool.py

import os
import logging
import requests
from langchain.tools import StructuredTool
from schemas.config_schemas import LLMConfig, EmbedderConfig
from .tool_registry import ToolRegistry
from .duckduckgo_search_tool import DuckDuckGoSearchTool
from .tedx_search_tool import TEDxSearchTool
from .tedx_slug_tool import TEDxSlugTool
from .tedx_transcript_tool import TEDxTranscriptTool
from .sdg_align_tool import SDGAlignTool
from .sustainability_impact_tool import SustainabilityImpactTool

# Set up logging with DEBUG level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Local CSV file location
LOCAL_CSV_FILE = 'github-mauropelucchi-tedx_dataset-update_2024-details.csv'
REMOTE_CSV_URL = 'https://raw.githubusercontent.com/lloydchang/mauropelucchi-tedx_dataset/refs/heads/master/update_2024/details.csv'

# Function to download the CSV file if it doesn't exist
def download_csv_if_not_exists():
    if not os.path.exists(LOCAL_CSV_FILE):
        logger.info(f"Downloading CSV file from {REMOTE_CSV_URL}")
        response = requests.get(REMOTE_CSV_URL)
        if response.status_code == 200:
            with open(LOCAL_CSV_FILE, 'wb') as f:
                f.write(response.content)
            logger.info(f"CSV file saved to {LOCAL_CSV_FILE}")
        else:
            logger.error(f"Failed to download CSV file. Status code: {response.status_code}")
            raise Exception("Failed to download CSV file")

# Ensure CSV file is downloaded and ready to use
download_csv_if_not_exists()

def extract_query_string(query_input: Union[str, Dict[str, Any]]) -> str:
    """Extracts a query string from input (string, dict, or other objects)."""
    try:
        if isinstance(query_input, str):
            return query_input.strip()
        elif isinstance(query_input, dict):
            return query_input.get('search_query', query_input.get('query', query_input.get('q', ''))).strip()
        return str(query_input).strip()
    except Exception as e:
        logger.error(f"Error extracting query string: {e}")
        return ""

def create_custom_tool(tool_name: str, llm_config: LLMConfig, embedder_config: EmbedderConfig) -> StructuredTool:
    logger.info(f"Creating custom tool: {tool_name}")

    try:
        if tool_name == "tedx_search":
            return TEDxSearchTool(llm_config=llm_config, embedder_config=embedder_config)
        elif tool_name == "tedx_slug":
            return TEDxSlugTool(llm_config=llm_config, embedder_config=embedder_config)
        elif tool_name == "tedx_transcript":
            return TEDxTranscriptTool(llm_config=llm_config, embedder_config=embedder_config)
        elif tool_name == "sdg_align":
            return SDGAlignTool(llm_config=llm_config, embedder_config=embedder_config)
        elif tool_name == "sustainability_impact":
            return SustainabilityImpactTool(llm_config=llm_config, embedder_config=embedder_config)
        elif tool_name == "duckduckgo_search":
            return DuckDuckGoSearchTool(llm_config=llm_config, embedder_config=embedder_config)
        else:
            raise ValueError(f"Unknown tool name: {tool_name}")

    except Exception as e:
        logger.error(f"Failed to create tool '{tool_name}': {e}", exc_info=True)
        raise
