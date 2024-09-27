#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
import sys
from crew import run_crew, __version__ as crew_version

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Disable the OpenTelemetry SDK by setting the environment variable
os.environ['OTEL_SDK_DISABLED'] = 'true'

# Get the logger used by OpenTelemetry (adjust the logger name if necessary)
opentelemetry_logger = logging.getLogger('opentelemetry')
opentelemetry_logger.setLevel(logging.ERROR)

# Disable Chroma DB telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Disable Embedchain telemetry
os.environ['EMBEDCHAIN_ANONYMOUS_ID'] = 'False'

# Set verbose logging for litellm via environment variable
os.environ['LITELLM_LOG'] = 'DEBUG'  # Enables verbose mode for litellm

def run():
    """
    Run the crew function and handle any exceptions.
    """
    logger.info(f"Starting crew execution. Crew version: {crew_version}")
    try:
        result = run_crew()
        logger.info(f"Crew execution completed. Result: {result}")
    except RuntimeError as e:
        logger.error("A runtime error occurred while running the crew: %s", e, exc_info=True)
    except Exception as e:
        logger.error("An unexpected error occurred while running the crew: %s", e, exc_info=True)
    finally:
        logger.info("Crew execution process finished.")

if __name__ == "__main__":
    run()