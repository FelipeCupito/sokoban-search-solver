
from src.core.interfaces import ISearchAlgorithm, IHeuristic
from src.core.state_node import StateNode


class GreedyAlgorithm(ISearchAlgorithm):
    """Breadth-First Search con estructura de datos integrada"""
    
    def __init__(self):
        self._nodes = []
    
    def add(self, item: StateNode, heuristic: IHeuristic):
        self._nodes.append((heuristic.calculate(item.state), item))
        self._nodes.sort(key=lambda x:x[0])
    
    def get_next(self) -> StateNode:
        return self._nodes.pop(0)[1]
    
    def has_next(self) -> bool:
        return len(self._nodes) > 0
    
    def size(self) -> int:
        return len(self._nodes)
    
    def needs_heuristic(self) -> bool:
        return True

    def should_cache_cost(self) -> bool:
        return False

    def get_algorithm_type(self) -> str:
        return "Greedy"