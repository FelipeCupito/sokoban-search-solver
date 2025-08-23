from enum import Enum
from src.core.interfaces import IHeuristic
from .manhattan_heu import ManhattanHeuristic
from .deadlock import DeadlockDetector
from .perfect_match import PerfectMatch
from .sum_of_distance import SumOfDistanceMinimalMatchingCost


class HeuristicType(Enum):
    MANHATTAN = "MANHATTAN"
    DEADLOCK = "DEADLOCK"
    PERFECT_MATCH = "PERFECTMATCH"
    SUM_OF_DISTANCE = "SUM_OF_DISTANCE"


class HeuristicMapper:

    @staticmethod
    def get_heuristic_by_type(heuristic_type: HeuristicType) -> IHeuristic:
        if HeuristicType.MANHATTAN == heuristic_type:
            return ManhattanHeuristic()
        elif HeuristicType.DEADLOCK == heuristic_type:
            return DeadlockDetector()
        elif HeuristicType.PERFECT_MATCH == heuristic_type:
            return PerfectMatch()
        elif HeuristicType.SUM_OF_DISTANCE == heuristic_type:
            return SumOfDistanceMinimalMatchingCost()
        else:
            raise ValueError(f"Heurística desconocida: {heuristic_type}")

    @staticmethod
    def from_string(heuristic_name: str) -> IHeuristic:
        try:
            heuristic_type = HeuristicType[heuristic_name.upper()]
            return HeuristicMapper.get_heuristic_by_type(heuristic_type)
        except KeyError:
            raise ValueError(f"Algoritmo desconocido: {heuristic_name}")