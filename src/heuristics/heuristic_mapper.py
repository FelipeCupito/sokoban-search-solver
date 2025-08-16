from enum import Enum
from src.core.interfaces import IHeuristic


class HeuristicType(Enum):
    MANHATTAN = "Manhattan" # TODO: Implementar
    EUCLIDEAN = "Euclidean" # TODO: Implementar


class HeuristicMapper:

    @staticmethod
    def get_heuristic_by_type(heuristic_type: HeuristicType) -> IHeuristic:
        if HeuristicType.MANHATTAN == heuristic_type:
            raise NotImplementedError("Heurística Manhattan aún no implementada")
        elif HeuristicType.EUCLIDEAN == heuristic_type:
            raise NotImplementedError("Heurística Manhattan aún no implementada")
        else:
            raise ValueError(f"Heurística desconocida: {heuristic_type}")

    @staticmethod
    def from_string(heuristic_name: str) -> IHeuristic:
        try:
            heuristic_type = HeuristicType[heuristic_name.upper()]
            return HeuristicMapper.get_heuristic_by_type(heuristic_type)
        except KeyError:
            raise ValueError(f"Algoritmo desconocido: {heuristic_name}")