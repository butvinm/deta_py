"""Deta Base queries module.

Contains types and utilities for querying Deta Base.
"""

from typing import Any, Union

# See https://deta.space/docs/en/build/reference/deta-base/queries
# for full reference
SimpleQuery = dict[str, Any]
Query = Union[SimpleQuery, list[SimpleQuery]]


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
