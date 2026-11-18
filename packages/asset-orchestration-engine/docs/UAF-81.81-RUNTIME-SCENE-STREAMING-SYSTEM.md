# UAF-81.81 — UNIVERSAL RUNTIME SCENE STREAMING, HLOD, WORLD PARTITIONING & LEVEL OF DETAIL ORCHESTRATION SYSTEM

## UAF-81.81-ARCH

### ARQUITECTURA NORMATIVA DE PARTICIONADO ESPACIAL EN RUNTIME, STREAMING DETERMINISTA, CONTROL DE RESIDENCIA, PRESUPUESTOS DE MEMORIA (RAM/VRAM), MÁQUINA DE ESTADOS DE CELDAS, JERARQUÍA HLOD, VISIBILIDAD DESACOPLADA, PREFETCH DIRECCIONAL, PROTECCIÓN ANTI-THRASHING Y ADAPTADOR DE WORLD PARTITION PARA UNREAL ENGINE 5

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.81 — Universal Runtime Scene Streaming & World Partitioning System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.80  
**Next Phase:** UAF-81.82  

---

# 1. PURPOSE

UAF-81.81 define el sistema de streaming espacial en tiempo real y particionado de mundo para el motor generador de UAF. Su responsabilidad es gobernar de manera determinista, presupuestada y observable cómo entran y salen del espacio de memoria los recursos y entidades de mundos arbitrariamente grandes sin bloquear el simulation tick, sin corromper el `state_hash` ni introducir no-determinismo por tiempos de E/S o del planificador del sistema operativo.

La fase proporciona:

```text
SPATIAL GRID (MULTI-LEVEL DETERMINISTIC GRID)
CELL KEY (FROZEN, ORDERED COMPACT TUPLE)
CELL BOUNDS (AABB & DISTANCE METRICS)
CELL STATE MACHINE (UNLOADED -> LOADING -> LOADED -> ACTIVE -> UNLOADING)
DETERMINISTIC STREAMING SCHEDULER
TOTAL ORDER QUEUES (PRIORITY, DISTANCE, CELL COORDINATES)
PREDICTIVE VELOCITY PREFETCH
MEMORY BUDGET ENFORCEMENT (CAN_FIT PREVENTIVE ADMISSION)
ORDERED EVICTION POLICY
HIERARCHICAL LEVEL OF DETAIL (HLOD LOD0..LOD3 AS DERIVED RESOURCES)
VISIBILITY & FRUSTUM CULLING (DECOUPLED FROM GRAPHICS BACKEND)
ANTI-THRASHING HYSTERESIS PROTECTION
ASYNC SIMULATION & NON-BLOCKING TICK ISOLATION
SNAPSHOTS & DETERMINISTIC STATE HASH (SHA-256)
UNREAL ENGINE 5 WORLD PARTITION & DATA LAYERS EXPORT
```

---

# 2. OWNERSHIP MODEL

El Streaming System es propietario exclusivo de:

```text
STREAMING SYSTEM
 ├── SPATIAL GRID & CELL REGISTRY
 ├── CELL RESIDENCY & ACTIVE MEMBERSHIP
 ├── STREAMING QUEUES (LOAD / UNLOAD)
 ├── BUDGET TRACKER (RAM & VRAM ALLOCATION)
 ├── HLOD CLUSTERS & TRANSITION STATE
 ├── VISIBILITY CACHE
 └── STREAMING SNAPSHOTS & AUDIT LOGS
```

No deberá apropiarse del ownership de:

```text
RuntimeWorldModel (entidades lógicas y componentes ECS)
PhysicsWorld (cuerpos rígidos y árboles BVH físicos)
RenderWorld (mallas instanciadas y pipelines de sombreado)
AnimationWorld (evaluación de esqueletos y clips)
GameplayWorld (reglas de juego, inventario y habilidades)
```

---

# 3. DETERMINISTIC CELL MODEL

Cada celda espacial se identifica de forma inmutable y unívoca por un `CellKey`:

```python
@dataclass(frozen=True, order=True)
class CellKey:
    level: int  # 0=base (p.ej. 64m), 1=128m, 2=256m, etc.
    x: int
    y: int
    z: int
```

Toda celda posee un estado observable canónico:

```python
@dataclass(frozen=True)
class CellSnapshot:
    key: CellKey
    state: CellState
    lod: int
    resident: bool
    visible: bool
    entity_count: int
    ram_bytes: int
    vram_bytes: int
    revision: int
```

**Regla de Oro**: Ninguna información efímera (dirección de memoria, ID de hilo de trabajo, tiempo real de reloj de pared o latencia de disco) formará parte del snapshot ni del hash canónico. El estado hash dependerá únicamente de la configuración lógica de celdas y decisiones tomadas.

---

# 4. CELL STATE MACHINE

Las celdas transicionan exclusivamente a través del siguiente grafo estricto:

```text
                    ┌─────────────┐
                    │  UNLOADED   │
                    └──────┬──────┘
                           │ request_load
                           ▼
                    ┌─────────────┐
                    │   LOADING   │
                    └──────┬──────┘
                           │ resources_ready
                           ▼
                    ┌─────────────┐
             ┌──────│   LOADED    │──────┐
             │      └──────┬──────┘      │
       activate             │             │ unload
             │              │             │
             ▼              │             ▼
       ┌─────────────┐      │       ┌─────────────┐
       │   ACTIVE    │      │       │  UNLOADING  │
       └──────┬──────┘      │       └──────┬──────┘
              │             │              │
              └─────────────┘              ▼
                                    ┌─────────────┐
                                    │  UNLOADED   │
                                    └─────────────┘
```

Cualquier transición no contemplada (p. ej. `UNLOADED -> ACTIVE` directo o `LOADING -> ACTIVE`) arrojará un error de contrato explícito (`InvalidCellStateTransitionError`).

---

# 5. DETERMINISTIC SCHEDULER & TOTAL ORDERING

La prioridad de carga se evalúa mediante una función pura:

```text
priority =
    distance_score
  + velocity_prediction_score
  + visibility_score
  + gameplay_criticality
  + neighbor_continuity
  - memory_cost_penalty
  - thrashing_penalty
```

Para asegurar total reproducibilidad entre plataformas y ejecuciones, la cola de carga se ordena mediante una tupla lexicográfica estricta:

```text
sort_key = (-priority, distance, key.level, key.x, key.y, key.z)
```

---

# 6. MEMORY BUDGET & ADMISSION CONTROL

El presupuesto de memoria se define mediante `StreamingBudget`:

```python
@dataclass(frozen=True)
class StreamingBudget:
    ram_bytes: int
    vram_bytes: int
    max_loaded_cells: int
    max_active_cells: int
    max_loads_per_tick: int
    max_unloads_per_tick: int
```

**Regla Normativa de Admisión Preventiva (`CAN_FIT`)**:
Bajo ninguna circunstancia se admitirá una carga que exceda el presupuesto de memoria después de aplicar las evicciones permitidas.

```text
REQUEST -> ESTIMATE -> CAN_FIT?
  ├── YES -> ADMIT LOAD
  └── NO  -> PLAN EVICTIONS -> CAN_FIT?
               ├── YES -> EXECUTE EVICTIONS -> ADMIT LOAD
               └── NO  -> REJECT / DEFER LOAD
```

---

# 7. HIERARCHICAL LEVEL OF DETAIL (HLOD)

Los niveles HLOD se definen como recursos derivados no destructivos:

* **LOD0**: Geometría y actores completos a nivel de celda cercana.
* **LOD1**: Mallas simplificadas y reducción de densidad de entidades.
* **LOD2**: Proxy HLOD agrupado (*Cluster Proxy* combinando celdas hijas en nivel `level + 1`).
* **LOD3 / Impostor**: Representación de ultra bajo coste para horizontes lejanos.

---

# 8. VISIBILITY & OCCLUSION CULLING

El cálculo de visibilidad opera de forma matemática desacoplada:
* Prueba de intersección AABB contra Frustum y cono de visión del observador (`ObserverState`).
* Caché de visibilidad para amortizar evaluaciones cuadro a cuadro.

---

# 9. INTEGRACIÓN Y EXPORTACIÓN A UNREAL ENGINE 5

El empaquetador genera manifiestos compatibles con:
* **World Partition Grids**: Tamaño de celda (`CellSize`), distancia de carga (`LoadingRange`).
* **Data Layers**: Asignación de capas para contenido condicional o streaming por misiones.
* **HLOD Layer Assets**: Mapeo de clusters hacia mallas de sustitución estandarizadas.

---

# 10. NEXT PHASE

```text
UAF-81.82 — UNIVERSAL RUNTIME AI, NAVIGATION MESH, DYNAMIC AVOIDANCE & BEHAVIOR TREE SYSTEM
```
