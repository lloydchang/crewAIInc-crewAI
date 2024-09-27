# tools/tedx_slug_tool.py

"""
Module for TEDxSlugTool which retrieves TEDx content details based on a provided slug.
"""

import logging

logger = logging.getLogger(__name__)

class TEDxSlugTool(BaseModel):
    """Tool for retrieving TEDx content using slugs."""

    _name: str = "tedx_slug"
    _description: str = "Retrieves TEDx content using the slug."
    _args_schema = None  # Define the argument schema if necessary

    def invoke(self, input: Dict[str, str]) -> str:
        """
        Retrieves TEDx content using the slug.

        Args:
            input (dict): Dictionary containing 'slug' for TEDx talk lookup.

        Returns:
            str: The details of the TEDx talk based on the slug.
        """
        slug = input.get('slug', '')
        logger.debug("Looking up TEDx content by slug: %s", slug)

        if not slug:
            return "Slug cannot be empty."

        try:
            # Simulate TEDx slug lookup (replace with actual logic)
            tedx_content = {
                "title": "A talk on sustainability",
                "description": "An inspiring TEDx talk on eco-friendly initiatives.",
                "url": "https://www.tedx.com/talk/slug-example"
            }

            logger.debug("Retrieved TEDx content: %s", tedx_content)
            return f"Final Answer: TEDx Content:\nTitle: {tedx_content['title']}\nDescription: {tedx_content['description']}\nURL: {tedx_content['url']}"
        except Exception as e:
            logger.error("Error retrieving TEDx content by slug: %s", e, exc_info=True)
            return "An error occurred while retrieving TEDx content."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    class Config:
        arbitrary_types_allowed = True

