# crew.py

import logging
from manager.manager import CrewAIManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting CrewAI initialization.")
        manager = CrewAIManager(
            agents_config_path="config/agents.yaml",
            tasks_config_path="config/tasks.yaml",
            model_config_path="config/model.yaml",
            tools_config_path="config/tools.yaml"
        )
        crew = manager.initialize_crew()
        logger.info("Crew initialized successfully. Starting execution.")
        crew.run()
    except Exception as e:
        logger.error("Failed to initialize or run the crew: %s", e, exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()
