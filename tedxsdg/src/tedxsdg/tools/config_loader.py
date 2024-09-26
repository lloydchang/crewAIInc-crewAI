# tools/config_loader.py

import yaml
import logging
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def load_config(config_path: str, config_section: str, schema: Type[T]) -> T:
    """
    Loads a specific section from a YAML configuration file and validates it against a Pydantic schema.
    
    Args:
        config_path (str): Path to the YAML configuration file.
        config_section (str): The section/key to load from the YAML.
        schema (Type[T]): The Pydantic schema to validate the configuration.
    
    Returns:
        T: The validated configuration as a Pydantic model.
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
            # Validate using Pydantic schema
            validated_config = schema(**section)
            logger.debug("Validated '%s' configuration successfully.", config_section)
            return validated_config
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_path)
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file '%s': %s", config_path, e)
        raise
    except ValidationError as ve:
        logger.error("Validation error for section '%s': %s", config_section, ve)
        raise
    except Exception as e:
        logger.error("Unexpected error loading config '%s': %s", config_path, e)
        raise
