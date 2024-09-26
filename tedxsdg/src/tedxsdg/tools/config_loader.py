# tools/config_loader.py

import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(config_path: str, config_section: str) -> Dict[str, Any]:
    """
    Loads a specific section from a YAML configuration file.
    
    Args:
        config_path (str): Path to the YAML configuration file.
        config_section (str): The section/key to load from the YAML.
    
    Returns:
        Dict[str, Any]: The loaded configuration section.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            section = config.get(config_section, {})
            logger.debug("Loaded %s configuration: %s", config_section, section)
            return section
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_path)
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error loading config: %s", e)
        raise
