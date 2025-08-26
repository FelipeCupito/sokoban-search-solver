from typing import List
import json
from dataclasses import dataclass
from src.core.state import SokobanState
import csv
from src.core.utils import handle_file_path, ResultFileType, OutputFormat


@dataclass
class SearchResult:
    success: bool
    states_path: List[SokobanState]
    actions_path: List[str]  # aligned with states_path; index 0 is "START"
    cost: int
    nodes_expanded: int
    max_frontier_size: int
    processing_time: float
    algorithm_type: str

    @property
    def solution_cost(self) -> int:
        """Alias para cost para compatibilidad"""
        return self.cost

    @classmethod
    def create_success(cls, states_path: List[SokobanState], actions_path: List[str], nodes_expanded: int,
                      max_frontier_size: int, processing_time: float,
                      algorithm_type: str) -> 'SearchResult':
        cost = max(0, len(states_path) - 1)
        return cls(
            success=True,
            states_path=states_path,
            actions_path=actions_path,
            cost=cost,
            nodes_expanded=nodes_expanded,
            max_frontier_size=max_frontier_size,
            processing_time=processing_time,
            algorithm_type=algorithm_type
        )
    
    @classmethod
    def create_success_metrics_only(cls, solution_cost: int, nodes_expanded: int,
                                   max_frontier_size: int, processing_time: float,
                                   algorithm_type: str) -> 'SearchResult':
        """Crear resultado exitoso sin almacenar estados/acciones para benchmarks"""
        return cls(
            success=True,
            states_path=[],  # Vacío para ahorrar memoria
            actions_path=[],  # Vacío para ahorrar memoria
            cost=solution_cost,
            nodes_expanded=nodes_expanded,
            max_frontier_size=max_frontier_size,
            processing_time=processing_time,
            algorithm_type=algorithm_type
        )
    
    @classmethod
    def create_failure(cls, nodes_expanded: int, max_frontier_size: int, 
                      processing_time: float, algorithm_type: str) -> 'SearchResult':
        return cls(
            success=False,
            states_path=[],
            actions_path=[],
            cost=0,
            nodes_expanded=nodes_expanded,
            max_frontier_size=max_frontier_size,
            processing_time=processing_time,
            algorithm_type=algorithm_type
        )
    
    def export_solution(self, filename: str = None, generate_animation_file: bool = False):
        if not self.success:
            raise ValueError("Cannot export solution for unsuccessful search.")

        solution_data = {
            "algorithm": self.algorithm_type,
            "success": self.success,
            "cost": self.cost,
            "path_length": len(self.states_path),
            "metrics": {
                "nodes_expanded": self.nodes_expanded,
                "max_frontier_size": self.max_frontier_size,
                "processing_time_seconds": round(self.processing_time, 4)
            }
        }

        metric_file_path = handle_file_path(ResultFileType.METRICS, OutputFormat.JSON, filename)
        with open(metric_file_path, 'w') as f:
            json.dump(solution_data, f, indent=2)

        if generate_animation_file:
            self._extract_states_for_animation(filename)

    def print_summary(self):
        print(f"\n=== {self.algorithm_type} Search Result ===")
        print(f"Success: {self.success}")
        if self.success:
            print(f"Solution cost: {self.cost}")
            print(f"Path length: {len(self.states_path)} states")
        else:
            print("No solution found.")
        print(f"Nodes expanded: {self.nodes_expanded}")
        print(f"Max frontier size: {self.max_frontier_size}")
        print(f"Processing time: {self.processing_time:.4f} seconds")
        print("=" * 50)


    def _extract_moves(self) -> List[str]:
        if not self.states_path or len(self.states_path) < 2:
            return []
        
        # Skip the first action (START)
        return self.actions_path[1:]

    def _extract_states_for_animation(self, file_name: str = None) -> None:
        file_path = handle_file_path(ResultFileType.ANIMATION, OutputFormat.CSV, file_name)
        headers = ["step", "player_pos", "boxes_pos", "action"]

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for i, state in enumerate(self.states_path):
                boxes_str = ";".join([f"({r},{c})" for r, c in sorted(list(state.boxes))])
                player_str = f"({state.player_pos[0]},{state.player_pos[1]})"
                writer.writerow([
                    i,
                    player_str,
                    boxes_str,
                    self.actions_path[i] if i < len(self.actions_path) else ("START" if i == 0 else "")
                ])
