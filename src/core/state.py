from typing import Iterable, Tuple, List, Optional


class SokobanState:
    def __init__(self, player_pos: Tuple[int, int],
                 boxes: Iterable[Tuple[int, int]],
                 walls: frozenset[Tuple[int, int]],
                 goals: frozenset[Tuple[int, int]]):
        self.player_pos = player_pos
        self.boxes = frozenset(boxes)  # Inmutable para hashing
        self.walls = walls
        self.goals = goals
        
        # Para reconstruir el path
        self.parent: Optional['SokobanState'] = None
        self.action: Optional[str] = None
        self.cost: int = 0
        
        # Cache para optimización
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
    
    def get_successors(self) -> List['SokobanState']:
        successors = []
        directions = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
        
        for dr, dc, action in directions:
            new_player_pos = (self.player_pos[0] + dr, self.player_pos[1] + dc)
            
            # Verificar si la nueva posición del jugador es válida
            if new_player_pos in self.walls:
                continue
            
            boxes = self.boxes

            # Si hay una caja en la nueva posición del jugador
            if new_player_pos in self.boxes:
                new_box_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                
                # Verificar si la nueva posición de la caja es válida
                if new_box_pos in self.walls or new_box_pos in self.boxes:
                    continue
                
                # Verificar deadlock antes de crear el estado
                if DeadlockDetector.is_deadlock(new_box_pos, self.boxes, self.walls, self.goals):
                    continue

                # New boxes instance only in case of push
                new_boxes = set(self.boxes)
                new_boxes.remove(new_player_pos)
                new_boxes.add(new_box_pos)
                boxes = frozenset(new_boxes)
                action += "_PUSH"

            new_state = SokobanState(new_player_pos, boxes, self.walls, self.goals)
            new_state.parent = self
            new_state.action = action
            new_state.cost = self.cost + 1
            successors.append(new_state)
        
        return successors
    
    

class DeadlockDetector:
    """ By claude, la verda no se que onda """
    
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
        
        # Deadlock 2: Caja contra pared sin goals accesibles
        if DeadlockDetector._is_wall_deadlock(box_pos, walls, goals):
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