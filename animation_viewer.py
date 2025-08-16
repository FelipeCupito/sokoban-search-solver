from src.core.animator import SokobanAnimator


def main():    
    animation_file = "output/animation_test_main_solution.csv"
    map_file = "maps/level_3.txt"
    animation_speed = 1.5
    auto_play = True

    try:
        print(f"📁 Cargando: {animation_file}")
        animator = SokobanAnimator(animation_file, map_file)
        
        # Mostrar resumen
        animator.show_summary()
        
        print("\n🎬 Reproduciendo animación...")
        animator.play(speed=animation_speed, auto_play=auto_play)
        
    except Exception as e:
        print(f"❌ Error: {e}")



if __name__ == "__main__":
    main()