import logging
import sys
from crewai_manager.manager import CrewAIManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  
)
logger = logging.getLogger(__name__)

# Get configuration paths from environment variables
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", "config/model.yaml")

def initialize_crew():
    """
    Initialize and run the crew based on the configurations provided.
    """
    try:
        manager = CrewAIManager(AGENTS_CONFIG_PATH, TASKS_CONFIG_PATH, MODEL_CONFIG_PATH)
        crew = manager.initialize_crew()
        logger.info("Crew initialization successful.")
        return crew
    except Exception as e:
        logger.error(f"Failed to initialize crew: {str(e)}", exc_info=True)
        sys.exit(1)

def run_crew():
    """
    Run the initialized crew and kick off the process.
    """
    crew = initialize_crew()

    try:
        result = crew.kickoff()  # Run the crew
        logger.info("Crew execution completed successfully.")
        return result
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = run_crew()
    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
