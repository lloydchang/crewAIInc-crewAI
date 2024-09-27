#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
import sys
from dotenv import load_dotenv

# Centralized logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to stdout
    ]
)

logger = logging.getLogger(__name__)

try:
    from manager.manager import CrewAIManager
except ImportError as e:
    logger.error("Failed to import CrewAIManager: %s", str(e), exc_info=True)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get configuration paths from environment variables or use default paths
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "config/tools.yaml")


def initialize_crew():
    """
    Initialize the CrewAIManager and return the Crew instance.
    """
    logger.debug("Initializing crew with configurations.")
    try:
        manager = CrewAIManager(
            agents_config_path=AGENTS_CONFIG_PATH,
            tasks_config_path=TASKS_CONFIG_PATH,
            tools_config_path=TOOLS_CONFIG_PATH
        )
        logger.info("Crew initialization successful.")

        # Initialize the crew
        crew = manager.initialize_crew()

        # Safely list available methods on Crew instance
        available_methods = []
        for method in dir(crew):
            if method.startswith("__"):
                continue  # Skip private methods

            try:
                if callable(getattr(crew, method)):
                    available_methods.append(method)
            except Exception as e:
                logger.debug(f"Could not access method '{method}': {e}")

        logger.debug("Available methods in Crew: %s", available_methods)

        return crew
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
        if crew is None:
            logger.error("CrewAIManager instance is None. Exiting.")
            return "Error: CrewAIManager instance is None."

        # Log the crew instance type for debugging
        logger.debug("Crew instance: %s, Type: %s", crew, type(crew))

        # Log all attributes of the crew instance
        all_attributes = dir(crew)
        logger.debug("All attributes of Crew: %s", all_attributes)

        # Check for available callable methods
        available_methods = []
        for method in all_attributes:
            try:
                if callable(getattr(crew, method)) and not method.startswith("__"):
                    available_methods.append(method)
            except AttributeError:
                # Ignore any class-only attributes like __signature__
                continue

        logger.debug("Available methods in Crew: %s", available_methods)

        # Attempt to run the crew
        if 'run' in available_methods:
            logger.debug("Executing crew using 'run' method.")
            kickoff_result = crew.run()
        elif 'execute' in available_methods:
            logger.debug("Executing crew using 'execute' method.")
            kickoff_result = crew.execute()
        else:
            logger.error("No suitable method found to execute the crew.")
            return "Error: No suitable method found to execute the crew."

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
