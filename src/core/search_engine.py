from typing import Optional
from src.core.state import SokobanState
from src.core.result import SearchResult
from src.core.interfaces import ISearchAlgorithm
from src.core.interfaces import IHeuristic
import time


class SearchEngine:
    def __init__(self,

                 algorithm: ISearchAlgorithm,
                 heuristic: Optional[IHeuristic] = None
                 ):
        if algorithm is None:
            raise ValueError("Algorithm cannot be None")
        self.algorithm = algorithm

        if heuristic is not None and not algorithm.needs_heuristic():
            raise ValueError(f"{algorithm.get_algorithm_type()} does not require a heuristic function")
        self.heuristic = heuristic
        
        # Métricas
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.start_time = 0
    
    def search(self,
               initial_state: SokobanState,
               ) -> SearchResult:

        self.start_time = time.time()
        self._reset_metrics()
        
        # Verificar estado inicial
        if initial_state.is_goal():
            return SearchResult.create_success(
                initial_state, self.nodes_expanded, self.max_frontier_size,
                time.time() - self.start_time, self.algorithm.get_algorithm_type()
            )
        
        # Inicializar estructuras
        explored = set()
        
        # Agregar estado inicial - ahora algorithm ES la frontera
        self.algorithm.add(initial_state, self.heuristic )
        
        # Búsqueda principal
        while self.algorithm.has_next():
            # Actualizar métricas
            self.max_frontier_size = max(self.max_frontier_size, self.algorithm.size())
            
            # Obtener siguiente estado
            current_state = self.algorithm.get_next()
            
            # Skip si ya fue explorado
            if current_state in explored:
                continue
            
            explored.add(current_state)
            self.nodes_expanded += 1
            
            # Generar sucesores
            for successor in current_state.get_successors():
                if successor in explored:
                    continue
                
                # Verificar si es objetivo
                if successor.is_goal():
                    return SearchResult.create_success(
                        successor, self.nodes_expanded, self.max_frontier_size,
                        time.time() - self.start_time, self.algorithm.get_algorithm_type()
                    )
                
                # Agregar a frontera
                self.algorithm.add(successor, self.heuristic)
        
        # No se encontró solución
        return SearchResult.create_failure(
            self.nodes_expanded, self.max_frontier_size,
            time.time() - self.start_time, self.algorithm.get_algorithm_type()
        )
    
    def _reset_metrics(self):
        self.nodes_expanded = 0
        self.max_frontier_size = 0

    
