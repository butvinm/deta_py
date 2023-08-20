"""Integration tests for the AsyncDetaBase class."""

from datetime import datetime, timedelta
from typing import AsyncGenerator

import pytest
from deta.base import _Base  # type: ignore # noqa: WPS450

from deta_py.deta_base.async_base import AsyncDetaBase
from deta_py.deta_base.queries import ItemUpdate
from deta_py.deta_base.utils import TTL_ATTRIBUTE
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
async def base(
    credentials: tuple[str, str],
    deta_base: _Base,
) -> AsyncGenerator[AsyncDetaBase, None]:
    """Return an AsyncDetaBase instance.

    Clear the base before and after the test.

    Args:
        credentials (tuple[str, str]): A tuple of test data key and base name.
        deta_base (_Base): A deta.base._Base instance.

    Yields:
        AsyncDetaBase: An AsyncDetaBase instance.
    """
    clear_base(deta_base)

    base = AsyncDetaBase(credentials[0], credentials[1])
    yield base
    await base.close()

    clear_base(deta_base)


@pytest.fixture
async def base_with_data(
    base: AsyncDetaBase,
    deta_base: _Base,
) -> AsyncDetaBase:
    """Return an AsyncDetaBase instance with data.

    Put items in the base before test.

    Args:
        base (AsyncDetaBase): Clear base instance.
        deta_base (_Base): A deta.base._Base instance.

    Returns:
        AsyncDetaBase: An AsyncDetaBase instance with data.
    """
    put_items(deta_base, test_keyed_items)
    return base


async def test_base_init(
    base: AsyncDetaBase,
    credentials: tuple[str, str],
) -> None:
    """Test the AsyncDetaBase class initialization.

    Args:
        base (AsyncDetaBase): An AsyncDetaBase instance.
        credentials (tuple[str, str]): A tuple of test data key and base name.
    """
    assert base.data_key == credentials[0]
    assert base.base_name == credentials[1]


async def test_get(base_with_data: AsyncDetaBase) -> None:
    """Test the get method.

    Args:
        base_with_data (AsyncDetaBase): An AsyncDetaBase instance with data.
    """
    # Existing items
    assert await base_with_data.get('1') == test_keyed_items[0]
    assert await base_with_data.get('2') == test_keyed_items[1]

    # Non-existing item
    assert await base_with_data.get('not-exist') is None

    # Bad key
    assert await base_with_data.get(0) is None  # type: ignore
    assert await base_with_data.get(None) is None  # type: ignore


async def test_put(base: AsyncDetaBase) -> None:
    """Test the put method.

    Args:
        base (AsyncDetaBase): Empty AsyncDetaBase instance.
    """
    # Put single item
    assert await base.put(test_keyed_items[0]) == [test_keyed_items[0]]

    # Put multiple items
    assert await base.put(*test_keyed_items) == test_keyed_items

    # Put more than 25 items
    batch_size = 25
    items = [{'value': item_num} for item_num in range(batch_size * 2)]
    processed = await base.put(*items)
    assert len(processed) == batch_size * 2

    # Put items without keys
    processed = await base.put(*test_items)
    assert len(processed) == len(test_items)

    # Put with TTL
    item = {'value': 'test'}
    expires_at = datetime.now() + timedelta(hours=1)
    result = await base.put(item, expire_at=expires_at)
    assert TTL_ATTRIBUTE in result[0]

    # Put bad item
    assert not await base.put(0)  # type: ignore


async def test_delete(base_with_data: AsyncDetaBase, deta_base: _Base) -> None:
    """Test the delete method.

    Args:
        base_with_data (AsyncDetaBase): An AsyncDetaBase instance with data.
        deta_base (_Base): A deta.base._Base instance.
    """
    # Delete existing items
    await base_with_data.delete('1')
    await base_with_data.delete('2')

    items = get_items(deta_base)
    assert all(item['key'] not in {'1', '2'} for item in items)

    # Delete non-existing item
    await base_with_data.delete('not-exist')


async def test_insert(base: AsyncDetaBase) -> None:
    """Test the insert method.

    Args:
        base (AsyncDetaBase): Empty AsyncDetaBase instance.
    """
    # Insert single item
    assert await base.insert(test_keyed_items[0]) == test_keyed_items[0]

    # Insert existing item
    assert await base.insert(test_keyed_items[0]) is None

    # Insert with TTL
    item = {'value': 'test'}
    expires_at = datetime.now() + timedelta(hours=1)
    result = await base.insert(item, expire_at=expires_at)
    assert result is not None
    assert TTL_ATTRIBUTE in result

    # Insert bad item
    assert await base.insert(0) is None  # type: ignore


async def test_update(base_with_data: AsyncDetaBase, deta_base: _Base) -> None:
    """Test the update method.

    Args:
        base_with_data (AsyncDetaBase): AsyncDetaBase instance with data.
        deta_base (_Base): A deta.base._Base instance.
    """
    initial_item = test_keyed_items[0]

    # Test set, increment and append operations
    operations = ItemUpdate()
    operations.set(name='John Doe')
    operations.increment(age=1)
    operations.append(friends=['Jane Doe'])

    await base_with_data.update('1', operations)
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

    await base_with_data.update('1', operations)
    item = get_item(deta_base, '1')
    assert item is not None
    assert 'friends' not in item

    # Test update with TTL
    operations = ItemUpdate()
    operations.set(name='John Doe')
    expires_at = datetime.now() + timedelta(hours=1)
    await base_with_data.update('1', operations, expire_at=expires_at)
    item = get_item(deta_base, '1')
    assert item is not None
    assert TTL_ATTRIBUTE in item

    # Test bad key
    operations = ItemUpdate()
    await base_with_data.update(0, operations)  # type: ignore


async def test_query(base_with_data: AsyncDetaBase) -> None:
    """Test the query method.

    Args:
        base_with_data (AsyncDetaBase): An AsyncDetaBase instance with data.
    """
    # Fetch all items
    res = await base_with_data.query()
    assert len(res.items) == len(test_keyed_items)

    # Fetch items with limit
    res = await base_with_data.query(limit=2)
    assert len(res.items) == 2
    assert res.last == '2'

    # Fetch items with pagination
    res = await base_with_data.query(limit=1)
    items = res.items
    while res.last:
        res = await base_with_data.query(last=res.last, limit=1)
        items += res.items

    assert all(item in items for item in test_keyed_items)

    # Fetch items with query
    res = await base_with_data.query(query=[{'age?lt': 30, 'age?gt': 21}])
    assert res.items[0] == test_keyed_items[2]

    # Bad query
    res = await base_with_data.query(query={'age?': 30})
    assert not res.items
