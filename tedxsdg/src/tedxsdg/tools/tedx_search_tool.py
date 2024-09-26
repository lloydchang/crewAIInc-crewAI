# tools/tedx_search_tool.py

import os
import logging
import csv
from typing import Dict
from langchain.tools import StructuredTool
from crewai_manager.config_loader import load_config

logger = logging.getLogger(__name__)

class TEDxSearchTool(StructuredTool):
    name: str = "tedx_search"
    description: str = "Searches TEDx content from the local CSV dataset."

    def __init__(self):
        super().__init__()
        config = load_config('config/tools.yaml', 'tools')
        self.data_path = config['tedx_search']['data_path']

        logger.info("Initializing TEDxSearchTool.")
        
        # Initialize the CSV search tool
        try:
            self.csv_data = self._load_csv_data()
        except Exception as e:
            logger.error(f"Error initializing TEDxSearchTool: {e}", exc_info=True)
            self.csv_search_tool = None
            self._invalidate_cache()
            raise

    def _invalidate_cache(self):
        """Invalidates the cache."""
        logger.info("Invalidating the cache via 'rm -rf db'.")
        try:
            os.system("rm -rf db")
        except Exception as e:
            logger.error(f"Error during cache invalidation: {e}", exc_info=True)

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """Load TEDx data from the CSV file."""
        slug_index = {}
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug(f"Loaded {len(slug_index)} slugs from CSV file.")
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise FileNotFoundError(f"File not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}", exc_info=True)
            raise Exception("Failed to load CSV data.")
        return slug_index

    def _run(self, search_query: str) -> str:
        """Executes the search on the TEDx dataset based on the search query."""
        logger.debug(f"Running TEDx search for query: {search_query}")
        results = [data for key, data in self.csv_data.items() if search_query.lower() in key.lower()]
        
        if not results:
            return "No results found."

        return f"Final Answer: TEDx Search Results:\n{results}"
