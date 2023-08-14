"""Deta Base module.

That module contains DetaBase class that is used to interact with Deta Base.

See https://deta.space/docs/en/build/reference/deta-base for reference.
"""


from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Optional, Union

from requests import Response, request

from deta_py.utils import parse_data_key

BASE_API_URL = 'https://database.deta.sh/v1/{project_id}/{base_name}'

# max number of items to put in one request
ITEMS_BATCH_SIZE = 25

# Timeout for requests to Deta Base API
REQUEST_TIMEOUT = 10  # seconds

# Deta Base item TTL attribute name
# Taken from official Deta Base Python SDK
TTL_ATTRIBUTE = '__expires'

# See https://deta.space/docs/en/build/reference/deta-base/queries
# for full reference
SimpleQuery = dict[str, Any]
Query = Union[SimpleQuery, list[SimpleQuery]]

# Item expire attribute
ExpireAt = Union[datetime, int, float]
ExpireIn = Union[timedelta, int, float]


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


class DetaBase(object):  # noqa: WPS214
    """Deta Base class.

    Wraps Deta Base HTTP API.
    See https://deta.space/docs/en/build/reference/http-api/base for reference.
    """

    def __init__(self, data_key: str, base_name: str):
        """Deta Base class.

        Args:
            data_key (str): Data key.
            base_name (str): Base name.
        """
        self.data_key = data_key
        self.base_name = base_name

        project_id, _ = parse_data_key(data_key)
        self.host = BASE_API_URL.format(
            project_id=project_id,
            base_name=base_name,
        )

    def put(
        self,
        *items: dict[str, Any],
        expire_at: Optional[ExpireAt] = None,
        expire_in: Optional[ExpireIn] = None,
    ) -> list[dict[str, Any]]:
        """Put items to the base.

        If item with the same key already exists, it will be overwritten.

        Items are put in batches of 25 items.

        You can specify either expire_at or expire_in to set item TTL.
        If both are specified, expire_at will be used.

        Args:
            items (dict[str, Any]): Items to put.
            expire_at (Optional[ExpireAt]): Item expire time.
            expire_in (Optional[ExpireIn]): Item expire time delta.

        Returns:
            list[dict[str, Any]]: List of successfully processed items.
        """
        processed = []
        while items:
            items_slice = [
                insert_ttl(item, expire_at, expire_in)
                for item in items[:ITEMS_BATCH_SIZE]
            ]
            items = items[ITEMS_BATCH_SIZE:]

            response = self._request(
                'PUT',
                '/items',
                json={'items': items_slice},
            )
            if response.status_code == HTTPStatus.MULTI_STATUS:
                processed += response.json()['processed']['items']

        return processed

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get item from the base.

        Args:
            key (str): Item key.

        Returns:
            Optional[dict[str, Any]]: Item or None if not found.
        """
        response = self._request('GET', '/items/{key}'.format(key=key))
        if response.status_code == HTTPStatus.OK:
            item: dict[str, Any] = response.json()
            return item

        return None

    def delete(self, key: str) -> None:
        """Delete item from the base.

        Args:
            key (str): Item key.
        """
        self._request('DELETE', '/items/{key}'.format(key=key))

    def insert(
        self,
        item: dict[str, Any],
        expire_at: Optional[ExpireAt] = None,
        expire_in: Optional[ExpireIn] = None,
    ) -> Optional[dict[str, Any]]:
        """Insert item to the base.

        If item with the same key already exists, it will not be inserted.

        You can specify either expire_at or expire_in to set item TTL.
        If both are specified, expire_at will be used.

        Args:
            item (dict[str, Any]): Item to insert.
            expire_at (Optional[ExpireAt]): Item expire time.
            expire_in (Optional[ExpireIn]): Item expire time delta.

        Returns:
            Optional[dict[str, Any]]: Inserted item \
                or None if item with the same key already exists.
        """
        item = insert_ttl(item, expire_at, expire_in)
        response = self._request(
            'POST',
            '/items',
            json={'item': item},
        )
        if response.status_code == HTTPStatus.CREATED:
            inserted_item: dict[str, Any] = response.json()
            return inserted_item

        return None

    def update(
        self,
        key: str,
        operations: ItemUpdate,
        expire_at: Optional[ExpireAt] = None,
        expire_in: Optional[ExpireIn] = None,
    ) -> bool:
        """Update item in the base.

        You can specify either expire_at or expire_in to set item TTL.
        If both are specified, expire_at will be used.

        Example:
            >>> operations = ItemUpdate()
            >>> operations.set(name='John')
            >>> operations.increment(age=1)
            >>> operations.append(friends=['Jane'])
            >>> operations.delete('hobbies')
            >>> base.update(operations)

        Args:
            key (str): Item key.
            operations (ItemUpdate): Update operations.
            expire_at (Optional[ExpireAt]): Item expire time.
            expire_in (Optional[ExpireIn]): Item expire time delta.

        Returns:
            bool: True if item was updated, False if not found.
        """
        operations.set(**insert_ttl({}, expire_at, expire_in))
        response = self._request(
            'PATCH',
            '/items/{key}'.format(key=key),
            json=operations.as_json(),
        )
        return response.status_code == HTTPStatus.OK

    def query(
        self,
        query: Optional[Query] = None,
        limit: int = 1000,
        last: Optional[str] = None,
    ) -> QueryResult:
        """Query items in the base.

        If result contains more than 1000 items, it will be paginated.

        You can use `last` key from the previous query to get next page.
        Example:
        >>> query = [{'age': {'$gt': 18}}]
        >>> res = base.query(query)
        >>> items = res.items
        >>> while res.last:
        ...     res = db.fetch(last=res.last)
        ...     items += res.items

        Args:
            query (Optional[Query]): List of queries.
            limit (int): Limit of items to return.
            last (Optional[str]): Last key of the previous query.

        Returns:
            QueryResult: Query result.
        """
        if isinstance(query, dict):
            query = [query]

        response = self._request(
            'POST',
            '/query',
            json={
                'query': query,
                'limit': limit,
                'last': last,
            },
        )
        if response.status_code == HTTPStatus.OK:
            data: dict[str, Any] = response.json()
            return QueryResult(
                items=data['items'],
                count=data['paging']['size'],
                last=data['paging'].get('last'),
            )

        return QueryResult(items=[], count=0, last=None)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Any] = None,
    ) -> Response:
        """Send request to the base.

        Send request to the base with credentials.

        Args:
            method (str): HTTP method.
            path (str): Path to the resource.
            json (Optional[Any]): JSON data to send.

        Returns:
            Response: Response object.
        """
        return request(
            method,
            self.host + path,
            headers={
                'X-API-Key': self.data_key,
                'Content-Type': 'application/json',
            },
            json=json,
            timeout=REQUEST_TIMEOUT,
        )


def insert_ttl(
    item: dict[str, Any],
    expires_at: Optional[ExpireAt] = None,
    expires_in: Optional[ExpireIn] = None,
) -> dict[str, Any]:
    """Insert TTL attribute to item data.

    If both `expires_at` and `expires_in` are specified,
    `expires_at` will be used.

    Args:
        item (dict[str, Any]): Item data.
        expires_at (Optional[ExpireAt]): Expiration date. \
            In seconds if numeric.
        expires_in (Optional[ExpireIn]): Expiration delta. \
            In seconds if numeric.

    Returns:
        dict[str, Any]: Item data with TTL attribute.
    """
    if expires_at is not None:
        if isinstance(expires_at, datetime):
            # microseconds replacement taken from official SDK
            # can be removed in future
            expires_at = expires_at.replace(microsecond=0).timestamp()

        item[TTL_ATTRIBUTE] = expires_at
    elif expires_in is not None:
        if isinstance(expires_in, (int, float)):
            expires_in = timedelta(seconds=expires_in)

        expires_at = datetime.now() + expires_in
        expires_at = expires_at.replace(microsecond=0).timestamp()

        item[TTL_ATTRIBUTE] = expires_at

    return item
