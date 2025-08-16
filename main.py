import sys
from src.core.config_loader import ConfigLoader
from src.core.map_loader import MapLoader
from src.core.search_engine import SearchEngine
from src.core.utils import handle_file_path, ResultFileType, OutputFormat


def main():
    print(" -- 🎮 SOKOBAN 🎮 --")

    if len(sys.argv) < 2:
        print("Error: Se requiere un archivo de configuración como argumento.")
        print("Uso: python main.py <ruta_al_archivo_de_configuración>")
        exit(1)

    try:
        # Cargar configuración
        cfg = ConfigLoader(sys.argv[1])

        # Cargar mapa
        print(f"Cargando nivel: {cfg.map_name}...")
        initial_state = MapLoader.load_from_file(cfg.map_name)

        # Crear el motor de búsqueda con el algoritmo y heurística especificados
        engine = SearchEngine(cfg.algorithm, cfg.heuristic)

        # Iniciar la búsqueda
        print(f"Iniciando búsqueda con el algoritmo: {cfg.algorithm.get_algorithm_type()}...")
        result = engine.search(initial_state)

        # Imprimir resumen del resultado
        result.print_summary()

        # Exportar solución
        if result.success:
            print(f"Exportando solución a '{cfg.output_file}'...")
            result.export_solution(cfg.output_file, cfg.generate_animation_file)
            print(f"Solución exportada exitosamente.")

        # Mostrar información sobre archivos generados
        if cfg.generate_animation_file:
            animation_file = handle_file_path(ResultFileType.ANIMATION, OutputFormat.CSV, cfg.output_file)
            print(f"\n Archivo de animación generado: {animation_file}")
            print(f"Para ver la animación ejecuta: python test_animator.py")
        else:
            print("\nSolo se generaron archivos de métricas (no animación)")

    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()