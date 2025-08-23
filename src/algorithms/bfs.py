from collections import deque
from src.core.interfaces import ISearchAlgorithm, IHeuristic
from typing import Optional


class BFSAlgorithm(ISearchAlgorithm):
    """Breadth-First Search con estructura de datos integrada"""
    
    def __init__(self):
        self._queue = deque()
    
    def add(self, item, heuristic: Optional[IHeuristic] = None):
        self._queue.append(item)
    
    def get_next(self):
        return self._queue.popleft()
    
    def has_next(self) -> bool:
        return len(self._queue) > 0
    
    def size(self) -> int:
        return len(self._queue)
    
    def needs_heuristic(self) -> bool:
        return False

    def should_cache_cost(self) -> bool:
        return False

    def get_algorithm_type(self) -> str:
        return "BFS"