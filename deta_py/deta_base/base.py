"""Deta Base module.

That module contains DetaBase class that is used to interact with Deta Base.

See https://deta.space/docs/en/build/reference/deta-base for reference.
"""


from http import HTTPStatus
from typing import Any, Optional

from requests import Response, Session, request

from deta_py.deta_base.queries import ItemUpdate, QueryResult
from deta_py.deta_base.types import ExpireAt, ExpireIn, Query
from deta_py.deta_base.utils import (
    BASE_API_URL,
    ITEMS_BATCH_SIZE,
    REQUEST_TIMEOUT,
    insert_ttl,
)
from deta_py.utils import parse_data_key


class DetaBase(object):  # noqa: WPS214
    """Deta Base client.

    Wraps Deta Base HTTP API.
    See https://deta.space/docs/en/build/reference/http-api/base for reference.
    """

    def __init__(self, data_key: str, base_name: str):
        """Init Deta Base client.

        You can generate Data Key in your project or collection settings.

        Args:
            data_key (str): Data key.
            base_name (str): Base name.
        """
        self.data_key = data_key
        self.base_name = base_name

        project_id, _ = parse_data_key(data_key)
        self.base_url = BASE_API_URL.format(
            project_id=project_id,
            base_name=base_name,
        )

        self._session = Session()
        self._session.headers.update({
            'X-API-Key': data_key,
            'Content-Type': 'application/json',
        })

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
        """Fetch items in the base.

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
        return self._session.request(
            method,
            self.base_url + path,
            json=json,
            timeout=REQUEST_TIMEOUT,
        )
