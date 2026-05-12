from __future__ import annotations

import random
from collections import deque
from uuid import uuid4

from fastapi import HTTPException

from app.models.domain import MazeCell, MazePosition, MazeSession
from app.models.schemas import (
    MazeCellPayload,
    MazeMoveRequest,
    MazeMoveResponse,
    MazePositionPayload,
    MazeSessionResponse,
    MazeStartRequest,
)


class MazeService:
    """Manage maze sessions that reinforce correctly translated words."""

    _DIRECTIONS = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, default_size: int = 9) -> None:
        self._default_size = default_size
        self._sessions: dict[str, MazeSession] = {}

    def start_session(self, request: MazeStartRequest) -> MazeSessionResponse:
        target_word = "".join(ch for ch in request.target_word.strip() if ch.isalpha())
        if not target_word:
            raise HTTPException(status_code=400, detail="target_word must contain letters")

        size = max(self._default_size, len(target_word) * 3 + 5)
        if size % 2 == 0:
            size += 1

        grid = self._build_grid(size)
        start = MazePosition(row=size // 2, col=size // 2)
        letter_positions = self._assign_letters(target_word.upper(), start, grid)
        session_id = uuid4().hex
        session = MazeSession(
            session_id=session_id,
            target_word=target_word.upper(),
            collected_letters=[],
            player_position=start,
            cells=grid,
            letter_positions=letter_positions,
            status="active",
            steps_taken=0,
        )
        self._sessions[session_id] = session
        return self._to_response(session)

    def get_session(self, session_id: str) -> MazeSessionResponse:
        session = self._require_session(session_id)
        return self._to_response(session)

    def move(self, session_id: str, request: MazeMoveRequest) -> MazeMoveResponse:
        session = self._require_session(session_id)
        if session.status != "active":
            return MazeMoveResponse(
                moved=False,
                hit_wall=False,
                collected_letter="",
                completed=True,
                state=self._to_response(session),
                message="This maze is already completed.",
            )

        delta = self._DIRECTIONS.get(request.direction)
        if delta is None:
            raise HTTPException(status_code=400, detail="Invalid direction")

        next_row = session.player_position.row + delta[0]
        next_col = session.player_position.col + delta[1]
        target_cell = self._cell_at(session.cells, next_row, next_col)
        if target_cell is None or target_cell.kind == "wall":
            return MazeMoveResponse(
                moved=False,
                hit_wall=True,
                collected_letter="",
                completed=False,
                state=self._to_response(session),
                message="You hit a wall.",
            )

        session.player_position = MazePosition(row=next_row, col=next_col)
        session.steps_taken += 1

        collected_letter = ""
        message = "Moved."
        if target_cell.kind == "goal" and target_cell.letter:
            expected_letter = session.target_word[len(session.collected_letters)]
            if target_cell.letter == expected_letter:
                session.collected_letters.append(target_cell.letter)
                collected_letter = target_cell.letter
                target_cell.kind = "path"
                target_cell.letter = ""
                message = f"Collected {collected_letter}."
            else:
                message = f"Find {expected_letter} before collecting {target_cell.letter}."

        if len(session.collected_letters) == len(session.target_word):
            session.status = "completed"
            message = "Word completed!"

        return MazeMoveResponse(
            moved=True,
            hit_wall=False,
            collected_letter=collected_letter,
            completed=session.status == "completed",
            state=self._to_response(session),
            message=message,
        )

    def _require_session(self, session_id: str) -> MazeSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Maze session not found")
        return session

    def _build_grid(self, size: int) -> list[list[MazeCell]]:
        grid = [[MazeCell(row=row, col=col, kind="wall") for col in range(size)] for row in range(size)]
        start = MazePosition(row=size // 2, col=size // 2)
        stack = [start]
        grid[start.row][start.col].kind = "path"

        while stack:
            current = stack[-1]
            neighbors: list[tuple[MazePosition, MazePosition]] = []
            directions = list(self._DIRECTIONS.values())
            random.shuffle(directions)

            for delta_row, delta_col in directions:
                next_row = current.row + delta_row * 2
                next_col = current.col + delta_col * 2
                if not (1 <= next_row < size - 1 and 1 <= next_col < size - 1):
                    continue
                if grid[next_row][next_col].kind == "path":
                    continue
                wall = MazePosition(row=current.row + delta_row, col=current.col + delta_col)
                target = MazePosition(row=next_row, col=next_col)
                neighbors.append((wall, target))

            if not neighbors:
                stack.pop()
                continue

            wall, target = random.choice(neighbors)
            grid[wall.row][wall.col].kind = "path"
            grid[target.row][target.col].kind = "path"
            stack.append(target)

        return grid

    def _assign_letters(
        self,
        target_word: str,
        start: MazePosition,
        grid: list[list[MazeCell]],
    ) -> list[MazePosition]:
        distances = self._bfs_distances(start, grid)
        min_start_distance = max(4, len(grid) // 4)
        dead_ends: list[MazePosition] = []
        fallback: list[MazePosition] = []

        for row in range(len(grid)):
            for col in range(len(grid[row])):
                distance = distances.get((row, col))
                if distance is None or distance < min_start_distance:
                    continue
                if grid[row][col].kind != "path":
                    continue
                position = MazePosition(row=row, col=col)
                fallback.append(position)
                if self._is_dead_end(row, col, grid):
                    dead_ends.append(position)

        candidates = dead_ends if len(dead_ends) >= len(target_word) else fallback
        positions = self._choose_spread_positions(candidates, target_word, grid)
        if len(positions) < len(target_word):
            raise HTTPException(status_code=500, detail="Unable to place maze letters")

        for letter, position in zip(target_word, positions):
            grid[position.row][position.col].kind = "goal"
            grid[position.row][position.col].letter = letter
        return positions

    def _choose_spread_positions(
        self,
        candidates: list[MazePosition],
        target_word: str,
        grid: list[list[MazeCell]],
    ) -> list[MazePosition]:
        pair_min_distance = max(4, len(grid) // 5)
        for threshold in range(pair_min_distance, 1, -1):
            positions = self._try_choose_spread_positions(candidates, len(target_word), grid, threshold)
            if len(positions) == len(target_word):
                return positions

        shuffled = candidates[:]
        random.shuffle(shuffled)
        return shuffled[: len(target_word)]

    def _try_choose_spread_positions(
        self,
        candidates: list[MazePosition],
        count: int,
        grid: list[list[MazeCell]],
        threshold: int,
    ) -> list[MazePosition]:
        pool = candidates[:]
        random.shuffle(pool)
        selected: list[MazePosition] = []
        selected_distances: list[dict[tuple[int, int], int]] = []

        while pool and len(selected) < count:
            valid = [
                position for position in pool
                if all(distances.get((position.row, position.col), 0) >= threshold for distances in selected_distances)
            ]
            if not valid:
                break
            choice = random.choice(valid)
            selected.append(choice)
            selected_distances.append(self._bfs_distances(choice, grid))
            pool = [position for position in pool if position != choice]

        return selected

    def _bfs_distances(self, start: MazePosition, grid: list[list[MazeCell]]) -> dict[tuple[int, int], int]:
        queue = deque([(start.row, start.col, 0)])
        visited = {(start.row, start.col)}
        distances: dict[tuple[int, int], int] = {(start.row, start.col): 0}

        while queue:
            row, col, distance = queue.popleft()
            for delta_row, delta_col in self._DIRECTIONS.values():
                next_row = row + delta_row
                next_col = col + delta_col
                if (next_row, next_col) in visited:
                    continue
                cell = self._cell_at(grid, next_row, next_col)
                if cell is None or cell.kind == "wall":
                    continue
                visited.add((next_row, next_col))
                distances[(next_row, next_col)] = distance + 1
                queue.append((next_row, next_col, distance + 1))
        return distances

    def _shortest_path(self, start: MazePosition, goal: MazePosition, grid: list[list[MazeCell]]) -> list[MazePosition]:
        start_key = (start.row, start.col)
        goal_key = (goal.row, goal.col)
        queue = deque([start_key])
        parents: dict[tuple[int, int], tuple[int, int] | None] = {start_key: None}

        while queue:
            row, col = queue.popleft()
            if (row, col) == goal_key:
                break
            for delta_row, delta_col in self._DIRECTIONS.values():
                next_key = (row + delta_row, col + delta_col)
                if next_key in parents:
                    continue
                cell = self._cell_at(grid, next_key[0], next_key[1])
                if cell is None or cell.kind == "wall":
                    continue
                parents[next_key] = (row, col)
                queue.append(next_key)

        if goal_key not in parents:
            return []

        path: list[MazePosition] = []
        current: tuple[int, int] | None = goal_key
        while current is not None:
            path.append(MazePosition(row=current[0], col=current[1]))
            current = parents[current]
        path.reverse()
        return path

    def _is_dead_end(self, row: int, col: int, grid: list[list[MazeCell]]) -> bool:
        open_neighbors = 0
        for delta_row, delta_col in self._DIRECTIONS.values():
            cell = self._cell_at(grid, row + delta_row, col + delta_col)
            if cell is not None and cell.kind != "wall":
                open_neighbors += 1
        return open_neighbors <= 1

    @staticmethod
    def _cell_at(grid: list[list[MazeCell]], row: int, col: int) -> MazeCell | None:
        if row < 0 or col < 0 or row >= len(grid) or col >= len(grid[row]):
            return None
        return grid[row][col]

    def _to_response(self, session: MazeSession) -> MazeSessionResponse:
        next_letter, next_position, next_path = self._next_target_hint(session)
        next_distance = len(next_path) - 1 if next_path else None
        return MazeSessionResponse(
            session_id=session.session_id,
            target_word=session.target_word,
            collected_letters=session.collected_letters,
            remaining_letters=self._remaining_letters(session),
            player_position=MazePositionPayload(
                row=session.player_position.row,
                col=session.player_position.col,
            ),
            cells=[
                [MazeCellPayload(row=cell.row, col=cell.col, kind=cell.kind, letter=cell.letter) for cell in row]
                for row in session.cells
            ],
            status=session.status,
            steps_taken=session.steps_taken,
            shortest_goal_distance=next_distance,
            next_target_letter=next_letter,
            next_target_position=self._to_position_payload(next_position) if next_position else None,
            next_target_distance=next_distance,
            next_target_path=[self._to_position_payload(position) for position in next_path],
        )

    def _next_target_hint(self, session: MazeSession) -> tuple[str, MazePosition | None, list[MazePosition]]:
        next_index = len(session.collected_letters)
        if session.status != "active" or next_index >= len(session.target_word):
            return "", None, []

        position = session.letter_positions[next_index]
        cell = self._cell_at(session.cells, position.row, position.col)
        if cell is None or cell.kind != "goal":
            return "", None, []

        return session.target_word[next_index], position, self._shortest_path(session.player_position, position, session.cells)

    @staticmethod
    def _to_position_payload(position: MazePosition) -> MazePositionPayload:
        return MazePositionPayload(row=position.row, col=position.col)

    def _remaining_letters(self, session: MazeSession) -> list[str]:
        remaining = list(session.target_word)
        for letter in session.collected_letters:
            if letter in remaining:
                remaining.remove(letter)
        return remaining

    def _closest_goal_distance(self, session: MazeSession) -> int | None:
        remaining_positions = []
        for position in session.letter_positions:
            cell = self._cell_at(session.cells, position.row, position.col)
            if cell is not None and cell.kind == "goal" and cell.letter:
                remaining_positions.append(position)
        if not remaining_positions:
            return None

        distances = self._bfs_distances(session.player_position, session.cells)
        reachable = [
            distances[(position.row, position.col)]
            for position in remaining_positions
            if (position.row, position.col) in distances
        ]
        return min(reachable) if reachable else None
