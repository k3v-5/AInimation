# UAF-81.90 — UNIVERSAL PROCEDURAL LEVEL DESIGN, MODULAR ASSEMBLY (WFC) & DYNAMIC MISSION DIRECTOR

**Estado:** Fase normativa activa  
**Dependencias obligatorias:** UAF-81.73 Runtime World, UAF-81.79 Runtime Gameplay, UAF-81.81 World Streaming, UAF-81.82 Autonomous AI, UAF-81.85 Dynamic Lighting, UAF-81.88 Golden Vertical Slice, UAF-81.89 Advanced Next-Gen VFX.

---

# 1. OBJETIVO GENERAL

UAF-81.90 implementa el sistema universal de diseño procedimental de niveles, ensamblado arquitectónico modular mediante Wave Function Collapse (WFC), grafos de misiones no lineales con bucles de llaves y puertas (*Lock-and-Key Pacing*), y un Director de Pacing de IA en tiempo real para modular la tensión y el ritmo de combate.

El sistema comprende:
1. **Modelos de Espacio y Sockets Modulares**: Definición métrica de piezas arquitectónicas, caras cardinales de conexión (N, S, E, W, UP, DOWN) y reglas de compatibilidad de sockets simétricos y complementarios.
2. **Solvers Wave Function Collapse (WFC) 2D y 3D**: Algoritmo de superposición cuántica de estados, selección determinista por mínima entropía de Shannon (\(H(x)\)), propagación en cascada de restricciones (AC-3) y backtracking con checkpoints ante contradicciones.
3. **Topología de Conectividad y Garantía de Rutas**: Grafo de salas y puertas con verificación estricta de camino crítico continuo (Entrada $\to$ Objetivos $\to$ Extracción) mediante algoritmos A* / BFS.
4. **Bucles de Llaves y Puertas (Lock-and-Key Pacing)**: Colocación estratégica de tarjetas de acceso, terminales de hackeo y puertas bloqueadas con demostración matemática de ausencia de softlocks (la llave siempre precede a la puerta que desbloquea).
5. **Grafo de Misiones Dinámicas (Quest DAG)**: Árbol de dependencias lógicas (AND/OR), objetivos primarios y secundarios, disparadores volumétricos espaciales y condiciones de victoria/derrota.
6. **Director de Pacing de IA en Tiempo Real**: Curva matemática de tensión y estrés del jugador que gobierna una máquina de 5 fases (`CALM`, `BUILDUP`, `PEAK`, `SUSTAINED_PEAK`, `COOLDOWN`) con inyección táctica de patrullas fuera del cono de visión.
7. **Exportación a Unreal Engine 5**: Serialización en formatos estructurados listos para ser consumidos por el plugin `UAFBridge` e instanciar Static Meshes y Data Assets en el editor.

---

# 2. SUBFASES NORMATIVAS

## 81.90.0: Core Contracts, Sockets y Tipos de Espacio
- Direcciones cardinales: `NORTH`, `SOUTH`, `EAST`, `WEST`, `UP`, `DOWN`.
- Familias de sockets: `WALL`, `DOOR`, `CORRIDOR`, `OPEN`, `VENT`, `WINDOW`.
- `RoomType`: `CORRIDOR`, `ROOM`, `HUB`, `ARENA`, `DEAD_END`, `ENTRANCE`, `EXIT`, `SECRET_VAULT`, `ELEVATOR`.
- Invariantes de sockets: Dos caras vecinas solo pueden conectarse si sus sockets son mutuamente compatibles.

## 81.90.1: Wave Function Collapse (WFC) 2D/3D & Propagación
- Entropía de Shannon para celda \(x\) con estados candidatos \(S\):
  \[
  H(x) = \log\left(\sum_{i \in S} w_i\right) - \frac{\sum_{i \in S} w_i \log(w_i)}{\sum_{i \in S} w_i}
  \]
- Selección de celda no colapsada con menor entropía positiva.
- Propagación de compatibilidad hacia los 4 o 6 vecinos inmediatos.
- Pila de checkpoints para recuperación determinista si ocurre contradicción (*deadlock*).

## 81.90.2: Topología, Camino Crítico y Bucles de Llaves y Puertas
- Construcción del grafo \(G = (V, E)\) donde \(V\) son habitaciones colapsadas y \(E\) son puertas/conexiones transitables.
- Verificación formal de camino crítico Start $\to$ Exit.
- Invariante de solvabilidad de llaves:
  \[
  \text{Distance}(\text{Start} \to \text{Key}) < \text{Distance}(\text{Start} \to \text{LockedDoor})
  \]

## 81.90.3: Grafo de Misiones y Progresión
- Grafo dirigido acíclico de objetivos con nodos de tipo:
  - `ELIMINATE_TARGET`, `COLLECT_ITEM`, `HACK_TERMINAL`, `DEFEND_AREA`, `SURVIVE_WAVE`, `ESCORT_VIP`, `REACH_EXTRACTION`.
- Conectores de dependencia lógica `ALL_REQUIRED` (AND) y `ANY_REQUIRED` (OR).
- Evaluación en tiempo real de transiciones de estado.

## 81.90.4: Director de Pacing de IA
- Algoritmo de estrés del jugador:
  \[
  \text{Stress}(t) = 0.35 (1 - H_{ratio}) + 0.25 (1 - A_{ratio}) + 0.25 \min(1.0, N_{enemies}/6) + 0.15 R_{damage}
  \]
- Transiciones reguladas entre `CALM` $\to$ `BUILDUP` $\to$ `PEAK` $\to$ `COOLDOWN`.

## 81.90.5: Exportación a UE5
- Mapeo de celdas a coordenadas de mundo `(x * tile_size, y * tile_size, z * tile_size)`.
- Generación de manifiestos de instanciación para Static Meshes (suelo, muros, techos, puertas).
- Exportación de Data Assets de misión para HUD y objetivos.

## 81.90.6: Suite de Aceptación y Certificación
- Verificación determinista ante semillas idénticas.
- Cobertura de tests unitarios e integrados con 100% de éxito.
