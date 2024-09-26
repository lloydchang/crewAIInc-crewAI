# main.py

#!/usr/bin/env python

import os
import logging

# Disable the OpenTelemetry SDK by setting the environment variable
os.environ['OTEL_SDK_DISABLED'] = 'true'

# Get the logger used by OpenTelemetry (adjust the logger name if necessary)
opentelemetry_logger = logging.getLogger('opentelemetry')

# Set the logging level to ERROR to suppress warnings
opentelemetry_logger.setLevel(logging.ERROR)

# Importing run_crew from your crew file
from crew import run_crew

def run():
    try:
        run_crew()
    except Exception as e:
        logging.error("An error occurred while running the crew: %s", e)

if __name__ == "__main__":
    run()
