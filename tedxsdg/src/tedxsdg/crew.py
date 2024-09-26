# crew.py

#!/usr/bin/env python

import os
import logging
import sys
from crewai_manager.manager import CrewAIManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get configuration paths from environment variables or use default paths
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", "config/model.yaml")
TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "config/tools.yaml")  # Added tools_config_path

def initialize_crew():
    logger.debug("Initializing crew with configurations.")
    """
    Initialize and run the crew based on the configurations provided.
    """
    try:
        manager = CrewAIManager(
            agents_config_path=AGENTS_CONFIG_PATH, 
            tasks_config_path=TASKS_CONFIG_PATH, 
            model_config_path=MODEL_CONFIG_PATH,
            tools_config_path=TOOLS_CONFIG_PATH  # Pass tools_config_path
        )
        crew = manager.initialize_crew()
        logger.info("Crew initialization successful.")
        return crew
    except Exception as e:
        logger.error(f"Failed to initialize crew: {str(e)}", exc_info=True)
        sys.exit(1)
