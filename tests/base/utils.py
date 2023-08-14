"""Tests utilities.

Contains functions related to usage of official Deta SDK.
"""


from typing import Any, Optional

from deta.base import _Base  # type: ignore # noqa: WPS450


def clear_base(deta_base: _Base) -> None:
    """Clear the base.

    Args:
        deta_base (_Base): A deta.base._Base instance.
    """
    res = deta_base.fetch()
    items = res.items
    while res.last is not None:
        res = deta_base.fetch(last=res.last)
        items.extend(res.items)

    for item in items:
        deta_base.delete(item['key'])


def put_items(deta_base: _Base, items: list[dict[str, Any]]) -> None:
    """Put items in the base.

    Args:
        deta_base (_Base): A deta.base._Base instance.
        items (list[dict[str, str]]): A list of items to put in the base.
    """
    deta_base.put_many(items)


def get_items(deta_base: _Base) -> list[dict[str, Any]]:
    """Get items from the base.

    Args:
        deta_base (_Base): A deta.base._Base instance.

    Returns:
        list[dict[str, str]]: A list of items from the base.
    """
    res = deta_base.fetch()
    items: list[dict[str, Any]] = res.items
    while res.last is not None:
        res = deta_base.fetch(last=res.last)
        items.extend(res.items)

    return items


def get_item(deta_base: _Base, key: str) -> Optional[dict[str, Any]]:
    """Get an item from the base.

    Args:
        deta_base (_Base): A deta.base._Base instance.
        key (str): A key of the item.

    Returns:
        Optional[dict[str, str]]: An item from the base.
    """
    item: Optional[dict[str, Any]] = deta_base.get(key)
    return item
