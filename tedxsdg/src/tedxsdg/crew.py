# crew.py

import os
import logging
import sys
from dotenv import load_dotenv
import inspect

# Centralized logging configuration
logging.basicConfig(
    level=logging.DEBUG,
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
            tools_config_path=TOOLS_CONFIG_PATH  # Corrected here
        )
        logger.info("Crew initialization successful.")

        # Initialize the crew
        crew = manager.initialize_crew()

        # List available methods on Crew instance (if needed)
        methods = inspect.getmembers(crew, predicate=inspect.isfunction)
        method_names = [method[0] for method in methods if not method[0].startswith("__")]
        logger.debug(f"Available methods in Crew: {method_names}")

        return crew
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error("Failed to initialize crew: %s", str(e), exc_info=True)
    except Exception as e:
        logger.error("Failed to initialize crew: %s", str(e), exc_info=True)
        sys.exit(1)
