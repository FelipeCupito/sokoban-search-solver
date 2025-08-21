import time
from typing import Optional, Dict, Tuple, List, Set
from src.core.state import SokobanState, StateNode
from src.core.result import SearchResult
from src.core.interfaces import ISearchAlgorithm, IHeuristic


def _reconstruct_path(
        states_by_key: Dict[str, SokobanState],
        parents: Dict[str, Tuple[Optional[str], str]],
        goal_key: str,
) -> Tuple[List[SokobanState], List[str]]:
    """Build the sequence of states and actions from the start to the goal."""
    path_states: List[SokobanState] = []
    path_actions: List[str] = []

    current_key: Optional[str] = goal_key
    while current_key:
        path_states.append(states_by_key[current_key])
        parent_info = parents.get(current_key)
        if not parent_info:
            # Should not happen for a well-formed tree; treat as start
            break

        current_key, action = parent_info
        path_actions.append(action)

    return list(reversed(path_states)), ["START"] + list(reversed(path_actions))



class SearchEngine:
    """ Orchestrates a search using a provided algorithm and an optional heuristic."""

    def __init__(self, algorithm: ISearchAlgorithm, heuristic: Optional[IHeuristic] = None):
        if not algorithm:
            raise ValueError("Algorithm cannot be None")
        if heuristic and not algorithm.needs_heuristic():
            raise ValueError(f"{algorithm.get_algorithm_type()} does not require a heuristic")

        self.algorithm = algorithm
        self.heuristic = heuristic

    def search(self, initial_state: SokobanState) -> SearchResult:
        self._init_metrics()
        
        current_node = StateNode(initial_state)

        # Trivial case: already at the goal.
        if initial_state.is_goal():
            return self._create_success([initial_state], ["START"]) # TODO: hacer que resiva un node

        # Bookkeeping nodes
        closed_nodes: Set[int] = set()
        closed_nodes.add(current_node)

        self.algorithm.add(current_node, self.heuristic)

        # Core search loop driven by the algorithm implementation.
        while self.algorithm.has_next():
            self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())

            current_node = self.algorithm.get_next()

            if current_node in closed_nodes:
                continue

            closed_nodes.add(current_node)
            
            self.nodes_expanded += 1

            for successor_node in current_node.get_successors():

                if successor_node.state.is_goal():
                    return self._create_success(successor_node)

                self.algorithm.add(successor_node, self.heuristic)

        return self._create_failure()

    def _init_metrics(self) -> None:
        self.start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0


    def _create_success(self, state: SokobanState) -> SearchResult:
        
        
        return SearchResult.create_success(
            states = 
            actions,
            self.nodes_expanded,
            self.max_frontier_size,
            time.time() - self.start_time,
            self.algorithm.get_algorithm_type(),
            )

    def _create_failure(self) -> SearchResult:
        return SearchResult.create_failure(
            self.nodes_expanded,
            self.max_frontier_size,
            time.time() - self.start_time,
            self.algorithm.get_algorithm_type(),
            )