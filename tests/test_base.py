"""Tests for base module."""


from os import getenv

import pytest
from dotenv import load_dotenv

from deta_py.base import DetaBase

load_dotenv()


@pytest.fixture
def base() -> DetaBase:
    """Fixture for DetaBase class.

    Returns:
        DetaBase: DetaBase instance.
    """
    data_key = getenv('TEST_DATA_KEY')
    if data_key is None:
        pytest.skip('DETA_TEST_DATA_KEY is not set')

    return DetaBase(data_key=data_key, base_name='test')


def test_put(base: DetaBase) -> None:
    """Test put method.

    Args:
        base (DetaBase): DetaBase instance.
    """
    items = [
        {'key': '1', 'value': 'one'},
        {'key': '2', 'value': 'two'},
    ]
    processed = base.put(*items)
    assert processed == items

    items = [
        {'key': str(i)}
        for i in range(100)
    ]
    processed = base.put(*items)
    assert processed == items
