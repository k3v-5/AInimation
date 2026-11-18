# Índice de Conocimiento Maestro — Asset Orchestration Engine (AOE / UAF)

Este documento es el **mapa de navegación e índice técnico central** del Asset Orchestration Engine (AOE) y el Universal Asset Framework (UAF). Permite a cualquier **desarrollador o agente de IA** comprender de inmediato la estructura del repositorio, localizar especificaciones, inspeccionar código fuente y ejecutar herramientas de exportación e ingesta.

---

## 🗺️ Mapa Rápido de Inicio

| Objetivo | Documento / Comando Clave |
| :--- | :--- |
| **Arquitectura Next-Gen Global** | [`docs/UAF-NEXTGEN-ARCHITECTURE-GUIDE.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-NEXTGEN-ARCHITECTURE-GUIDE.md) |
| **Entrega Portátil para Unreal Engine 5** | [`docs/UE5-PORTABLE-WORKFLOW-GUIDE.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UE5-PORTABLE-WORKFLOW-GUIDE.md) |
| **Hoja de Ruta y Fases Pendientes** | [`docs/UAF-ROADMAP-PENDIENTES-BACKLOG.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-ROADMAP-PENDIENTES-BACKLOG.md) |
| **Ejecutar Suite Completa de Tests** | `py -3.13 -m pytest tests/ -q` (100% pasando, 0 regresiones) |
| **Exportar Paquete Portátil UE5** | `py -3.13 -m uaf.export.cli export-bundle --level L_GeneratedWorld --output ./export/` |

---

## 🏛️ 1. Estructura del Código Fuente (`src/`)

```
src/
├── uaf/                                 # Universal Asset Factory (UAF Core & Subsistemas)
│   ├── core/                           # UAF-81.0: Contratos base, identidad, hash canónico, paths y seguridad
│   │   ├── artifacts/                  # ArtifactLocation, ArtifactManifest, StorageBackend
│   │   ├── context.py                  # ProjectContext, ExecutionContext, ResourceBudget
│   │   ├── paths.py                    # PathSecurityValidator, UAFPathResolver
│   │   ├── hashing.py                  # CanonicalHasher (SHA-256 determinista)
│   │   ├── operations.py               # Máquina de estados de operaciones (STARTED, SUCCEEDED, etc.)
│   │   └── diagnostics.py              # Telemetría de ejecución, OperationMetrics, UAFError
│   │
│   ├── golden_slice/                   # UAF-81.88: Certificación Autónoma y Golden Vertical Slice
│   │   ├── pipeline/orchestrator.py    # Orquestador maestro de vertical slice jugable
│   │   ├── certification/gatekeeper.py # 7 Compuertas de certificación (GatekeeperResult)
│   │   ├── self_repair/repair_engine.py# Motor de auto-diagnóstico y auto-corrección
│   │   ├── packaging/packager.py       # Empaquetador de builds y validación de cook
│   │   └── reporting/html_report.py    # Generador de reportes visuales de certificación
│   │
│   ├── vfx_advanced/                   # UAF-81.89: VFX Avanzados, Fluidos y Acoplamiento Ambiental
│   │   ├── fluid/sph_solver.py         # Simulación de fluidos SPH con conservación de masa
│   │   ├── mesh_sampling/sampler.py    # Muestreo de huesos y mallas esqueléticas
│   │   ├── fracture/coupler.py         # Fracturas y escombros reactivos
│   │   ├── lighting/particle_lights.py # Luces puntuales virtuales (VPL) y sombras profundas
│   │   ├── lightning/breakdown.py      # Rayos dieléctricos (Laplace / Nemkov)
│   │   ├── optical/distortion.py       # Ondas de choque refractivas
│   │   ├── audio_spectral/coupler.py   # Acoplador espectral de audio (ADSR) a Niagara
│   │   └── jit/compiler.py             # Compilador JIT de scripts VFX a HLSL
│   │
│   ├── level_design/                   # UAF-81.90: Diseño de Niveles WFC, Topología & Misiones
│   │   ├── core/contracts.py           # Sockets modulares, RoomType, PlayerStressMetric
│   │   ├── wfc/solver2d.py             # Wave Function Collapse 2D (entropía de Shannon, AC-3)
│   │   ├── wfc/solver3d.py             # Wave Function Collapse 3D (escaleras, elevadores)
│   │   ├── wfc/presets.py              # Catálogos modulares Sci-Fi listos para usar
│   │   ├── topology/graph.py           # Grafo de conectividad transitable, A*, BFS, ciclos
│   │   ├── topology/lock_key.py        # Generador de puertas/llaves con cero-softlocks
│   │   ├── mission/graph.py            # Grafo de misiones DAG (algoritmo de Kahn, AND/OR)
│   │   ├── pacing/director.py          # Director de ritmo IA (curva de estrés, FSM de 5 fases)
│   │   └── export/ue5_exporter.py      # Manifiesto JSON y script Python para Unreal Editor
│   │
│   ├── landscape/                      # UAF-81.91: Macro-Paisajes, Erosión y Sustrato PCG
│   │   ├── core/contracts.py           # Heightfield2D (elevación continua, RAW 16-bit .r16)
│   │   ├── generation/noise.py         # Perlin, FBM, Ridge Multifractal, Voronoi, Domain Warping
│   │   ├── erosion/hydraulic.py        # Erosión hidráulica por partículas (gotas)
│   │   ├── erosion/thermal.py          # Relajación térmica de talud (conservación estricta de masa)
│   │   ├── ecology/biomes.py           # Clima Whittaker (temperatura, lluvia) y weightmaps de 5 capas
│   │   ├── infrastructure/drainage.py  # Cuencas de drenaje D8, lechos fluviales y splines de ríos
│   │   ├── infrastructure/road_network.py # Enrutamiento A* por superficie de costo y splines Catmull-Rom
│   │   ├── distribution/foliage.py     # Dispersión Blue Noise por disco de Poisson (sustrato PCG)
│   │   └── export/ue5_landscape_exporter.py # Exportador de .r16, .r8 y script de ingesta UE5
│   │
│   ├── ai/                             # UAF-81.92: IA Cognitiva GOAP, Escuadrones y Facciones
│   │   ├── core/contracts.py           # WorldState, GOAPAction, GOAPGoal, FactionId, TacticalRole
│   │   ├── goap/planner.py             # Planificador A* en espacio de estados y replanificación
│   │   ├── squad/tactics.py            # Bounding overwatch, flanqueo >= 60° y brecha de puertas
│   │   ├── perception/sensor.py        # Conos de visión con oclusión raycast, decaimiento de memoria
│   │   ├── faction/reputation.py       # Matriz diplomática con efecto cascada por alianzas
│   │   └── export/ue5_ai_exporter.py   # Exportador de StateTree y Blackboard para UE5
│   │
│   └── export/                         # Pipeline Portátil de Entrega UE5
│       ├── uaf_bundle_exporter.py      # Empaquetador de bundles portátiles (CLI aoe export-bundle)
│       ├── cli.py                      # Interfaz de línea de comandos del motor
│       └── UAFBridge/                  # Plugin C++ / Blueprint drop-in para Unreal Engine 5
│
└── unreal/                             # Módulos locales de compatibilidad con Unreal
```

---

## 📚 2. Catálogo Maestro de Especificaciones y Documentación (`docs/`)

### A. Guías de Integración y Flujo de Trabajo
- [`docs/UAF-NEXTGEN-ARCHITECTURE-GUIDE.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-NEXTGEN-ARCHITECTURE-GUIDE.md): **Guía maestra de la arquitectura Next-Gen** (Fases 81.88 a 81.92 integradas).
- [`docs/UE5-PORTABLE-WORKFLOW-GUIDE.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UE5-PORTABLE-WORKFLOW-GUIDE.md): Manual paso a paso para transferir assets a cualquier PC con Unreal Engine 5 sin dependencias locales.
- [`docs/UAF-ROADMAP-PENDIENTES-BACKLOG.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-ROADMAP-PENDIENTES-BACKLOG.md): Registro de fases pendientes (UAF-81.93 a UAF-81.102: Economía/Loot, MetaSounds, LiveLink, QA Playtesting, Cinemáticas Sequencer, Narrativa/Diálogos, Destrucción Chaos, Clima Volumétrico, Studio Web UI, Vertical Slice Master Builder).

### B. Especificaciones Normativas de Fases Estratégicas Recientes
- [`docs/UAF-81.88-GOLDEN-VERTICAL-SLICE-SPEC.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-81.88-GOLDEN-VERTICAL-SLICE-SPEC.md): Certificación autónoma, compuertas de calidad y empaquetado de builds reproducibles.
- [`docs/UAF-81.89-ADVANCED-NEXTGEN-VFX-SPEC.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-81.89-ADVANCED-NEXTGEN-VFX-SPEC.md): Simulación de fluidos SPH, acoplamiento espectral de audio y compilador JIT Niagara.
- [`docs/UAF-81.90-PROCEDURAL-LEVEL-DESIGN-SPEC.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-81.90-PROCEDURAL-LEVEL-DESIGN-SPEC.md): Wave Function Collapse 2D/3D, topología, bucles Lock-and-Key cero-softlock y director de ritmo.
- [`docs/UAF-81.91-PROCEDURAL-MACRO-LANDSCAPE-SPEC.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-81.91-PROCEDURAL-MACRO-LANDSCAPE-SPEC.md): Macro-paisajes continuos, erosión física, weightmaps Whittaker y carreteras Catmull-Rom.
- [`docs/UAF-81.92-MULTI-AGENT-GOAP-SPEC.md`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/docs/UAF-81.92-MULTI-AGENT-GOAP-SPEC.md): IA cognitiva GOAP, tácticas de escuadrón, percepción sensorial, memoria y exportación StateTree.

### C. Fases Fundacionales y de Especialización (UAF-81.0 a UAF-81.87)
- `docs/UAF-81.0-FOUNDATION.md`: Especificación, identidades, operaciones y gobernanza de artefactos.
- `docs/UAF-81.1-SPECIFICATION.md` a `docs/UAF-81.8-ASSEMBLY-OPTIMIZATION.md`: Generadores base de mallas, texturas PBR, rigs bípedos, modularidad y optimización LOD/Nanite.
- `docs/UAF-81.9-` a `docs/UAF-81.79-`: Módulos especializados de fauna, ropa multicapa, armaduras, biomas naturales y lógica de juego.
- `docs/UAF-81.80-` a `docs/UAF-81.87-`: Runtime streaming, World Partition, redes multijugador, iluminación Lumen y puente LiveLink UE5.

---

## 🧪 3. Suite de Verificación y Pruebas Automatizadas (`tests/`)

El repositorio cuenta con **93 archivos de pruebas de aceptación** que certifican el 100% de los subsistemas sin dependencias externas:

| Archivo de Prueba | Dominio Verificado | Casos de Prueba |
| :--- | :--- | :--- |
| [`test_acceptance_uaf81_88.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_uaf81_88.py) | Golden Vertical Slice, 7 Compuertas, Auto-reparación | 22 tests |
| [`test_acceptance_uaf81_89.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_uaf81_89.py) | Fluidos SPH, Rayos, JIT Niagara, Audio Coupling | 20 tests |
| [`test_acceptance_ue5_bundle.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_ue5_bundle.py) | Exportación de bundle portátil y CLI `aoe` | 5 tests |
| [`test_acceptance_uaf81_90.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_uaf81_90.py) | WFC 2D/3D, Cero Softlocks, Misiones DAG, Pacing | 14 tests |
| [`test_acceptance_uaf81_91.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_uaf81_91.py) | RAW 16-bit, Erosión Hidráulica/Térmica, Splines | 15 tests |
| [`test_acceptance_uaf81_92.py`](file:///d:/Proyectos/TEST/AssetOrchestrationEngine/tests/uaf/test_acceptance_uaf81_92.py) | GOAP $A^*$, Escuadrones, Percepción, Facciones, StateTree | 15 tests |
| `test_acceptance_uaf81_1.py` a `81_87.py` | Geometría, Texturas, Rigs, Redes, Streaming, etc. | 2400+ tests |

**Comando de ejecución global:**
```powershell
$env:PYTHONPATH='src'; py -3.13 -m pytest tests/uaf/test_acceptance_*.py -q
```
*Resultado actual: 100% de tests aprobados sin fallos ni advertencias.*
