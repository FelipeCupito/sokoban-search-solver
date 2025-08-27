import json
import sys
import time
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional
from src.core.map_loader import MapLoader
from src.core.search_engine import SearchEngine
from src.algorithms.algorithm_mapper import AlgorithmMapper
from src.heuristics.heuristic_mapper import HeuristicMapper
from src.core.result import SearchResult


@dataclass
class BenchmarkMetrics:
    """Métricas promedio de múltiples ejecuciones"""
    algorithm: str                    # Nombre del algoritmo
    heuristic: str                   # Nombre de la heurística (o "None")
    successful_runs: int             # Número de ejecuciones exitosas
    total_runs: int                  # Total de ejecuciones intentadas
    avg_solution_cost: float         # Promedio de movimientos de las soluciones exitosas
    avg_nodes_expanded: float        # Promedio de nodos expandidos de ejecuciones exitosas
    avg_max_frontier_size: float     # Promedio del tamaño máximo de frontera de ejecuciones exitosas
    avg_processing_time: float       # Promedio de tiempo de procesamiento de ejecuciones exitosas
    std_processing_time: float       # Desviación estándar de tiempo (float('inf') si solo 1 muestra)
    success_rate: float              # successful_runs / total_runs (0.0 - 1.0)
    min_processing_time: float       # Tiempo mínimo observado en ejecuciones exitosas
    max_processing_time: float       # Tiempo máximo observado en ejecuciones exitosas
    confidence_score: float          # Score 0-1: 50% success_rate + 30% samples + 20% consistency


@dataclass
class BenchmarkConfig:
    """Configuración del benchmark"""
    map_name: str
    repetitions: int
    timeout_minutes: int
    max_threads: int
    pruning: bool


class BenchmarkRunner:
    def __init__(self, config_file: str):
        self.config = self._load_config(config_file)
        self.initial_state = MapLoader.load_from_file(self.config.map_name)
        
    def _load_config(self, config_file: str) -> BenchmarkConfig:
        """Cargar configuración del benchmark"""
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return BenchmarkConfig(
            map_name=config_data.get("map_name", "maps/level_1.txt"),
            repetitions=config_data.get("repetitions", 5),
            timeout_minutes=config_data.get("timeout_minutes", 5),  # 5 minutos por defecto
            max_threads=config_data.get("max_threads", 4),
            pruning=config_data.get("pruning", False)
        )
    
    def _run_single_algorithm(self, algorithm_type, heuristic_type, run_id: int) -> Optional[SearchResult]:
        """Ejecuta una sola prueba de algoritmo (timeout manejado por ThreadPoolExecutor)"""
        try:
            algorithm = AlgorithmMapper.get_algorithm_by_type(algorithm_type)
            heuristic = HeuristicMapper.get_heuristic_by_type(heuristic_type) if heuristic_type else None
            
            # Validar si el algoritmo necesita heurística
            if algorithm.needs_heuristic() and heuristic is None:
                return None
            
            # Usar metrics_only para ahorrar tiempo y memoria
            engine = SearchEngine(algorithm, heuristic, self.config.pruning, metrics_only=True)
            result = engine.search(self.initial_state)
            
            return result if result.success else None
            
        except Exception as e:
            print(f"Error in run {run_id}: {e}")
            return None
    
    def _calculate_confidence_score(self, success_rate: float, successful_runs: int, 
                                   std_time: float, avg_time: float) -> float:
        """
        Calcula score de confiabilidad (0-1) basado en múltiples factores
        
        FÓRMULA: confidence = success_factor*0.5 + sample_factor*0.3 + consistency_factor*0.2
        
        success_factor = success_rate (0-1)
        sample_factor = min(successful_runs / 5.0, 1.0) - normalizado a 5 muestras
        consistency_factor = 1 - coeficiente_variacion (menor variación = más consistente)
        """
        
        # Factor 1: Tasa de éxito (0-1) - Directo de success_rate
        success_factor = success_rate
        
        # Factor 2: Número de muestras exitosas (0-1) - Normalizado a 5 muestras máximo
        sample_factor = min(successful_runs / 5.0, 1.0)
        
        # Factor 3: Consistencia de tiempo (0-1) - Basado en coeficiente de variación
        if std_time == float('inf') or avg_time == 0:
            consistency_factor = 0.0  # Una sola muestra o tiempo cero = no consistencia
        else:
            cv = std_time / avg_time  # Coeficiente de variación = std/mean
            consistency_factor = max(0.0, 1.0 - min(cv, 1.0))  # Invertir: menor CV = mejor
        
        # Score ponderado final
        confidence = (
            success_factor * 0.5 +        # 50% peso a tasa de éxito
            sample_factor * 0.3 +         # 30% peso a número de muestras  
            consistency_factor * 0.2      # 20% peso a consistencia temporal
        )
        
        return confidence
    
    def _benchmark_combination(self, algorithm_type, heuristic_type) -> BenchmarkMetrics:
        """Ejecuta múltiples pruebas para una combinación algoritmo-heurística"""
        algo_name = algorithm_type.value
        heur_name = heuristic_type.value if heuristic_type else "None"
        
        print(f"📊 Benchmarking {algo_name} + {heur_name} ({self.config.repetitions} runs)...")
        
        # Ejecutar tareas con threading y timeout
        timeout_seconds = self.config.timeout_minutes * 60
        with ProcessPoolExecutor(max_workers=self.config.max_threads) as executor:
            # Enviar todas las tareas
            futures = {
                executor.submit(self._run_single_algorithm, algorithm_type, heuristic_type, i): i 
                for i in range(self.config.repetitions)
            }
            
            # Recoger resultados con timeout
            results = []
            completed = 0
            
            for future in as_completed(futures, timeout=timeout_seconds * self.config.repetitions):
                completed += 1
                try:
                    result = future.result(timeout=timeout_seconds)
                    if result:
                        results.append(result)
                except Exception:
                    # Timeout o error en la ejecución
                    pass
                
                # Progreso
                print(f"  {completed:2d}/{self.config.repetitions} completed", end="\r")
        
        print()  # Nueva línea después del progreso
        
        # Calcular estadísticas
        successful_runs = len(results)
        success_rate = successful_runs / self.config.repetitions
        
        if not results:
            return BenchmarkMetrics(
                algorithm=algo_name,
                heuristic=heur_name,
                successful_runs=0,
                total_runs=self.config.repetitions,
                avg_solution_cost=0,
                avg_nodes_expanded=0,
                avg_max_frontier_size=0,
                avg_processing_time=0,
                std_processing_time=0,
                success_rate=0.0,
                min_processing_time=0,
                max_processing_time=0,
                confidence_score=0.0
            )
        
        # Extraer métricas solo de ejecuciones exitosas (ignora timeouts/errores)
        solution_costs = [r.solution_cost for r in results]        # Movimientos para llegar a la solución
        nodes_expanded = [r.nodes_expanded for r in results]        # Nodos explorados por el algoritmo
        max_frontier_sizes = [r.max_frontier_size for r in results] # Máximo tamaño de la frontera
        processing_times = [r.processing_time for r in results]     # Tiempo real de ejecución
        
        # Calcular desviación estándar (float('inf') si solo hay 1 muestra)
        std_time = statistics.stdev(processing_times) if len(processing_times) > 1 else float('inf')
        
        # Calcular score de confiabilidad combinando múltiples factores
        confidence_score = self._calculate_confidence_score(
            success_rate, successful_runs, std_time, statistics.mean(processing_times)
        )
        
        return BenchmarkMetrics(
            algorithm=algo_name,
            heuristic=heur_name,
            successful_runs=successful_runs,                         # Contador de ejecuciones exitosas
            total_runs=self.config.repetitions,                     # Total configurado en el JSON
            avg_solution_cost=statistics.mean(solution_costs),      # Promedio aritmético de movimientos
            avg_nodes_expanded=statistics.mean(nodes_expanded),     # Promedio aritmético de nodos
            avg_max_frontier_size=statistics.mean(max_frontier_sizes), # Promedio aritmético de frontera máx
            avg_processing_time=statistics.mean(processing_times),  # Promedio aritmético de tiempo
            std_processing_time=std_time,                           # Desviación estándar de tiempo
            success_rate=success_rate,                              # successful_runs / total_runs
            min_processing_time=min(processing_times),              # Tiempo mínimo de las exitosas
            max_processing_time=max(processing_times),              # Tiempo máximo de las exitosas
            confidence_score=confidence_score                       # Score calculado con fórmula ponderada
        )
    
    def run_full_benchmark(self) -> List[BenchmarkMetrics]:
        """Ejecuta benchmark completo de todas las combinaciones válidas en paralelo"""
        algorithms = AlgorithmMapper.get_all_algorithms()
        heuristics = HeuristicMapper.get_all_heuristics()
        
        # Generar solo combinaciones válidas
        combinations = []
        invalid_combinations = []
        
        for algo in algorithms:
            for heur in heuristics:
                # Crear instancia temporal para verificar requirements
                algo_instance = AlgorithmMapper.get_algorithm_by_type(algo)
                
                # Si el algoritmo necesita heurística pero no hay una, skip
                if algo_instance.needs_heuristic() and heur is None:
                    invalid_combinations.append((algo, heur))
                    continue
                    
                combinations.append((algo, heur))
        
        total_combinations = len(combinations)
        total_invalid = len(invalid_combinations)
        
        print(f"\n🚀 Starting full benchmark...")
        print(f"Map: {self.config.map_name}")
        print(f"Repetitions per combination: {self.config.repetitions}")
        print(f"Timeout per run: {self.config.timeout_minutes} minutes")
        print(f"Max threads: {self.config.max_threads}")
        print(f"Valid combinations: {total_combinations}")
        if total_invalid > 0:
            print(f"Skipped invalid combinations: {total_invalid} (algorithms requiring heuristics)")
        print()  # Línea vacía
        
        # Ejecutar todas las combinaciones en paralelo
        all_metrics = []
        completed = 0
        
        with ProcessPoolExecutor(max_workers=self.config.max_threads) as executor:
            # Enviar todas las combinaciones como tareas
            future_to_combination = {
                executor.submit(self._benchmark_combination, algo, heur): (algo, heur)
                for algo, heur in combinations
            }
            
            # Recoger resultados conforme van completándose
            for future in as_completed(future_to_combination):
                completed += 1
                algo_type, heur_type = future_to_combination[future]
                algo_name = algo_type.value
                heur_name = heur_type.value if heur_type else "None"
                
                metrics = future.result()
                all_metrics.append(metrics)
                
                # Mostrar progreso con resultado
                progress = f"[{completed:2d}/{total_combinations}]"
                if metrics.successful_runs > 0:
                    result = f"✅ {algo_name} + {heur_name}: {metrics.success_rate:.1%} success, avg: {metrics.avg_processing_time:.3f}s"
                else:
                    result = f"❌ {algo_name} + {heur_name}: No successful runs"
                
                print(f"{progress} {result}")
        
        # Ordenar resultados por nombre de algoritmo y heurística para consistencia
        all_metrics.sort(key=lambda m: (m.algorithm, m.heuristic))
        return all_metrics
    
    def print_results(self, all_metrics: List[BenchmarkMetrics]):
        """Imprime reporte final del benchmark con análisis estadísticamente robusto"""
        print("\n" + "="*110)
        print("📈 BENCHMARK RESULTS")
        print("="*110)
        
        # Filtrar solo combinaciones exitosas
        successful_metrics = [m for m in all_metrics if m.successful_runs > 0]
        
        if not successful_metrics:
            print("❌ No successful combinations found!")
            return
        
        # Separar por nivel de confiabilidad (umbrales fijos)
        high_confidence = [m for m in successful_metrics if m.confidence_score >= 0.7]    # ≥70%
        medium_confidence = [m for m in successful_metrics if 0.4 <= m.confidence_score < 0.7] # 40-70%
        low_confidence = [m for m in successful_metrics if m.confidence_score < 0.4]      # <40%
        
        print(f"\n✅ Successful combinations: {len(successful_metrics)}/{len(all_metrics)}")
        print(f"   🟢 High confidence (≥70%): {len(high_confidence)}")
        print(f"   🟡 Medium confidence (40-70%): {len(medium_confidence)}")
        print(f"   🔴 Low confidence (<40%): {len(low_confidence)}\n")
        
        # Mostrar tabla principal con todas las métricas
        self._print_detailed_table(successful_metrics)
        
        # Estadísticas destacadas - solo con alta confiabilidad
        if high_confidence:
            print(f"\n🏆 TOP PERFORMERS (High Confidence Only):")
            self._print_top_performers(high_confidence)
        else:
            print(f"\n⚠️  No high-confidence results available for reliable comparisons")
            if medium_confidence:
                print(f"🟡 BEST MEDIUM-CONFIDENCE PERFORMERS:")
                self._print_top_performers(medium_confidence)
    
    def _print_detailed_table(self, metrics: List[BenchmarkMetrics]):
        """Imprime tabla detallada con todas las métricas"""
        # Ordenar por confidence score primero, luego por tiempo
        metrics.sort(key=lambda x: (-x.confidence_score, x.avg_processing_time))
        
        # Header extendido
        header = f"{'Algorithm':<12} {'Heuristic':<15} {'Success':<8} {'Conf':<5} {'Time':<8} {'±Std':<8} {'Range':<12} {'Moves':<6} {'Nodes':<8} {'Front':<8}"
        print(header)
        print("-" * len(header))
        
        for m in metrics:
            # Indicador de confiabilidad
            conf_icon = "🟢" if m.confidence_score >= 0.7 else "🟡" if m.confidence_score >= 0.4 else "🔴"
            
            # Formatear rango de tiempo
            time_range = f"{m.min_processing_time:.2f}-{m.max_processing_time:.2f}s"
            
            # Formatear desviación estándar
            std_display = "N/A" if m.std_processing_time == float('inf') else f"{m.std_processing_time:.3f}"
            
            print(f"{m.algorithm:<12} {m.heuristic:<15} {m.success_rate:<8.1%} "
                  f"{conf_icon}{m.confidence_score:<4.2f} {m.avg_processing_time:<8.3f} {std_display:<8} "
                  f"{time_range:<12} {m.avg_solution_cost:<6.1f} {m.avg_nodes_expanded:<8.0f} {m.avg_max_frontier_size:<8.0f}")
    
    def _print_top_performers(self, metrics: List[BenchmarkMetrics]):
        """Imprime estadísticas destacadas"""
        if not metrics:
            return
            
        # Más rápido: min(avg_processing_time) - menor tiempo promedio
        fastest = min(metrics, key=lambda x: x.avg_processing_time)
        print(f"⚡ Fastest: {fastest.algorithm} + {fastest.heuristic} "
              f"({fastest.avg_processing_time:.3f}s, confidence: {fastest.confidence_score:.2f})")
        
        # Menos nodos: min(avg_nodes_expanded) - algoritmo más eficiente en exploración
        fewest_nodes = min(metrics, key=lambda x: x.avg_nodes_expanded)
        print(f"🎯 Fewest nodes: {fewest_nodes.algorithm} + {fewest_nodes.heuristic} "
              f"({fewest_nodes.avg_nodes_expanded:.0f} nodes, confidence: {fewest_nodes.confidence_score:.2f})")
        
        # Solución más corta: min(avg_solution_cost) - menos movimientos para resolver
        shortest = min(metrics, key=lambda x: x.avg_solution_cost)
        print(f"🎯 Shortest solution: {shortest.algorithm} + {shortest.heuristic} "
              f"({shortest.avg_solution_cost:.1f} moves, confidence: {shortest.confidence_score:.2f})")
        
        # Más confiable: max(confidence_score) - mejor score de confiabilidad estadística  
        most_reliable = max(metrics, key=lambda x: x.confidence_score)
        print(f"🏅 Most reliable: {most_reliable.algorithm} + {most_reliable.heuristic} "
              f"({most_reliable.success_rate:.1%} success, confidence: {most_reliable.confidence_score:.2f})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <benchmark_config.json>")
        print("\nExample config:")
        print("""{
  "map_name": "maps/level_2.txt",
  "repetitions": 5,
  "timeout_minutes": 5,
  "max_threads": 4,
  "pruning": false
}""")
        exit(1)
    
    try:
        runner = BenchmarkRunner(sys.argv[1])
        start_time = time.time()
        
        metrics = runner.run_full_benchmark()
        runner.print_results(metrics)
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Total benchmark time: {total_time:.1f}s")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()