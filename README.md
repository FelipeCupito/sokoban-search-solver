# 🎮 Sokoban Search Solver

Un solver avanzado de Sokoban que implementa múltiples algoritmos de búsqueda con detección inteligente de deadlocks y capacidades de animación.

## ✨ Características

- 🔍 **Algoritmos de búsqueda:** BFS (Breadth-First Search) con arquitectura extensible
- 🚫 **Detección de deadlocks:** Evita explorar estados imposibles para mayor eficiencia
- 🎬 **Animación visual:** Reproduce las soluciones paso a paso
- 📊 **Métricas detalladas:** Estadísticas completas de rendimiento
- 🗺️ **Mapas flexibles:** Carga desde archivos o strings con validación automática
- ⚙️ **Configuración JSON:** Control completo mediante archivos de configuración

## 🏗️ Arquitectura

### Componentes clave

#### 🧠 **SokobanState**
- Representa el estado del juego (jugador, cajas, paredes, objetivos)
- Cache inteligente para optimización de performance
- Generación eficiente de estados sucesores

#### 🚫 **DeadlockDetector**
- **Deadlock de esquinas:** Cajas atrapadas en esquinas sin objetivos
- **Deadlock de paredes:** Cajas contra paredes sin camino a objetivos
- **Deadlock de bloqueo mutuo:** Cuadrados 2x2 de cajas sin objetivos

#### 🔍 **SearchEngine**
- Motor genérico que funciona con cualquier algoritmo
- Control de límites de tiempo y nodos
- Métricas automáticas de rendimiento

#### 📊 **SearchResult**
- Factory methods para creación de resultados
- Exportación a JSON (métricas) y CSV (animación)
- Reconstrucción automática de caminos

## 🚀 Uso

### Ejecución básica
```bash
# Ejecutar con configuración
python main.py config/test_config.json
```

### Archivo de configuración
```json
{
  "algorithm": "BFS",
  "map_name": "maps/level_1_easy.txt",
  "output_file": "mi_solucion",
  "generate_animation": true
}
```

### Ver animaciones
```bash
# Animar una solución específica
python test_animator.py
```

## 🗺️ Formato de mapas

### Símbolos estándar
- `#` - Pared
- `@` - Jugador
- `$` - Caja
- `.` - Objetivo
- ` ` - Espacio libre

### Ejemplo de mapa
```
######
#.@$ #
# $. #
#  $ #
# . ##
######
```

## 🔧 Configuración

### Parámetros disponibles
- **algorithm:** Algoritmo a usar (`"BFS"`)
- **heuristic:** Heurística opcional (no implementada en BFS)
- **map_name:** Ruta al archivo de mapa
- **output_file:** Nombre base para archivos de salida
- **generate_animation:** Generar archivo CSV para animación (`true`/`false`)

## 🎬 Animación

El sistema genera archivos CSV que pueden ser reproducidos visualmente:

### Formato CSV
```csv
step,player_pos,boxes_pos,action
0,"(1,1)","(1,2)",START
1,"(1,2)","(1,3)",RIGHT_PUSH
```

## 🔮 Extensibilidad

### Agregar nuevos algoritmos
1. Implementar `ISearchAlgorithm` en `src/algorithms/`
2. Registrar en `AlgorithmMapper`
3. ¡Listo para usar!

```python
class DFSAlgorithm(ISearchAlgorithm):
    def __init__(self):
        self._stack = []
    
    def add(self, item, heuristic=None):
        self._stack.append(item)
    
    def get_next(self):
        return self._stack.pop()
    
    # ... implementar otros métodos
```

### Agregar nuevas heurísticas
1. Implementar `IHeuristic` en `src/heuristics/`
2. Registrar en `HeuristicMapper`
3. Configurar en JSON



## 📁 Archivos generados

### Métricas (JSON)
```json
{
  "algorithm": "BFS",
  "success": true,
  "cost": 14,
  "path_length": 15,
  "metrics": {
    "nodes_expanded": 241,
    "max_frontier_size": 81,
    "processing_time_seconds": 0.0010
  }
}
```
