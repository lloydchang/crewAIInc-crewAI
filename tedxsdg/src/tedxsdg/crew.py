#!/usr/bin/env python

#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
import sys
from dotenv import load_dotenv
from manager import CrewAIManager

__version__ = "0.2.0"  # Updated version number

# Centralized logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get configuration paths from environment variables or use default paths
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "config/tools.yaml")

def initialize_test_crew():
    '''
    Initialize the test CrewAI instance with hardcoded agents and tasks.
    '''
    logger.debug("Initializing test crew with hardcoded agents and tasks.")
    try:
        # Create Agents and Tasks for test purposes
        agent1 = Agent(
            role='Researcher',
            goal='Gather information',
            backstory='You are an expert researcher with vast knowledge.',
            allow_delegation=False
        )
        agent2 = Agent(
            role='Writer',
            goal='Create content',
            backstory='You are a skilled writer capable of creating engaging content.',
            allow_delegation=False
        )

        task1 = Task(
            description='Research the topic',
            agent=agent1,
            expected_output='Research report summarizing findings on the given topic.'  # Added expected_output
        )
        task2 = Task(
            description='Write an article based on the research',
            agent=agent2,
            expected_output='A written article based on the research findings.'  # Added expected_output
        )

        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            verbose=True
        )

        logger.info("Test crew initialization successful.")
        return crew
    except Exception as e:
        logger.error("Failed to initialize test crew: %s", str(e), exc_info=True)
        return None

def run_crew():
    """
    Run the crew using configuration files for agents, tasks, and tools.
    """
    logger.debug("Starting crew initialization using configuration files.")
    try:
        # Initialize the CrewAIManager with the paths to the config files
        manager = CrewAIManager(
            agents_config_path=AGENTS_CONFIG_PATH,
            tasks_config_path=TASKS_CONFIG_PATH,
            tools_config_path=TOOLS_CONFIG_PATH
        )
        
        # Commented out the test crew initialization
        # crew = initialize_test_crew()

        # Initialize the real crew based on configurations
        crew = manager.initialize_crew()

        # Run the crew
        if hasattr(crew, 'kickoff') and callable(getattr(crew, 'kickoff')):
            logger.debug("Executing crew using 'kickoff' method.")
            kickoff_result = crew.kickoff()
        elif hasattr(crew, 'run') and callable(getattr(crew, 'run')):
            logger.debug("Executing crew using 'run' method.")
            kickoff_result = crew.run()
        else:
            logger.error("No suitable method found to execute the crew.")
            return "Error: No suitable method found to execute the crew."

        logger.info("Crew execution completed successfully.")
        return kickoff_result
    except Exception as e:
        logger.error("An error occurred while running the real crew: %s", str(e), exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = run_crew()
    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")
