from src.core.interfaces import ISearchAlgorithm


class DFS(ISearchAlgorithm):
    """Pure Depth-First Search"""
    def __init__(self):
        self._stack = []

    def add(self, item, heuristic=None):
        self._stack.append(item)

    def get_next(self):
        return self._stack.pop()

    def has_next(self) -> bool:
        return len(self._stack) > 0

    def size(self) -> int:
        return len(self._stack)

    def needs_heuristic(self) -> bool:
        return False

    def should_cache_cost(self) -> bool:
        return False

    def get_algorithm_type(self) -> str:
        return "DFS"