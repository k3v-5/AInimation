# UAF-81.82 — UNIVERSAL RUNTIME AI, NAVIGATION MESH, DYNAMIC AVOIDANCE & BEHAVIOR TREE SYSTEM

**Estado:** Fase Normativa en Ejecución  
**Dependencias Obligatorias:**  
- UAF-81.73 Runtime World Model  
- UAF-81.74 Runtime Physics  
- UAF-81.75 Runtime Rendering  
- UAF-81.77 Runtime Input  
- UAF-81.79 Runtime Gameplay  
- UAF-81.80 Runtime Animation  
- UAF-81.81 Spatial Streaming / HLOD / World Partitioning  
- Event Bus determinista, Replay Engine, Checkpoint/Recovery, Asset Registry y sistema SHA-256 de estado canónico.

---

# 1. OBJETIVO DEL SISTEMA

UAF-81.82 implementa un subsistema universal de inteligencia artificial runtime desacoplado del motor gráfico capaz de proporcionar:
- Navegación precisa sobre NavMesh estática y dinámica con particionado en tiles espaciales.
- Búsqueda de caminos determinista mediante A* con costes de área y orden lexicográfico en colas de prioridad.
- Algoritmo Funnel (String Pulling) y suavizado de ruta restringido estrictamente a los polígonos transitables.
- Evasión local reactiva y cinemática (RVO y ORCA) con ladder de fallback determinista y protección contra división por cero.
- Percepción sensorial multicanal (visión con cono y LOS, oído con atenuación acústica, detección de daño) con memoria sensorial y decaimiento temporal de confianza por ticks lógicos.
- Blackboards tipados y serializables para intercambio de información contextual.
- Árboles de comportamiento (Behavior Trees) con secuencias, selectores, paralelos con políticas explícitas, decoradores (Inverter, Repeater, Cooldown, Timeout, ConditionGate), servicios periódicos y tareas asíncronas con enter/tick/exit/abort.
- Selección de objetivos tácticos por funciones de utilidad y relaciones de equipo (Friendly, Neutral, Hostile, Unknown).
- Niveles de detalle de simulación (AI LOD0 a LOD4) e integración con el particionado espacial de UAF-81.81 (migración de celdas sin pérdida de memoria ni estado).
- Invarianza numérica absoluta con rechazo inmediato de `NaN`/`Infinity` (`AINumericStateError`) y recuperación segura (`SafeIdleState`).
- Snapshots inmutables con `state_hash` canónico SHA-256 para replay y checkpoints bit-exactos.
- Exportación e interoperabilidad con subsistemas de Unreal Engine 5.

El sistema funciona de manera 100% headless sin requerir el editor ni bibliotecas de Unreal Engine, Blender o ventanas de visualización.

---

# 2. PRINCIPIO ARQUITECTÓNICO DE CAPAS

```text
                 UAF-81.82 RUNTIME AI
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
  NAVIGATION         PERCEPTION          DECISION
       │                  │                  │
       ▼                  ▼                  ▼
  NavMesh / Tiles      Sensors          Behavior Tree
  A* Pathfinder        Vision / LOS     Blackboard
  Funnel Algorithm     Hearing / Damage Target Utility
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                       STEERING
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
          RVO / ORCA          Movement Intent
               │                     │
               └──────────┬──────────┘
                          ▼
                   Runtime Gameplay
                          │
                          ▼
                  Runtime Animation
```

El núcleo lógico no depende de `UWorld`, `AActor`, `Pawn`, `CharacterMovementComponent` ni de ningún tipo dependiente de GPU o sistema operativo.

---

# 3. ENTIDAD AI Y PERFIL DE NAVEGACIÓN

Toda entidad controlada por IA se define mediante:

```python
@dataclass(frozen=True)
class AIEntity:
    entity_id: str
    agent_id: str
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    radius: float
    height: float
    navigation_profile: str
    team_id: str
    enabled: bool
```

Cada perfil de navegación parametriza la transitabilidad:

```python
@dataclass(frozen=True)
class NavigationProfile:
    profile_id: str
    radius: float
    height: float
    max_slope_degrees: float
    max_step_height: float
    can_jump: bool
    allowed_areas: Tuple[str, ...]
```

---

# 4. NAVMESH Y POLÍGONOS CONVEXOS

El NavMesh se compone de polígonos convexos planares indexados por `polygon_id ASC`:

```python
@dataclass(frozen=True)
class NavPolygon:
    polygon_id: int
    vertices: Tuple[Tuple[float, float, float], ...]
    neighbors: Tuple[int, ...]
    area_type: str
    traversal_cost: float
```

Reglas obligatorias:
1. `len(vertices) >= 3`.
2. Convexidad estricta (producto cruz en plano horizontal con signo constante).
3. Geometría no degenerada (área plana > $\epsilon$).
4. Vértices en orden canónico antihorario (CCW).
5. Vecinos existentes y simétricos.

---

# 5. A* DETERMINISTA Y FUNNEL ALGORITHM

La búsqueda de caminos garantiza orden determinista mediante la clave de prioridad:
`sort_key = (f, g, polygon_id)`

1. **A***: Encuentra la secuencia de polígonos convexos con coste acumulado mínimo admisible.
2. **Portales**: Extrae los segmentos comunes entre polígonos adyacentes de la ruta (`Portal(left, right, from_poly, to_poly)`).
3. **Funnel (String Pulling)**: Estrecha los rayos izquierdo y derecho hasta detectar esquinas reflexivas, generando el camino continuo de mínima longitud sin salir de los polígonos.

---

# 6. EVASIÓN LOCAL RVO / ORCA

La evasión se desacopla del pathfinding global:
1. El camino genera una velocidad deseada (`preferred_velocity`).
2. Los vecinos se ordenan estrictamente por:
   `neighbor_sort_key = (distance ASC, agent_id ASC)`
3. El solver ORCA construye los semiplanos de restricción de velocidad en 2D.
4. Si el sistema de restricciones no es factible, se aplica el **ladder de fallback determinista**:
   - Nivel 1: Velocidad preferida (si no viola restricciones críticas).
   - Nivel 2: Mínima violación cuadrática calculada determinísticamente.
   - Nivel 3: Velocidad cero (`(0.0, 0.0, 0.0)`).
5. Protección estricta contra divisiones por cero o solapamiento exacto de posiciones.

---

# 7. PERCEPCIÓN Y MEMORIA SENSORIAL

Canales sensoriales independientes:
- **Visión**: Cono angular (`vision_angle`), distancia máxima (`vision_range`) y prueba de línea de visión (LOS) vía raycast de `runtime_physics` o trazado de segmentos.
- **Oído**: `SoundStimulus` con atenuación cuadrática $I / (1 + d^2)$ y umbrales de sensibilidad del agente.
- **Daño**: Recepción de `DamageStimulus` desde `runtime_gameplay`.

La memoria sensorial almacena estímulos con confianza decreciente en ticks de simulación:
$$\text{confidence}(t) = \max\left(0.0, \text{confidence}_0 \cdot \left(1.0 - \frac{\text{elapsed\_ticks}}{\text{ttl\_ticks}}\right)\right)$$
Los estímulos con confianza cero se eliminan determinísticamente.

---

# 8. BEHAVIOR TREES Y BLACKBOARDS

Estructura determinista de control:
- **Nodos Compuestos**:
  - `Sequence`: Falla si alguno falla, avanza secuencialmente.
  - `Selector`: Éxito si alguno tiene éxito, prueba alternativas secuencialmente.
  - `Parallel`: Requiere política explícita obligatoria (`SUCCESS_ON_ALL`, `SUCCESS_ON_ONE`, `FAIL_ON_ONE`, `FAIL_ON_ALL`).
- **Decoradores**: `Inverter`, `Repeater`, `UntilSuccess`, `UntilFailure`, `Cooldown`, `Timeout`, `ConditionGate`.
- **Servicios**: `BTService` ejecutado a intervalos fijos de ticks (`interval_ticks`).
- **Tareas**: `BTTask` con interfaz canónica `enter()`, `tick()`, `exit()`, `abort()`.

---

# 9. INTEGRACIÓN CON STREAMING ESPACIAL (UAF-81.81)

- Las celdas espaciales de `runtime_streaming` (`CellKey`) poseen correspondencia directa 1:1 con `NavTile`.
- Cuando una celda se descarga: el tile pasa a no-residente y las consultas que crucen la zona reciben `NAVIGATION_UNAVAILABLE`.
- Los agentes que cruzan fronteras de celda migran de celda espacial sin perder su Blackboard, estado de Behavior Tree, target ni memoria sensorial.

---

# 10. DETERMINISMO, SNAPSHOTS Y REGLA DE NaN

1. **RNG Determinista**: Toda aleatoriedad se deriva de `DeterministicRNG(world_seed, agent_id, tick, stream_id)`.
2. **Orden Total**: Todos los bucles iteran por identificadores canónicos ordenados (`agent_id ASC`, `stimulus_id ASC`, `polygon_id ASC`).
3. **Regla de Oro contra NaN/Infinity**: La presencia de cualquier valor no finito en posiciones, velocidades, costes o puntuaciones arroja inmediatamente `AINumericStateError` y activa el `SafeIdleState`.
4. **State Hash**: Cada snapshot genera un SHA-256 canónico derivado de componentes puros, excluyendo punteros, tiempos reales de CPU e IDs de hilos.
