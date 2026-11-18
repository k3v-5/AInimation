# UAF-81 — UNIVERSAL ASSET FACTORY

## SYSTEM BOUNDARY, CODE ORGANIZATION & AOE INTEGRATION

**Project:** Asset Orchestration Engine  
**Program:** UAF-81 — Universal Asset Factory  
**Document Type:** System Boundary & Code Organization Specification  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

Este documento define:

* dónde vive UAF-81 dentro de AOE;
* qué componentes existentes serán reutilizados;
* qué componentes nuevos deberán crearse;
* qué responsabilidades permanecerán en AOE;
* qué responsabilidades pertenecerán a UAF-81;
* cómo deberán comunicarse ambos sistemas;
* qué dependencias están permitidas;
* qué dependencias están prohibidas;
* cómo deberá evolucionar la estructura física del repositorio.

El objetivo es evitar:

```text
AOE
 └── UAF
      └── otro AOE
           └── scripts
                └── lógica duplicada
```

La arquitectura correcta deberá ser:

```text
AOE CORE
   │
   ├── Existing Infrastructure
   │
   └── UAF-81
         │
         ├── Domain
         ├── Application
         ├── Generation
         ├── Validation
         ├── Optimization
         └── Target Adapters
```

---

# 2. ARCHITECTURAL POSITION

UAF-81 no reemplaza inmediatamente a AOE.

UAF-81 constituye una nueva capa especializada para producción universal de assets.

La relación será:

```text
Asset Orchestration Engine
        │
        ├── Existing capabilities
        │
        └── Universal Asset Factory
```

AOE continuará siendo responsable de la infraestructura general de orquestación.

UAF-81 será responsable del dominio de producción de contenido.

---

# 3. RESPONSIBILITY SPLIT

## AOE

AOE deberá conservar responsabilidades como:

```text
Project Governance
Task Management
Permissions
History
Diagnostics
Checkpointing
Persistence Infrastructure
Execution Infrastructure
General Orchestration
```

## UAF-81

UAF deberá encargarse de:

```text
Asset Specifications
Asset Generation
Asset Assembly
Asset Validation
Asset Optimization
Asset Packaging
Asset Variants
Asset Dependencies
Asset Production Profiles
Unreal Asset Delivery
```

---

# 4. DEPENDENCY DIRECTION

La dependencia deberá seguir:

```text
             AOE INFRASTRUCTURE
                    ▲
                    │
                    │
                 UAF-81
                    │
                    ▼
             Asset Generators
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Blender   Texture   Unreal
```

Los generadores no deberán depender directamente de módulos arbitrarios del orquestador.

Deberán comunicarse mediante contratos.

---

# 5. NEW DIRECTORY

El nuevo sistema deberá utilizar un namespace explícito.

Ubicación recomendada:

```text
src/universal_asset_factory/
```

No deberá utilizarse:

```text
src/uaf/
```

como namespace principal.

El nombre completo deberá permanecer explícito para facilitar mantenimiento y descubrimiento.

---

# 6. PROPOSED DIRECTORY TREE

La estructura inicial será:

```text
src/
└── universal_asset_factory/
    │
    ├── __init__.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── identity.py
    │   ├── specification.py
    │   ├── dependencies.py
    │   ├── context.py
    │   ├── results.py
    │   ├── errors.py
    │   ├── lifecycle.py
    │   └── versioning.py
    │
    ├── contracts/
    │   ├── __init__.py
    │   ├── generator.py
    │   ├── backend.py
    │   ├── validator.py
    │   ├── optimizer.py
    │   ├── assembler.py
    │   ├── artifact_store.py
    │   └── package.py
    │
    ├── planning/
    │   ├── __init__.py
    │   ├── generation_plan.py
    │   ├── operation.py
    │   ├── planner.py
    │   ├── capability_registry.py
    │   └── dependency_resolver.py
    │
    ├── artifacts/
    │   ├── __init__.py
    │   ├── artifact.py
    │   ├── metadata.py
    │   ├── manifest.py
    │   ├── store.py
    │   └── hashing.py
    │
    ├── generation/
    │   ├── __init__.py
    │   ├── registry.py
    │   ├── dispatcher.py
    │   ├── execution.py
    │   └── policies.py
    │
    ├── assets/
    │   ├── __init__.py
    │   ├── character/
    │   ├── creature/
    │   ├── weapon/
    │   ├── prop/
    │   ├── material/
    │   ├── texture/
    │   ├── modular/
    │   ├── environment/
    │   ├── world/
    │   └── level/
    │
    ├── validation/
    │   ├── __init__.py
    │   ├── engine.py
    │   ├── rules.py
    │   ├── technical/
    │   ├── visual/
    │   ├── performance/
    │   └── unreal/
    │
    ├── optimization/
    │   ├── __init__.py
    │   ├── engine.py
    │   ├── geometry/
    │   ├── textures/
    │   ├── materials/
    │   ├── collision/
    │   └── world/
    │
    ├── assembly/
    │   ├── __init__.py
    │   ├── character.py
    │   ├── modular.py
    │   ├── world.py
    │   └── package.py
    │
    ├── targets/
    │   ├── __init__.py
    │   ├── unreal/
    │   └── generic/
    │
    ├── profiles/
    │   ├── __init__.py
    │   ├── quality.py
    │   ├── target.py
    │   └── style.py
    │
    ├── cache/
    │   ├── __init__.py
    │   ├── keys.py
    │   └── manager.py
    │
    └── integration/
        ├── __init__.py
        ├── aoe/
        ├── blender/
        └── unreal/
```

Esta estructura deberá considerarse inicial.

No deberán crearse decenas de módulos vacíos anticipadamente.

Los directorios deberán materializarse cuando la fase correspondiente los necesite.

---

# 7. TEST STRUCTURE

Los tests deberán mantenerse separados del código productivo.

Estructura:

```text
tests/
└── universal_asset_factory/
    ├── core/
    ├── contracts/
    ├── planning/
    ├── artifacts/
    ├── generation/
    ├── assets/
    │   ├── character/
    │   ├── texture/
    │   ├── modular/
    │   └── world/
    ├── validation/
    ├── optimization/
    ├── assembly/
    ├── targets/
    ├── integration/
    └── end_to_end/
```

---

# 8. DOCUMENTATION STRUCTURE

La documentación deberá seguir el mismo modelo conceptual:

```text
docs/
└── UAF-81/
    ├── UAF-81-MASTER.md
    ├── UAF-81-ARCHITECTURE.md
    ├── UAF-81-PHASE-ROADMAP.md
    ├── UAF-81-CONTRACTS.md
    ├── UAF-81-INTEGRATION.md
    ├── UAF-81-DATA-MODEL.md
    ├── UAF-81-VALIDATION.md
    ├── UAF-81-UNREAL.md
    └── phases/
        ├── UAF-81.0-FOUNDATION.md
        ├── UAF-81.1-ASSET-IDENTITY.md
        └── ...
```

---

# 9. REUSE POLICY

Antes de crear una nueva infraestructura deberá buscarse una capacidad existente en AOE.

El orden de decisión será:

```text
1. Reuse existing component
2. Extend existing component
3. Create adapter
4. Create new component
```

No deberá implementarse una segunda versión de una capacidad existente sin justificación arquitectónica.

---

# 10. COMPONENTS EXPECTED TO BE REUSED

UAF-81 deberá evaluar y reutilizar, cuando los contratos sean compatibles:

```text
Operation Log
Checkpoint Manager
Task Manager
Permission Firewall
Scope Firewall
Diagnostics
Evaluation APIs
Golden APIs
Graph Store
Persistence Infrastructure
Strategy Selection
Specification Infrastructure
```

La reutilización deberá realizarse mediante interfaces estables.

---

# 11. COMPONENTS THAT MUST NOT BE COPIED

No deberán crearse duplicados de:

```text
TaskManager
CheckpointManager
PermissionFirewall
ScopeFirewall
OperationLog
DiagnosticsAPI
GraphStore
```

si el componente existente satisface las necesidades contractuales.

Si no las satisface, deberá analizarse primero si puede extenderse o adaptarse.

---

# 12. ADAPTER POLICY

Cuando un componente existente tenga una interfaz incompatible, deberá utilizarse un adapter.

Ejemplo:

```text
ExistingGraphStore
       │
       ▼
AOEGraphAdapter
       │
       ▼
UAFAssetGraph
```

Esto evita contaminar el dominio UAF con detalles históricos del sistema.

---

# 13. LEGACY INTEGRATION

El código existente no deberá modificarse masivamente durante UAF-81.0.

Las primeras fases deberán ser aditivas.

Es decir:

```text
Existing AOE
      +
UAF Foundation
```

antes que:

```text
Rewrite Existing AOE
```

---

# 14. MIGRATION STRATEGY

La migración deberá ocurrir gradualmente.

Modelo:

```text
Existing Component
        │
        ▼
Adapter
        │
        ▼
UAF Contract
        │
        ▼
New Implementation
```

Una implementación nueva solamente reemplazará una existente cuando:

1. exista equivalencia funcional;
2. existan tests;
3. exista migración;
4. no existan regresiones;
5. exista una decisión explícita de reemplazo.

---

# 15. GENERATOR REGISTRY

Todos los generadores UAF deberán registrarse mediante un mecanismo común.

Conceptualmente:

```text
GeneratorRegistry
        │
        ├── CharacterGenerator
        ├── CreatureGenerator
        ├── WeaponGenerator
        ├── TextureGenerator
        ├── ModularGenerator
        └── WorldGenerator
```

El planner consultará este registry.

No deberá existir un conjunto de `if/elif` centralizado que crezca indefinidamente:

```text
if type == CHARACTER:
...
elif type == WEAPON:
...
elif type == WORLD:
...
```

---

# 16. BACKEND REGISTRY

Los backends deberán seguir un modelo equivalente:

```text
BackendRegistry
        │
        ├── BlenderBackend
        ├── UnrealBackend
        ├── TextureBackend
        └── GenericBackend
```

El backend deberá declarar capacidades.

---

# 17. CAPABILITY DISCOVERY

El planner deberá poder consultar:

```text
Which generators can produce this asset?
Which backend can execute them?
Which quality levels are supported?
Which targets are supported?
What limitations exist?
```

La selección no deberá depender de nombres hardcodeados.

---

# 18. ASSET GENERATOR ORGANIZATION

Cada categoría podrá tener:

```text
assets/
└── character/
    ├── specification.py
    ├── generator.py
    ├── assembler.py
    ├── validators.py
    ├── profiles.py
    └── strategies/
        ├── anatomical.py
        ├── hard_surface.py
        ├── modular.py
        └── hybrid.py
```

No todas las categorías deberán tener exactamente esta estructura.

Se deberá evitar sobrearquitectura.

---

# 19. CHARACTER GENERATION ARCHITECTURE

El Character Factory deberá diseñarse como sistema híbrido.

```text
Character
│
├── Anatomy
│   └── Procedural
│
├── Head
│   ├── Procedural
│   ├── Modular
│   └── Specialized
│
├── Clothing
│   ├── Modular
│   ├── Procedural
│   └── Simulation-assisted
│
├── Armor
│   ├── Hard Surface
│   └── Modular
│
├── Equipment
│   └── Modular
│
├── Materials
│   └── Surface Factory
│
├── Textures
│   └── Texture Factory
│
└── Rig
    └── Rig Factory
```

Esta estructura resuelve explícitamente la limitación actual del remesh como técnica universal.

---

# 20. GEOMETRY STRATEGY SELECTION

La selección geométrica deberá realizarse por componente.

Ejemplo:

```text
Body
    → Anatomical

Head
    → Specialized

Armor
    → HardSurface

Clothing
    → Modular

Boots
    → HardSurface

Hands
    → Anatomical

Equipment
    → Modular
```

No deberá seleccionarse una única estrategia para todo el personaje.

---

# 21. GEOMETRY BACKEND ABSTRACTION

Los generadores geométricos deberán producir una representación abstracta siempre que sea posible.

Conceptualmente:

```text
GeometryRequest
       ↓
GeometryGenerator
       ↓
GeometryResult
       ↓
Backend Materialization
```

Esto permitirá cambiar la tecnología de generación sin modificar el modelo de dominio.

---

# 22. BLENDER INTEGRATION

Blender deberá tratarse como una plataforma de ejecución.

El código específico de Blender deberá permanecer en:

```text
integration/blender/
```

o en implementaciones claramente identificadas como backend.

No deberá filtrarse `bpy` hacia:

```text
core/
contracts/
planning/
```

---

# 23. UNREAL INTEGRATION

El código específico de Unreal deberá permanecer en:

```text
targets/unreal/
```

o:

```text
integration/unreal/
```

El dominio universal no deberá importar conceptos específicos de Unreal.

---

# 24. PATH POLICY

No se permitirán rutas absolutas de proyecto en el código UAF.

Prohibido:

```text
E:\Darx_Proyect
D:\Proyectos\TEST
C:\Project
```

Las rutas deberán derivarse de:

```text
Configuration
Environment
Project Context
Storage Provider
```

---

# 25. STORAGE ROOT

Deberá existir una única abstracción para el root de almacenamiento.

Ejemplo conceptual:

```text
StorageConfiguration
├── project_root
├── artifact_root
├── cache_root
├── logs_root
└── reports_root
```

La implementación deberá funcionar en Windows y, cuando sea viable, en otros sistemas.

---

# 26. ENVIRONMENT CONFIGURATION

La configuración deberá poder provenir de:

```text
Defaults
Environment Variables
Configuration File
Execution Context
Explicit Runtime Configuration
```

La prioridad deberá estar documentada y ser determinista.

---

# 27. IMPORT RULES

El núcleo deberá permanecer liviano.

Regla:

```text
core
  ↓
standard library / domain dependencies

contracts
  ↓
core

planning
  ↓
core + contracts

generation
  ↓
planning + contracts

integration
  ↓
external systems
```

No deberá existir:

```text
core → blender
core → unreal
core → filesystem implementation
```

---

# 28. CIRCULAR DEPENDENCY POLICY

No se permitirán dependencias circulares entre paquetes UAF.

Especialmente:

```text
core ↔ generation
planning ↔ assets
contracts ↔ integration
```

Los contratos deberán permanecer en una capa inferior.

---

# 29. PUBLIC API

`universal_asset_factory/__init__.py` deberá exponer únicamente APIs públicas seleccionadas.

No deberá exportar automáticamente todos los módulos internos.

Ejemplo conceptual:

```text
AssetSpecification
AssetIdentity
GenerationPlan
GenerationResult
Artifact
ValidationResult
```

Las implementaciones internas deberán permanecer privadas.

---

# 30. INTERNAL VS PUBLIC

Cada módulo deberá distinguir:

```text
PUBLIC CONTRACT
INTERNAL IMPLEMENTATION
```

La modificación de una implementación interna no deberá considerarse breaking change si el contrato permanece estable.

---

# 31. LOGGING

UAF deberá utilizar el sistema de logging existente cuando sea compatible.

No deberán crearse múltiples sistemas de logging paralelos.

Los eventos deberán incluir:

```text
execution_id
asset_id
operation_id
artifact_id
component
severity
```

---

# 32. DIAGNOSTICS

Los errores UAF deberán poder integrarse con Diagnostics.

Ejemplo:

```text
GenerationFailure
      ↓
Diagnostics Adapter
      ↓
AOE Diagnostics
```

El diagnóstico deberá conservar el contexto UAF.

---

# 33. CHECKPOINTING

Las operaciones largas deberán integrarse con el sistema de checkpoints existente.

Especialmente:

```text
Character Generation
Texture Baking
World Generation
Large Modular Assembly
Unreal Packaging
```

---

# 34. PERMISSION BOUNDARY

Los generadores no deberán poder modificar arbitrariamente cualquier recurso del proyecto.

Las operaciones deberán declarar su scope.

Ejemplo:

```text
READ_ASSET
CREATE_ARTIFACT
MODIFY_ASSET
WRITE_PACKAGE
MODIFY_UNREAL
```

La ejecución deberá respetar los mecanismos de firewall existentes.

---

# 35. TRANSACTION BOUNDARY

Las operaciones que modifiquen estado persistente deberán poder ejecutarse dentro de una transacción cuando el backend lo permita.

Ejemplo:

```text
Begin
 ↓
Generate
 ↓
Validate
 ↓
Commit
```

En caso de fallo:

```text
Rollback
```

---

# 36. TEST ISOLATION

Los tests UAF deberán poder ejecutarse sin:

```text
Blender instalado
Unreal instalado
E:\ drive
external DCC
production project
```

salvo aquellos tests explícitamente marcados como integration/e2e.

---

# 37. TEST LEVELS

Los tests deberán clasificarse:

```text
UNIT
CONTRACT
INTEGRATION
SYSTEM
END_TO_END
PRODUCTION
```

---

# 38. EXTERNAL DEPENDENCY POLICY

Las dependencias externas deberán estar aisladas.

Ejemplo:

```text
Unit Test
    ↓
Mock Backend

Integration Test
    ↓
Real Blender

E2E Test
    ↓
Blender + Unreal
```

---

# 39. PERFORMANCE

El sistema deberá registrar:

```text
generation_time
validation_time
optimization_time
packaging_time
memory_usage
artifact_size
```

La optimización del pipeline deberá basarse en datos.

---

# 40. CACHE

El cache deberá estar separado del artifact store.

```text
Artifact Store
    = authoritative content

Cache
    = disposable acceleration layer
```

Eliminar el cache no deberá destruir la fuente de verdad.

---

# 41. SOURCE OF TRUTH

La fuente de verdad deberá ser:

```text
Specification
+
Versioned Dependencies
+
Build Information
```

El archivo generado no deberá convertirse por sí solo en la única fuente de verdad.

---

# 42. FILE SYSTEM POLICY

El sistema no deberá asumir que:

```text
artifact filename
=
asset identity
```

Los nombres físicos serán una preocupación del storage adapter.

---

# 43. MIGRATION OF EXISTING CHARACTER SCRIPT

El script existente:

```text
blender_player_skin_dark_fluid.py
```

no deberá copiarse directamente dentro de UAF.

Deberá convertirse progresivamente en una implementación del contrato:

```text
CharacterGenerator
```

La lógica útil deberá extraerse y encapsularse.

El objetivo será pasar de:

```text
script
```

a:

```text
generator backend
```

---

# 44. LEGACY SCRIPT TRANSITION

La transición recomendada:

```text
Existing Script
      ↓
Legacy Adapter
      ↓
CharacterGenerator Contract
      ↓
New Character Pipeline
```

Posteriormente:

```text
Legacy Adapter
      ↓
Deprecated
      ↓
Removed
```

solamente después de alcanzar equivalencia funcional.

---

# 45. EXISTING ASSET RULES

Las reglas existentes de DarX no deberán desaparecer.

Deberán convertirse progresivamente en perfiles y validators.

Ejemplo:

```text
DarX Character Profile
      │
      ├── Capsule
      ├── Orientation
      ├── Scale
      ├── PBR
      └── Visual Rules
```

Esto permite conservar conocimiento de producción sin convertirlo en reglas universales rígidas.

---

# 46. DARX PROFILE

Las reglas específicas de DarX deberán vivir como configuración/perfil.

No deberán convertirse automáticamente en requisitos universales de UAF.

Conceptualmente:

```text
Universal Rules
      +
DarX Profile
      =
DarX Production Rules
```

---

# 47. UNIVERSAL VS PROJECT-SPECIFIC

El sistema deberá distinguir:

```text
UNIVERSAL
    Asset identity
    Artifact lifecycle
    Determinism
    Validation
    Packaging

PROJECT-SPECIFIC
    Capsule dimensions
    Style
    Naming conventions
    Material palette
    Unreal project paths
    Gameplay constraints
```

---

# 48. PROFILE SYSTEM

Los perfiles deberán permitir:

```text
Base Profile
    +
Project Profile
    +
Asset Profile
    +
Target Profile
```

Ejemplo:

```text
Universal
   +
DarX
   +
Character
   +
UE5 Production
```

---

# 49. NO HARD-CODED ART DIRECTION

No deberá existir en el core:

```text
purple
obsidian
red emissive
192cm
34cm
- Y
```

como reglas universales.

Estos valores deberán pertenecer a perfiles.

---

# 50. FEATURE FLAGS

Las capacidades experimentales deberán poder aislarse.

Ejemplo:

```text
experimental_texture_generation
experimental_world_generation
experimental_skinning
```

No deberán modificar silenciosamente el comportamiento estable.

---

# 51. VERSION COMPATIBILITY

UAF deberá registrar:

```text
AOE version
UAF version
Generator version
Backend version
Target version
Specification version
```

Esto permitirá reproducir builds.

---

# 52. BUILD MANIFEST

Cada producción deberá generar un manifest.

Ejemplo conceptual:

```text
BuildManifest
├── build_id
├── asset_id
├── specification_hash
├── dependencies
├── generators
├── backend_versions
├── seed
├── target
├── artifacts
├── validations
└── timestamps
```

---

# 53. OBSERVABILITY GRAPH

Una producción deberá poder reconstruirse mediante:

```text
Build
 │
 ├── Specification
 │
 ├── Dependencies
 │
 ├── Generator
 │
 ├── Backend
 │
 ├── Operations
 │
 ├── Artifacts
 │
 ├── Validations
 │
 └── Package
```

---

# 54. FIRST IMPLEMENTATION BOUNDARY

UAF-81.0 solamente deberá implementar:

```text
universal_asset_factory/
├── core/
├── contracts/
└── minimal integration/
```

No deberá implementar todavía:

```text
CharacterFactory
WorldFactory
TextureFactory
UnrealExporter
```

Esas capacidades pertenecen a fases posteriores.

---

# 55. FIRST FILE SET

La primera implementación deberá crear como mínimo:

```text
src/universal_asset_factory/__init__.py

src/universal_asset_factory/core/__init__.py
src/universal_asset_factory/core/identity.py
src/universal_asset_factory/core/specification.py
src/universal_asset_factory/core/context.py
src/universal_asset_factory/core/results.py
src/universal_asset_factory/core/errors.py
src/universal_asset_factory/core/lifecycle.py

src/universal_asset_factory/contracts/__init__.py
src/universal_asset_factory/contracts/generator.py
src/universal_asset_factory/contracts/backend.py
src/universal_asset_factory/contracts/validator.py
src/universal_asset_factory/contracts/artifact_store.py
```

La lista podrá ampliarse únicamente si una dependencia real lo requiere.

---

# 56. FIRST TEST SET

Deberán existir inicialmente tests para:

```text
AssetIdentity
AssetSpecification
ExecutionContext
GenerationResult
ErrorModel
Lifecycle
GeneratorContract
BackendContract
ValidatorContract
ArtifactStoreContract
```

---

# 57. FIRST ACCEPTANCE GATE

UAF-81.0 no podrá declararse aceptada hasta demostrar:

```text
import universal_asset_factory
        ↓
create specification
        ↓
create identity
        ↓
create execution context
        ↓
execute mock generator
        ↓
receive generation result
        ↓
produce artifact metadata
        ↓
validate result
```

sin utilizar Blender ni Unreal.

---

# 58. SECOND ACCEPTANCE GATE

Además deberá demostrarse:

```text
same specification
+
same seed
+
same versions
+
same dependencies
=
equivalent result
```

en el contexto donde el generador sea determinista.

---

# 59. THIRD ACCEPTANCE GATE

La infraestructura deberá ejecutarse correctamente en un entorno donde no exista:

```text
E:\
```

Esto deberá validar que el nuevo subsistema no hereda la dependencia de rutas físicas del entorno original.

---

# 60. FINAL ARCHITECTURAL BOUNDARY

La arquitectura objetivo será:

```text
┌─────────────────────────────────────────────────────┐
│                    AOE CORE                         │
│                                                     │
│ Governance │ Tasks │ Permissions │ Diagnostics      │
│ Checkpoints │ History │ Persistence │ Orchestration  │
└───────────────────────┬─────────────────────────────┘
                        │
                        │ contracts / adapters
                        ▼
┌─────────────────────────────────────────────────────┐
│              UNIVERSAL ASSET FACTORY                │
│                                                     │
│ Specification                                       │
│ Identity                                            │
│ Dependencies                                        │
│ Planning                                            │
│ Generation                                          │
│ Assembly                                            │
│ Validation                                          │
│ Optimization                                        │
│ Packaging                                           │
└───────────────┬───────────────────┬─────────────────┘
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │   BLENDER    │    │    UNREAL    │
        │   BACKEND    │    │    TARGET    │
        └──────────────┘    └──────────────┘
                │                   │
                └─────────┬─────────┘
                          ▼
                 PRODUCTION ARTIFACTS
```

---

# 61. ARCHITECTURAL DECISION

UAF-81 deberá construirse como una **capacidad nativa de AOE**, no como una aplicación externa ni como un conjunto independiente de scripts.

El objetivo es que AOE proporcione la infraestructura industrial y UAF-81 proporcione la fábrica de contenido.

---

# 62. IMPLEMENTATION RULE

A partir de este punto, cada nueva capacidad deberá responder primero:

```text
Is this an existing AOE capability?
Is this an extension of an existing capability?
Is this an adapter?
Is this genuinely new UAF functionality?
```

Solamente después de responder estas preguntas deberá crearse código.

---

# 63. FINAL TARGET

La arquitectura deberá permitir finalmente:

```text
                 ASSET REQUEST
                       │
                       ▼
                 SPECIFICATION
                       │
                       ▼
                    PLANNER
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       GENERATOR    GENERATOR    GENERATOR
          │            │            │
       Geometry     Surface       World
          │            │            │
          └────────────┼────────────┘
                       ▼
                    ASSEMBLY
                       │
                       ▼
                   VALIDATION
                       │
                       ▼
                  OPTIMIZATION
                       │
                       ▼
                   PACKAGING
                       │
                       ▼
                     UNREAL
                       │
                       ▼
                PRODUCTION BUILD
```

Este flujo deberá convertirse progresivamente en la ruta estándar para la creación de contenido.

El resultado final no será simplemente un generador de personajes mejorado.

Será una infraestructura capaz de transformar especificaciones de producción en contenido digital verificable, optimizado y preparado para Unreal Engine.
