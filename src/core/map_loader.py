from enum import Enum
from typing import List
from src.core.state import SokobanState

class TileType(Enum):
    WALL = '#'
    PLAYER = '@'  
    BOX = '$'
    GOAL = '.'
    SPACE = ' '
    BOX_ON_GOAL = '*'
    PLAYER_ON_GOAL = '+'

class MapLoader:
    """Loads Sokoban maps from strings or files"""

    @staticmethod
    def load_from_file(file_path: str) -> SokobanState:
        """Loads a map from file"""
        with open(file_path, 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]
        return MapLoader._parse_lines(lines)
    
    @staticmethod
    def _parse_lines(lines: List[str]) -> SokobanState:
        """Parses map lines and creates SokobanState"""
        walls = set()
        boxes = set()
        goals = set()
        player_pos = None
        
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                pos = (row, col)

                if char == TileType.WALL.value:
                    walls.add(pos)
                elif char == TileType.PLAYER.value:
                    player_pos = pos
                elif char == TileType.PLAYER_ON_GOAL.value:
                    player_pos = pos
                    goals.add(pos)
                elif char == TileType.BOX.value:
                    boxes.add(pos)
                elif char == TileType.BOX_ON_GOAL.value:
                    boxes.add(pos)
                    goals.add(pos)
                elif char == TileType.GOAL.value:
                    goals.add(pos)
                elif char == TileType.SPACE.value:
                    continue
                else:
                    raise ValueError(f"Unknown character '{char}' in map")
        
        if player_pos is None:
            raise ValueError(f"Player ({TileType.PLAYER}) not found in map")
        
        if not boxes:
            raise ValueError(f"Boxes ({TileType.BOX}) not found in map")
        
        if not goals:
            raise ValueError(f"Goals ({TileType.GOAL}) not found in map")
        
        if len(boxes) != len(goals):
            raise ValueError(f"Number of boxes ({len(boxes)}) doesn't match goals ({len(goals)})")
        
        return SokobanState(
            player_pos=player_pos,
            boxes=boxes,
            walls=frozenset(walls),
            goals=frozenset(goals)
        )