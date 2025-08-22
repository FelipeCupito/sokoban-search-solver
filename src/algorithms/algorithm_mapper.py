from enum import Enum
from src.core.interfaces import ISearchAlgorithm
from src.algorithms.bfs import BFSAlgorithm
from src.algorithms.dfs import DFS
from src.algorithms.greedy import GreedyAlgorithm

class AlgorithmType(Enum):
    BFS = "BFS"
    DFS = "DFS"
    ASTAR = "A*"
    GREEDY = "GREEDY"
    

class AlgorithmMapper:

    @staticmethod
    def get_algorithm_by_type(algorithm_type: AlgorithmType) -> ISearchAlgorithm:
        if AlgorithmType.BFS == algorithm_type:
            return BFSAlgorithm()
        elif AlgorithmType.DFS == algorithm_type:
            return DFS()
        elif AlgorithmType.GREEDY == algorithm_type:
            return GreedyAlgorithm()
        else:
            raise ValueError(f"Algoritmo desconocido: {algorithm_type}")

    @staticmethod
    def from_string(algorithm_name: str) -> ISearchAlgorithm:
        try:
            algorithm_type = AlgorithmType[algorithm_name.upper()]
            return AlgorithmMapper.get_algorithm_by_type(algorithm_type)
        except KeyError:
            raise ValueError(f"Algoritmo desconocido: {algorithm_name}")