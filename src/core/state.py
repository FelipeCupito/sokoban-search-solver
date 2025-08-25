from typing import Iterable, Tuple, Optional
from enum import Enum
import src.core as core
from src.heuristics.deadlock import DeadlockDetector


class Action(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    PUSH = "PUSH"

class SokobanState:
    __slots__ = (
        'player_pos', 'boxes', 'walls', 'goals', '_hash', '_is_goal_cache',
    )

    def __init__(self, player_pos: Tuple[int, int],
                 boxes: Iterable[Tuple[int, int]],
                 walls: frozenset[Tuple[int, int]],
                 goals: frozenset[Tuple[int, int]]):
        self.player_pos = player_pos
        self.boxes = frozenset(boxes)  # immutable for hashing
        self.walls = walls
        self.goals = goals
        self._hash = None
        self._is_goal_cache = None

    def __eq__(self, other):
        if not isinstance(other, SokobanState):
            return False
        return (self.player_pos == other.player_pos and 
                self.boxes == other.boxes)
    
    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self.player_pos, self.boxes))
        return self._hash

    def is_goal(self) -> bool:
        if self._is_goal_cache is None:
            self._is_goal_cache = self.boxes == self.goals
        return self._is_goal_cache

    def get_successors(self) -> Iterable[Tuple['SokobanState', Action]]:
        directions = [(-1, 0, Action.UP), (1, 0, Action.DOWN), (0, -1, Action.LEFT), (0, 1, Action.RIGHT)]

        for dr, dc, action in directions:
            new_player_pos = (self.player_pos[0] + dr, self.player_pos[1] + dc)
            
            # invalid if hits wall
            if new_player_pos in self.walls:
                continue
            
            boxes = self.boxes

            # Si hay una caja en la nueva posición del jugador
            if new_player_pos in self.boxes:
                new_box_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                
                if new_box_pos in self.walls or new_box_pos in self.boxes:
                    continue

                new_boxes = set(self.boxes)
                new_boxes.remove(new_player_pos)
                new_boxes.add(new_box_pos)
                temp_boxes = frozenset(new_boxes)
                if core.pruning and DeadlockDetector.is_deadlock(new_box_pos, temp_boxes, self.walls, self.goals):
                    continue

                # New boxes instance only in case of push
                boxes = temp_boxes

            new_state = SokobanState(new_player_pos, boxes, self.walls, self.goals)
            yield new_state, action


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
