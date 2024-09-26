# tools/tedx_slug_tool.py

"""
Module for TEDxSlugTool which retrieves TEDx content details based on a provided
slug.
"""

import logging
import csv
from typing import Any, Dict
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class TEDxSlugToolArgs(BaseModel):
    """Arguments for TEDxSlugTool."""
    slug: str = Field(..., description="The TEDx talk slug to retrieve details for.")


class TEDxSlugTool(BaseModel):
    """Tool to retrieve TEDx content details based on a provided slug."""

    _name: str = "tedx_slug"
    _description: str = "Retrieves TEDx content details based on a provided slug."
    _args_schema = TEDxSlugToolArgs

    data_path: str = Field(..., description="Path to the TEDx dataset CSV")
    csv_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Loaded CSV data")

    @validator('csv_data', pre=True, always=True)
    def load_csv_data(cls, v, values):
        data_path = values.get('data_path')
        if not data_path:
            raise ValueError("`data_path` must be provided in the configuration.")
        logger.info("Loading TEDxSlugTool with data_path: %s", data_path)
        try:
            slug_index = {}
            with open(data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip().lower()
                    if slug:
                        slug_index[slug] = row
            logger.debug("Loaded %d slugs from CSV file.", len(slug_index))
            return slug_index
        except FileNotFoundError as exc:
            logger.error("File not found: %s", data_path, exc_info=True)
            raise FileNotFoundError(f"File not found: {data_path}") from exc
        except Exception as e:
            logger.error("Error loading CSV data: %s", e, exc_info=True)
            raise Exception("Failed to load CSV data.") from e

    def run(self, slug: str) -> str:
        """
        Retrieve data for the given slug.

        Args:
            slug (str): The TEDx talk slug.

        Returns:
            str: The details for the TEDx talk.
        """
        logger.debug("Running TEDxSlugTool for slug: %s", slug)
        slug_lower = slug.lower()

        if slug_lower not in self.csv_data:
            return f"No data found for slug '{slug}'. Please ensure the slug is correct."

        entry = self.csv_data[slug_lower]

        formatted_result = (
            f"Title: {entry.get('title', 'No Title')}\n"
            f"Description: {entry.get('description', 'No Description')}\n"
            f"URL: {entry.get('url', 'No URL')}"
        )
        
        logger.debug("Result for slug '%s': %s", slug, formatted_result)
        return f"Final Answer: TEDx Talk Details for slug '{slug}':\n{formatted_result}"

    # Class property methods
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> BaseModel:
        return self._args_schema

    class Config:
        arbitrary_types_allowed = True
