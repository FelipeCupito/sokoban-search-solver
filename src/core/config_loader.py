import json
import os
import time
from src.core.interfaces import ISearchAlgorithm
from src.algorithms.algorithm_mapper import AlgorithmMapper
from src.heuristics.heuristic_mapper import HeuristicMapper


class ConfigLoader:
    """Carga y valida configuración desde archivos JSON"""
    
    DEFAULT_LEVEL = "level_1_easy.txt"
    DEFAULT_ALGORITHM = "BFS"
    DEFAULT_OUTPUT_FILE = f"result_{int(time.time())}"
    DEFAULT_ANIMATION_FLAG = False

    def __init__(self, config_path: str):
        self.config_path = config_path
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"El archivo de configuración '{config_path}' no fue encontrado.")

        with open(config_path, "r") as f:
            config = json.load(f)

        # Cargar configuración con valores por defecto
        self.algorithm: ISearchAlgorithm = AlgorithmMapper.from_string(
            config.get("algorithm", self.DEFAULT_ALGORITHM)
        )
        
        self.heuristic = None
        if config.get("heuristic"):
            self.heuristic = HeuristicMapper.from_string(config.get("heuristic"))
        
        self.map_name = config.get("map_name", self.DEFAULT_LEVEL)
        self.output_file = config.get("output_file", self.DEFAULT_OUTPUT_FILE)
        self.generate_animation_file = config.get("generate_animation", self.DEFAULT_ANIMATION_FLAG)
