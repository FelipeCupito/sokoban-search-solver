from munkres import Munkres
from src.core.interfaces import IHeuristic
from src.core.state import SokobanState
from typing import List, Tuple
import numpy as np


class SumOfDistanceMinimalMatchingCost(IHeuristic):
    """Heuristic that sums the distance from the player to the nearest box
    with the minimal matching cost between boxes and goals.

    - The distance metric used: Minkowski distance (``p=2`` by default)
    - Optimal box-goal matching: Hungarian algorithm (Munkres implementation)
    """

    def __init__(self, p: int = 2):
        self.p = p
        self._munkres = Munkres()

    def _minkowski(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        diff = np.abs(np.array(a) - np.array(b)) ** self.p

        return np.power(diff.sum(), 1 / self.p)

    def _player_to_box(self, player: Tuple[int, int], boxes: List[Tuple[int, int]]) -> float:
        distances = [self._minkowski(player, box) for box in boxes]

        return min(distances) if distances else 0.0

    def _match_boxes_goals(self, boxes: List[Tuple[int, int]], goals: List[Tuple[int, int]]) -> float:
        if not boxes:
            return 0.0
        cost_matrix = [[self._minkowski(box, goal) for goal in goals] for box in boxes]
        indexes = self._munkres.compute(cost_matrix)

        return float(sum(cost_matrix[row][col] for row, col in indexes))

    def calculate(self, state: SokobanState) -> int:
        boxes = [b for b in state.boxes if b not in state.goals]
        goals = list(state.goals)
        h1 = self._player_to_box(state.player_pos, boxes)
        h2 = self._match_boxes_goals(boxes, goals)

        return int(h1 + h2)