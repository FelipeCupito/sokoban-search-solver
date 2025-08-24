import sys
from src.core.config_loader import ConfigLoader
from src.core.map_loader import MapLoader
from src.core.search_engine import SearchEngine
from src.core.utils import handle_file_path, ResultFileType, OutputFormat


def main():
    print(" -- 🎮 SOKOBAN 🎮 --")

    if len(sys.argv) < 2:
        print("Error: A configuration file is required as an argument.")
        print("Usage: python main.py <path_to_config_file>")
        exit(1)

    try:
        cfg = ConfigLoader(sys.argv[1])
        print(f"Loading level: {cfg.map_name}...")
        initial_state = MapLoader.load_from_file(cfg.map_name)

        engine = SearchEngine(cfg.algorithm, cfg.heuristic, cfg.pruning)
        print(f"Starting search with algorithm: {cfg.algorithm.get_algorithm_type()}...")
        print(f"Heuristic: {cfg.heuristic.__class__.__name__ if cfg.heuristic else 'None'}")
        print(f"Pruning: {'Enabled' if cfg.pruning else 'Disabled'}")
        result = engine.search(initial_state)
        result.print_summary()

        if result.success:
            print(f"Exporting solution to 'output/{cfg.output_file}'...")
            result.export_solution(cfg.output_file, cfg.generate_animation_file)
            print(f"Solution exported successfully.")
            if cfg.generate_animation_file:
                animation_file = handle_file_path(ResultFileType.ANIMATION, OutputFormat.CSV, cfg.output_file)
                print(f"\nAnimation file generated: {animation_file}")
                print(f"To view the animation, run: python -m src.core.animator {animation_file} {cfg.map_name}")
            else:
                print("\nOnly metrics files were generated (no animation)")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()