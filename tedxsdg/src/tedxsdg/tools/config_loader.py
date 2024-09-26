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
            if not config:
                logger.error("Configuration file '%s' is empty.", config_path)
                raise ValueError(f"Configuration file '{config_path}' is empty.")
            section = config.get(config_section)
            if section is None:
                logger.error("Section '%s' not found in configuration file '%s'.", config_section, config_path)
                raise KeyError(f"Section '{config_section}' not found in configuration file.")
            logger.debug("Loaded '%s' configuration: %s", config_section, section)
            return section
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_path)
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file '%s': %s", config_path, e)
        raise
    except Exception as e:
        logger.error("Unexpected error loading config '%s': %s", config_path, e)
        raise
