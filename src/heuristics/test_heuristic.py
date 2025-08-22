import sys
from ..core.config_loader import ConfigLoader
from ..core.map_loader import MapLoader 

print(" -- 🎮 SOKOBAN 🎮 --")

if len(sys.argv) < 2:
    print("Error: A configuration file is required as an argument.")
    print("Usage: python main.py <path_to_config_file>")
    exit(1)

try:
    cfg = ConfigLoader(sys.argv[1])
    print(f"Loading level: {cfg.map_name}...")
    initial_state = MapLoader.load_from_file(cfg.map_name)
    h = cfg.heuristic
    est_cost = h.calculate(initial_state)
    boxes = initial_state.boxes
    goals = initial_state.goals
    i=0
    for box in boxes:
        print(f'Box {i} pos= {box}')
        i = i+1
    i=0
    for goal in goals:
        print(f'Goal {i} pos= {goal}')
        i = i+1
    print(f'h={est_cost}', flush=True)
except Exception as e:
    print(f"Unexpected error: {e}")