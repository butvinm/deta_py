"""Deta Base utilities.

Contains constants and utility functions for working with Deta Base.
"""


from datetime import datetime, timedelta
from typing import Any, Optional

from deta_py.deta_base.types import ExpireAt, ExpireIn

BASE_API_URL = 'https://database.deta.sh/v1/{project_id}/{base_name}'

# Max number of items to put in one request
# Taken from official Deta Base Python SDK
ITEMS_BATCH_SIZE = 25

# Timeout for requests to Deta Base API
REQUEST_TIMEOUT = 10  # seconds

# Deta Base item TTL attribute name
# Taken from official Deta Base Python SDK
TTL_ATTRIBUTE = '__expires'


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
