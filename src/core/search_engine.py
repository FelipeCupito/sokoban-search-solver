import time
from typing import Optional, List, Set, Tuple
from src.core.state import SokobanState, StateNode
from src.core.result import SearchResult
from src.core.interfaces import ISearchAlgorithm, IHeuristic


def _reconstruct_path_from_node(goal_node: StateNode) -> Tuple[List[SokobanState], List[str]]:
    states, actions = [], []
    while goal_node:
        states.append(goal_node.state)
        actions.append(goal_node.action)
        goal_node = goal_node.parent

    return states[::-1], actions[::-1]


class SearchEngine:
    """ Orchestrates a search using a provided algorithm and an optional heuristic."""

    def __init__(self, algorithm: ISearchAlgorithm, heuristic: Optional[IHeuristic] = None):
        if not algorithm:
            raise ValueError("Algorithm cannot be None")
        if algorithm.needs_heuristic() and heuristic is None:
            raise ValueError(f"{algorithm.get_algorithm_type()} requires a heuristic")

        self.algorithm = algorithm
        self.heuristic = heuristic

    def search(self, initial_state: SokobanState) -> SearchResult:
        self._init_metrics()
        current_node = StateNode(initial_state, parent=None, action="START")

        if initial_state.is_goal():
            states, actions = _reconstruct_path_from_node(current_node)
            return self._create_success(states, actions)

        closed_states: Set[SokobanState] = set()
        closed_states.add(current_node.state)

        self.algorithm.add(current_node, self.heuristic)
        self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())

        # Core search loop driven by the algorithm implementation.
        while self.algorithm.has_next():
            current_node = self.algorithm.get_next()
            self.nodes_expanded += 1

            for successor_node in current_node.get_successors():
                if successor_node.state in closed_states:
                    continue
                closed_states.add(successor_node.state)

                if successor_node.state.is_goal():
                    states, actions = _reconstruct_path_from_node(successor_node)
                    return self._create_success(states, actions)

                self.algorithm.add(successor_node, self.heuristic)
                self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())

        return self._create_failure()

    def _init_metrics(self) -> None:
        self.start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

    def _create_success(self, states: List[SokobanState], actions: List[str]) -> SearchResult:
        return SearchResult.create_success(
            states,
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
