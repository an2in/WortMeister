from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")


def merge_sort(items: Sequence[T], key: Callable[[T], K] | None = None) -> list[T]:
    values = list(items)
    if len(values) <= 1:
        return values

    middle = len(values) // 2
    left = merge_sort(values[:middle], key)
    right = merge_sort(values[middle:], key)
    return _merge(left, right, key)


def _merge(left: list[T], right: list[T], key: Callable[[T], K] | None) -> list[T]:
    merged: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        left_value = key(left[left_index]) if key else left[left_index]
        right_value = key(right[right_index]) if key else right[right_index]
        if left_value <= right_value:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1

    return merged
