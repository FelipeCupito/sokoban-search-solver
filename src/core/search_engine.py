import time
from typing import Optional, List, Set, Tuple, Dict, Callable
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
        start_node = StateNode(initial_state, parent=None, action="START")
        if initial_state.is_goal():
            return self._create_success_from_node(start_node)

        self.algorithm.add(start_node, self.heuristic)
        self._update_frontier_size()

        if self.algorithm.cache_cost():
            return self._search_with_cost_caching(initial_state)
        else:
            return self._search_without_cost_caching(initial_state)

    def _search_with_cost_caching(self, initial_state: SokobanState) -> SearchResult:
        best_costs: Dict[SokobanState, int] = {initial_state: 0}
        closed_set: Set[SokobanState] = set()

        while self.algorithm.has_next():
            current_node = self.algorithm.get_next()
            if current_node.cost > best_costs.get(current_node.state, float("inf")):
                continue

            closed_set.add(current_node.state)
            if current_node.state.is_goal():
                return self._create_success_from_node(current_node)

            self.nodes_expanded += 1

            for successor_node in current_node.get_successors():
                state = successor_node.state
                g = successor_node.cost
                if g >= best_costs.get(state, float("inf")):
                    continue

                best_costs[state] = g
                successor_node.parent = current_node
                if state in closed_set:
                    closed_set.remove(state)

                self.algorithm.add(successor_node, self.heuristic)
                self._update_frontier_size()

        return self._create_failure()

    def _search_without_cost_caching(self, initial_state: SokobanState) -> SearchResult:
        closed_states: Set[SokobanState] = {initial_state}

        while self.algorithm.has_next():
            current_node = self.algorithm.get_next()
            if current_node.state.is_goal():
                return self._create_success_from_node(current_node)

            self.nodes_expanded += 1

            for successor_node in current_node.get_successors():
                state = successor_node.state
                if state in closed_states:
                    continue

                closed_states.add(state)
                successor_node.parent = current_node
                self.algorithm.add(successor_node, self.heuristic)
                self._update_frontier_size()

        return self._create_failure()

    def _update_frontier_size(self) -> None:
        self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())

    def _create_success_from_node(self, node: StateNode) -> SearchResult:
        states, actions = _reconstruct_path_from_node(node)
        return self._create_success(states, actions)

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
