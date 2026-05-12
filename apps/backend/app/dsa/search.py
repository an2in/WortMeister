from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")


def lower_bound(items: Sequence[T], target: K, key: Callable[[T], K] | None = None) -> int:
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
