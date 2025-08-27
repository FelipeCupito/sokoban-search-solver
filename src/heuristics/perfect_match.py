from typing import Tuple
from munkres import Munkres
from src.core.interfaces import IHeuristic
from src.core.state import SokobanState
import numpy as np

class PerfectMatch(IHeuristic):
    """
    Optimal box-goal matching: Hungarian algorithm (Munkres implementation)
    """
    def __init__(self):
        self._munkres = Munkres()
        return

    def calculate(self, state: SokobanState) -> int:
        boxes = [b for b in state.boxes if b not in state.goals]
        goals = list(state.goals)
        if len(boxes) == 0:
            return 0

        cost_matrix = [[self._minkowski(box, goal) for goal in goals] for box in boxes]
        indexes = self._munkres.compute(cost_matrix)

        return sum(cost_matrix[row][col] for row, col in indexes)

    def _minkowski(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        diff = np.abs(np.array(a) - np.array(b)) ** 1

        return np.power(diff.sum(), 1 / 1)
