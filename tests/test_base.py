"""Integration tests for the DetaBase class.

This is beta implementation, so the tests are not complete.
"""

import os

import pytest
from dotenv import load_dotenv

from deta_py.base import DetaBase, ItemUpdate

load_dotenv()

TEST_DATA_KEY = os.getenv('TEST_DATA_KEY')

TEST_BASE_NAME = os.getenv('TEST_BASE_NAME')


@pytest.fixture
def base() -> DetaBase:
    """Fixture for DetaBase class.

    Returns:
        DetaBase: DetaBase instance.
    """
    if not TEST_DATA_KEY or not TEST_BASE_NAME:
        pytest.skip('Missing test data key or base name.')

    return DetaBase(
        data_key=TEST_DATA_KEY,
        base_name=TEST_BASE_NAME,
    )


def test_put_and_get_item(base: DetaBase) -> None:
    """Test put and get item.

    Args:
        base (DetaBase): DetaBase instance.
    """
    test_item = {'key': 'test_key', 'value': 'test_value'}

    # Put the item
    processed_items = base.put(test_item)
    assert processed_items == [test_item]

    # Get the item
    retrieved_item = base.get(test_item['key'])

    assert retrieved_item is not None
    assert retrieved_item['value'] == test_item['value']


def test_update_item(base: DetaBase) -> None:
    """Test update item.

    Args:
        base (DetaBase): DetaBase instance.
    """
    test_key = 'test_key'
    test_item = {
        'key': test_key,
        'field1': 'value',
        'field2': ['value'],
        'field3': 0,
        'field4': None,
    }
    base.put(test_item)

    # Update the item
    update_operations = ItemUpdate()
    update_operations.set(field1='new_value')
    update_operations.append(field2=['new_value'])
    update_operations.increment(field3=1)
    update_operations.delete('field4')

    result = base.update(test_key, update_operations)
    assert result

    # Get the updated item
    retrieved_item = base.get(test_key)

    assert retrieved_item is not None
    assert retrieved_item['field1'] == 'new_value'
    assert retrieved_item['field2'] == ['value', 'new_value']
    assert retrieved_item['field3'] == 1
    assert 'field4' not in retrieved_item


def test_delete_item(base: DetaBase) -> None:
    """Test delete item.

    Args:
        base (DetaBase): DetaBase instance.
    """
    test_key = 'test_key'
    test_item = {'key': test_key, 'value': 'to_be_deleted'}
    base.put(test_item)

    # Delete the item
    base.delete(test_key)

    # Try to get the deleted item
    retrieved_item = base.get(test_key)

    assert retrieved_item is None


def test_insert_item(base: DetaBase) -> None:
    """Test insert item.

    Args:
        base (DetaBase): DetaBase instance.
    """
    test_item = {'key': 'test_key', 'value': 'test_value'}

    # Insert the item
    inserted_item = base.insert(test_item)

    assert inserted_item is not None
    assert inserted_item['key'] == test_item['key']


def test_query_items(base: DetaBase) -> None:
    """Test query items.

    Args:
        base (DetaBase): DetaBase instance.
    """
    test_items = [
        {'key': 'item1', 'value': 'value1'},
        {'key': 'item2', 'value': 'value2'},
        # Add more test items
    ]
    base.put(*test_items)

    # Query for items
    query = [{'value': 'value1'}]
    query_result = base.query(query)

    assert query_result.items
    assert query_result.count == 1
    assert query_result.last is None
