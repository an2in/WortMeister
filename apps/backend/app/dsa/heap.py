from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    """Array-backed min heap used by scheduling services."""

    def __init__(self, values: list[T] | None = None) -> None:
        """Build a heap from optional initial values."""
        self._items = list(values or [])
        self._heapify()

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def push(self, value: T) -> None:
        """Insert a value while preserving the heap invariant."""
        self._items.append(value)
        self._sift_up(len(self._items) - 1)

    def pop(self) -> T:
        """Remove and return the smallest value."""
        if not self._items:
            raise IndexError("pop from empty heap")

        root = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return root

    def _heapify(self) -> None:
        index = len(self._items) // 2 - 1
        while index >= 0:
            self._sift_down(index)
            index -= 1

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._items[parent] <= self._items[index]:
                break
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def _sift_down(self, index: int) -> None:
        length = len(self._items)
        while True:
            left = index * 2 + 1
            right = left + 1
            smallest = index

            if left < length and self._items[left] < self._items[smallest]:
                smallest = left
            if right < length and self._items[right] < self._items[smallest]:
                smallest = right
            if smallest == index:
                break

            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest
