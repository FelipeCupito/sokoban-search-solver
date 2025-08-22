from src.core.interfaces import IHeuristic
from src.core.state import SokobanState
import numpy as np

class PerfectMatch(IHeuristic):
    """Heuristic that matches box-goal pairs to ensure minimum l1 distance.

    Args:
        IHeuristic (_type_): _description_
    """
    def __init__(self):
        return
    
    def calculate(self, state: SokobanState) -> int:
        """Calculates the total sum of the Manhattan distance from each box to it's nearest goal.

        Args:
            state (SokobanState): Current map of the game.

        Returns:
            int: total sum of all Manhatan distances
        """
        boxes = np.array(list(state.boxes))
        goals = np.array(list(state.goals))
        h = 0
        l1_mat = np.zeros((len(boxes),len(goals)))
        for i,box in enumerate(boxes):
            l1_mat[i:] = np.abs(goals-box).sum(axis=1)
        for i in range(len(boxes)):
            min_idx = np.argmin(l1_mat)
            box_idx = min_idx//len(goals)
            goal_idx = min_idx%len(goals)
            h = h+l1_mat[box_idx,goal_idx]
            l1_mat[box_idx] = np.inf
            l1_mat[:,goal_idx] = np.inf
        return h

