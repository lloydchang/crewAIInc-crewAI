"""
Module for loading configuration files.
"""

import logging
import os
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str, config_type: str) -> dict:
    """
    Load a YAML configuration file.

    Args:
        config_path (str): The path to the configuration file.
        config_type (str): The type of configuration being loaded.

    Returns:
        dict: The loaded configuration.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            if os.stat(config_path).st_size > 0:
                file.seek(0)
                config = yaml.safe_load(file)
                if config is None:
                    config = {}
            else:
                logger.warning(
                    "Configuration file is empty: '%s'.", config_path
                )
                config = {}
            logger.info("Loaded %s configuration from '%s'.",
                        config_type, config_path)
            if not isinstance(config, dict):
                logger.error(
                    "Loaded configuration is not a dictionary: '%s'.",
                    config_path
                )
                raise ValueError(
                    f"Loaded configuration is not a dictionary: "
                    f"'{config_path}'"
                )
            return config
    except FileNotFoundError:
        logger.error("Configuration file not found: '%s'.", config_path)
        raise
    except yaml.YAMLError as yaml_err:
        logger.error("YAML error loading %s configuration from '%s': %s",
                     config_type, config_path, str(yaml_err))
        raise
    except Exception as e:
        logger.error("Error loading %s configuration from '%s': %s",
                     config_type, config_path, str(e))
        raise
