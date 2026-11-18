# UAF-81.2 — CAPABILITY & GENERATION STRATEGY FABRIC

## UAF-81.2-ARCH

### ARQUITECTURA DEL SISTEMA UNIVERSAL DE CAPACIDADES Y ESTRATEGIAS DE GENERACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.2 — Capability & Generation Strategy Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.2 define el sistema encargado de determinar cómo deberá producirse un asset a partir de una `ResolvedAssetSpecification`.

Esta fase deberá transformar:

```text
ResolvedAssetSpecification
        ↓
Capability Analysis
        ↓
Strategy Discovery
        ↓
Strategy Evaluation
        ↓
Strategy Composition
        ↓
Generation Plan
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá evitar que exista una única estrategia universal de generación.

La arquitectura deberá permitir múltiples estrategias especializadas que puedan combinarse.

Ejemplo:

```text
Hero Character
├── Anatomy Generator
├── Face Generator
├── Hair Generator
├── Clothing Generator
├── Armor Generator
├── Weapon Generator
├── Material Generator
├── Texture Generator
├── Rig Generator
├── Skinning Generator
├── LOD Generator
└── Unreal Packaging
```

---

# 3. FUNDAMENTAL RULE

Una capability representa:

```text
WHAT THE SYSTEM CAN DO
```

Una strategy representa:

```text
HOW THE SYSTEM INTENDS TO DO IT
```

Un implementation representa:

```text
WHICH COMPONENT ACTUALLY EXECUTES IT
```

Estas tres abstracciones no deberán mezclarse.

---

# 4. ARCHITECTURAL MODEL

```text
Capability
     ↓
Strategy
     ↓
Implementation
     ↓
Execution
```

Ejemplo:

```text
Capability:
advanced_facial_geometry

Strategy:
procedural_facial_mesh

Implementation:
FacialMeshGeneratorV2

Execution:
BlenderBackend
```

---

# 5. CAPABILITY

Cada capability deberá declarar:

```text
capability_id
version
name
description
asset_types
operations
inputs
outputs
requirements
limitations
quality_levels
targets
determinism
resource_profile
```

---

# 6. CAPABILITY TYPES

Categorías mínimas:

```text
GEOMETRY
ANATOMY
FACE
CLOTHING
HAIR
RIGGING
SKINNING
MATERIAL
TEXTURE
UV
ANIMATION
PHYSICS
MODULAR_ASSEMBLY
TERRAIN
VEGETATION
ENVIRONMENT
LEVEL
WORLD
VFX
AUDIO
OPTIMIZATION
VALIDATION
PACKAGING
EXPORT
IMPORT
```

---

# 7. CAPABILITY GRANULARITY

Las capabilities deberán ser suficientemente pequeñas para ser combinables.

Incorrecto:

```text
create_character
```

Preferido:

```text
generate_anatomy
generate_face
generate_hair
generate_clothing
generate_materials
generate_textures
generate_rig
generate_skin_weights
```

---

# 8. COMPOSITE CAPABILITIES

Podrán existir capabilities compuestas.

Ejemplo:

```text
production_character_generation
```

que requiera:

```text
anatomy
face
clothing
materials
textures
rigging
skinning
optimization
```

---

# 9. CAPABILITY VERSIONING

Las capabilities deberán versionarse.

Ejemplo:

```text
advanced_face@1.0
advanced_face@1.1
advanced_face@2.0
```

El selector deberá poder comparar compatibilidad.

---

# 10. CAPABILITY COMPATIBILITY

Cada capability podrá declarar:

```text
compatible_with
incompatible_with
requires
conflicts_with
```

---

# 11. CAPABILITY LIMITATIONS

Las limitaciones deberán ser explícitas.

Ejemplo:

```text
PrimitiveCharacterGenerator:

supports:
    C0
    C1
    C2

does_not_support:
    C4 facial fidelity
    complex cloth
    realistic hair
    production skinning
```

---

# 12. NO OVERCLAIMING

Una implementación no podrá declarar una capability que no pueda satisfacer.

La validación deberá comprobar la declaración contra tests de capability.

---

# 13. CAPABILITY CONTRACT

Cada capability deberá tener un contrato formal:

```text
CapabilityContract
```

con:

```text
input_schema
output_schema
preconditions
postconditions
quality_guarantees
failure_modes
```

---

# 14. PRECONDITIONS

Antes de ejecutar una capability deberán comprobarse sus precondiciones.

Ejemplo:

```text
generate_skin_weights
```

requiere:

```text
valid_skeleton
compatible_mesh
bone_names
bind_pose
```

---

# 15. POSTCONDITIONS

Una capability deberá declarar qué garantiza.

Ejemplo:

```text
generate_skin_weights
```

deberá producir:

```text
vertex_groups
bone_weights
weight_normalization
skeleton_binding
```

si el contrato indica dichas garantías.

---

# 16. STRATEGY MODEL

Se deberá crear:

```text
GenerationStrategy
```

con:

```text
strategy_id
version
name
description
supported_assets
required_capabilities
optional_capabilities
constraints
quality
cost
risk
determinism
```

---

# 17. STRATEGY CATEGORIES

Se deberán soportar:

```text
PROCEDURAL
PARAMETRIC
MODULAR
KITBASH
REFERENCE_DRIVEN
SCAN_DRIVEN
SIMULATION
TEXTURE_DRIVEN
HYBRID
EXTERNAL_GENERATOR
MANUAL_ASSISTED
```

---

# 18. STRATEGY COMPOSITION

Las estrategias podrán componerse.

Ejemplo:

```text
HybridCharacterStrategy
├── ParametricAnatomy
├── ReferenceDrivenFace
├── ModularArmor
├── ProceduralMaterials
├── TextureDrivenMicrodetail
└── AutomaticRigging
```

---

# 19. STRATEGY SELECTION

El selector deberá recibir:

```text
ResolvedAssetSpecification
CapabilityRegistry
StrategyRegistry
TargetProfile
QualityProfile
ResourceBudget
```

y producir:

```text
GenerationPlan
```

---

# 20. GENERATION PLAN

Deberá contener:

```text
plan_id
asset_id
strategy
nodes
dependencies
execution_order
estimated_cost
expected_quality
risks
fallbacks
```

---

# 21. GENERATION PLAN GRAPH

El plan deberá representarse como DAG.

Ejemplo:

```text
Reference
   ↓
Anatomy
   ↓
Face ─────┐
   ↓      │
Clothing  │
   ↓      │
Armor     │
   ↓      │
Materials │
   ↓      │
Textures  │
   ↓      │
Rig ──────┘
   ↓
Skinning
   ↓
Optimization
   ↓
Validation
   ↓
Packaging
```

---

# 22. NODE MODEL

Cada nodo deberá declarar:

```text
node_id
operation
capability
implementation
inputs
outputs
dependencies
resource_budget
quality_requirement
failure_policy
```

---

# 23. IMPLEMENTATION SELECTION

Una capability podrá tener múltiples implementaciones.

Ejemplo:

```text
generate_geometry

Implementations:
    PrimitiveGeometryV1
    ParametricGeometryV2
    SculptGeometryV1
    ExternalMeshGeneratorV1
```

El selector deberá elegir la implementación adecuada.

---

# 24. SELECTION FACTORS

La selección deberá considerar:

```text
asset complexity
quality profile
target
available capabilities
resource budget
execution environment
determinism
performance
compatibility
reliability
historical quality
```

---

# 25. HARD REQUIREMENTS

Si una capability requerida es `HARD`, una estrategia que no la satisfaga deberá ser descartada.

No podrá seleccionarse como fallback silencioso.

---

# 26. SOFT REQUIREMENTS

Una capability `SOFT` podrá ser sustituida por una alternativa compatible.

La sustitución deberá registrarse.

---

# 27. STRATEGY SCORE

Cada estrategia deberá producir una evaluación multidimensional.

Conceptualmente:

```text
score =
    quality_score
  + compatibility_score
  + reliability_score
  + determinism_score
  + performance_score
  - resource_cost
  - risk
```

La fórmula exacta deberá ser configurable y versionada.

---

# 28. NO SINGLE SCORE ONLY

El sistema no deberá depender exclusivamente de un número opaco.

Deberá conservar:

```text
quality_score
cost_score
risk_score
compatibility_score
confidence
```

para explicar la decisión.

---

# 29. DECISION TRACE

Cada selección deberá generar:

```text
StrategyDecisionTrace
```

Ejemplo:

```text
Candidate A
Rejected:
missing advanced_face

Candidate B
Accepted:
all hard capabilities satisfied

Candidate C
Rejected:
target incompatible
```

---

# 30. EXPLAINABILITY

El sistema deberá poder responder:

```text
Why was this strategy selected?
```

con información estructurada.

---

# 31. FALLBACK SYSTEM

Cada nodo podrá declarar fallbacks:

```text
primary
fallback_1
fallback_2
fallback_3
```

---

# 32. FALLBACK RULE

Un fallback únicamente podrá ejecutarse si:

```text
fallback capability
```

satisface todas las restricciones `HARD`.

---

# 33. QUALITY DEGRADATION

Los fallbacks deberán declarar su posible degradación.

Ejemplo:

```text
Primary:
FaceGenerator_High

Fallback:
FaceGenerator_Medium

Expected degradation:
facial microdetail
```

---

# 34. NO SILENT QUALITY LOSS

El sistema no deberá producir un asset inferior sin registrar:

```text
degradation
reason
affected_requirements
severity
```

---

# 35. FAIL-EARLY

Si ninguna estrategia puede satisfacer una especificación:

```text
NO_VALID_STRATEGY
```

deberá producirse antes de comenzar operaciones costosas.

---

# 36. CAPABILITY GAP

Deberá producirse:

```text
CapabilityGapReport
```

con:

```text
missing_capabilities
available_alternatives
blocked_operations
affected_quality
suggested_new_capabilities
```

---

# 37. EXAMPLE — CURRENT CHARACTER GENERATOR

El generador procedural actual deberá registrarse como una capability especializada.

Ejemplo:

```text
PrimitiveHumanoidGenerator
```

Puede declarar:

```text
strengths:
    humanoid proportions
    robotic anatomy
    hard-surface forms
    deterministic geometry
    rapid generation

limitations:
    realistic face
    complex cloth
    hair
    fingers with high fidelity
    advanced skin deformation
```

No deberá eliminarse.

---

# 38. CHARACTER STRATEGY MATRIX

El sistema deberá permitir una matriz similar a:

```text
Complexity   Strategy
C0           Primitive
C1           Parametric
C2           Parametric + Modular
C3           Hybrid
C4           Hybrid Advanced
C5           Specialist Pipeline
```

Los límites exactos deberán depender del capability registry y no estar codificados exclusivamente por número.

---

# 39. C4 CHARACTER

Un personaje C4 deberá poder generar un plan similar a:

```text
Anatomy
→ Advanced Face
→ Hair
→ Clothing
→ Armor
→ Materials
→ Textures
→ Skeleton
→ Skinning
→ LOD
→ Collision
→ Validation
→ Unreal Packaging
```

---

# 40. GEOMETRY STRATEGY

Geometry deberá separarse en:

```text
BASE_FORM
SECONDARY_FORM
TERTIARY_FORM
MICRO_DETAIL
```

Esto evitará exigir que una única técnica produzca toda la complejidad.

---

# 41. DETAIL STRATEGY

El sistema deberá determinar dónde colocar cada nivel de detalle.

Ejemplo:

```text
Primary:
geometry

Secondary:
geometry / displacement

Tertiary:
normal / height

Micro:
material / shader
```

---

# 42. CHARACTER DETAIL DISTRIBUTION

Un personaje podrá utilizar:

```text
silhouette → geometry
muscle definition → geometry
wrinkles → normal
pores → material/normal
fabric weave → normal/material
scratches → material
micro variation → shader
```

La decisión deberá formar parte del plan.

---

# 43. TEXTURE STRATEGY

La generación de texturas deberá poder utilizar:

```text
procedural
baked
hand-authored
reference-driven
hybrid
```

---

# 44. MATERIAL STRATEGY

Los materiales deberán poder construirse desde:

```text
base material
layer system
surface masks
procedural variation
texture inputs
target adapter
```

---

# 45. MODULAR STRATEGY

Los assets modulares deberán poder generarse mediante:

```text
module selection
socket matching
grid placement
variant selection
material assignment
validation
```

---

# 46. ENVIRONMENT STRATEGY

Environment deberá poder componerse:

```text
terrain
biomes
vegetation
structures
props
lighting
atmosphere
navigation
```

Cada subsistema podrá utilizar una estrategia distinta.

---

# 47. WORLD STRATEGY

World deberá dividirse en:

```text
macro generation
region generation
biome generation
landmark generation
gameplay generation
streaming generation
```

---

# 48. PARALLEL EXECUTION

El DAG permitirá ejecutar nodos independientes en paralelo.

Ejemplo:

```text
Face ────────┐
Clothing ────┼──→ Assembly
Armor ───────┤
Weapon ──────┘
```

---

# 49. RESOURCE-AWARE SCHEDULING

El scheduler deberá considerar:

```text
CPU
GPU
RAM
VRAM
disk
process limits
external tool limits
```

---

# 50. EXCLUSIVE RESOURCES

Una capability podrá declarar recursos exclusivos.

Ejemplo:

```text
BlenderSession
UnrealEditorSession
GPU0
```

El scheduler deberá impedir conflictos incompatibles.

---

# 51. EXTERNAL TOOLS

Una implementation podrá ejecutarse mediante un proceso externo.

Deberá declarar:

```text
executable
version
arguments
environment
inputs
outputs
timeout
resource_requirements
```

---

# 52. EXTERNAL TOOL VERSION

La versión de la herramienta deberá formar parte de provenance.

Ejemplo:

```text
Blender 4.x
Unreal Engine 5.5
```

La versión exacta deberá registrarse cuando esté disponible.

---

# 53. TOOL AVAILABILITY

Antes de ejecutar una implementation externa deberá comprobarse:

```text
installed
version
license/status
permissions
required plugins
required files
available resources
```

---

# 54. TOOL FAILURE

Si un proceso externo falla:

```text
ExternalProcessError
```

deberá conservar:

```text
exit_code
stdout
stderr
command_metadata
duration
inputs
```

según las políticas de seguridad y logging.

---

# 55. CACHE

Generation nodes deberán poder declarar si son cacheables.

La cache key deberá incluir como mínimo:

```text
specification_hash
node_configuration_hash
implementation_version
tool_version
input_artifact_hashes
```

---

# 56. CACHE INVALIDATION

Un cambio en cualquiera de los elementos relevantes deberá invalidar la cache.

No deberá reutilizarse un resultado incompatible.

---

# 57. DETERMINISM

Cada strategy deberá declarar:

```text
DETERMINISTIC
SEEDED_DETERMINISTIC
NON_DETERMINISTIC
```

---

# 58. SEEDED DETERMINISM

Cuando sea posible, una strategy deberá aceptar un seed explícito.

```text
seed
```

deberá formar parte del plan.

---

# 59. NON-DETERMINISTIC STRATEGIES

Si una strategy no puede ser determinista deberá declararlo.

Su resultado deberá registrar suficiente provenance para reproducir el proceso lo máximo posible.

---

# 60. QUALITY GATE

Antes de aceptar un strategy plan deberá comprobarse:

```text
all hard capabilities
all hard constraints
target compatibility
resource feasibility
quality feasibility
```

---

# 61. STRATEGY PLAN VALIDATOR

Se deberá crear:

```text
GenerationPlanValidator
```

que valide:

```text
DAG
dependencies
capabilities
implementations
inputs
outputs
resources
fallbacks
quality
target
```

---

# 62. PLAN FREEZE

Una vez iniciado un plan de producción, el plan deberá quedar versionado.

Las modificaciones deberán generar una nueva versión.

---

# 63. PLAN PROVENANCE

El plan deberá conservar:

```text
specification_hash
strategy_registry_version
capability_registry_version
implementation_versions
tool_versions
configuration_hash
```

---

# 64. STRATEGY REGISTRY

Se deberá crear:

```text
StrategyRegistry
```

con:

```text
register()
get()
find()
list()
evaluate()
```

---

# 65. IMPLEMENTATION REGISTRY

Se deberá crear:

```text
ImplementationRegistry
```

para separar:

```text
capability
strategy
implementation
```

---

# 66. CAPABILITY DISCOVERY

El sistema deberá poder consultar:

```text
find_capabilities(
    asset_type,
    quality_profile,
    target
)
```

---

# 67. STRATEGY DISCOVERY

Deberá existir:

```text
find_strategies(
    specification
)
```

---

# 68. IMPLEMENTATION DISCOVERY

Deberá existir:

```text
find_implementations(
    capability
)
```

---

# 69. STRATEGY CONFLICT

Si dos componentes generan outputs incompatibles:

```text
StrategyConflict
```

deberá detectarse durante planificación.

No durante la generación final.

---

# 70. OUTPUT CONTRACT

Cada generation node deberá declarar exactamente qué produce.

Ejemplo:

```text
FaceGenerator
OUTPUT:
    Mesh
    UV
    MaterialSlots
    FaceMetadata
```

---

# 71. INPUT CONTRACT

También deberá declarar qué necesita:

```text
FaceGenerator
INPUT:
    BaseHeadMesh
    FaceParameters
    ReferenceData
```

---

# 72. TYPE COMPATIBILITY

El planner deberá validar que:

```text
output_type(A)
```

sea compatible con:

```text
input_type(B)
```

antes de conectar dos nodos.

---

# 73. VERSION COMPATIBILITY

También deberá comprobar:

```text
schema version
artifact version
capability version
implementation version
```

cuando corresponda.

---

# 74. PLAN EXAMPLE — HERO CHARACTER

```text
SPECIFICATION
      ↓
Capability Analysis
      ↓
Hero Character Strategy
      │
      ├── Anatomy Generator
      ├── Face Generator
      ├── Hair Generator
      ├── Clothing Generator
      ├── Armor Generator
      ├── Weapon Generator
      ├── Material Generator
      ├── Texture Generator
      ├── UV Generator
      ├── Skeleton Generator
      ├── Skinning Generator
      ├── LOD Generator
      ├── Collision Generator
      ├── Validation
      └── Unreal Package
```

---

# 75. PLAN EXAMPLE — SIMPLE ROBOT

```text
SPECIFICATION
      ↓
Simple Procedural Strategy
      ↓
Geometry
      ↓
Materials
      ↓
Collision
      ↓
Validation
      ↓
Unreal Package
```

---

# 76. PLAN EXAMPLE — MODULAR BUILDING

```text
Specification
      ↓
Modular Strategy
      ↓
Module Generation
      ↓
Socket Validation
      ↓
Assembly
      ↓
Materials
      ↓
Collision
      ↓
Optimization
      ↓
Unreal Package
```

---

# 77. PLAN EXAMPLE — WORLD

```text
Specification
      ↓
World Strategy
      ↓
Macro Layout
      ↓
Regions
      ↓
Terrain
      ↓
Biomes
      ↓
Structures
      ↓
Props
      ↓
Navigation
      ↓
Streaming
      ↓
Optimization
      ↓
Unreal Package
```

---

# 78. STRATEGY QUALITY HISTORY

El sistema deberá permitir registrar resultados históricos de strategies.

Métricas posibles:

```text
success_rate
validation_pass_rate
average_duration
average_resource_usage
average_quality_score
failure_rate
fallback_rate
```

Esto podrá utilizarse posteriormente como señal de selección.

---

# 79. HISTORICAL DATA RULE

Los datos históricos no deberán invalidar una hard constraint.

Una estrategia con historial excelente no podrá seleccionarse si actualmente viola una condición obligatoria.

---

# 80. CONFIDENCE

La selección deberá producir:

```text
confidence
```

basada en:

```text
capability coverage
compatibility
historical reliability
quality evidence
```

---

# 81. HUMAN OVERRIDE

El sistema deberá permitir seleccionar explícitamente una strategy cuando el usuario/proyecto lo requiera.

Sin embargo, deberá validar igualmente sus contratos.

No se permitirá ejecutar una strategy incompatible únicamente por override.

---

# 82. STRATEGY LOCK

Una producción podrá declarar:

```text
strategy_lock = true
```

impidiendo que futuras reevaluaciones cambien automáticamente la estrategia.

---

# 83. REPLANNING

Si una strategy falla antes de producir un resultado válido, el sistema podrá generar:

```text
ReplanRequest
```

El replanner deberá considerar:

```text
remaining_budget
failed_node
available_fallbacks
current_artifacts
quality requirements
```

---

# 84. PARTIAL RESULTS

Los artifacts válidos producidos antes de un fallo podrán conservarse.

No deberán marcarse como finalizados.

Estado:

```text
PARTIAL
```

---

# 85. ROLLBACK

El sistema deberá poder revertir artifacts temporales cuando el contrato de la operación lo requiera.

Los artifacts publicados no deberán eliminarse automáticamente sin política explícita.

---

# 86. STRATEGY SAFETY

Una strategy no podrá ejecutar operaciones fuera de sus capabilities declaradas.

Esto deberá integrarse con los mecanismos de permisos existentes.

---

# 87. TESTING — CAPABILITY

Cada capability deberá tener:

```text
contract test
positive test
negative test
boundary test
compatibility test
failure test
```

---

# 88. TESTING — STRATEGY

Cada strategy deberá probar:

```text
selection
rejection
composition
fallback
resource validation
quality validation
determinism
```

---

# 89. TESTING — PLANNER

El planner deberá probar:

```text
DAG construction
cycle detection
dependency ordering
type compatibility
resource conflicts
capability gaps
strategy conflicts
```

---

# 90. ACCEPTANCE CRITERIA

UAF-81.2 estará terminada cuando el sistema pueda:

```text
1. registrar capabilities;
2. registrar strategies;
3. registrar implementations;
4. descubrir capabilities;
5. descubrir strategies;
6. evaluar strategies;
7. seleccionar una strategy;
8. componer múltiples strategies;
9. generar un DAG;
10. validar el DAG;
11. detectar capability gaps;
12. utilizar fallbacks;
13. detectar degradaciones;
14. calcular resource requirements;
15. registrar determinism;
16. producir decision trace;
17. producir generation plan;
18. versionar el plan;
19. cachear nodos compatibles;
20. replanificar operaciones fallidas.
```

---

# 91. CRITICAL ACCEPTANCE TEST

Deberán existir al menos dos generadores ficticios:

```text
Generator_A:
simple_geometry

Generator_B:
advanced_geometry
```

y una specification cuya calidad requiera `advanced_geometry`.

El sistema deberá seleccionar automáticamente `Generator_B`.

Si `Generator_B` no está disponible:

```text
CapabilityGapReport
```

deberá indicar que no existe una alternativa capaz de cumplir los requisitos.

No deberá degradar automáticamente a `Generator_A` si esto viola una hard requirement.

---

# 92. CHARACTER ACCEPTANCE TEST

Se deberá demostrar:

```text
C1 Character
→ Primitive Strategy

C3 Character
→ Hybrid Strategy

C4 Character
→ Advanced Hybrid Strategy
```

según capabilities registradas.

---

# 93. ARCHITECTURAL RESULT

Después de UAF-81.2:

```text
SPECIFICATION
      ↓
"What must exist?"
      ↓
CAPABILITY SYSTEM
      ↓
"What can produce it?"
      ↓
STRATEGY SYSTEM
      ↓
"How should it be produced?"
      ↓
IMPLEMENTATION SYSTEM
      ↓
"Which component executes it?"
      ↓
GENERATION PLAN
```

---

# 94. NEXT PHASE

La siguiente fase será:

# UAF-81.3 — PROCEDURAL GEOMETRY & ASSET CONSTRUCTION FABRIC

Esta fase será la primera gran capa de producción física.

Deberá absorber y evolucionar el generador procedural existente.

No deberá limitarse a personajes.

Deberá establecer una infraestructura común para:

```text
meshes
assemblies
hard surface
organic forms
modular pieces
terrain geometry
architectural geometry
detail geometry
collision geometry
LODs
UVs
```

y, especialmente, deberá introducir una arquitectura de **multi-resolution geometry**, para que un personaje complejo no dependa de una única operación de voxel remesh.

El objetivo será pasar de:

```text
primitive → remesh → smooth
```

a:

```text
semantic structure
      ↓
primary geometry
      ↓
secondary geometry
      ↓
tertiary detail
      ↓
micro detail
      ↓
optimization
```

sin perder determinismo, validación ni compatibilidad con Unreal.
