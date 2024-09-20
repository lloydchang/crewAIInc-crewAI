#!/usr/bin/env python

# main.py

import os
from solarconnection.crew import run_crew

def main():
    result = run_crew()
    print(result)

def run():
    # This will call the run_crew function from crew.py to start the crew
    result = run_crew()
    if result:
        print(result)

# Ensure that this is the entry point when running crewai run
if __name__ == "__main__":
    run()
