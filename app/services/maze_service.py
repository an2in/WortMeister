from __future__ import annotations

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

        size = max(self._default_size, len(target_word) * 2 + 3)
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
            )

        session.player_position = MazePosition(row=next_row, col=next_col)
        session.steps_taken += 1

        collected_letter = ""
        if target_cell.kind == "goal" and target_cell.letter:
            if target_cell.letter not in session.collected_letters:
                session.collected_letters.append(target_cell.letter)
                collected_letter = target_cell.letter
            target_cell.kind = "path"
            target_cell.letter = ""

        if len(session.collected_letters) >= len(session.target_word):
            session.status = "completed"

        return MazeMoveResponse(
            moved=True,
            hit_wall=False,
            collected_letter=collected_letter,
            completed=session.status == "completed",
            state=self._to_response(session),
        )

    def _require_session(self, session_id: str) -> MazeSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Maze session not found")
        return session

    def _build_grid(self, size: int) -> list[list[MazeCell]]:
        grid: list[list[MazeCell]] = []
        for row in range(size):
            current_row: list[MazeCell] = []
            for col in range(size):
                is_border = row in {0, size - 1} or col in {0, size - 1}
                kind = "wall" if is_border else "path"
                if row % 4 == 0 and 1 < col < size - 2:
                    kind = "wall"
                if col % 4 == 0 and 1 < row < size - 2:
                    kind = "wall"
                current_row.append(MazeCell(row=row, col=col, kind=kind))
            grid.append(current_row)

        center = size // 2
        for offset in range(-1, 2):
            grid[center][center + offset].kind = "path"
            grid[center + offset][center].kind = "path"
        return grid

    def _assign_letters(
        self,
        target_word: str,
        start: MazePosition,
        grid: list[list[MazeCell]],
    ) -> list[MazePosition]:
        distances = self._bfs_distances(start, grid)
        candidate_cells: list[tuple[int, int, int]] = []
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                distance = distances.get((row, col))
                if distance is None or distance < 3:
                    continue
                if grid[row][col].kind != "path":
                    continue
                if self._is_dead_end(row, col, grid):
                    candidate_cells.append((distance, row, col))

        candidate_cells.sort(reverse=True)
        if len(candidate_cells) < len(target_word):
            fallback_cells: list[tuple[int, int, int]] = []
            for row in range(len(grid)):
                for col in range(len(grid[row])):
                    distance = distances.get((row, col))
                    if distance is None or distance < 3:
                        continue
                    if grid[row][col].kind != "path":
                        continue
                    fallback_cells.append((distance, row, col))
            fallback_cells.sort(reverse=True)
            candidate_cells = fallback_cells

        if len(candidate_cells) < len(target_word):
            raise HTTPException(status_code=500, detail="Unable to place maze letters")

        positions: list[MazePosition] = []
        for index, letter in enumerate(target_word):
            _, row, col = candidate_cells[index]
            grid[row][col].kind = "goal"
            grid[row][col].letter = letter
            positions.append(MazePosition(row=row, col=col))
        return positions

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
            shortest_goal_distance=self._closest_goal_distance(session),
        )

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
