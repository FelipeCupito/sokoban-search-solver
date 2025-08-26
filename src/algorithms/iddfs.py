from src.core.interfaces import ISearchAlgorithm
from typing import Optional
from src.core.state_node import StateNode
from src.core.interfaces import IHeuristic


class IDDFS(ISearchAlgorithm):
    """Iterative Deepening Depth-First Search"""
    
    _INITIAL_DEPTH_LIMIT = 50
    _DEPTH_INCREMENT = 5
    
    def __init__(self):
        self._stack = []
        self._current_depth_limit = self._INITIAL_DEPTH_LIMIT
        self._items_at_depth = {}
        self._max_depth_reached = False

    def add(self, item: StateNode, heuristic: Optional[IHeuristic] = None):
        depth = self._get_node_depth(item)
        
        if depth <= self._current_depth_limit:
            self._stack.append(item)
        else:
            if depth not in self._items_at_depth:
                self._items_at_depth[depth] = []
            self._items_at_depth[depth].append(item)
            self._max_depth_reached = True
    
    def get_next(self):
        if self._stack:
            return self._stack.pop()
        
        if self._max_depth_reached:
            self._increase_depth_limit()
            self._reload_items_for_current_depth()
            if self._stack:
                return self._stack.pop()
        
        return None
    
    def has_next(self) -> bool:
        return len(self._stack) > 0 or self._max_depth_reached
    
    def size(self) -> int:
        total_size = len(self._stack)
        for items_list in self._items_at_depth.values():
            total_size += len(items_list)
        return total_size
    
    def needs_heuristic(self) -> bool:
        return False
    
    def should_cache_cost(self) -> bool:
        return False
    
    def get_algorithm_type(self) -> str:
        return "IDDFS"
    
    def _get_node_depth(self, node: 'StateNode') -> int:
        depth = 0
        current = node
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth
    
    def _increase_depth_limit(self):
        self._current_depth_limit += self._DEPTH_INCREMENT
        self._max_depth_reached = False
    
    def _reload_items_for_current_depth(self):
        for depth in range(self._current_depth_limit + 1):
            if depth in self._items_at_depth:
                self._stack.extend(self._items_at_depth[depth])
                del self._items_at_depth[depth]