from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")


def lower_bound(items: Sequence[T], target: K, key: Callable[[T], K] | None = None) -> int:
    """Find the first index whose value is not less than the target.

    Args:
        items: Sorted sequence to search.
        target: Boundary value to locate.
        key: Optional function that maps each item to its comparable key.

    Returns:
        The insertion index that keeps the sequence sorted.
    """
    left = 0
    right = len(items)

    while left < right:
        middle = (left + right) // 2
        value = key(items[middle]) if key else items[middle]
        if value < target:
            left = middle + 1
        else:
            right = middle

    return left
