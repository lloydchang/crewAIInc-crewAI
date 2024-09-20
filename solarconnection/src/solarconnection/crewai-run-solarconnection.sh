#!/bin/bash -x

cd $(dirname $0)

# Prerequisite steps:
pushd ../../..
python -m venv venv
source venv/bin/activate
pip install 'crewai[tools]'
pip install poetry
pip install ollama
pip install duckduckgo-search
popd

pushd ../..
poetry install
popd

# Disable telemetry https://docs.crewai.com/telemetry/Telemetry/
OTEL_SDK_DISABLED=true

OUTPUT_FILE_PREFIX=$(basename "$0")
OUTPUT_FILE_SYMLINK=$(basename "$0").log
OUTPUT_FILE=$OUTPUT_FILE_PREFIX-$(date +"%Y-%m-%d_%H-%M-%S").log

ln -sfn $OUTPUT_FILE $OUTPUT_FILE_SYMLINK

# Redirect all output (stdout and stderr) to both the terminal and the file
exec > >(tee -a $OUTPUT_FILE) 2>&1

# Enable command echoing for debugging
set -x

export START_DATE=$(date)
echo "Start time: $START_DATE"

echo "Running crewai..."
time crewai run
echo "crewai run completed."

export END_DATE=$(date)
echo "End time: $END_DATE"
