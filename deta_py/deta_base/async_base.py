"""Async Deta Base module.

Async implementation of DetaBase.
"""

from http import HTTPStatus
from typing import Any, Optional

from aiohttp import ClientSession, ClientTimeout

from deta_py.deta_base.queries import ItemUpdate, Query
from deta_py.deta_base.results import QueryResult
from deta_py.deta_base.utils import (
    BASE_API_URL,
    ITEMS_BATCH_SIZE,
    REQUEST_TIMEOUT,
    ExpireAt,
    ExpireIn,
    insert_ttl,
)
from deta_py.utils import parse_data_key


class AsyncDetaBase(object):  # noqa: WPS214
    """Async Deta Base client."""

    def __init__(self, data_key: str, base_name: str):
        """Init async Deta Base client.

        You can generate Data Key in your project or collection settings.

        New aiohttp session is initialized.
        Don't forget to call `base.close()` to close connection.

        Args:
            data_key (str): Deta project data key.
            base_name (str): Deta Base name.
        """
        self.data_key = data_key
        self.base_name = base_name

        project_id, _ = parse_data_key(data_key)
        self.base_url = BASE_API_URL.format(
            project_id=project_id,
            base_name=base_name,
        )

        self._session = ClientSession(
            headers={
                'X-API-Key': self.data_key,
                'Content-Type': 'application/json',
            },
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
        )

    async def put(
        self,
        *items: dict[str, Any],
        expire_at: Optional[ExpireAt] = None,
        expire_in: Optional[ExpireIn] = None,
    ) -> list[dict[str, Any]]:
        """Put items to the base.

        If item with the same key already exists, it will be overwritten.

        Items are splitted into batches of 25 items and put in parallel.

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
            batch_items = list(items[:ITEMS_BATCH_SIZE])
            items = items[ITEMS_BATCH_SIZE:]
            batch_processed = await self._put_batch(
                batch_items,
                expire_at=expire_at,
                expire_in=expire_in,
            )
            processed.extend(batch_processed)

        return processed

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get item from the base.

        Args:
            key (str): Item key.

        Returns:
            Optional[dict[str, Any]]: Item or None if not found.
        """
        async with self._session.get(
            self._get_url('/items/{key}', key=key),
        ) as response:
            if response.status == HTTPStatus.OK:
                item: dict[str, Any] = await response.json()
                return item
            return None

    async def delete(self, key: str) -> None:
        """Delete item from the base.

        Args:
            key (str): Item key.
        """
        # probably some response processing will be added in future,
        # so empty manager body currently ignored
        async with self._session.delete(  # noqa: WPS328
            self._get_url('/items/{key}', key=key),
        ):
            pass  # noqa: WPS420

    async def insert(
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
        async with self._session.post(
            self._get_url('/items'),
            json={'item': item},
        ) as response:
            if response.status == HTTPStatus.CREATED:
                inserted_item: dict[str, Any] = await response.json()
                return inserted_item
            return None

    async def update(
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
            >>> await base.update(operations)

        Args:
            key (str): Item key.
            operations (ItemUpdate): Update operations.
            expire_at (Optional[ExpireAt]): Item expire time.
            expire_in (Optional[ExpireIn]): Item expire time delta.

        Returns:
            bool: True if item was updated, False if not found.
        """
        operations.set(**insert_ttl({}, expire_at, expire_in))
        async with self._session.patch(
            self._get_url('/items/{key}', key=key),
            json=operations.as_json(),
        ) as response:
            return response.status == HTTPStatus.OK

    async def query(
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

        async with self._session.post(
            self._get_url('/query'),
            json={
                'query': query,
                'limit': limit,
                'last': last,
            },
        ) as response:
            if response.status == HTTPStatus.OK:
                data: dict[str, Any] = await response.json()
                return QueryResult(
                    items=data['items'],
                    count=data['paging']['size'],
                    last=data['paging'].get('last'),
                )

            return QueryResult(items=[], count=0, last=None)

    async def close(self) -> None:
        """Close aiohttp session."""
        await self._session.close()

    async def _put_batch(
        self,
        batch_items: list[dict[str, Any]],
        expire_at: Optional[ExpireAt] = None,
        expire_in: Optional[ExpireIn] = None,
    ) -> list[dict[str, Any]]:
        """Put batch of items to the base.

        Args:
            batch_items (list[dict[str, Any]]): Items to put.
            expire_at (Optional[ExpireAt]): Item expire time.
            expire_in (Optional[ExpireIn]): Item expire time delta.

        Returns:
            list[dict[str, Any]]: List of successfully processed items.
        """
        batch_items = [
            insert_ttl(item, expire_at, expire_in)
            for item in batch_items
        ]
        async with self._session.put(
            self._get_url('/items'),
            json={'items': batch_items},
        ) as response:
            if response.status == HTTPStatus.MULTI_STATUS:
                data = await response.json()
                items: list[dict[str, Any]] = data['processed']['items']
                return items

            return []

    def _get_url(self, path: str, **kwargs: str) -> str:
        """Return full url for the given path.

        Args:
            path (str): Relative path.
            kwargs (str): Path params.

        Returns:
            str: Full url.
        """
        return self.base_url + path.format(**kwargs)
