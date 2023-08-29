"""Deta Base responses.

This package contains results types of DetaBase methods.
"""


from typing import Any, Optional


class QueryResult(object):
    """Paginated query response."""

    def __init__(
        self,
        items: list[dict[str, Any]],
        count: int,
        last: Optional[str],
    ) -> None:
        """Init query response.

        Args:
            items (list[dict[str, Any]]): Items.
            count (int): Total number of items.
            last (Optional[str]): Last item key.
        """
        self.items = items
        self.count = count
        self.last = last
