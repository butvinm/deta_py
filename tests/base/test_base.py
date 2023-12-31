"""Integration tests for the DetaBase class."""


from datetime import datetime, timedelta
from typing import Any, Generator

import pytest
from deta.base import _Base  # type: ignore # noqa: WPS450

from deta_py.deta_base.base import DetaBase
from deta_py.deta_base.queries import ItemUpdate
from deta_py.deta_base.utils import TTL_ATTRIBUTE, insert_ttl
from tests.base.utils import clear_base, get_item, get_items, put_items

test_keyed_items = [
    {'key': '1', 'name': 'John', 'age': 20, 'friends': ['Jane']},
    {'key': '2', 'name': 'Jane', 'age': 21, 'friends': ['John']},
    {'key': '3', 'name': 'Bob', 'age': 22, 'friends': ['John', 'Jane']},
]

test_items = [
    {'name': 'John', 'age': 20, 'friends': ['Jane']},
    {'name': 'Jane', 'age': 21, 'friends': ['John']},
    {'name': 'Bob', 'age': 22, 'friends': ['John', 'Jane']},
]


@pytest.fixture
def base(
    credentials: tuple[str, str],
    deta_base: _Base,
) -> Generator[DetaBase, None, None]:
    """Return a DetaBase instance.

    Clear the base before and after the test.

    Args:
        credentials (tuple[str, str]): A tuple of test data key and base name.
        deta_base (_Base): A deta.base._Base instance.

    Yields:
        DetaBase: A DetaBase instance.
    """
    clear_base(deta_base)

    with DetaBase(credentials[0], credentials[1]) as base:
        yield base

    clear_base(deta_base)


@pytest.fixture
def base_with_data(base: DetaBase, deta_base: _Base) -> DetaBase:
    """Return a DetaBase instance with data.

    Put items in the base before test.

    Args:
        base (DetaBase): Clear base instance.
        deta_base (_Base): A deta.base._Base instance.

    Returns:
        DetaBase: A DetaBase instance with data.
    """
    put_items(deta_base, test_keyed_items)
    return base


def test_insert_ttl(base: DetaBase) -> None:
    """Test the insert_ttl method.

    Args:
        base (DetaBase): Empty DetaBase instance.
    """
    item: dict[str, Any] = {}

    # Test with expires_at as datetime
    expires_at_datetime = datetime.now()
    result_datetime = insert_ttl(
        item,
        expires_at=expires_at_datetime,
    )
    assert TTL_ATTRIBUTE in result_datetime
    assert result_datetime[TTL_ATTRIBUTE] == expires_at_datetime.replace(
        microsecond=0,
    ).timestamp()

    # Test with expires_at as numeric
    expires_at_numeric = datetime.now().timestamp()
    result_numeric = insert_ttl(
        item,
        expires_at=expires_at_numeric,
    )
    assert TTL_ATTRIBUTE in result_numeric
    assert result_numeric[TTL_ATTRIBUTE] == expires_at_numeric

    # Test with expires_in as seconds
    expires_in_seconds = timedelta(hours=1).total_seconds()
    result_seconds = insert_ttl(
        item,
        expires_in=expires_in_seconds,
    )
    assert TTL_ATTRIBUTE in result_seconds
    expected_expires_at = datetime.now() + timedelta(hours=1)
    expected_expires_at_seconds = expected_expires_at.replace(
        microsecond=0,
    ).timestamp()
    assert result_seconds[TTL_ATTRIBUTE] == expected_expires_at_seconds

    # Test with expires_in as timedelta
    expires_in_timedelta = timedelta(hours=2)
    result_timedelta = insert_ttl(
        item, expires_in=expires_in_timedelta.total_seconds())
    assert TTL_ATTRIBUTE in result_timedelta
    expected_expires_at = datetime.now() + expires_in_timedelta
    expected_expires_at_timedelta = expected_expires_at.replace(
        microsecond=0,
    ).timestamp()
    assert result_timedelta[TTL_ATTRIBUTE] == expected_expires_at_timedelta

    # Test with both expires_at and expires_in
    expires_at = datetime.now()
    expires_in = timedelta(hours=1).total_seconds()
    result_both = insert_ttl(
        item,
        expires_at=expires_at,
        expires_in=expires_in,
    )
    assert TTL_ATTRIBUTE in result_both
    assert result_both[TTL_ATTRIBUTE] == expires_at.replace(
        microsecond=0,
    ).timestamp()


def test_base_init(
    base: DetaBase,
    credentials: tuple[str, str],
) -> None:
    """Test the DetaBase class initialization.

    Args:
        base (DetaBase): A DetaBase instance.
        credentials (tuple[str, str]): A tuple of test data key and base name.
    """
    assert base.data_key == credentials[0]
    assert base.base_name == credentials[1]


def test_get(base_with_data: DetaBase) -> None:
    """Test the get method.

    Args:
        base_with_data (DetaBase): A DetaBase instance with data.
    """
    # Existing items
    assert base_with_data.get('1') == test_keyed_items[0]
    assert base_with_data.get('2') == test_keyed_items[1]

    # Non-existing item
    assert base_with_data.get('not-exist') is None

    # Bad key
    assert base_with_data.get(0) is None  # type: ignore
    assert base_with_data.get(None) is None  # type: ignore


def test_put(base: DetaBase) -> None:
    """Test the put method.

    Args:
        base (DetaBase): Empty DetaBase instance.
    """
    # Put single item
    assert base.put(test_keyed_items[0]) == [test_keyed_items[0]]

    # Put multiple items
    assert base.put(*test_keyed_items) == test_keyed_items

    # Put more than 25 items
    batch_size = 25
    items = [{'value': item_num} for item_num in range(batch_size * 2)]
    processed = base.put(*items)
    assert len(processed) == batch_size * 2

    # Put items without keys
    processed = base.put(*test_items)
    assert len(processed) == len(test_items)

    # Put with TTL
    item = {'value': 'test'}
    expires_at = datetime.now() + timedelta(hours=1)
    result = base.put(item, expire_at=expires_at)
    assert TTL_ATTRIBUTE in result[0]

    # Put bad item
    assert not base.put(0)  # type: ignore


def test_delete(base_with_data: DetaBase, deta_base: _Base) -> None:
    """Test the delete method.

    Args:
        base_with_data (DetaBase): A DetaBase instance with data.
        deta_base (_Base): A deta.base._Base instance.
    """
    # Delete existing items
    base_with_data.delete('1')
    base_with_data.delete('2')

    items = get_items(deta_base)
    assert all(item['key'] not in {'1', '2'} for item in items)

    # Delete non-existing item
    base_with_data.delete('not-exist')


def test_insert(base: DetaBase) -> None:
    """Test the insert method.

    Args:
        base (DetaBase): Empty DetaBase instance.
    """
    # Insert single item
    assert base.insert(test_keyed_items[0]) == test_keyed_items[0]

    # Insert existing item
    assert base.insert(test_keyed_items[0]) is None

    # Insert with TTL
    item = {'value': 'test'}
    expires_at = datetime.now() + timedelta(hours=1)
    result = base.insert(item, expire_at=expires_at)
    assert result is not None
    assert TTL_ATTRIBUTE in result

    # Insert bad item
    assert base.insert(0) is None  # type: ignore


def test_update(base_with_data: DetaBase, deta_base: _Base) -> None:
    """Test the update method.

    Args:
        base_with_data (DetaBase): DetaBase instance with data.
        deta_base (_Base): A deta.base._Base instance.
    """
    initial_item = test_keyed_items[0]

    # Test set, increment and append operations
    operations = ItemUpdate()
    operations.set(name='John Doe')
    operations.increment(age=1)
    operations.append(friends=['Jane Doe'])

    base_with_data.update('1', operations)
    item = get_item(deta_base, '1')
    assert item == {
        'key': initial_item['key'],
        'name': 'John Doe',
        'age': initial_item['age'] + 1,  # type: ignore
        'friends': initial_item['friends'] + ['Jane Doe'],  # type: ignore
    }

    # Test delete operation
    operations = ItemUpdate()
    operations.delete('friends')

    base_with_data.update('1', operations)
    item = get_item(deta_base, '1')
    assert item is not None
    assert 'friends' not in item

    # Test update with TTL
    operations = ItemUpdate()
    operations.set(name='John Doe')
    expires_at = datetime.now() + timedelta(hours=1)
    base_with_data.update('1', operations, expire_at=expires_at)
    item = get_item(deta_base, '1')
    assert item is not None
    assert TTL_ATTRIBUTE in item

    # Test bad key
    operations = ItemUpdate()
    base_with_data.update(0, operations)  # type: ignore


def test_query(base_with_data: DetaBase) -> None:
    """Test the query method.

    Args:
        base_with_data (DetaBase): A DetaBase instance with data.
    """
    # Fetch all items
    res = base_with_data.query()
    assert len(res.items) == len(test_keyed_items)

    # Fetch items with limit
    res = base_with_data.query(limit=2)
    assert len(res.items) == 2
    assert res.last == '2'

    # Fetch items with pagination
    res = base_with_data.query(limit=1)
    items = res.items
    while res.last:
        res = base_with_data.query(last=res.last, limit=1)
        items += res.items

    assert all(item in items for item in test_keyed_items)

    # Fetch items with query
    res = base_with_data.query(query=[{'age?lt': 30, 'age?gt': 21}])
    assert res.items[0] == test_keyed_items[2]

    # Bad query
    res = base_with_data.query(query={'age?': 30})
    assert not res.items
