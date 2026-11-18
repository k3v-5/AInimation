# UAF-81 — UNIVERSAL ASSET FACTORY

## PHYSICAL REPOSITORY STRUCTURE & SUBSYSTEM INTEGRATION MATRIX

**Project:** Asset Orchestration Engine (AOE)  
**Program:** UAF-81 — Universal Asset Factory  
**Document Type:** Physical Topology & Subsystem Integration Specification  
**Status:** FOUNDATIONAL / NORMATIVE  
**Version:** 1.0.0  
**Parent Documents:**

* `UAF-81-UNIVERSAL-ASSET-FACTORY-MASTER.md`
* `UAF-81-ARCHITECTURE.md`
* `UAF-81-PHASE-ROADMAP.md`
* `UAF-81-CONTRACTS.md`

---

# 1. PROPÓSITO

Este documento define la **topología física exacta de directorios y archivos** para el subsistema UAF-81 dentro del repositorio, y establece las **reglas no negociables de coexistencia e integración con el código existente en `src/`** (Fases 1 a 80).

El objetivo es garantizar que UAF-81:
1. No cree una arquitectura paralela desarticulada que ignore lo construido en las 80 fases anteriores.
2. No rompa ninguno de los 1,382 tests automáticos existentes.
3. Clasifique qué módulos existentes se **reutilizan directamente**, cuáles se **encapsulan tras adaptadores**, cuáles se **adaptan** y cuáles **no se deben tocar**.
4. Establezca reglas de importación unidireccionales estrictas para impedir dependencias circulares y fugas de backend (*backend leakage*).

---

# 2. TOPOLOGÍA FÍSICA DE `src/uaf/`

Todo el nuevo desarrollo de UAF-81 residirá dentro del paquete unificado `src/uaf/`:

```text
src/uaf/
├── __init__.py                  # Fachada pública unificada de UAF-81
│
├── core/                        # UAF-81.0: Infraestructura base agnóstica
│   ├── __init__.py
│   ├── context.py               # ExecutionContext, LogEntry, LogLevel
│   ├── status.py                # LifecycleState, ResultStatus, ValidationStatus
│   ├── errors.py                # Jerarquía de excepciones: UAFError, BackendError, etc.
│   ├── results.py               # GenerationResult, OperationReport
│   ├── lifecycle.py             # AssetLifecycleStateMachine (transacciones seguras)
│   ├── configuration.py         # UAFConfiguration y StorageResolver (cero rutas fijas)
│   └── protocols.py             # Protocolos core (IBackendAdapter, IGenerator, etc.)
│
├── identity/                    # UAF-81.1: Identidad lógica y de contenido
│   ├── __init__.py
│   ├── asset_id.py              # AssetID y validación de namespaces
│   ├── artifact_id.py           # ArtifactID canónico
│   └── hashing.py               # SHA-256 canónico de especificaciones y contenidos
│
├── specification/               # UAF-81.2: Modelos declarativos (WHAT)
│   ├── __init__.py
│   ├── base.py                  # UniversalAssetSpec base
│   ├── profiles.py              # QualityProfile, TargetProfile, StyleProfile
│   ├── constraints.py           # ConstraintSpec y políticas de validación
│   └── categories/              # Extensiones tipadas por categoría
│       ├── __init__.py
│       ├── character.py         # CharacterSpecification y CharacterDNA
│       ├── weapon.py            # WeaponSpecification y SocketRequirements
│       ├── modular_kit.py       # ModularKitSpecification y GridContracts
│       ├── world.py             # WorldSpecification y ZoneRequirements
│       └── surface.py           # SurfaceSpecification y MaterialProfiles
│
├── dependencies/                # UAF-81.3: Grafo de dependencias e invalidación
│   ├── __init__.py
│   ├── dependency.py            # DependencyModel y tipos de relación
│   ├── graph.py                 # DependencyGraph y cálculo de árbol
│   └── invalidator.py           # Detección de ciclos y cálculo de cascada de impacto
│
├── planning/                    # UAF-81.4: Compilación de plan DAG (HOW)
│   ├── __init__.py
│   ├── plan.py                  # GenerationPlan y PlanTask
│   ├── planner.py               # GenerationPlanner (Spec -> Plan)
│   ├── scheduler.py             # Orden topológico y optimizador de concurrencia
│   └── seed_manager.py          # Aislamiento de PRNG por tarea
│
├── artifacts/                   # UAF-81.5: Sistema de artefactos y almacenamiento
│   ├── __init__.py
│   ├── artifact.py              # Artifact y ArtifactMetadata
│   ├── store.py                 # IArtifactStore y LocalDiskArtifactStore
│   └── manifest.py              # Generador y verificador de ArtifactManifest
│
├── backends/                    # Capa de aislamiento de herramientas y DCCs
│   ├── __init__.py
│   ├── base.py                  # Protocolo abstracto IBackendAdapter
│   ├── blender/                 # Backend Blender (aislamiento estricto de bpy)
│   │   ├── __init__.py
│   │   ├── adapter.py           # BlenderBackendAdapter
│   │   └── bridge.py            # Puente con src/blender_capability_layer
│   ├── unreal/                  # Backend Unreal Engine
│   │   ├── __init__.py
│   │   ├── adapter.py           # UnrealBackendAdapter
│   │   └── bridge.py            # Puente con src/unreal y src/game_engine_readiness
│   ├── texture/                 # Backend de horneado y texturas
│   │   ├── __init__.py
│   │   └── adapter.py           # TextureBackendAdapter
│   └── mock/                    # Backend en memoria determinista para tests
│       ├── __init__.py
│       └── adapter.py           # MockBackendAdapter (sin dependencias de DCC)
│
├── generators/                  # UAF-81.6 a 81.9: Generadores especializados
│   ├── __init__.py
│   ├── base.py                  # Protocolo abstracto IGenerator y Capabilities
│   ├── geometry/                # UAF-81.6: Primitivas, Hard-surface, Curvas, Voxel
│   │   ├── __init__.py
│   │   ├── primitive_gen.py
│   │   ├── hard_surface_gen.py
│   │   └── voxel_remesh_gen.py  # Estrategia de voxel existente preservada
│   ├── character/               # UAF-81.7 & 81.10: Ensamblaje híbrido de personajes
│   │   ├── __init__.py
│   │   ├── character_factory.py # Orquestador de personajes
│   │   ├── body_builder.py
│   │   ├── armor_builder.py
│   │   └── rig_builder.py       # UAF-81.10: Jerarquías UE Mannequin y pesos
│   ├── surface/                 # UAF-81.8 & 81.9: Superficies y texturas PBR
│   │   ├── __init__.py
│   │   ├── surface_factory.py   # SurfaceDefinition y capas de desgaste
│   │   └── texture_factory.py   # Curvatura, AO, máscaras de ruido y empaque ORM
│   ├── modular/                 # UAF-81.11: Kits modulares con rejilla métrica
│   │   ├── __init__.py
│   │   └── kit_factory.py       # Contratos de 100 cm y sockets magnéticos
│   └── world/                   # UAF-81.12: World Graph y distribución de niveles
│       ├── __init__.py
│       ├── world_factory.py     # Generador de mundos
│       └── world_graph.py       # Grafo de regiones, zonas, pasillos y arenas
│
├── assemblers/                  # Ensamblaje de piezas y verificación de sockets
│   ├── __init__.py
│   ├── socket_solver.py         # Alineación matricial de sockets
│   └── safety_buffer.py         # Guardián de Zero-Clipping (>= 30 mm)
│
├── validation/                  # UAF-81.15: Quality Gates (Técnico y Visual)
│   ├── __init__.py
│   ├── gatekeeper.py            # QualityGatekeeper (orquestador de QA)
│   ├── technical_gate.py        # Manifold, escala métrica, pivots en (0,0,0), UCX
│   └── visual_gate.py           # Rúbrica independiente: silueta, 4 vistas, Lumen PBR
│
├── optimization/                # UAF-81.14: Reducción de coste y Nanite
│   ├── __init__.py
│   ├── lod_optimizer.py         # Cadena de LODs y preservación de bordes
│   └── nanite_optimizer.py      # Presupuesto de memoria y draw calls
│
└── packaging/                   # UAF-81.13 & 81.16: Empaquetado final y entrega
    ├── __init__.py
    ├── package_sealer.py        # Sellado criptográfico de paquetes
    ├── unreal_manifest.py       # Generador de manifiestos nativos para UE5
    └── delivery_gateway.py      # Publicación y registro en Knowledge Graph
```

---

# 3. MATRIZ DE INTEGRACIÓN CON LAS 80 FASES EXISTENTES

Para evitar duplicar código y respetar la inversión de ingeniería previa, clasificamos los módulos existentes de `src/` en **4 categorías de interacción**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MATRIZ DE INTEGRACIÓN UAF <-> AOE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. REUTILIZACIÓN DIRECTA  -> Usar tal cual mediante importación pública     │
│ 2. ENCAPSULACIÓN ADAPTER  -> Aislar tras IBackendAdapter (Cero fuga de API) │
│ 3. ADAPTACIÓN & EXTENSIÓN -> Mapear tipos existentes hacia contratos UAF    │
│ 4. NO TOCAR (CONGELADO)   -> Código legacy y tests existentes intocables     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Categoría 1: REUTILIZACIÓN DIRECTA (Invocados como servicios core)

| Módulo Existente | Fase Original | Razón de Reutilización Directa |
| :--- | :--- | :--- |
| `src.governance`, `src.tool_governance` | F22, F49, F72 | Gobernanza de permisos (`ResourceLockManager`, `ToolGuard`, `MutationGuard`). Ya satisfacen el principio de *Fail-Closed*. |
| `src.knowledge_graph` | F74 | Almacén persistente de relaciones (`ProjectKnowledgeGraphStore`). UAF registrará sus assets aquí sin crear un segundo grafo. |
| `src.golden`, `src.golden_assets` | F76 | Biblioteca de activos dorados y baselines de referencia (`GoldenRegistry`, `GoldenComparator`). |
| `src.diagnostics`, `src.failure_analysis` | F77 | Diagnóstico semántico de fallos (`RootCauseAnalyzer`, `IncidentStore`). UAF enrutará sus fallos aquí. |
| `src.cost_performance` | F79 | Optimizador multiobjetivo y frontera de Pareto (`ParetoAnalyzer`, `BudgetChecker`). |
| `src.long_running_job_recovery` | F70 | Persistencia de jobs largos y recuperación tras reinicio (`JobStore`, `RecoveryDecisionEngine`). |
| `src.geometric_validation_qa` | F62 | Reglas de topología y mallas (`TopologyValidationRule`, `NormalValidationRule`, `MeshInventoryScanner`). |
| `src.automated_visual_evaluation` | F61 | Métricas visuales analíticas (`SilhouetteMetric`, `ProportionMetric`, `ColorMaterialMetric`). |

---

### Categoría 2: ENCAPSULACIÓN MEDIANTE ADAPTERS (Cero fuga hacia el Core)

Estos módulos contienen implementaciones concretas que **nunca deben importarse directamente desde el dominio UAF**; deben pasar siempre por su adaptador en `src/uaf/backends/`:

| Módulo Existente | Fase Original | Adaptador Encapsulador en UAF | Regla de Aislamiento |
| :--- | :--- | :--- | :--- |
| `src.blender_capability_layer`, `src.blender` | F53 | `uaf.backends.blender.BlenderBackendAdapter` | Prohibido importar `bpy` o `BlenderCapabilityAPI` fuera del adaptador de Blender. |
| `src.unreal`, `src.game_engine_readiness`, `src.production_pipeline_unreal` | F25, F48, F68 | `uaf.backends.unreal.UnrealBackendAdapter` | Prohibido invocar comandos de Unreal fuera del adaptador de Unreal. |
| `src.appearance`, `src.material_surface_generation` | F5, F6, F59 | `uaf.backends.texture.TextureBackendAdapter` | Las definiciones de nodos de shader se consumen a través de la interfaz abstracta de texturas. |

---

### Categoría 3: ADAPTACIÓN Y EXTENSIÓN (Mapeo a Contratos UAF)

Sistemas conceptualmente similares que UAF estandariza bajo sus nuevos contratos tipados:

| Módulo Existente | Fase Original | Evolución en UAF |
| :--- | :--- | :--- |
| `src.specification`, `src.amsl`, `src.spec_compiler` | F14, F31, F35, F56 | Se crea `uaf.specification.UniversalAssetSpec` como modelo canónico único. Se proporciona un conversor bidireccional desde `AssetSpecification` legado. |
| `src.generation_strategy_engine`, `src.procedural_modeling_strategy` | F52, F57 | Se reutiliza su lógica de selección dentro de `uaf.planning.GenerationPlanner`. |
| `src.procedural_templates` (F15), `scripts/blender_player_skin_*.py` | F15, Scripts | Se desacoplan en generadores especializados (`uaf.generators.character.body_builder`, `hard_surface_gen`). |
| `src.production_orchestration` | F80 | El orquestador de producción de 19 etapas de F80 se convierte en el motor subyacente que `uaf.packaging` y el pipeline ejecutan. |

---

### Categoría 4: NO TOCAR (Congelado e Inviolable)

Para asegurar estabilidad absoluta:
1. **Los 82 archivos de pruebas de `tests/` existentes** (`test_suite_phase1.py` a `test_suite_phase80.py`) **no se modifican ni se eliminan**. Deben continuar arrojando `PASS` en todo momento.
2. **Los scripts de prueba y validación en `scripts/` y `examples/`** permanecen como artefactos históricos de referencia.
3. Las nuevas pruebas de UAF-81 se ubicarán estrictamente en `tests/uaf/` (ej. `tests/uaf/test_uaf_81_0_foundation.py`).

---

# 4. REGLAS DE IMPORTACIÓN Y FLUJO DE DEPENDENCIAS

Para evitar acoplamientos indeseados y dependencias circulares, el flujo de importaciones entre paquetes seguirá una dirección estrictamente descendente:

```text
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 1: uaf.core (Context, Status, Errors, Protocols)      │
│          (No importa nada superior ni ningún backend)       │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 2: uaf.identity, uaf.specification, uaf.dependencies   │
│          (Dependen de Nivel 1. No conocen backends)         │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 3: uaf.planning, uaf.artifacts                        │
│          (Dependen de Niveles 1 y 2)                        │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 4: uaf.backends (Blender, Unreal, Texture, Mock)       │
│          (Implementan protocolos de Nivel 1. Aíslan DCCs)    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 5: uaf.generators, uaf.assemblers, uaf.validation     │
│          (Invocan backends mediante IBackendAdapter)        │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 6: uaf.optimization, uaf.packaging                    │
│          (Operan sobre artefactos producidos por Nivel 5)    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ NIVEL 7: uaf.pipeline (UAFProductionPipeline)               │
│          (Orquesta de extremo a extremo los Niveles 1 a 6)  │
└─────────────────────────────────────────────────────────────┘
```

### Reglas Prohibitivas de Código:
- ❌ **Prohibido**: `from uaf.core import ...` dentro de un script de Blender intentando controlar la fábrica.
- ❌ **Prohibido**: `import bpy` dentro de `uaf.core`, `uaf.specification` o `uaf.planning`.
- ❌ **Prohibido**: `from uaf.backends.blender import ...` dentro de `uaf.specification`.
- ❌ **Prohibido**: Rutas absolutas cableadas (`E:\`, `D:\`). Toda ruta se resuelve vía `ExecutionContext.storage_root` o `UAFPathResolver`.

---

# 5. RESOLUCIÓN DEFINITIVA DE ALMACENAMIENTO PORTABLE

El componente `src/uaf/core/configuration.py` implementará el contrato formal de resolución de almacenamiento para todo UAF:

```python
import os
from typing import Optional

class StorageResolver:
    """
    Resuelve de forma portable y determinista los directorios de almacenamiento.
    Elimina cualquier dependencia rígida con letras de unidad o rutas de desarrollador.
    """
    @staticmethod
    def resolve_storage_root(explicit_path: Optional[str] = None) -> str:
        # 1. Prioridad: Parámetro explícito inyectado en la sesión
        if explicit_path:
            os.makedirs(explicit_path, exist_ok=True)
            return os.path.abspath(explicit_path)

        # 2. Variable de entorno del proyecto
        env_root = os.environ.get("UAF_STORAGE_ROOT") or os.environ.get("DARX_PROJECT_ROOT")
        if env_root and os.path.exists(env_root):
            saved_dir = os.path.join(env_root, "Saved")
            os.makedirs(saved_dir, exist_ok=True)
            return os.path.abspath(saved_dir)

        # 3. Ruta de desarrollo DarX si existe físicamente en la máquina
        if os.path.exists(r"E:\Darx_Proyect"):
            saved_dir = r"E:\Darx_Proyect\Saved"
            os.makedirs(saved_dir, exist_ok=True)
            return os.path.abspath(saved_dir)

        # 4. Fallback seguro garantizado en el espacio de trabajo local
        local_saved = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Saved"))
        os.makedirs(local_saved, exist_ok=True)
        return local_saved
```

---

# 6. DEFINICIÓN DEL PUNTO DE ENTRADA: FASE UAF-81.0

Con este mapa cerrado, el desarrollo arranca de forma inmediata con **`UAF-81.0 — Foundation`**:

### Archivos a crear en `UAF-81.0`:
1. `src/uaf/__init__.py`
2. `src/uaf/core/__init__.py`
3. `src/uaf/core/context.py`
4. `src/uaf/core/status.py`
5. `src/uaf/core/errors.py`
6. `src/uaf/core/results.py`
7. `src/uaf/core/lifecycle.py`
8. `src/uaf/core/configuration.py`
9. `src/uaf/core/protocols.py`
10. `tests/uaf/__init__.py`
11. `tests/uaf/test_uaf_81_0_foundation.py`

### Evidencia requerida para cerrar UAF-81.0:
- 100% de tests de `test_uaf_81_0_foundation.py` pasando (`PASS`).
- Los 1,382 tests previos de AOE intactos y en verde.
- Cero dependencias de estado global o rutas `E:\` no verificadas.
