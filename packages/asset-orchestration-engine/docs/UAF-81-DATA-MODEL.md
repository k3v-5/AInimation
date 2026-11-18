# UAF-81 — UNIVERSAL ASSET FACTORY

## DATA MODEL & DOMAIN CONTRACTS

**Project:** Asset Orchestration Engine  
**Program:** UAF-81 — Universal Asset Factory  
**Document Type:** Data Model & Domain Contracts  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

Este documento define el modelo de datos canónico de UAF-81.

Deberá proporcionar una representación común para:

* personajes;
* criaturas;
* armas;
* props;
* materiales;
* texturas;
* módulos;
* arquitectura;
* vegetación;
* entornos;
* mundos;
* niveles;
* VFX;
* audio;
* paquetes destinados a Unreal Engine;
* artefactos intermedios;
* resultados de validación;
* builds de producción.

El modelo deberá ser independiente de Blender y Unreal.

---

# 2. FUNDAMENTAL PRINCIPLE

UAF-81 deberá separar claramente:

```text
WHAT
    AssetSpecification

WHO
    AssetIdentity

HOW
    GenerationPlan

WITH WHAT
    Dependencies

WHAT WAS PRODUCED
    Artifact

IS IT VALID
    ValidationResult

HOW WAS IT BUILT
    BuildManifest

WHERE IS IT DESTINED
    TargetProfile
```

No deberá mezclarse especificación con implementación.

---

# 3. DOMAIN MODEL

El modelo conceptual será:

```text
Asset
│
├── Identity
├── Specification
├── Dependencies
├── GenerationPlan
├── Artifacts
├── Validations
├── BuildManifest
└── Target
```

---

# 4. ASSET IDENTITY

Todo asset deberá poseer una identidad estable.

Conceptualmente:

```text
AssetIdentity
├── asset_id
├── namespace
├── name
├── category
└── revision
```

---

# 5. ASSET ID

`asset_id` deberá ser un identificador único.

Características obligatorias:

* estable;
* no dependiente del nombre físico del archivo;
* no dependiente de la ruta;
* serializable;
* comparable;
* utilizable en grafos de dependencia.

El cambio de nombre de un archivo no deberá modificar `asset_id`.

---

# 6. NAMESPACE

Los assets deberán poder pertenecer a namespaces.

Ejemplos:

```text
darx.characters
darx.weapons
darx.environment
uaf.examples
project.production
```

El namespace no deberá determinar la implementación.

---

# 7. NAME

`name` será el identificador humano del asset.

Podrá cambiar durante una operación de rename.

El sistema deberá diferenciar:

```text
asset_id
```

de:

```text
name
```

---

# 8. REVISION

Cada cambio significativo de contenido deberá generar una revisión.

Conceptualmente:

```text
AssetIdentity
    asset_id = stable

revision
    1
    2
    3
```

No deberá reutilizarse una revisión para contenido diferente.

---

# 9. ASSET CATEGORY

Las categorías deberán ser extensibles.

El modelo base deberá soportar como mínimo:

```text
CHARACTER
CREATURE
WEAPON
PROP
MATERIAL
TEXTURE
MODULAR
ARCHITECTURE
VEGETATION
ENVIRONMENT
WORLD
LEVEL
VFX
AUDIO
```

No deberá implementarse la categoría mediante lógica que impida futuras extensiones.

---

# 10. ASSET SPECIFICATION

`AssetSpecification` representa la intención de producción.

Ejemplo conceptual:

```text
AssetSpecification
├── identity
├── category
├── description
├── parameters
├── constraints
├── style_profile
├── quality_profile
├── target_profile
├── dependencies
└── seed
```

---

# 11. SPECIFICATION IS SOURCE OF INTENT

La especificación deberá responder:

```text
What should exist?
What properties should it have?
What constraints apply?
What quality is required?
What target is required?
```

No deberá contener instrucciones específicas de Blender salvo que formen parte de un contrato de backend explícito.

---

# 12. PARAMETERS

Los parámetros deberán representar características variables.

Ejemplo para personaje:

```text
height
body_proportions
head_scale
limb_length
armor_density
surface_complexity
detail_level
```

Ejemplo para textura:

```text
resolution
channels
material_type
roughness_range
normal_strength
tiling
```

Ejemplo para mundo:

```text
size
biome
density
landmarks
navigation_requirements
streaming_requirements
```

---

# 13. CONSTRAINTS

Las constraints representan condiciones que deberán cumplirse.

Ejemplos:

```text
maximum_polygon_count
minimum_texel_density
maximum_texture_memory
collision_required
socket_required
orientation
scale
bounds
```

Una constraint no deberá confundirse con un parámetro.

```text
parameter
    = desired property

constraint
    = boundary that must be respected
```

---

# 14. HARD VS SOFT CONSTRAINTS

Cada constraint deberá indicar su severidad.

```text
HARD
    violation = build failure

SOFT
    violation = warning / optimization candidate
```

Ejemplo:

```text
capsule_radius
    HARD

preferred_triangle_count
    SOFT
```

---

# 15. STYLE PROFILE

El estilo visual deberá estar desacoplado del asset.

Ejemplo:

```text
StyleProfile
├── palette
├── material_language
├── shape_language
├── surface_language
├── proportion_language
└── visual_rules
```

Esto permitirá reutilizar una misma fábrica para:

```text
Sci-Fi
Fantasy
Stylized
Realistic
Horror
Industrial
```

---

# 16. QUALITY PROFILE

La calidad requerida deberá expresarse mediante un perfil.

Ejemplo:

```text
QualityProfile
├── geometry_quality
├── texture_quality
├── material_quality
├── animation_quality
├── collision_quality
├── optimization_level
└── validation_level
```

---

# 17. QUALITY LEVELS

El sistema deberá soportar niveles configurables.

Ejemplo:

```text
PROTOTYPE
STANDARD
PRODUCTION
HERO
CINEMATIC
```

Los nombres podrán evolucionar, pero el concepto deberá permanecer.

---

# 18. TARGET PROFILE

El target define dónde será utilizado el resultado.

Ejemplo:

```text
TargetProfile
├── engine
├── engine_version
├── platform
├── rendering_mode
├── memory_budget
├── package_requirements
└── naming_rules
```

---

# 19. UNREAL TARGET

Para Unreal deberá poder especificarse:

```text
engine_version
platform
nanite_policy
virtual_shadow_maps
lod_policy
collision_policy
material_policy
texture_policy
package_policy
```

Estos valores no deberán estar codificados en los generadores universales.

---

# 20. DEPENDENCY MODEL

Un asset podrá depender de otros assets.

Ejemplo:

```text
Character
├── Body Material
├── Armor Material
├── Weapon
├── Skeleton
├── Animation Set
└── Texture Set
```

---

# 21. DEPENDENCY OBJECT

Conceptualmente:

```text
AssetDependency
├── source_asset_id
├── target_asset_id
├── dependency_type
├── required
├── version_constraint
└── metadata
```

---

# 22. DEPENDENCY TYPES

El sistema deberá soportar como mínimo:

```text
GEOMETRY
MATERIAL
TEXTURE
RIG
ANIMATION
SOCKET
COLLISION
VARIANT
TEMPLATE
PARENT
INSTANCE
WORLD_MODULE
```

---

# 23. DEPENDENCY GRAPH

Las dependencias deberán formar un grafo dirigido.

Ejemplo:

```text
Character
   │
   ├── Armor
   │     └── Material
   │           └── Texture
   │
   └── Weapon
         └── Material
```

El sistema deberá detectar ciclos inválidos.

---

# 24. GENERATION PLAN

La especificación no constituye por sí sola un plan de ejecución.

El planner deberá producir:

```text
GenerationPlan
├── plan_id
├── specification_hash
├── operations
├── dependencies
├── selected_generators
├── selected_backends
└── execution_policy
```

---

# 25. GENERATION OPERATION

Cada operación deberá ser explícita.

Ejemplo:

```text
GenerateBaseMesh
GenerateHead
GenerateClothing
GenerateMaterials
GenerateTextures
GenerateCollision
BuildLODs
Validate
Package
```

---

# 26. OPERATION ID

Cada operación deberá poseer un identificador estable dentro del plan.

Esto permitirá:

* checkpoints;
* retries;
* observabilidad;
* debugging;
* rollback;
* métricas.

---

# 27. OPERATION DEPENDENCIES

Las operaciones deberán poder declarar precedencias.

Ejemplo:

```text
GenerateBody
      ↓
GenerateArmor
      ↓
GenerateMaterials
      ↓
GenerateTextures
      ↓
Optimize
      ↓
Validate
      ↓
Package
```

No deberá dependerse de orden accidental de ejecución.

---

# 28. ARTIFACT

Un `Artifact` representa un resultado materializado.

Ejemplos:

```text
FBX
GLB
OBJ
PNG
EXR
TGA
UASSET
UMAP
JSON
Manifest
Collision Mesh
LOD Mesh
Material Definition
```

---

# 29. ARTIFACT MODEL

Conceptualmente:

```text
Artifact
├── artifact_id
├── asset_id
├── type
├── format
├── version
├── content_hash
├── size
├── location
├── metadata
└── provenance
```

---

# 30. ARTIFACT IDENTITY

El artifact deberá poseer identidad independiente del path físico.

```text
artifact_id
    ≠
file path
```

Un artifact movido de ubicación seguirá siendo el mismo artifact si su identidad y contenido permanecen válidos.

---

# 31. CONTENT HASH

Los artifacts deberán poseer hash de contenido.

El algoritmo deberá ser explícito y configurable.

El hash deberá permitir:

```text
integrity checking
cache keys
deduplication
reproducibility
change detection
```

---

# 32. ARTIFACT PROVENANCE

Cada artifact deberá conservar información de procedencia.

Ejemplo:

```text
Provenance
├── source_specification
├── generator
├── generator_version
├── backend
├── backend_version
├── seed
├── dependencies
└── build_id
```

---

# 33. VALIDATION RESULT

La validación deberá producir datos estructurados.

```text
ValidationResult
├── validation_id
├── asset_id
├── status
├── score
├── checks
├── failures
├── warnings
└── timestamp
```

---

# 34. VALIDATION STATUS

Estados mínimos:

```text
PASS
WARN
FAIL
BLOCKED
NOT_EVALUATED
```

---

# 35. VALIDATION CHECK

Cada check deberá identificar:

```text
check_id
rule
severity
actual_value
expected_value
status
message
```

Ejemplo:

```text
triangle_budget
actual = 145000
maximum = 120000
status = FAIL
severity = ERROR
```

---

# 36. VALIDATION DOMAINS

Las validaciones deberán separarse por dominio:

```text
IDENTITY
GEOMETRY
TOPOLOGY
MATERIAL
TEXTURE
RIG
ANIMATION
COLLISION
PERFORMANCE
VISUAL
UNREAL
PACKAGING
```

---

# 37. VISUAL VALIDATION

La calidad visual deberá considerarse una dimensión independiente.

Un asset podrá:

```text
technical = PASS
visual = FAIL
```

y deberá poder ser rechazado.

Esto preserva el principio de que una validación técnica correcta no garantiza calidad artística.

---

# 38. BUILD MANIFEST

El build manifest será la representación completa de una ejecución.

```text
BuildManifest
├── build_id
├── asset
├── specification
├── plan
├── dependencies
├── execution
├── generators
├── backends
├── artifacts
├── validations
├── target
└── reproducibility
```

---

# 39. BUILD ID

Cada ejecución deberá tener un identificador único.

El `build_id` no deberá sustituir al `asset_id`.

```text
asset_id
    = identity of content

build_id
    = identity of production execution
```

---

# 40. REPRODUCIBILITY RECORD

El build deberá registrar:

```text
seed
specification_hash
dependency_hashes
generator_versions
backend_versions
configuration_hash
target_profile_hash
```

---

# 41. DETERMINISM

Cuando un generador se declare determinista:

```text
same specification
+
same dependencies
+
same versions
+
same seed
+
same configuration
```

deberá producir un resultado equivalente.

El sistema deberá distinguir:

```text
DETERMINISTIC
BEST_EFFORT_DETERMINISTIC
NON_DETERMINISTIC
```

---

# 42. RANDOM SEED

Los procesos procedurales deberán utilizar un seed explícito cuando requieran aleatoriedad.

No deberá utilizarse implícitamente:

```text
system time
global random state
untracked randomness
```

en pipelines declarados como deterministas.

---

# 43. VARIANTS

Un asset podrá generar múltiples variantes.

Ejemplo:

```text
Character
├── Variant A
├── Variant B
├── Variant C
```

Las variantes deberán conservar relación con el asset base.

---

# 44. VARIANT MODEL

Conceptualmente:

```text
AssetVariant
├── variant_id
├── parent_asset_id
├── variant_parameters
├── specification_delta
└── artifact_set
```

---

# 45. INSTANCING

El modelo deberá diferenciar:

```text
COPY
VARIANT
INSTANCE
```

Una instancia no deberá duplicar innecesariamente el artifact original.

Esto será especialmente importante para:

* modular kits;
* vegetación;
* props repetitivos;
* world generation.

---

# 46. MODULAR ASSETS

Los assets modulares deberán poder declarar:

```text
Module
├── dimensions
├── connection_points
├── sockets
├── compatibility_rules
├── materials
└── variants
```

Esto permitirá construir:

```text
Wall
Door
Floor
Ceiling
Room
Building
Dungeon
```

a partir de módulos compatibles.

---

# 47. WORLD MODEL

Un mundo no deberá representarse únicamente como un archivo monolítico.

Conceptualmente:

```text
World
├── WorldSpecification
├── Terrain
├── Biomes
├── Modules
├── Landmarks
├── Foliage
├── Roads
├── Navigation
├── Streaming
└── WorldArtifacts
```

---

# 48. LEVEL MODEL

Un level deberá poder referenciar:

```text
Actors
Assets
Instances
Volumes
Lighting
Navigation
World Partition Data
```

El modelo universal no deberá asumir que todo level es un simple archivo de geometría.

---

# 49. MATERIAL MODEL

Los materiales deberán separarse de sus texturas.

```text
Material
├── shader_model
├── parameters
├── textures
├── instances
├── quality_profile
└── target_profile
```

Una textura podrá ser compartida por múltiples materiales.

---

# 50. TEXTURE MODEL

Una textura deberá poder describir:

```text
Texture
├── resolution
├── format
├── channels
├── color_space
├── compression
├── mip_policy
├── tiling
├── semantic
└── target_constraints
```

---

# 51. TEXTURE SEMANTICS

El sistema deberá distinguir al menos:

```text
BASE_COLOR
NORMAL
ROUGHNESS
METALLIC
AO
EMISSIVE
MASK
HEIGHT
OPACITY
ORM
CUSTOM
```

---

# 52. CHARACTER MODEL

Un personaje deberá poder declarar componentes:

```text
Character
├── anatomy
├── head
├── eyes
├── hair
├── clothing
├── armor
├── equipment
├── materials
├── textures
├── skeleton
├── skinning
├── animation_sets
└── collision
```

No deberá obligarse a todos los personajes a implementar todos los componentes.

---

# 53. CREATURE MODEL

Creature script/infrastructure deberá compartir con Character cuando sea posible.

Sin embargo, no deberá asumir:

```text
humanoid skeleton
humanoid proportions
two arms
two legs
human anatomy
```

La arquitectura deberá permitir criaturas no humanoides.

---

# 54. WEAPON MODEL

Una weapon podrá declarar:

```text
geometry
materials
textures
sockets
collision
physics
attachments
animation_requirements
```

---

# 55. PROP MODEL

Los props deberán poder declarar:

```text
geometry
materials
collision
interaction_points
sockets
variants
```

---

# 56. ARTIFACT SET

Un asset podrá generar múltiples artifacts.

Ejemplo:

```text
Character
├── skeletal_mesh
├── physics_asset
├── materials
├── textures
├── collision
├── LODs
└── metadata
```

El conjunto deberá permanecer relacionado mediante `asset_id`.

---

# 57. PACKAGE

Un package representa un conjunto preparado para consumo de un target.

```text
Package
├── package_id
├── asset_ids
├── artifacts
├── manifest
├── target
├── dependencies
└── validation
```

---

# 58. UNREAL PACKAGE

El package para Unreal deberá poder incluir:

```text
Static Mesh
Skeletal Mesh
Physics Asset
Materials
Material Instances
Textures
Niagara Assets
Animation Assets
Blueprint Dependencies
Level Assets
Metadata
```

La representación física exacta dependerá del target adapter.

---

# 59. ERROR MODEL

Los errores deberán ser estructurados.

Categorías mínimas:

```text
SPECIFICATION_ERROR
PLANNING_ERROR
GENERATION_ERROR
VALIDATION_ERROR
OPTIMIZATION_ERROR
PACKAGING_ERROR
BACKEND_ERROR
DEPENDENCY_ERROR
PERSISTENCE_ERROR
CONFIGURATION_ERROR
```

---

# 60. ERROR CONTEXT

Cada error deberá incluir cuando sea posible:

```text
error_code
message
asset_id
build_id
operation_id
component
cause
recoverability
```

---

# 61. RECOVERABILITY

Los errores deberán indicar si pueden reintentarse.

```text
RETRYABLE
NON_RETRYABLE
REQUIRES_INTERVENTION
UNKNOWN
```

---

# 62. SERIALIZATION

Los objetos de dominio deberán poder serializarse de forma determinista.

El formato inicial recomendado será JSON-compatible.

No deberá incluirse información dependiente de:

```text
memory address
object repr
runtime-specific pointer
unordered implementation details
```

---

# 63. CANONICAL SERIALIZATION

Para hashing deberá existir una serialización canónica.

La serialización deberá definir:

* orden de claves;
* representación de valores;
* valores nulos;
* floats;
* enums;
* listas;
* identificadores.

---

# 64. FLOAT POLICY

Los valores flotantes utilizados para identidad/hash deberán normalizarse de manera determinista.

No deberá permitirse que pequeñas diferencias de representación generen hashes inconsistentes cuando el dominio considere los valores equivalentes.

---

# 65. SCHEMA VERSION

Todo objeto persistible deberá poder identificar su versión de schema.

Ejemplo:

```text
schema_version = "1.0"
```

Un cambio incompatible deberá incrementar la versión correspondiente.

---

# 66. FORWARD COMPATIBILITY

Los lectores deberán tolerar campos adicionales cuando sea seguro.

Los writers no deberán producir campos incompatibles sin incrementar la versión correspondiente.

---

# 67. BACKWARD COMPATIBILITY

Las migraciones deberán ser explícitas.

Ejemplo:

```text
schema 1.0
    ↓
migration
    ↓
schema 1.1
```

No deberá modificarse silenciosamente la semántica de datos históricos.

---

# 68. IMMUTABILITY

Los siguientes objetos deberán considerarse inmutables una vez utilizados para un build:

```text
AssetSpecification
GenerationPlan
BuildManifest
Artifact provenance
```

Una modificación deberá generar una nueva revisión/versión.

---

# 69. EXECUTION CONTEXT

La ejecución deberá poseer contexto explícito.

```text
ExecutionContext
├── execution_id
├── project
├── environment
├── target
├── seed
├── configuration
├── storage
└── capabilities
```

---

# 70. CAPABILITIES

El contexto deberá declarar capacidades disponibles.

Ejemplo:

```text
BLENDER_AVAILABLE
UNREAL_AVAILABLE
GPU_AVAILABLE
CUDA_AVAILABLE
TEXTURE_BAKER_AVAILABLE
DCC_VERSION
```

Un plan deberá poder bloquearse si una capacidad requerida no está disponible.

---

# 71. CAPABILITY REQUIREMENT

Los generadores deberán declarar requisitos.

Ejemplo:

```text
CharacterGenerator
requires:
    BLENDER
    SKELETON_SUPPORT
```

El planner verificará las capacidades antes de ejecutar.

---

# 72. RESOURCE BUDGET

Una specification podrá declarar presupuestos.

```text
ResourceBudget
├── max_memory
├── max_time
├── max_disk
├── max_triangles
├── max_texture_memory
└── max_artifact_size
```

---

# 73. COST ESTIMATION

El planner podrá producir una estimación:

```text
EstimatedCost
├── cpu_time
├── gpu_time
├── memory
├── disk
└── output_size
```

Esta información podrá utilizarse posteriormente para selección de estrategia.

---

# 74. QUALITY/COST TRADEOFF

El sistema deberá poder representar:

```text
quality target
+
resource budget
=
generation strategy
```

Esto será fundamental para decidir cuándo utilizar:

```text
high-detail geometry
normal maps
nanite
procedural detail
texture detail
LOD simplification
```

---

# 75. ASSET GRAPH RELATIONSHIP

UAF deberá integrarse con el grafo semántico existente.

Las relaciones deberán representar:

```text
DEPENDS_ON
GENERATED_FROM
PRODUCES
VALIDATED_BY
PACKAGED_IN
VARIANT_OF
INSTANCE_OF
USES
REFERENCES
```

---

# 76. GRAPH SOURCE OF TRUTH

El grafo no sustituirá al objeto de dominio.

El modelo será:

```text
Domain Objects
      ↓
Graph Representation
```

y no:

```text
Graph
  ↓
arbitrary domain state
```

salvo que una decisión arquitectónica futura lo establezca explícitamente.

---

# 77. PROVENANCE GRAPH

Deberá ser posible reconstruir:

```text
Specification
      ↓
Plan
      ↓
Operations
      ↓
Generators
      ↓
Artifacts
      ↓
Validation
      ↓
Package
```

---

# 78. SECURITY

Los datos de dominio no deberán permitir ejecución arbitraria.

Una specification deberá describir intención.

No deberá contener directamente:

```text
arbitrary Python code
shell commands
untrusted executable paths
```

Las capacidades de ejecución deberán estar controladas por backend y permisos.

---

# 79. EXTENSION MODEL

Las categorías deberán poder extenderse sin modificar el core.

Ejemplo:

```text
AssetCategory = CUSTOM
type_id = "vehicle"
```

siempre que el nuevo tipo respete los contratos base.

---

# 80. DOMAIN INVARIANTS

Como mínimo:

```text
asset_id must be unique

revision must be positive

artifact must reference an asset

dependency target must exist or be explicitly unresolved

build must reference a specification

validation must reference a build or asset

package must reference artifacts

deterministic build must contain a seed

hashable objects must have canonical serialization
```

---

# 81. INVALID STATES

El sistema deberá impedir o rechazar estados como:

```text
Artifact without asset
Build without specification
Dependency without target
Package without target profile
Deterministic generator without seed
Revision zero
Negative resource budgets
Circular mandatory dependency
```

---

# 82. CONTRACT PRIORITY

Cuando exista conflicto:

```text
Domain Invariants
      >
Schema
      >
Implementation Convenience
```

La implementación nunca deberá invalidar una invariante para simplificar código.

---

# 83. DOMAIN INDEPENDENCE

Los objetos de `core` no deberán importar:

```text
bpy
unreal
maya
houdini
filesystem-specific APIs
```

Los adapters deberán realizar la traducción.

---

# 84. IMPLEMENTATION MAPPING

La primera implementación deberá materializar como mínimo:

```text
core/identity.py
    AssetIdentity

core/specification.py
    AssetSpecification
    Constraint
    Parameter

core/dependencies.py
    AssetDependency

core/context.py
    ExecutionContext

core/results.py
    GenerationResult
    ValidationResult
    ArtifactReference

core/lifecycle.py
    AssetLifecycle

core/versioning.py
    Version information
```

Los nombres podrán ajustarse durante implementación siempre que las responsabilidades permanezcan.

---

# 85. CONTRACT TESTING

Cada contrato público deberá tener tests que verifiquen:

```text
construction
validation
serialization
deserialization
equality
hashing where applicable
immutability where required
invalid-state rejection
schema compatibility
```

---

# 86. GOLDEN DATA

Deberán crearse fixtures canónicos.

Ejemplos:

```text
minimal_character.json
minimal_texture.json
minimal_material.json
minimal_modular_asset.json
minimal_world.json
minimal_package.json
```

Estos fixtures servirán para detectar cambios accidentales en schemas.

---

# 87. MIGRATION TESTS

Cada migración de schema deberá poseer al menos:

```text
old fixture
    ↓
migration
    ↓
new object
    ↓
validation
```

---

# 88. NO PREMATURE IMPLEMENTATION

No deberán implementarse todavía:

```text
CharacterGenerator
TextureGenerator
WorldGenerator
BlenderBackend
UnrealBackend
```

hasta que los contratos base estén implementados y probados.

---

# 89. DATA MODEL ACCEPTANCE TEST

La fase será considerada completa cuando sea posible:

```text
create AssetSpecification
        ↓
create AssetIdentity
        ↓
add constraints
        ↓
add dependencies
        ↓
create GenerationPlan
        ↓
serialize
        ↓
deserialize
        ↓
produce deterministic hash
        ↓
create BuildManifest
        ↓
attach Artifact
        ↓
attach ValidationResult
        ↓
serialize complete production record
```

sin utilizar Blender ni Unreal.

---

# 90. FINAL CANONICAL MODEL

El modelo conceptual final será:

```text
                         ASSET
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         IDENTITY     SPECIFICATION   DEPENDENCIES
                           │
                           ▼
                    GENERATION PLAN
                           │
                           ▼
                       EXECUTION
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          GENERATOR     BACKEND      RESOURCES
              │
              ▼
           ARTIFACTS
              │
              ▼
          VALIDATION
              │
              ▼
           PACKAGE
              │
              ▼
            TARGET
```

---

# 91. ARCHITECTURAL DECISION

El modelo de datos de UAF-81 deberá diseñarse primero alrededor de **assets y producción**, y posteriormente especializarse para cada categoría.

La arquitectura no deberá comenzar con:

```text
Character = special case
```

sino con:

```text
Asset = universal production entity
```

y posteriormente:

```text
Character
Texture
Material
World
...
```

serán especializaciones.

---

# 92. FINAL PRINCIPLE

UAF-81 deberá ser capaz de describir una producción completa sin conocer todavía cómo se genera físicamente.

Por ejemplo:

```text
"Crear un personaje humanoide sci-fi,
2 metros de altura,
calidad HERO,
materiales metálicos,
4 variantes,
rig compatible con UE5,
presupuesto de 150k triángulos,
texturas 4K,
colisiones,
LOD,
y paquete final para Unreal"
```

deberá poder representarse como datos estructurados antes de ejecutar Blender.

La generación será una consecuencia de esa especificación, no la especificación misma.

---

# 93. NEXT PHASE

Después de este modelo deberá implementarse:

**UAF-81.0 — FOUNDATION**

La fase deberá crear exclusivamente:

1. Domain models.
2. Contracts.
3. Serialization.
4. Canonical hashing.
5. Validation of invariants.
6. Basic lifecycle.
7. Test fixtures.
8. Integration boundary con AOE.

No deberá comenzar todavía la generación avanzada de personajes.

La primera demostración de UAF-81 deberá ser un **Mock Asset Production Pipeline**, completamente determinista y ejecutable sin Blender ni Unreal.

Ese mock será el contrato contra el cual se construirán posteriormente los generadores reales.
