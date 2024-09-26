"""
Module for utility functions.
"""

import logging
from typing import Any, Dict, Union

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug logging is working at the top of the script.")


def extract_query_string(query_input: Union[str, Dict[str, Any]]) -> str:
    """Extracts a query string from input (string, dict, or other objects)."""
    try:
        if isinstance(query_input, str):
            return query_input.strip()
        if isinstance(query_input, dict):
            return query_input.get(
                'search_query', query_input.get(
                    'query', query_input.get('q', '')
                )
            ).strip()
        return str(query_input).strip()
    except (TypeError, AttributeError) as e:
        logger.error("Error extracting query string: %s", e)
        return ""
