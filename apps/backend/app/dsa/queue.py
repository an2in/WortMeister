from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class ArrayQueue(Generic[T]):
    """FIFO queue backed by a list and moving head index."""

    def __init__(self, values: list[T] | None = None) -> None:
        """Create a queue from optional initial values."""
        self._items = list(values or [])
        self._head = 0

    def __bool__(self) -> bool:
        return self._head < len(self._items)

    def push(self, value: T) -> None:
        """Append a value to the back of the queue."""
        self._items.append(value)

    def pop(self) -> T:
        """Remove and return the front queue value."""
        if not self:
            raise IndexError("pop from empty queue")

        value = self._items[self._head]
        self._head += 1
        if self._head > 32 and self._head * 2 > len(self._items):
            self._items = self._items[self._head:]
            self._head = 0
        return value
