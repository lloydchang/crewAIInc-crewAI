# tools/utils.py

import logging
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug("Debug logging is working at the top of the script.")

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
