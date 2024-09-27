# tools/utils.py

"""
Module for utility functions.
"""

import logging
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

def extract_query_string(query_input: Union[str, Dict[str, Any]]) -> str:
    """
    Extracts a query string from input, which can be a string, dictionary, or other objects.
    
    Args:
        query_input (Union[str, Dict[str, Any]]): The input from which to extract the query.
    
    Returns:
        str: The extracted query string, or an empty string if extraction fails.
    """
    try:
        if isinstance(query_input, str):
            extracted = query_input.strip()
            logger.debug("Extracted query from string: %s", extracted)
            return extracted
        if isinstance(query_input, dict):
            extracted = query_input.get('search_query') or query_input.get('query') or query_input.get('q', '')
            if isinstance(extracted, str):
                extracted = extracted.strip()
                logger.debug("Extracted query from dict: %s", extracted)
                return extracted
            else:
                logger.warning("Extracted query is not a string: %s", extracted)
                return ""
        extracted = str(query_input).strip()
        logger.debug("Extracted query from non-str/dict input: %s", extracted)
        return extracted
    except (TypeError, AttributeError) as e:
        logger.error("Error extracting query string: %s", e)
        return ""
