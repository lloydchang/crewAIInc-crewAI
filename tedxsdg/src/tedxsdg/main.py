# main.py

#!/usr/bin/env python

# This module sets up the environment and runs the crew.

import os
import logging
from crew import run_crew

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

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
    try:
        run_crew()
    except RuntimeError as e:
        logging.error("A runtime error occurred while running the crew: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred while running the crew: %s", e)


if __name__ == "__main__":
    run()
