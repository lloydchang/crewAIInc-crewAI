# main.py

#!/usr/bin/env python

import os
import logging

# Disable the OpenTelemetry SDK by setting the environment variable
os.environ['OTEL_SDK_DISABLED'] = 'true'

# Disable chroma telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Disable embedchain telemetry
os.environ['EMBEDCHAIN_ANONYMOUS_ID'] = 'False'

# Get the logger used by OpenTelemetry (adjust the logger name if necessary)
opentelemetry_logger = logging.getLogger('opentelemetry')

# Set the logging level to ERROR to suppress warnings
opentelemetry_logger.setLevel(logging.ERROR)

# Set verbose logging for litellm via environment variable
os.environ['LITELLM_LOG'] = 'DEBUG'  # Enables verbose mode for litellm

# Importing run_crew from your crew file
from tedxsdg.crew import run_crew

def run():
    try:
        run_crew()
    except Exception as e:
        logging.error("An error occurred while running the crew: %s", e)

if __name__ == "__main__":
    run()
