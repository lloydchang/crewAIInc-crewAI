#!/usr/bin/env python

# main.py

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

from tedxsdg.crew import run_crew  # Importing run_crew from your crew file

def run():
    """
    This function will be called by the 'crewai run' command.
    """
    run_crew()

if __name__ == "__main__":
    run()
