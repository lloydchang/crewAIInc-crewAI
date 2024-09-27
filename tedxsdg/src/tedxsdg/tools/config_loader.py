# tools/config_loader.py

import yaml
import logging
from typing import Dict, Any, Optional
from crewai import LLM  # Assuming LLM class is imported from crewai

logger = logging.getLogger(__name__)

def load_config(config_path: str, config_section: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a specific section or the entire configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file.
        config_section (Optional[str]): The section/key to load from the YAML. If None, loads the entire configuration.

    Returns:
        Dict[str, Any]: The loaded configuration section or the entire config.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            if not config:
                logger.error("Configuration file '%s' is empty.", config_path)
                raise ValueError(f"Configuration file '{config_path}' is empty.")

            # If a specific section is requested, extract it
            if config_section:
                section = config.get(config_section)
                if section is None:
                    logger.error("Section '%s' not found in configuration file '%s'.", config_section, config_path)
                    raise KeyError(f"Section '{config_section}' not found in configuration file.")
                config = section

            logger.debug("Loaded configuration from '%s': %s", config_path, config)
            return config
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_path)
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file '%s': %s", config_path, e)
        raise
    except Exception as e:
        logger.error("Unexpected error loading config from '%s': %s", config_path, e)
        raise
