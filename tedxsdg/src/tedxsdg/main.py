# main.py

#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
from crew import main as run_crew  # Importing 'main' as 'run_crew' from crew.py

# Disable the opentelemetry sdk by setting the environment variable
os.environ['OTEL_SDK_DISABLED'] = 'true'

# Get the logger used by opentelemetry (adjust the logger name if necessary)
opentelemetry_logger = logging.getLogger('opentelemetry')

# Set the logging level to ERROR to suppress warnings
opentelemetry_logger.setLevel(logging.ERROR)

# Disable chroma db telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Disable embedchain telemetry
os.environ['EMBEDCHAIN_ANONYMOUS_ID'] = 'False'

# Set verbose logging for litellm via environment variable
os.environ['LITELLM_LOG'] = 'DEBUG'  # Enables verbose mode for litellm


def run():
    """
    Run the crew function and handle any exceptions.
    """
    try:
        run_crew()
    except RuntimeError as e:
        logging.error("A runtime error occurred while running the crew: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred while running the crew: %s", e)


if __name__ == "__main__":
    run()
