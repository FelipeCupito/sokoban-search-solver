from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from src.core.state import SokobanState, StateNode


class IHeuristic(ABC):
    @abstractmethod
    def calculate(self, state: 'SokobanState') -> int:
        raise NotImplementedError("This method should be overridden")


class ISearchAlgorithm(ABC):
    """Interfaz unificada que combina estructura de datos y lógica del algoritmo"""

    @abstractmethod
    def add(self, item: 'StateNode', heuristic: Optional[IHeuristic] = None):
        """Agrega un item a la frontera. La heurística es opcional."""
        raise NotImplementedError("This method should be overridden")

    @abstractmethod
    def get_next(self):
        """Obtiene el siguiente item de la frontera"""
        raise NotImplementedError("This method should be overridden")

    @abstractmethod
    def has_next(self) -> bool:
        """Verifica si la frontera tiene más elementos"""
        raise NotImplementedError("This method should be overridden")

    @abstractmethod
    def size(self) -> int:
        """Retorna el tamaño actual de la frontera"""
        raise NotImplementedError("This method should be overridden")
    
    @abstractmethod
    def needs_heuristic(self) -> bool:
        """Indica si el algoritmo requiere heurística"""
        raise NotImplementedError("This method should be overridden")

    @abstractmethod
    def get_algorithm_type(self) -> str:
        """Retorna el tipo de algoritmo como enum"""
        raise NotImplementedError("This method should be overridden")

    @abstractmethod
    def should_cache_cost(self) -> bool:
        """Indica si el algoritmo requiere seguimiento del costo del camino"""
        raise NotImplementedError("This method should be overridden")