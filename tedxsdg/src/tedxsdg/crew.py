#!/usr/bin/env python

"""
Module for initializing and running the CrewAI.
"""

import os
import logging
import sys
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from crewai_manager.manager import CrewAIManager
except ImportError as e:
    logger.error("Failed to import CrewAIManager: %s", str(e), exc_info=True)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get configuration paths from environment variables or use default paths
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", "config/model.yaml")
TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "config/tools.yaml")


def initialize_crew():
    """
    Initialize and run the crew based on the configurations provided.
    """
    logger.debug("Initializing crew with configurations.")
    try:
        manager = CrewAIManager(
            agents_config_path=AGENTS_CONFIG_PATH,
            tasks_config_path=TASKS_CONFIG_PATH,
            model_config_path=MODEL_CONFIG_PATH,
            tools_config_path=TOOLS_CONFIG_PATH
        )
        logger.info("Crew initialization successful.")
        
        # List available methods
        methods = [method for method in dir(manager) 
                   if callable(getattr(manager, method)) and not method.startswith("__")]
        logger.debug(f"Available methods in CrewAIManager: {methods}")
        
        return manager
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error("Failed to initialize crew: %s", str(e), exc_info=True)
    except Exception as e:
        logger.error("Failed to initialize crew: %s", str(e), exc_info=True)
        sys.exit(1)


def run_crew():
    """
    Run the initialized crew and kick off the process.
    """
    try:
        crew = initialize_crew()
        kickoff_result = crew.run()  # Use the correct method name identified earlier
        logger.info("Crew execution completed successfully.")
        return kickoff_result
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error("An error occurred while running the crew: %s", str(e), exc_info=True)
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error("An error occurred while running the crew: %s", str(e), exc_info=True)
        return f"Error: {str(e)}"


if __name__ == "__main__":
    result = run_crew()
    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
