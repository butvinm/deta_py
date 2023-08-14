"""Tests utilities.

Contains shared fixtures.
"""


from os import getenv

import pytest
from deta import Deta  # type: ignore
from deta.base import _Base  # type: ignore # noqa: WPS450
from dotenv import load_dotenv

load_dotenv()

TEST_DATA_KEY = getenv('TEST_DATA_KEY')

TEST_BASE_NAME = getenv('TEST_BASE_NAME')


@pytest.fixture(scope='session')
def credentials() -> tuple[str, str]:
    """Return a tuple of test data key and base name.

    Returns:
        tuple[str, str]: A tuple of test data key and base name.
    """
    if not TEST_DATA_KEY or not TEST_BASE_NAME:
        pytest.skip('No test data key or base name provided.')

    return TEST_DATA_KEY, TEST_BASE_NAME


@pytest.fixture(scope='session')
def deta_base(credentials: tuple[str, str]) -> _Base:
    """Return a deta.base._Base instance.

    Args:
        credentials (tuple[str, str]): A tuple of test data key and base name.

    Returns:
        _Base: A deta.base._Base instance.
    """
    deta = Deta(credentials[0])
    return deta.Base(credentials[1])
