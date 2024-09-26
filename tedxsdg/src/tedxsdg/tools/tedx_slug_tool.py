# tools/tedx_slug_tool.py

"""
Module for TEDxSlugTool which retrieves TEDx content details based on a provided
slug.
"""

import logging
import csv
from typing import Any, Dict
from langchain.tools import StructuredTool

logger = logging.getLogger(__name__)


class TEDxSlugTool(StructuredTool):
    """
    Tool to retrieve TEDx content details based on a provided slug.
    """
    name: str = "tedx_slug"
    description: str = (
        "Retrieves TEDx content details based on a provided slug."
    )

    def __init__(self, data_path: str, config: Dict[str, Any] = None):
        """
        Initialize the TEDxSlugTool with the given data path and optional configuration.
        """
        super().__init__()
        self.data_path = data_path
        if not self.data_path:
            raise ValueError("Data path is required for TEDxSlugTool.")
        # Load CSV data upon initialization
        self.csv_data = self._load_csv_data()

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load CSV data directly without dependency on TEDxSearchTool.
        """
        try:
            slug_index = {}
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug("Loaded %d slugs from CSV file.", len(slug_index))
            return slug_index
        except FileNotFoundError:
            logger.error("CSV file not found at path: %s", self.data_path)
            raise
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise

    def _run(self, slug: str) -> str:
        """
        Retrieve data for the given slug.
        """
        if not slug:
            return "Error: No slug provided."

        if not hasattr(self, 'csv_data') or self.csv_data is None:
            return "Error: CSV data is not loaded."

        row = self.csv_data.get(slug)
        if not row:
            return f"No data found for slug '{slug}'. Please ensure the slug is correct."

        return f"Final Answer: Data for slug '{slug}':\n{row}"
