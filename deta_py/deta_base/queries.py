"""Deta Base querying tools.

Provides tools for working with Deta Base queries.
"""

from typing import Any, Optional, Union


class ItemUpdate(object):
    """Utility for building update requests."""

    def __init__(self) -> None:
        """Init operations."""
        self._set: dict[str, Any] = {}
        self._increment: dict[str, Union[int, float]] = {}
        self._append: dict[str, list[Any]] = {}
        self._delete: list[str] = []

    def set(self, **kwargs: Any) -> 'ItemUpdate':
        """Set fields.

        Args:
            kwargs (Any): Fields to set.

        Returns:
            UpdateRequest: Self.
        """
        self._set.update(kwargs)
        return self

    def increment(self, **kwargs: int) -> 'ItemUpdate':
        """Increment fields.

        Args:
            kwargs (int): Fields to increment.

        Returns:
            UpdateRequest: Self.
        """
        self._increment.update(kwargs)
        return self

    def append(self, **kwargs: list[Any]) -> 'ItemUpdate':
        """Append fields.

        Args:
            kwargs (list[Any]): Fields to append.

        Returns:
            UpdateRequest: Self.
        """
        self._append.update(kwargs)
        return self

    def delete(self, *args: str) -> 'ItemUpdate':
        """Delete fields.

        Args:
            args (str): Fields to delete.

        Returns:
            UpdateRequest: Self.
        """
        self._delete.extend(args)
        return self

    def as_json(self) -> dict[str, Any]:
        """Build request body.

        Returns:
            dict[str, Any]: Request body.
        """
        return {
            'set': self._set,
            'increment': self._increment,
            'append': self._append,
            'delete': self._delete,
        }


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