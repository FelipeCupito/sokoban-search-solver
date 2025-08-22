from src.core.interfaces import IHeuristic
from src.core.state import SokobanState
import numpy as np

class ManhattanHeuristic(IHeuristic):
    """Manhattan distance heurisic fro Sokoban search algorithm

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
        for box in boxes:
            dist = np.abs(goals-box).sum(axis=1)
            h = h + dist.min()
        return h

