from typing import Optional, Iterable
from src.core.state import SokobanState


class StateNode:
    __slots__ = ('state', 'parent', 'action', 'cost', 'depth')

    def __init__(self, state: SokobanState, parent: Optional['StateNode'] = None, action: str = "START"):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = 0 if parent is None else parent.cost + 1
        self.depth = 0 if parent is None else parent.depth + 1

    def __hash__(self):
        return self.state.__hash__()

    def __eq__(self, other):
        return self.state.__eq__(other.state) if isinstance(other, StateNode) else False

    def get_successors(self) -> Iterable["StateNode"]:
        # Generator avoids building an intermediate list.
        for successor_state, action in self.state.get_successors():
            yield StateNode(successor_state, parent=self, action=action.value)
