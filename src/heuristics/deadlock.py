from src.core.interfaces import IHeuristic
from src.core.state import SokobanState
import numpy as np
from typing import Tuple

class DeadlockDetector(IHeuristic):
    """Applies Manhattan distance heuristic plus detects and prunes deadlocks.

    """
    def calculate(self, state: SokobanState) -> int:
        h = 0
        boxes = np.array(list(state.boxes))
        goals = np.array(list(state.goals))
        for box in boxes:
            dist = np.abs(goals-box).sum(axis=1)
            h = h + dist.min()
        for box in state.boxes:
            if self.is_deadlock(box, state.boxes, state.walls, state.goals):
                h = np.inf
                break
        return h
        
    @staticmethod
    def is_deadlock(
            box_pos: Tuple[int, int],
            boxes: frozenset[Tuple[int, int]],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]]
    ) -> bool:
        """Detecta si una caja está en deadlock"""
        
        # Deadlock 1: Caja en esquina que no es goal
        if DeadlockDetector._is_corner_deadlock(box_pos, walls, goals):
            return True
        
        # Deadlock 3: Cuadrado 2x2 de cajas sin goals
        if DeadlockDetector._is_square_deadlock(box_pos, boxes, goals):
            return True
        
        return False
    
    @staticmethod
    def _is_corner_deadlock(
            pos: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica si la posición es una esquina sin goal"""
        if pos in goals:
            return False
            
        r, c = pos
        # Verificar las 4 posibles esquinas
        corner_patterns = [
            [(r-1, c), (r, c-1)],  # Superior izquierda
            [(r-1, c), (r, c+1)],  # Superior derecha  
            [(r+1, c), (r, c-1)],  # Inferior izquierda
            [(r+1, c), (r, c+1)]   # Inferior derecha
        ]
        
        for pattern in corner_patterns:
            if all(wall_pos in walls for wall_pos in pattern):
                return True
        
        return False
    
    @staticmethod
    def _is_wall_deadlock(
            pos: Tuple[int, int],
            walls: frozenset[Tuple[int, int]],
            goals: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica deadlock contra pared"""
        r, c = pos
        
        # Contra pared horizontal
        if (r - 1, c) in walls or (r + 1, c) in walls:
            row_goals = [g for g in goals if g[0] == r]
            if not row_goals:
                return True
            # Verificar si hay path horizontal libre
            for goal in row_goals:
                if DeadlockDetector._has_clear_horizontal_path(pos, goal, walls):
                    return False
            return True
        
        # Contra pared vertical
        if (r, c - 1) in walls or (r, c + 1) in walls:
            col_goals = [g for g in goals if g[1] == c]
            if not col_goals:
                return True
            # Verificar si hay path vertical libre
            for goal in col_goals:
                if DeadlockDetector._has_clear_vertical_path(pos, goal, walls):
                    return False
            return True
        
        return False
    
    @staticmethod
    def _is_square_deadlock(pos: Tuple[int, int], boxes: frozenset[Tuple[int, int]],
                           goals: frozenset[Tuple[int, int]]) -> bool:
        """Detecta cuadrados 2x2 de cajas sin goals"""
        r, c = pos
        
        # Verificar 4 posibles cuadrados donde esta caja participa
        squares = [
            [(r, c), (r, c+1), (r+1, c), (r+1, c+1)],      # pos en superior izquierda
            [(r-1, c-1), (r-1, c), (r, c-1), (r, c)],      # pos en inferior derecha
            [(r-1, c), (r-1, c+1), (r, c), (r, c+1)],      # pos en inferior izquierda
            [(r, c-1), (r, c), (r+1, c-1), (r+1, c)]       # pos en superior derecha
        ]
        
        for square in squares:
            if all(square_pos in boxes for square_pos in square):
                # Si ninguna posición del cuadrado tiene goal, es deadlock
                if not any(square_pos in goals for square_pos in square):
                    return True
        
        return False
    
    @staticmethod
    def _has_clear_horizontal_path(
            start: Tuple[int, int],
            end: Tuple[int, int],
            walls: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica path horizontal libre"""
        r = start[0]
        start_c, end_c = sorted([start[1], end[1]])
        
        for c in range(start_c, end_c + 1):
            if (r, c) in walls:
                return False
        return True
    
    @staticmethod
    def _has_clear_vertical_path(
            start: Tuple[int, int],
            end: Tuple[int, int],
            walls: frozenset[Tuple[int, int]]
    ) -> bool:
        """Verifica path vertical libre"""
        c = start[1]
        start_r, end_r = sorted([start[0], end[0]])
        
        for r in range(start_r, end_r + 1):
            if (r, c) in walls:
                return False
        return True