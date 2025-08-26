import heapq
import itertools
import math
from typing import Optional, Any

from src.core.interfaces import ISearchAlgorithm, IHeuristic
from src.core.state_node import StateNode


def _eval_heuristic(h: IHeuristic | Any, node: StateNode) -> float:
    """Evaluate heuristic on the node's state and return as float (may be inf)."""
    state = node.state
    if hasattr(h, "calculate"):
        return float(h.calculate(state))

    return float(h(state))


class AStar(ISearchAlgorithm):
    """A* search algorithm implementation using a priority queue"""

    def __init__(self) -> None:
        # (f, h, tie, node) where f and h are floats to allow inf
        self._pq: list[tuple[float, float, int, StateNode]] = []
        self._tie = itertools.count()

    def add(self, node: StateNode, heuristic: Optional[IHeuristic] = None) -> None:
        if heuristic is None:
            raise ValueError("A* requires a heuristic")

        g = node.cost
        h = _eval_heuristic(heuristic, node)
        # infinite heuristic (deadlocks or pruned states)
        if math.isinf(h):
            return
        f = g + h
        heapq.heappush(self._pq, (f, h, next(self._tie), node))

    def get_next(self) -> StateNode:
        _, _, _, node = heapq.heappop(self._pq)
        return node

    def has_next(self) -> bool:
        return bool(self._pq)

    def should_cache_cost(self) -> bool:
        return True

    def size(self) -> int:
        return len(self._pq)

    def needs_heuristic(self) -> bool:
        return True

    def get_algorithm_type(self) -> str:
        return "ASTAR"