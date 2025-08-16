from enum import Enum
from typing import List
from src.core.state import SokobanState

class TileType(Enum):
    WALL = '#'
    PLAYER = '@'  
    BOX = '$'
    GOAL = '.'
    SPACE = ' '

class MapLoader:
    """Carga mapas de Sokoban desde strings o archivos"""

    @staticmethod
    def load_from_file(file_path: str) -> SokobanState:
        """Carga un mapa desde archivo"""
        with open(file_path, 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]
        return MapLoader._parse_lines(lines)
    
    @staticmethod
    def _parse_lines(lines: List[str]) -> SokobanState:
        """Parsea las líneas del mapa y crea SokobanState"""
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
                elif char == TileType.BOX.value:
                    boxes.add(pos)
                elif char == TileType.GOAL.value:
                    goals.add(pos)
                # TileType.SPACE se ignora (espacio libre)
        
        if player_pos is None:
            raise ValueError(f"No se encontró jugador ({TileType.PLAYER}) en el mapa")
        
        if not boxes:
            raise ValueError(f"No se encontraron cajas ({TileType.BOX}) en el mapa")
        
        if not goals:
            raise ValueError(f"No se encontraron objetivos ({TileType.WALL}) en el mapa")
        
        if len(boxes) != len(goals):
            raise ValueError(f"Número de cajas ({len(boxes)}) no coincide con objetivos ({len(goals)})")
        
        return SokobanState(
            player_pos=player_pos,
            boxes=boxes,
            walls=frozenset(walls),
            goals=frozenset(goals)
        )