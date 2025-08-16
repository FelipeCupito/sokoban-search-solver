import csv
import time
import os
from typing import List, Tuple, Set
from dataclasses import dataclass


""" Animador de Sokoban by Claude """

@dataclass
class AnimationFrame:
    step: int
    player_pos: Tuple[int, int]
    boxes: Set[Tuple[int, int]]
    action: str


class SokobanAnimator:
    
    def __init__(self, animation_file: str, map_file: str = None):
        self.animation_file = animation_file
        self.frames = self._load_frames()
        self.walls, self.goals = self._load_map_info(map_file) if map_file else (set(), set())
        
        # Configuración de visualización
        self.symbols = {
            'wall': '█',
            'player': '@',
            'box': '$',
            'goal': '.',
            'box_on_goal': '*',
            # 'player_on_goal': '+',
            'space': ' '
        }
    
    def _load_frames(self) -> List[AnimationFrame]:
        """Carga los frames desde el archivo CSV"""
        frames = []
        
        if not os.path.exists(self.animation_file):
            raise FileNotFoundError(f"Archivo de animación no encontrado: {self.animation_file}")
        
        with open(self.animation_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parsear posición del jugador: "(1,1)"
                player_str = row['player_pos'].strip('()')
                player_pos = tuple(map(int, player_str.split(',')))
                
                # Parsear posiciones de cajas: "(1,2);(3,4)"
                boxes = set()
                if row['boxes_pos'].strip():
                    box_positions = row['boxes_pos'].split(';')
                    for box_str in box_positions:
                        if box_str.strip():
                            box_coords = box_str.strip('()').split(',')
                            boxes.add((int(box_coords[0]), int(box_coords[1])))
                
                frames.append(AnimationFrame(
                    step=int(row['step']),
                    player_pos=player_pos,
                    boxes=boxes,
                    action=row['action']
                ))
        
        return frames
    
    def _load_map_info(self, map_file: str) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Carga información de paredes y objetivos del mapa original"""
        from src.core.map_loader import MapLoader
        
        try:
            initial_state = MapLoader.load_from_file(map_file)
            return set(initial_state.walls), set(initial_state.goals)
        except:
            # Si no se puede cargar el mapa, inferir del primer frame
            return self._infer_map_boundaries(), set()
    
    def _infer_map_boundaries(self) -> Set[Tuple[int, int]]:
        """Infiere las dimensiones del mapa desde los frames"""
        if not self.frames:
            return set()
        
        # Obtener todas las posiciones usadas
        all_positions = set()
        for frame in self.frames:
            all_positions.add(frame.player_pos)
            all_positions.update(frame.boxes)
        
        if not all_positions:
            return set()
        
        # Calcular dimensiones
        max_row = max(pos[0] for pos in all_positions)
        max_col = max(pos[1] for pos in all_positions)
        
        # Crear paredes en los bordes
        walls = set()
        for row in range(-1, max_row + 2):
            walls.add((row, -1))
            walls.add((row, max_col + 1))
        for col in range(-1, max_col + 2):
            walls.add((-1, col))
            walls.add((max_row + 1, col))
        
        return walls
    
    def _get_map_dimensions(self) -> Tuple[int, int, int, int]:
        """Obtiene las dimensiones del mapa"""
        if not self.frames:
            return 0, 0, 0, 0
        
        all_positions = set()
        all_positions.update(self.walls)
        all_positions.update(self.goals)
        for frame in self.frames:
            all_positions.add(frame.player_pos)
            all_positions.update(frame.boxes)
        
        if not all_positions:
            return 0, 0, 0, 0
        
        min_row = min(pos[0] for pos in all_positions)
        max_row = max(pos[0] for pos in all_positions)
        min_col = min(pos[1] for pos in all_positions)
        max_col = max(pos[1] for pos in all_positions)
        
        return min_row, max_row, min_col, max_col
    
    def _render_frame(self, frame: AnimationFrame) -> str:
        """Renderiza un frame como string"""
        min_row, max_row, min_col, max_col = self._get_map_dimensions()
        
        lines = []
        for row in range(min_row, max_row + 1):
            line = []
            for col in range(min_col, max_col + 1):
                pos = (row, col)
                
                if pos in self.walls:
                    line.append(self.symbols['wall'])
                elif pos == frame.player_pos:
                    if pos in self.goals:
                        #line.append(self.symbols['player_on_goal'])
                        line.append(self.symbols['player'])
                    else:
                        line.append(self.symbols['player'])
                elif pos in frame.boxes:
                    if pos in self.goals:
                        line.append(self.symbols['box_on_goal'])
                    else:
                        line.append(self.symbols['box'])
                elif pos in self.goals:
                    line.append(self.symbols['goal'])
                else:
                    line.append(self.symbols['space'])
            
            lines.append(''.join(line))
        
        return '\n'.join(lines)
    
    def play(self, speed: float = 1.0, auto_play: bool = True):
        """Reproduce la animación"""
        if not self.frames:
            print("❌ No hay frames para reproducir")
            return
        
        print("🎬 ANIMACIÓN DE SOLUCIÓN SOKOBAN")
        print("=" * 50)
        print(f"📊 Total de pasos: {len(self.frames)}")
        print(f"⏱️  Velocidad: {speed}x")
        
        if not auto_play:
            print("🎮 Controles: ENTER = siguiente paso, 'q' + ENTER = salir")
        
        print("\n" + "=" * 50)
        
        for i, frame in enumerate(self.frames):
            # Limpiar pantalla
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Mostrar header
            print("🎬 ANIMACIÓN DE SOLUCIÓN SOKOBAN")
            print("=" * 50)
            
            # Mostrar información del paso
            print(f"📍 Paso {frame.step + 1}/{len(self.frames)}")
            print(f"🎯 Acción: {frame.action}")
            print(f"👤 Jugador: {frame.player_pos}")
            print(f"📦 Cajas: {sorted(list(frame.boxes))}")
            print()
            
            # Mostrar mapa
            print(self._render_frame(frame))
            print()
            
            # Mostrar barra de progreso
            progress = (i + 1) / len(self.frames)
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"Progreso: [{bar}] {progress:.1%}")
            
            # Control de reproducción
            if auto_play:
                if i < len(self.frames) - 1:  # No esperar en el último frame
                    time.sleep(1.0 / speed)
            else:
                if i < len(self.frames) - 1:
                    user_input = input("\nPulsa ENTER para continuar, 'q' para salir: ")
                    if user_input.lower() == 'q':
                        break
        
        print("\n🎉 ¡Animación completada!")
    
    def show_summary(self):
        """Muestra un resumen de la animación"""
        if not self.frames:
            print("❌ No hay frames cargados")
            return
        
        print("📋 RESUMEN DE ANIMACIÓN")
        print("=" * 30)
        print(f"📊 Total de pasos: {len(self.frames)}")
        print(f"🎯 Acciones realizadas:")
        
        actions = [frame.action for frame in self.frames[1:]]
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        for action, count in action_counts.items():
            print(f"  • {action}: {count} vez(es)")
        
        print(f"\n🏁 Estado final:")
        final_frame = self.frames[-1]
        print(f"  👤 Jugador: {final_frame.player_pos}")
        print(f"  📦 Cajas: {sorted(list(final_frame.boxes))}")


def main():
    """Función principal para probar el animador"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python -m src.core.animator <archivo_animacion.csv> [archivo_mapa.txt]")
        print("\nEjemplos:")
        print("  python -m src.core.animator output/animation_test_main_solution.csv")
        print("  python -m src.core.animator output/animation_level_1_solution.csv maps/level_1_easy.txt")
        return
    
    animation_file = sys.argv[1]
    map_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        animator = SokobanAnimator(animation_file, map_file)
        
        # Mostrar resumen
        animator.show_summary()
        
        # Preguntar modo de reproducción
        print("\n🎮 ¿Cómo quieres ver la animación?")
        print("1. Automática (velocidad normal)")
        print("2. Automática (velocidad rápida)")
        print("3. Manual (paso a paso)")
        
        choice = input("Selecciona una opción (1-3): ").strip()
        
        if choice == "1":
            animator.play(speed=1.0, auto_play=True)
        elif choice == "2":
            animator.play(speed=2.0, auto_play=True)
        elif choice == "3":
            animator.play(speed=1.0, auto_play=False)
        else:
            print("Opción inválida, reproduciendo automáticamente...")
            animator.play(speed=1.0, auto_play=True)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()