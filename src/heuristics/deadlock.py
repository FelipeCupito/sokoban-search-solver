from src.core.interfaces import IHeuristic
from typing import Tuple, Set, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from src.core.state import SokobanState


class DeadlockDetector(IHeuristic):
    """Applies Manhattan distance heuristic plus detects and prunes deadlocks."""
    # Cache of aisle-end pruning per (walls, goals)
    _aisle_cache: Dict[tuple[frozenset[Tuple[int, int]], frozenset[Tuple[int, int]]], frozenset[Tuple[int, int]]] = {}

    def calculate(self, state: 'SokobanState') -> int:
        h = 0
        boxes = np.array(list(state.boxes))
        goals = np.array(list(state.goals))
        for box in boxes:
            dist = np.abs(goals - box).sum(axis=1)
            h = h + dist.min()
        for box in state.boxes:
            if self.is_deadlock(box, state.boxes, state.walls, state.goals):
                h = np.inf
                break
        return h

    @staticmethod
    def is_deadlock(
            box_pos: Tuple[int, int],
            boxes: frozenset[Tuple[int, int]],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]],
    ) -> bool:
        """Detecta si una caja está en deadlock"""
        if DeadlockDetector._is_corner_deadlock(box_pos, walls, goals):
            return True
        if DeadlockDetector._is_square_deadlock(box_pos, boxes, goals):
            return True
        if DeadlockDetector._is_between_corners_no_door(box_pos, walls, goals):
            return True
        if DeadlockDetector._is_aisle_end_cell(box_pos, walls, goals) and box_pos not in goals:
            return True
        return False

    @staticmethod
    def _is_corner_deadlock(
            pos: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica si la posición es una esquina sin goal"""
        if pos in goals:
            return False

        r, c = pos
        corner_patterns = [
            [(r - 1, c), (r, c - 1)],  # Superior izquierda
            [(r - 1, c), (r, c + 1)],  # Superior derecha
            [(r + 1, c), (r, c - 1)],  # Inferior izquierda
            [(r + 1, c), (r, c + 1)],  # Inferior derecha
        ]
        return any(all(wp in walls for wp in pattern) for pattern in corner_patterns)

    @staticmethod
    def _is_square_deadlock(
            pos: Tuple[int, int],
            boxes: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]]
    ) -> bool:
        """Detecta cuadrados 2x2 de cajas sin goals"""
        r, c = pos
        squares = [
            [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)],       # pos en superior izquierda
            [(r - 1, c - 1), (r - 1, c), (r, c - 1), (r, c)],       # pos en inferior derecha
            [(r - 1, c), (r - 1, c + 1), (r, c), (r, c + 1)],       # pos en inferior izquierda
            [(r, c - 1), (r, c), (r + 1, c - 1), (r + 1, c)],       # pos en superior derecha
        ]
        for square in squares:
            if all(p in boxes for p in square) and not any(p in goals for p in square):
                return True
        return False

    @staticmethod
    def _has_clear_horizontal_path(
            start: Tuple[int, int],
            end: Tuple[int, int],
            walls: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica path horizontal libre"""
        r = start[0]
        start_c, end_c = sorted([start[1], end[1]])
        for c in range(start_c, end_c + 1):
            if (r, c) in walls:
                return False
        return True

    @staticmethod
    def _has_clear_vertical_path(
            start: Tuple[int, int],
            end: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
    ) -> bool:
        """Verifica path vertical libre"""
        c = start[1]
        start_r, end_r = sorted([start[0], end[0]])
        for r in range(start_r, end_r + 1):
            if (r, c) in walls:
                return False
        return True

    @staticmethod
    def _bounds(walls: frozenset[Tuple[int, int]], goals: frozenset[Tuple[int, int]]):
        points = list(walls) + list(goals)
        if not points:
            return 0, 0, 0, 0
        rs = [p[0] for p in points]
        cs = [p[1] for p in points]
        return min(rs), max(rs), min(cs), max(cs)

    @staticmethod
    def _is_between_corners_no_door(
            pos: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]],
    ) -> bool:
        """
        Checks if a box is against a continuous wall (without a "door") and between two corners.
        If no goals are present in the segment, the position is a deadlock.
        """
        r, c = pos
        min_r, max_r, min_c, max_c = DeadlockDetector._bounds(walls, goals)

        # Horizontal scan (top/bottom wall)
        def row_segment_no_door(row: int, col_start: int, wall_row_offset: int) -> bool:
            left = col_start
            while (row + wall_row_offset, left) in walls:
                if (row, left - 1) in walls:
                    break
                left -= 1
                if left < min_c - 2:
                    return False

            right = col_start
            while (row + wall_row_offset, right) in walls:
                if (row, right + 1) in walls:
                    break
                right += 1
                if right > max_c + 2:
                    return False

            return all((row, cc) not in goals for cc in range(left, right + 1))

        # Vertical scan (left/right wall); requires no "door" along the side wall.
        def col_segment_doorless(col: int, row_start: int, adj_col_delta: int) -> bool:
            up = row_start
            while True:
                if (up, col + adj_col_delta) not in walls:
                    return False # door found
                if (up - 1, col) in walls:
                    break  # superior corner
                up -= 1
                if up < min_r - 2:
                    return False

            down = row_start
            while True:
                if (down, col + adj_col_delta) not in walls:
                    return False
                if (down + 1, col) in walls:
                    break  # inferior corner
                down += 1
                if down > max_r + 2:
                    return False

            for rr in range(up, down + 1):
                if (rr, col) in goals:
                    return False # goal found

            return True

        if (r - 1, c) in walls and row_segment_no_door(r, c, -1):
            return True
        if (r + 1, c) in walls and row_segment_no_door(r, c, +1):
            return True
        if (r, c - 1) in walls and col_segment_doorless(c, r, -1):
            return True
        if (r, c + 1) in walls and col_segment_doorless(c, r, +1):
            return True

        return False

    @staticmethod
    def _is_aisle_end_cell(
            pos: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]],
    ) -> bool:
        pruned = DeadlockDetector._get_aisle_pruned_cells(walls, goals)
        return pos in pruned

    @staticmethod
    def _get_aisle_pruned_cells(
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]],
    ) -> frozenset[Tuple[int, int]]:
        """Identifies and caches cells in a grid that are considered "pruned" based on their surroundings"""
        key = (walls, goals)
        cached = DeadlockDetector._aisle_cache.get(key)
        if cached is not None:
            return cached

        min_r, max_r, min_c, max_c = DeadlockDetector._bounds(walls, goals)

        # candidates: all cells (no walls) within bounds
        floor: Set[Tuple[int, int]] = set(
            (r, c)
            for r in range(min_r, max_r + 1)
            for c in range(min_c, max_c + 1)
            if (r, c) not in walls
        )
        blocked: Set[Tuple[int, int]] = set(walls)
        protected_goals = set(goals)

        def is_blocked_neighbor(rr: int, cc: int) -> bool:
            if rr < min_r or rr > max_r or cc < min_c or cc > max_c:
                return True  # out of bounds
            return (rr, cc) in blocked

        changed = True
        while changed:
            changed = False
            to_add = []
            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for (r, c) in floor:
                if (r, c) in blocked or (r, c) in protected_goals:
                    continue
                cnt = sum(1 for dr, dc in dirs if is_blocked_neighbor(r + dr, c + dc))
                if cnt >= 3:
                    to_add.append((r, c))
            if to_add:
                blocked.update(to_add)
                changed = True

        pruned_cells = frozenset(p for p in blocked if p not in walls)
        DeadlockDetector._aisle_cache[key] = pruned_cells

        return pruned_cells