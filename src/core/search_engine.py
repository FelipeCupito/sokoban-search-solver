import time
from typing import Optional, Dict, Tuple, List, Set
from src.core.state import SokobanState
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
        self._reset_metrics()

    def search(self, initial_state: SokobanState) -> SearchResult:
        self.start_time = time.time()
        self._reset_metrics()

        # Trivial case: already at the goal.
        if initial_state.is_goal():
            return self._create_success([initial_state], ["START"])

        # Bookkeeping maps and sets.
        parents: Dict[str, Tuple[Optional[str], str]] = {}
        states_by_key: Dict[str, SokobanState] = {}
        closed_keys: Set[str] = set()
        seen_keys: Set[str] = set()

        # Seed the frontier with the initial state.
        init_key = initial_state.key()
        parents[init_key] = (None, "START")
        states_by_key[init_key] = initial_state
        seen_keys.add(init_key)
        self.algorithm.add(initial_state, self.heuristic)

        # Core search loop driven by the algorithm implementation.
        while self.algorithm.has_next():
            self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())

            current_state = self.algorithm.get_next()
            current_key = current_state.key()

            if current_key in closed_keys:
                continue

            closed_keys.add(current_key)
            self.nodes_expanded += 1

            for successor, action in current_state.get_successors():
                successor_key = successor.key()
                if successor_key in seen_keys:
                    continue

                parents[successor_key] = (current_key, action)
                states_by_key[successor_key] = successor
                seen_keys.add(successor_key)

                if successor.is_goal():
                    states, actions = _reconstruct_path(states_by_key, parents, successor_key)
                    return self._create_success(states, actions)

                self.algorithm.add(successor, self.heuristic)

        return self._create_failure()

    def _reset_metrics(self) -> None:
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