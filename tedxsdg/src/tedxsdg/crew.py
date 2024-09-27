#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
import sys
from dotenv import load_dotenv

__version__ = "0.1.0"  # Add a version number for tracking

# Centralized logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    from crewai import Crew, Agent, Task
    logger.info(f"Successfully imported crewai. Version: {crewai.__version__}")
except ImportError as e:
    logger.error("Failed to import crewai: %s", str(e), exc_info=True)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get configuration paths from environment variables or use default paths
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/agents.yaml")
TASKS_CONFIG_PATH = os.getenv("TASKS_CONFIG_PATH", "config/tasks.yaml")
TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "config/tools.yaml")

def initialize_crew():
    """
    Initialize the CrewAI and return the Crew instance.
    """
    logger.debug("Initializing crew with configurations.")
    try:
        # Here, instead of using CrewAIManager, we'll directly create Agents and Tasks
        # This is a simplified example. Adjust according to your specific needs.
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
            agent=agent1
        )
        task2 = Task(
            description='Write an article based on the research',
            agent=agent2
        )

        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            verbose=True
        )

        logger.info("Crew initialization successful.")
        return crew
    except Exception as e:
        logger.error("Failed to initialize crew: %s", str(e), exc_info=True)
        return None

def run_crew():
    """
    Run the initialized crew and kick off the process.
    """
    try:
        crew = initialize_crew()
        if crew is None:
            logger.error("Crew instance is None. Exiting.")
            return "Error: Crew instance is None."

        logger.debug("Crew instance: %s, Type: %s", crew, type(crew))
        logger.debug("Available methods in Crew: %s", [method for method in dir(crew) if not method.startswith("__")])

        # Attempt to run the crew
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
        logger.error("An error occurred while running the crew: %s", str(e), exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = run_crew()
    print("\n######################")
    print("Crew Execution Result:")
    print(result)
    print("######################")