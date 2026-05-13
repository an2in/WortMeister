from __future__ import annotations

import random
from typing import TypeVar

T = TypeVar("T")


def shuffle_in_place(items: list[T]) -> None:
    """Shuffle values in place with the Fisher-Yates algorithm.

    Args:
        items: Mutable list whose values will be reordered in place.
    """
    index = len(items) - 1
    while index > 0:
        swap_index = random.randrange(index + 1)
        items[index], items[swap_index] = items[swap_index], items[index]
        index -= 1


def choose_one(items: list[T]) -> T:
    """Return one random item by generating an index manually.

    Args:
        items: Non-empty list to sample from.

    Returns:
        A randomly selected value from the list.

    Raises:
        IndexError: If the list is empty.
    """
    if not items:
        raise IndexError("choose from empty list")
    return items[random.randrange(len(items))]
