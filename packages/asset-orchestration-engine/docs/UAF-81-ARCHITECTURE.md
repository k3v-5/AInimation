# UAF-81 — UNIVERSAL ASSET FACTORY

## ARCHITECTURE SPECIFICATION

**Project:** Asset Orchestration Engine  
**Program:** UAF-81 — Universal Asset Factory  
**Document Type:** Detailed Software Architecture  
**Status:** FOUNDATIONAL  
**Version:** 1.0.0  
**Parent Architecture:** Asset Orchestration Engine  
**Target:** Unreal Engine 5.x  
**Primary DCC:** Blender 4.x/5.x  

---

# 1. ARCHITECTURAL PURPOSE

Este documento define la arquitectura técnica de UAF-81 y establece la separación de responsabilidades entre el núcleo existente de Asset Orchestration Engine y las nuevas capacidades de Universal Asset Factory.

El objetivo es transformar AOE en una plataforma capaz de producir assets completos y composiciones de mundo a partir de especificaciones formales.

La arquitectura deberá evitar que los nuevos sistemas se conviertan en una colección de generadores independientes.

---

# 2. ARCHITECTURAL MISSION

La arquitectura deberá permitir:

```text
SPECIFICATION
    ↓
PLANNING
    ↓
GENERATION
    ↓
ASSEMBLY
    ↓
VALIDATION
    ↓
OPTIMIZATION
    ↓
PACKAGING
    ↓
TARGET INTEGRATION
```

Cada etapa deberá tener responsabilidades claramente delimitadas.

---

# 3. HIGH-LEVEL ARCHITECTURE

La arquitectura UAF-81 se organizará en ocho dominios principales:

```text
┌─────────────────────────────────────────────────────┐
│                 UAF CONTROL PLANE                   │
│ Intent / Specification / Planning / Governance      │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                  ASSET DOMAIN                       │
│ Identity / Components / Dependencies / Variants     │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                GENERATION DOMAIN                    │
│ Geometry / Character / Surface / World / VFX        │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 ASSEMBLY DOMAIN                     │
│ Composition / Kits / Prefabs / Worlds               │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                VALIDATION DOMAIN                    │
│ Technical / Visual / Performance / Unreal QA        │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│               OPTIMIZATION DOMAIN                   │
│ LOD / Memory / Shader / Geometry / Runtime          │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                PACKAGING DOMAIN                     │
│ Build / Export / Artifact / Delivery                │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 BACKEND DOMAIN                      │
│ Blender / Unreal / Filesystem / External Tools      │
└─────────────────────────────────────────────────────┘
```

---

# 4. EXISTING AOE INTEGRATION

UAF-81 deberá extender AOE, no reemplazarlo.

Las capacidades existentes deberán conservarse cuando ya satisfagan los requisitos.

Los sistemas existentes relacionados con:

* specification;
* intent;
* strategy selection;
* semantic asset graph;
* governance;
* checkpoints;
* diagnostics;
* task management;
* operation history;
* production orchestration;
* permissions;
* scope control;

deberán considerarse infraestructura base.

UAF-81 deberá consumir estas capacidades mediante interfaces públicas.

No deberán crearse implementaciones paralelas cuando exista una capacidad equivalente y compatible.

---

# 5. NEW CORE DOMAINS

Se establecerán los siguientes dominios conceptuales:

```text
uaf/
├── core/
├── identity/
├── specification/
├── planning/
├── generation/
├── assembly/
├── surface/
├── character/
├── geometry/
├── world/
├── validation/
├── optimization/
├── packaging/
├── integration/
├── dependencies/
├── variants/
└── profiles/
```

La estructura física definitiva podrá adaptarse a la organización actual de `src`, pero las responsabilidades deberán mantenerse.

---

# 6. UAF CORE

`uaf.core` será el núcleo de coordinación de Universal Asset Factory.

Será responsable de:

* lifecycle;
* execution context;
* operation contracts;
* shared abstractions;
* result handling;
* error model;
* status model.

No deberá contener lógica específica de Blender, Unreal, personajes o materiales.

---

# 7. ASSET IDENTITY DOMAIN

El dominio de identidad será responsable de identificar assets y artifacts.

Conceptualmente:

```text
AssetIdentity
├── asset_id
├── asset_type
├── project_id
├── specification_hash
├── generator_hash
├── dependency_hash
├── build_hash
└── content_hash
```

La identidad deberá permanecer separada del nombre visible del archivo.

El nombre de archivo no deberá utilizarse como identificador primario.

---

# 8. ASSET SPECIFICATION DOMAIN

La especificación deberá describir el resultado deseado.

No deberá describir directamente operaciones internas de Blender.

Ejemplo conceptual:

```text
CharacterSpecification
├── identity
├── body
├── appearance
├── equipment
├── style
├── quality_tier
├── target
└── constraints
```

La especificación deberá ser serializable.

Formatos posibles:

```text
JSON
YAML
Python Model
Internal Typed Model
```

El formato canónico deberá definirse durante la implementación.

---

# 9. GENERATION PLAN DOMAIN

La especificación deberá convertirse en un plan de ejecución.

```text
AssetSpecification
        ↓
GenerationPlanner
        ↓
GenerationPlan
```

El plan deberá contener:

```text
GenerationPlan
├── operations
├── dependencies
├── generators
├── backends
├── parameters
├── checkpoints
├── validations
└── expected_artifacts
```

El plan será la representación intermedia entre intención y ejecución.

---

# 10. GENERATION DOMAIN

El dominio de generación será responsable de producir componentes.

No deberá asumir cómo se ensamblarán posteriormente.

Subdominios:

```text
generation/
├── geometry/
├── character/
├── creature/
├── surface/
├── texture/
├── modular/
├── world/
├── vfx/
├── audio/
└── specialized/
```

Cada generador deberá implementar un contrato común.

---

# 11. GENERATOR CONTRACT

Todo generador deberá declarar conceptualmente:

```text
Generator
├── supported_asset_types
├── supported_quality_tiers
├── supported_targets
├── required_inputs
├── produced_artifacts
├── dependencies
├── deterministic
└── version
```

Y deberá proporcionar una operación equivalente a:

```text
generate(specification, context) → GenerationResult
```

La firma concreta deberá establecerse en los contratos de código.

---

# 12. GENERATION STRATEGIES

Una categoría podrá tener múltiples estrategias.

Ejemplo:

```text
CHARACTER
│
├── PrimitiveStrategy
├── AnatomicalStrategy
├── HardSurfaceStrategy
├── ModularStrategy
├── CreatureStrategy
└── HybridStrategy
```

El `StrategySelector` existente deberá poder evolucionar para utilizar las características de UAF-81.

La selección deberá ser explícita y registrable.

No deberá existir una selección silenciosa imposible de auditar.

---

# 13. GEOMETRY DOMAIN

El dominio geométrico será responsable exclusivamente de la creación y transformación de representación geométrica.

Deberá soportar progresivamente:

```text
Primitive
Parametric
Curve
SDF
Voxel
Remesh
HardSurface
Modular
GeometryNodes
Specialized
```

Deberá proporcionar operaciones comunes como:

```text
create
transform
combine
boolean
remesh
smooth
validate
optimize
generate_lod
generate_collision
```

Las operaciones específicas deberán depender de capacidades del backend.

---

# 14. CHARACTER DOMAIN

El dominio de personajes coordinará los subsistemas especializados necesarios para producir un personaje completo.

No deberá implementar directamente todas las técnicas geométricas.

Arquitectura:

```text
CharacterFactory
│
├── BodyGenerator
├── HeadGenerator
├── ClothingGenerator
├── ArmorGenerator
├── EquipmentGenerator
├── SkeletonGenerator
├── SkinningSystem
├── MaterialResolver
├── TextureResolver
├── LODGenerator
├── CollisionGenerator
└── CharacterValidator
```

El `CharacterFactory` será un orquestador especializado.

---

# 15. HYBRID CHARACTER PIPELINE

Un personaje complejo podrá utilizar diferentes generadores simultáneamente.

Ejemplo:

```text
CharacterFactory
│
├── Anatomical Body
├── Parametric Head
├── Modular Clothing
├── HardSurface Armor
├── Curve Cables
├── Procedural Materials
└── Skeleton
```

El sistema deberá mantener los componentes separados hasta que una operación explícita determine que deben fusionarse.

Esto evitará destruir información útil demasiado pronto.

---

# 16. SURFACE DOMAIN

El dominio Surface será responsable de la apariencia.

```text
SurfaceDefinition
├── channels
├── masks
├── parameters
├── texture_requirements
├── material_requirements
└── target_constraints
```

Deberá existir una separación entre:

```text
SurfaceDefinition
MaterialArtifact
TextureArtifact
```

No deberán tratarse como el mismo objeto.

---

# 17. TEXTURE DOMAIN

El sistema de texturas deberá poder producir:

```text
BaseColor
Normal
Roughness
Metallic
AO
Height
Emissive
Masks
ORM
Decals
```

El sistema deberá permitir tanto:

```text
Procedural Generation
```

como:

```text
Baked Output
```

cuando el pipeline lo requiera.

---

# 18. MATERIAL DOMAIN

Los materiales deberán poder existir como definiciones independientes de una geometría concreta.

Una misma definición podrá alimentar múltiples assets.

```text
MaterialDefinition
        ↓
MaterialArtifact
        ↓
MaterialInstance / Target Representation
```

Las variantes deberán reutilizar el material base cuando sea posible.

---

# 19. MODULAR ASSEMBLY DOMAIN

Este dominio será responsable de ensamblar componentes compatibles.

Cada componente modular deberá declarar:

```text
dimensions
grid
sockets
orientation
compatibility
tags
collision
materials
```

El ensamblador deberá comprobar compatibilidad antes de realizar conexiones.

No deberá asumir que dos piezas son compatibles simplemente porque sus nombres coincidan.

---

# 20. WORLD DOMAIN

El World Domain será responsable de representar y construir composiciones de gran escala.

Componentes:

```text
WorldFactory
├── WorldGraph
├── TerrainGenerator
├── BiomeGenerator
├── ModularAssembler
├── BuildingGenerator
├── PropDistributor
├── LightingSystem
├── GameplayLayout
├── NavigationLayout
└── WorldValidator
```

El `WorldGraph` será una representación intermedia fundamental.

---

# 21. WORLD GRAPH

El World Graph deberá representar:

```text
Nodes
Edges
Regions
Zones
Connections
Constraints
Metadata
```

Ejemplo:

```text
World
│
├── Region_A
│   ├── Room_A1
│   ├── Corridor_A
│   └── Arena_A
│
├── Region_B
│   └── Factory_B
│
└── Boss_Arena
```

El World Graph deberá existir antes de la construcción geométrica completa del mundo.

---

# 22. DEPENDENCY DOMAIN

El Dependency Domain será responsable de:

* registrar dependencias;
* resolver dependencias;
* detectar ciclos;
* calcular invalidaciones;
* determinar reconstrucciones;
* calcular hashes de dependencias;
* reutilizar artifacts compatibles.

Deberá integrarse con el Semantic Asset Graph existente cuando sea apropiado.

No deberán mantenerse dos grafos independientes para la misma información.

---

# 23. VARIANT DOMAIN

Las variantes deberán representar cambios respecto a un asset base.

Ejemplo:

```text
BaseCharacter
│
├── Damaged
├── Elite
├── Corrupted
└── Boss
```

Cada variante deberá declarar:

```text
base_asset
changed_components
override_parameters
additional_dependencies
```

Una variante no deberá copiar innecesariamente todo el artifact base.

---

# 24. VALIDATION DOMAIN

La validación deberá ser modular.

```text
Validator
├── GeometryValidator
├── MaterialValidator
├── TextureValidator
├── RigValidator
├── AnimationValidator
├── UnrealValidator
├── PerformanceValidator
├── DependencyValidator
└── VisualValidator
```

Cada validator deberá producir resultados estructurados.

---

# 25. VALIDATION RESULT

Conceptualmente:

```text
ValidationResult
├── validator_id
├── status
├── severity
├── metric
├── expected
├── actual
├── evidence
├── message
└── remediation
```

Estados mínimos:

```text
PASS
WARN
FAIL
NOT_APPLICABLE
NOT_EVALUATED
```

`NOT_EVALUATED` no deberá equivaler a `PASS`.

---

# 26. QUALITY GATES

Las validaciones deberán agruparse en Quality Gates.

Ejemplo:

```text
Gate: GEOMETRY
Gate: SURFACE
Gate: CHARACTER
Gate: UNREAL
Gate: PERFORMANCE
Gate: VISUAL
Gate: PACKAGE
```

Un asset no podrá pasar a `PRODUCTION_READY` mientras exista un fallo crítico en un gate obligatorio.

---

# 27. OPTIMIZATION DOMAIN

El optimizador deberá operar sobre artifacts ya válidos o sobre estados explícitamente permitidos.

Componentes:

```text
GeometryOptimizer
TextureOptimizer
MaterialOptimizer
LODOptimizer
CollisionOptimizer
MemoryOptimizer
PerformanceOptimizer
```

El optimizador deberá registrar cualquier modificación.

No deberá modificar silenciosamente un artifact sin generar una nueva identidad o versión de build.

---

# 28. PACKAGING DOMAIN

El packaging deberá transformar artifacts validados en unidades de entrega.

```text
Artifacts
    ↓
Build
    ↓
Package
```

El paquete deberá contener metadata suficiente para identificar:

```text
source specification
artifact versions
dependencies
target
validation status
build configuration
```

---

# 29. UNREAL INTEGRATION DOMAIN

Este dominio será responsable de representar artifacts en el formato requerido por Unreal.

Deberá soportar progresivamente:

```text
Static Mesh
Skeletal Mesh
Material
Material Instance
Texture
Physics Asset
Animation
Niagara
Sound
Data Asset
Level
World
```

La integración deberá ser tratada como una etapa formal del pipeline.

---

# 30. BACKEND CONTRACT

Un backend deberá declarar:

```text
Backend
├── capabilities
├── supported_formats
├── supported_operations
├── version
├── environment
└── health_status
```

El sistema deberá comprobar capacidades antes de ejecutar operaciones incompatibles.

---

# 31. BLENDER BACKEND

Blender será inicialmente uno de los backends principales.

Será responsable de operaciones que requieran Blender.

No deberá contener reglas de negocio de UAF-81.

La arquitectura deberá evitar que código como:

```text
bpy.*
```

se propague por todo el núcleo UAF.

Las llamadas a Blender deberán permanecer encapsuladas dentro del backend correspondiente.

---

# 32. UNREAL BACKEND

El Unreal Backend deberá proporcionar capacidades específicas del target Unreal.

Entre ellas:

```text
asset import
asset creation
material creation
material instance creation
level integration
metadata assignment
validation
packaging
```

La implementación concreta podrá evolucionar hacia integración mediante Python, Editor scripting, commandlets, plugins o mecanismos equivalentes.

---

# 33. EXECUTION CONTEXT

Toda ejecución deberá recibir un contexto explícito.

Conceptualmente:

```text
ExecutionContext
├── project
├── target
├── profile
├── seed
├── workspace
├── backend
├── permissions
├── cancellation
├── logging
└── checkpoint
```

No deberá dependerse de variables globales ocultas.

---

# 34. PROJECT PROFILE

El Project Profile determinará las reglas del proyecto.

```text
ProjectProfile
├── engine
├── platform
├── style
├── naming
├── paths
├── budgets
├── validation
├── packaging
└── capabilities
```

Esto permitirá que DarX sea un perfil de producción y no una dependencia arquitectónica.

---

# 35. QUALITY TIER

El Quality Tier deberá formar parte del contexto de generación.

Ejemplo:

```text
PROTOTYPE
GAMEPLAY
PRODUCTION
HERO
CINEMATIC
```

El tier podrá modificar:

* resolución;
* geometría;
* materiales;
* texturas;
* LOD;
* validación;
* budgets.

---

# 36. OPERATION MODEL

Toda operación UAF deberá poseer una identidad.

```text
Operation
├── operation_id
├── asset_id
├── operation_type
├── inputs
├── outputs
├── context
├── started_at
├── completed_at
├── status
└── evidence
```

Esto deberá integrarse con el `operation_log` existente.

---

# 37. CHECKPOINT MODEL

Las operaciones largas deberán poder producir checkpoints.

```text
Checkpoint
├── operation_id
├── stage
├── state
├── artifacts
├── dependencies
└── recoverability
```

Los checkpoints deberán ser compatibles con el mecanismo existente de recuperación de AOE.

---

# 38. ERROR MODEL

Los errores deberán clasificarse.

Categorías mínimas:

```text
SPECIFICATION_ERROR
PLANNING_ERROR
GENERATION_ERROR
ASSEMBLY_ERROR
VALIDATION_ERROR
OPTIMIZATION_ERROR
BACKEND_ERROR
DEPENDENCY_ERROR
PACKAGING_ERROR
ENVIRONMENT_ERROR
```

Cada error deberá proporcionar contexto suficiente para diagnóstico.

---

# 39. CACHE AND REUSE

UAF-81 deberá poder reutilizar artifacts compatibles.

Conceptualmente:

```text
Generation Request
        ↓
Artifact Cache
        ↓
Compatible?
   ├── YES → REUSE
   └── NO  → GENERATE
```

La compatibilidad deberá basarse en identidad, versión, parámetros y dependencias, no únicamente en el nombre del archivo.

---

# 40. CONTENT ADDRESSABILITY

Cuando resulte apropiado, los artifacts deberán poder identificarse mediante hashes de contenido.

Esto permitirá:

* deduplicación;
* cache;
* detección de cambios;
* integridad;
* reproducción.

---

# 41. OBSERVABILITY

Toda ejecución deberá producir logs estructurados.

Los sistemas existentes de diagnostics y operation history deberán reutilizarse.

No deberán existir sistemas de logging paralelos sin necesidad arquitectónica.

---

# 42. FILESYSTEM AND STORAGE

La persistencia deberá abstraerse.

Ningún módulo UAF deberá depender directamente de una ruta absoluta específica de una máquina.

La resolución deberá pasar por un servicio de workspace/storage.

Las rutas de proyecto deberán ser configurables.

---

# 43. SECURITY BOUNDARY

Los backends deberán ejecutarse dentro de límites definidos.

El acceso a:

* filesystem;
* procesos;
* Blender;
* Unreal;
* herramientas externas;

deberá pasar por las capacidades y permisos correspondientes.

La existencia de un backend no implica acceso ilimitado.

---

# 44. API BOUNDARIES

Los módulos deberán comunicarse mediante modelos tipados y contratos explícitos.

Deberá evitarse:

```text
dict
```

como mecanismo universal de comunicación interna cuando exista un modelo formal.

Los datos estructurados críticos deberán poseer tipos y validación.

---

# 45. NO GLOBAL STATE

El núcleo UAF no deberá depender de:

* variables globales mutables;
* estado implícito;
* current project global;
* current asset global;
* current backend global;
* current seed global.

Todo estado crítico deberá formar parte del contexto o de una dependencia explícita.

---

# 46. CONCURRENCY

La arquitectura deberá permitir ejecución concurrente cuando las dependencias lo permitan.

El Dependency Graph deberá utilizarse para determinar operaciones independientes.

No deberá asumirse que todas las generaciones son secuenciales.

Sin embargo, cualquier backend que no sea thread-safe deberá declarar esta limitación.

---

# 47. IDEMPOTENCY

Las operaciones de producción deberán ser idempotentes cuando sea técnicamente posible.

Ejecutar dos veces una operación equivalente no deberá producir corrupción ni duplicación accidental.

Los artifacts deberán identificarse antes de ser escritos.

---

# 48. TRANSACTIONAL GENERATION

Cuando una operación modifique múltiples artifacts, deberá existir una estrategia de commit/rollback o recuperación equivalente.

Una generación parcialmente completada no deberá marcar el asset como `READY`.

---

# 49. ARCHITECTURAL DEPENDENCY RULE

La dependencia entre capas deberá seguir:

```text
CONTROL
   ↓
DOMAIN
   ↓
SERVICES
   ↓
BACKENDS
```

Un backend no deberá importar lógica superior del dominio para ejecutar una operación.

Ejemplo prohibido:

```text
BlenderBackend → CharacterFactory
```

La dirección correcta será:

```text
CharacterFactory → BlenderBackend
```

---

# 50. UNREAL-FIRST ARTIFACT CONTRACT

Todo artifact destinado a Unreal deberá declarar su target.

Conceptualmente:

```text
TargetDefinition
├── engine_version
├── platform
├── quality_tier
├── rendering_features
├── budgets
└── compatibility
```

Esto permitirá que la validación se adapte al target real.

---

# 51. PROFESSIONAL PRODUCTION REQUIREMENT

UAF-81 no deberá considerar suficiente que un asset:

* se vea bien;
* exista en disco;
* abra correctamente en Blender.

Debe cumplir el contrato completo de producción correspondiente.

Un asset de personaje, por ejemplo, deberá poder requerir:

```text
Geometry
UV
Materials
Textures
Skeleton
Skinning
Collision
Sockets
LODs
Unreal Compatibility
Performance
Visual QA
Packaging
```

---

# 52. ARCHITECTURAL INTEGRATION WITH EXISTING AOE

La implementación deberá comenzar con un inventario de capacidades existentes.

Antes de crear un nuevo módulo se deberá comprobar si AOE ya posee una capacidad equivalente.

Prioridad:

```text
REUSE
   ↓
EXTEND
   ↓
ADAPT
   ↓
REPLACE
   ↓
CREATE NEW
```

Crear un segundo sistema para resolver el mismo problema deberá considerarse una excepción.

---

# 53. MIGRATION STRATEGY

UAF-81 deberá introducirse incrementalmente.

No deberá requerirse una reescritura completa del repositorio.

El primer objetivo será crear una capa de compatibilidad entre las abstracciones actuales y los contratos UAF.

---

# 54. FIRST IMPLEMENTATION TARGET

El primer vertical slice deberá ser:

```text
PRODUCTION CHARACTER
```

Debe recorrer:

```text
Character Specification
        ↓
Character Generation Plan
        ↓
Hybrid Character Generation
        ↓
Materials
        ↓
Skeleton
        ↓
Skinning
        ↓
LOD
        ↓
Collision
        ↓
Validation
        ↓
Unreal Integration
        ↓
Production Artifact
```

El vertical slice deberá utilizar al menos una capacidad existente de AOE y una capacidad nueva de UAF.

---

# 55. SECOND IMPLEMENTATION TARGET

Una vez validado el pipeline de personaje:

```text
MODULAR ENVIRONMENT
```

Deberá recorrer:

```text
Environment Specification
        ↓
World Graph
        ↓
Modular Kit
        ↓
Assembly
        ↓
Materials
        ↓
Props
        ↓
Lighting
        ↓
Navigation
        ↓
Validation
        ↓
Unreal Level
```

---

# 56. ARCHITECTURAL SUCCESS CONDITION

La arquitectura se considerará validada cuando el sistema pueda ejecutar los vertical slices definidos sin introducir:

* lógica duplicada;
* estado global;
* rutas absolutas;
* dependencias circulares;
* backend leakage;
* artifacts no trazables;
* resultados no reproducibles.

---

# 57. FINAL ARCHITECTURAL MODEL

El modelo definitivo deberá aproximarse a:

```text
                         USER INTENT
                              │
                              ▼
                     ASSET SPECIFICATION
                              │
                              ▼
                       ASSET GRAPH
                              │
                              ▼
                     GENERATION PLANNER
                              │
                              ▼
                      GENERATION PLAN
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          GEOMETRY         SURFACE           WORLD
              │               │                │
              ▼               ▼                ▼
         COMPONENTS       MATERIALS        STRUCTURES
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                           ASSEMBLY
                              │
                              ▼
                         VALIDATION
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  FAIL                 PASS
                    │                   │
                    ▼                   ▼
                 DIAGNOSE           OPTIMIZE
                                        │
                                        ▼
                                   PACKAGING
                                        │
                                        ▼
                                UNREAL INTEGRATION
                                        │
                                        ▼
                                PRODUCTION READY
```

Esta arquitectura constituye el contrato técnico para las fases de implementación posteriores de UAF-81.

Ninguna fase posterior deberá introducir una arquitectura incompatible con este documento sin una revisión formal.
