"""Deta Base module.

That module contains DetaBase class that is used to interact with Deta Base.

See https://deta.space/docs/en/build/reference/deta-base for reference.
"""


from http import HTTPStatus
from typing import Any, Mapping, Optional

from requests import Response, request

from deta_py.utils import parse_data_key

BASE_API_URL = 'https://database.deta.sh/v1/{project_id}/{base_name}'

# max number of items to put in one request
ITEMS_BATCH_SIZE = 25


class DetaBase(object):
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

    def put(self, *items: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Put items to the base.

        If item with the same key already exists, it will be overwritten.

        Items are put in batches of 25 items.

        Args:
            items (Mapping[str, Any]): Items to put.

        Returns:
            list[dict[str, Any]]: List of successfully processed items.
        """
        processed = []
        while items:
            items_slice = items[:ITEMS_BATCH_SIZE]
            items = items[ITEMS_BATCH_SIZE:]

            response = self._request(
                'PUT',
                '/items',
                json={'items': items_slice},
            )
            if response.status_code == HTTPStatus.MULTI_STATUS:
                processed += response.json()['processed']['items']

        return processed

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
            json (Optional[Any], optional): JSON data to send.

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
        )
