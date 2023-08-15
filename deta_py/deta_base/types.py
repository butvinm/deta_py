"""Deta Base types.

Include types for Deta Base operations entities.
"""

from datetime import datetime, timedelta
from typing import Any, Union

# See https://deta.space/docs/en/build/reference/deta-base/queries
# for full reference
SimpleQuery = dict[str, Any]
Query = Union[SimpleQuery, list[SimpleQuery]]

# Item expiration types
ExpireAt = Union[datetime, int, float]
ExpireIn = Union[timedelta, int, float]
