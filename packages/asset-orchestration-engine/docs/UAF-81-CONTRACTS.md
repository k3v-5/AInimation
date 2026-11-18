# UAF-81 — UNIVERSAL ASSET FACTORY

## UAF-81-CONTRACTS

### CORE ARCHITECTURAL CONTRACTS

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Document:** Core Architectural Contracts  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

Este documento define los contratos arquitectónicos obligatorios de UAF-81.

Estos contratos establecen cómo se comunican entre sí:

* specifications;
* planners;
* generators;
* backends;
* assemblers;
* validators;
* optimizers;
* artifact stores;
* package targets;
* checkpoints;
* recovery systems.

Ningún módulo de producción podrá definir su propio protocolo incompatible con estos contratos.

---

# 2. CORE PRINCIPLE

UAF-81 deberá separar estrictamente:

```text
WHAT
```

de:

```text
HOW
```

La specification describe **qué se quiere producir**.

El generator determina **cómo producirlo**.

El validator determina **si cumple**.

El optimizer determina **cómo hacerlo más eficiente**.

El packager determina **cómo entregarlo al target**.

---

# 3. MASTER PIPELINE CONTRACT

Toda producción deberá poder representarse mediante:

```text
Intent
  ↓
Specification
  ↓
Plan
  ↓
Execution
  ↓
Artifacts
  ↓
Validation
  ↓
Optimization
  ↓
Packaging
```

No deberá existir un generator que salte directamente desde intención hasta filesystem sin pasar por los contratos correspondientes.

---

# 4. ASSET SPECIFICATION CONTRACT

## 4.1 Required fields

Toda specification deberá contener como mínimo:

```text
asset_id
asset_type
version
target
quality_profile
generation_profile
parameters
constraints
dependencies
seed
```

---

# 5. ASSET IDENTITY

`asset_id` deberá ser estable.

No deberá depender de:

```text
filesystem location
timestamp
machine name
process ID
temporary UUID
```

La identidad lógica deberá permanecer estable mientras el asset represente el mismo objeto lógico.

---

# 6. VERSION

La specification deberá tener una versión explícita.

Ejemplo:

```text
spec_version = 1.0
```

Los cambios incompatibles deberán incrementar la versión mayor.

---

# 7. TARGET CONTRACT

El target deberá describir el entorno de destino.

Ejemplo:

```text
engine = unreal
engine_version = 5.5
platform = windows
renderer = nanite_lumen
```

El generator no deberá asumir un target implícito.

---

# 8. QUALITY PROFILE

La calidad deberá ser explícita.

Valores mínimos:

```text
PROTOTYPE
STANDARD
PRODUCTION
HERO
CINEMATIC
```

Los generadores podrán definir restricciones específicas por nivel.

---

# 9. GENERATION PROFILE

La generation profile deberá controlar las características de generación.

Ejemplo:

```text
detail_level
geometry_strategy
surface_strategy
material_strategy
texture_strategy
variation_level
```

---

# 10. DETERMINISM CONTRACT

Toda operación procedural deberá aceptar un seed cuando la operación sea estocástica.

Para una misma:

```text
Specification
+
Seed
+
Generator Version
+
Dependency Versions
+
Configuration
```

el resultado deberá ser equivalente.

---

# 11. DETERMINISTIC EQUIVALENCE

Equivalencia no significa necesariamente igualdad binaria.

Se deberá distinguir:

```text
Binary Determinism
Structural Determinism
Visual Determinism
Semantic Determinism
```

Cada generator deberá declarar cuál garantiza.

---

# 12. GENERATOR CONTRACT

Un generator deberá implementar conceptualmente:

```text
identify_capabilities()
validate_input()
estimate_cost()
plan()
generate()
validate_output()
publish()
```

---

# 13. GENERATOR INPUT

El generator no deberá recibir parámetros arbitrarios sin schema.

La entrada deberá ser:

```text
GenerationRequest
```

conteniendo:

```text
Specification
ExecutionContext
GenerationPlan
```

---

# 14. GENERATOR OUTPUT

El generator no deberá devolver simplemente:

```text
path
```

Deberá producir:

```text
GenerationResult
```

que incluya:

```text
status
artifacts
metrics
warnings
diagnostics
provenance
```

---

# 15. GENERATOR STATUS

Los estados mínimos serán:

```text
PENDING
PLANNED
RUNNING
SUCCEEDED
FAILED
CANCELLED
PARTIAL
RECOVERABLE
```

---

# 16. FAILURE CONTRACT

Los errores deberán clasificarse.

Categorías mínimas:

```text
INPUT_ERROR
CONFIGURATION_ERROR
CAPABILITY_ERROR
DEPENDENCY_ERROR
GENERATION_ERROR
VALIDATION_ERROR
RESOURCE_ERROR
IO_ERROR
PACKAGING_ERROR
INTEGRATION_ERROR
INTERNAL_ERROR
```

---

# 17. ERROR INFORMATION

Cada error deberá proporcionar:

```text
error_code
message
phase
operation
asset_id
recoverable
retryable
details
```

---

# 18. RETRY CONTRACT

Un error podrá declarar:

```text
retryable = true
```

pero deberá existir una razón operacional.

Ejemplos:

```text
temporary IO failure
external process timeout
temporary Blender failure
resource contention
```

No se deberá reintentar indefinidamente un error determinista.

---

# 19. RETRY POLICY

Deberá existir:

```text
max_attempts
backoff
retry_scope
```

El retry podrá ser:

```text
operation
component
stage
asset
batch
```

---

# 20. CANCELLATION CONTRACT

Toda operación larga deberá soportar cancelación cooperativa cuando sea técnicamente posible.

La cancelación deberá producir:

```text
CANCELLED
```

y preservar información suficiente para diagnóstico.

---

# 21. CHECKPOINT CONTRACT

Las operaciones largas deberán poder crear checkpoints.

Un checkpoint deberá contener:

```text
checkpoint_id
asset_id
operation_id
generator_version
input_hash
state
artifacts
timestamp
```

---

# 22. RESUME CONTRACT

Un proceso reanudado deberá verificar:

```text
input compatibility
generator compatibility
dependency compatibility
artifact integrity
checkpoint integrity
```

antes de continuar.

---

# 23. ARTIFACT CONTRACT

Un artifact es cualquier resultado material producido por el pipeline.

Ejemplos:

```text
mesh
texture
material
skeleton
animation
collision
level
world
blueprint
metadata
manifest
```

---

# 24. ARTIFACT IDENTITY

Cada artifact deberá tener:

```text
artifact_id
artifact_type
content_hash
producer
producer_version
source_operation
```

---

# 25. CONTENT HASH

El hash deberá utilizarse para:

```text
deduplication
cache
change detection
integrity
provenance
incremental builds
```

---

# 26. ARTIFACT PROVENANCE

Todo artifact deberá poder responder:

```text
Who produced me?
From which specification?
With which generator?
With which version?
Using which dependencies?
Using which seed?
```

---

# 27. ARTIFACT LIFECYCLE

Estados mínimos:

```text
CREATED
VALIDATING
VALID
INVALID
OPTIMIZING
PACKAGING
PUBLISHED
SUPERSEDED
DELETED
```

---

# 28. VALIDATOR CONTRACT

Todo validator deberá implementar conceptualmente:

```text
supports()
validate()
report()
```

---

# 29. VALIDATION SCOPE

Un validator deberá declarar qué valida.

Ejemplos:

```text
GeometryValidator
TopologyValidator
UVValidator
MaterialValidator
TextureValidator
RigValidator
CollisionValidator
PerformanceValidator
UnrealValidator
VisualValidator
```

---

# 30. VALIDATION RESULT

Toda validación deberá producir:

```text
ValidationResult
```

con:

```text
status
checks
errors
warnings
metrics
recommendations
```

---

# 31. VALIDATION STATUS

Valores:

```text
PASS
PASS_WITH_WARNINGS
FAIL
NOT_APPLICABLE
BLOCKED
```

---

# 32. HARD FAILURE VS WARNING

Los checks deberán clasificarse:

```text
BLOCKING
NON_BLOCKING
INFORMATIONAL
```

Un warning nunca deberá convertirse silenciosamente en error.

---

# 33. VALIDATION PROFILE

La validación deberá depender del target y quality profile.

Ejemplo:

```text
PROTOTYPE
```

podrá permitir:

```text
higher triangle count
temporary materials
missing final textures
```

mientras:

```text
PRODUCTION
```

no.

---

# 34. OPTIMIZER CONTRACT

El optimizer deberá implementar conceptualmente:

```text
analyze()
estimate()
optimize()
validate()
report()
```

---

# 35. OPTIMIZER RULE

La optimización no podrá cambiar silenciosamente la intención artística.

Deberá declarar:

```text
what changed
why
expected benefit
quality impact
```

---

# 36. OPTIMIZATION EXAMPLES

```text
LOD generation
texture resizing
material consolidation
mesh simplification
instance conversion
collision simplification
Nanite preparation
```

---

# 37. ASSEMBLER CONTRACT

El assembler combina artifacts.

Ejemplo:

```text
Body
+
Armor
+
Weapon
+
Materials
+
Skeleton
```

→

```text
Character
```

---

# 38. ASSEMBLY RULE

El assembler deberá validar compatibilidad antes de ensamblar.

Ejemplos:

```text
skeleton compatibility
scale compatibility
coordinate convention
material compatibility
socket compatibility
LOD compatibility
```

---

# 39. MODULAR CONNECTION CONTRACT

Todo módulo conectable deberá declarar:

```text
connection_type
position
orientation
scale
compatibility_tags
```

Ejemplo:

```text
DoorFrame
socket = WALL_A
orientation = FRONT
```

---

# 40. BACKEND CONTRACT

Los backends encapsularán herramientas externas.

Ejemplos:

```text
BlenderBackend
UnrealBackend
TextureBackend
ImageBackend
AudioBackend
```

---

# 41. BACKEND RESPONSIBILITY

Un backend deberá encargarse de:

```text
tool invocation
environment setup
input translation
execution
output collection
tool errors
cleanup
```

No deberá contener reglas de negocio de alto nivel.

---

# 42. BACKEND CAPABILITIES

Cada backend deberá registrar:

```text
capability_id
version
supported_assets
supported_operations
supported_targets
limitations
```

---

# 43. EXTERNAL PROCESS CONTRACT

Los procesos externos deberán ejecutarse mediante un wrapper controlado.

El wrapper deberá registrar:

```text
command
version
environment
start_time
end_time
exit_code
stdout
stderr
artifacts
```

---

# 44. RESOURCE CONTRACT

Una operación podrá declarar:

```text
cpu
memory
gpu
disk
time
external_processes
```

---

# 45. RESOURCE ESTIMATION

Antes de ejecutar operaciones costosas, el planner deberá poder estimar recursos.

Ejemplo:

```text
estimated_memory
estimated_disk
estimated_duration
estimated_gpu
```

La estimación podrá ser aproximada pero deberá existir cuando la operación sea potencialmente costosa.

---

# 46. CACHE CONTRACT

El cache deberá identificarse mediante una clave derivada de:

```text
operation
input_hash
configuration_hash
generator_version
dependency_versions
```

---

# 47. CACHE INVALIDATION

Un cache deberá invalidarse cuando cambie cualquier dependencia relevante.

Nunca deberá reutilizarse un resultado incompatible únicamente porque coincida el `asset_id`.

---

# 48. PACKAGE TARGET CONTRACT

Todo target deberá definir cómo convertir artifacts internos en outputs de producción.

Ejemplo:

```text
UnrealTarget
```

podrá producir:

```text
.uasset
.fbx
.png
.exr
.json
manifest
```

según corresponda.

---

# 49. TARGET VALIDATION

Antes de publicar un package deberán ejecutarse validaciones específicas del target.

Para Unreal:

```text
naming
folder
dependencies
materials
textures
collision
LODs
metadata
import compatibility
```

---

# 50. MANIFEST CONTRACT

Toda producción deberá terminar con un manifest.

El manifest deberá contener:

```text
production_id
asset_id
specification_hash
generator_versions
artifacts
artifact_hashes
validation
optimization
package
dependencies
```

---

# 51. PRODUCTION ID

Cada ejecución deberá tener un identificador de producción.

El `production_id` deberá distinguir ejecuciones aunque produzcan el mismo asset lógico.

---

# 52. LOGGING CONTRACT

Todos los componentes deberán producir logs estructurados.

Cada evento deberá poder asociarse a:

```text
production_id
asset_id
operation_id
phase
component
timestamp
severity
```

---

# 53. OBSERVABILITY

El sistema deberá registrar como mínimo:

```text
duration
success/failure
artifact count
artifact size
validation status
retry count
cache hits
cache misses
```

---

# 54. SECURITY / PERMISSION CONTRACT

Los backends y generators deberán declarar los recursos que requieren.

Ejemplo:

```text
filesystem_read
filesystem_write
blender_execution
unreal_execution
network
process_execution
```

La ejecución deberá pasar por el sistema de permisos correspondiente.

---

# 55. FILESYSTEM CONTRACT

Los componentes no deberán asumir rutas absolutas específicas de una máquina.

Quedan prohibidos como defaults arquitectónicos:

```text
E:\
D:\
C:\Users\<user>\
```

Las rutas deberán resolverse mediante:

```text
ProjectRoot
Workspace
ArtifactRoot
CacheRoot
OutputRoot
```

---

# 56. CONFIGURATION CONTRACT

La configuración deberá tener precedencia explícita:

```text
defaults
    ↓
project config
    ↓
environment config
    ↓
runtime config
    ↓
operation override
```

---

# 57. SCHEMA CONTRACT

Los schemas deberán:

```text
validate input
provide defaults where safe
reject unknown critical fields
support versioning
```

Los cambios incompatibles deberán ser explícitos.

---

# 58. COMPATIBILITY CONTRACT

Cada componente deberá declarar:

```text
schema version
API version
generator version
backend version
```

---

# 59. PLANNER CONTRACT

El planner deberá producir un DAG de operaciones.

Ejemplo:

```text
CreateBody
   │
   ├── CreateHead
   │
   ├── CreateArmor
   │
   └── CreateMaterials
          │
          ▼
      CreateTextures
          │
          ▼
       Assemble
          │
          ▼
       Validate
```

---

# 60. DAG RULE

Una operación no deberá ejecutarse hasta que sus dependencias hayan producido outputs válidos.

---

# 61. PARTIAL BUILD CONTRACT

Si solamente cambia:

```text
texture configuration
```

el sistema deberá evitar regenerar:

```text
anatomy
skeleton
armor
```

si continúan siendo válidos.

---

# 62. INVALIDATION GRAPH

Cada artifact deberá registrar sus consumidores.

Ejemplo:

```text
BodyMesh
 ├── Skeleton
 ├── Collision
 ├── UV
 └── TextureBake
```

Un cambio en `BodyMesh` deberá invalidar únicamente los descendientes afectados.

---

# 63. TRANSACTION CONTRACT

Las operaciones mutables deberán poder ejecutarse de forma transaccional cuando afecten outputs compartidos.

Estados:

```text
BEGIN
PREPARE
COMMIT
ROLLBACK
```

---

# 64. ATOMIC PUBLISH

Un artifact no deberá considerarse publicado hasta que:

```text
generation
validation
integrity
```

hayan sido completadas según el profile correspondiente.

---

# 65. IDEMPOTENCY CONTRACT

Ejecutar dos veces una operación con exactamente los mismos inputs deberá producir:

```text
equivalent result
```

y no generar duplicación lógica accidental.

---

# 66. MULTI-ASSET CONTRACT

Una producción podrá contener múltiples assets.

Ejemplo:

```text
EnemyPack
 ├── Enemy01
 ├── Enemy02
 ├── Enemy03
 ├── Weapon01
 └── MaterialSet01
```

Los artifacts compartidos deberán poder reutilizarse.

---

# 67. BATCH CONTRACT

Los batch jobs deberán permitir:

```text
continue_on_error
stop_on_error
retry_failed
resume
partial_publish
```

según configuración.

---

# 68. QUALITY GATE CONTRACT

Antes de pasar a la siguiente etapa:

```text
ValidationResult
```

deberá satisfacer el quality gate correspondiente.

---

# 69. QUALITY GATE EXAMPLE

```text
Geometry
PASS

Textures
PASS_WITH_WARNINGS

Rig
PASS

Unreal
PASS
```

→ Production puede continuar.

Pero:

```text
Geometry
FAIL BLOCKING
```

→ Production deberá detenerse.

---

# 70. HUMAN OVERRIDE

El sistema podrá permitir override explícito de determinados warnings.

Nunca deberá permitir silenciosamente un blocking failure.

Toda excepción deberá registrar:

```text
override_reason
operator
timestamp
affected_check
```

---

# 71. VISUAL VALIDATION CONTRACT

La validación visual deberá producir métricas y evidencia.

No deberá reducirse a:

```text
looks_good = true
```

Deberá poder almacenar:

```text
camera
view
reference
metric
threshold
result
evidence
```

---

# 72. REFERENCE CONTRACT

Los assets podrán tener referencias visuales o técnicas.

La referencia deberá poder identificarse mediante:

```text
reference_id
reference_type
source
hash
```

---

# 73. STYLE CONTRACT

El estilo visual deberá ser un input explícito.

Ejemplo:

```text
SCI_FI
REALISTIC
STYLIZED
FANTASY
HORROR
MILITARY
```

Los generators no deberán codificar permanentemente un único estilo.

---

# 74. CHARACTER CONTRACT

Un CharacterSpecification podrá declarar:

```text
species
body_type
height
proportions
anatomy
clothing
armor
equipment
materials
rig
animation_profile
```

---

# 75. MATERIAL CONTRACT

Un MaterialSpecification podrá declarar:

```text
surface_type
physical_properties
layers
wear
damage
color
roughness
metallic
emission
```

---

# 76. TEXTURE CONTRACT

Una TextureSpecification podrá declarar:

```text
resolution
channels
format
color_space
compression
mip_policy
tiling
projection
baking_source
```

---

# 77. MODULAR ASSET CONTRACT

Un ModularAssetSpecification podrá declarar:

```text
module_type
dimensions
grid
connections
compatibility
orientation
material_slots
```

---

# 78. WORLD CONTRACT

Un WorldSpecification podrá declarar:

```text
world_size
regions
biomes
terrain
landmarks
population_rules
navigation
streaming
performance_budget
```

---

# 79. UNREAL CONTRACT

El Unreal target deberá declarar:

```text
engine_version
project_id
content_root
platform
rendering_features
nanite_policy
virtual_texture_policy
```

---

# 80. CONTRACT ENFORCEMENT

Los contratos no deberán depender exclusivamente de documentación.

Cuando sea posible deberán existir:

```text
Python protocols
dataclasses
schemas
runtime validators
contract tests
```

---

# 81. CONTRACT TESTING

Cada implementación deberá superar:

```text
interface tests
schema tests
failure tests
determinism tests
serialization tests
compatibility tests
```

---

# 82. FORBIDDEN PATTERNS

Quedan prohibidos:

```text
global mutable production state
hard-coded machine paths
implicit generators
silent fallback
silent validation bypass
untracked external processes
untracked filesystem writes
unversioned schemas
unbounded retries
non-deterministic default seeds
```

---

# 83. CONTRACT PRIORITY

Cuando exista conflicto entre componentes:

```text
Safety / Integrity
      >
Specification
      >
Target requirements
      >
Quality profile
      >
Optimization
      >
Convenience
```

---

# 84. ARCHITECTURAL RULE

Los generadores deberán poder cambiarse sin modificar:

```text
Specification
Artifact system
Validation framework
Packaging contracts
```

siempre que continúen cumpliendo los mismos contratos.

---

# 85. FINAL CONTRACT GRAPH

```text
                  SPECIFICATION
                        │
                        ▼
                     PLANNER
                        │
                        ▼
                   GENERATION PLAN
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       GENERATOR     BACKEND       CACHE
          │             │
          └──────┬──────┘
                 ▼
              ARTIFACTS
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    VALIDATOR OPTIMIZER ASSEMBLER
        │        │        │
        └────────┼────────┘
                 ▼
             QUALITY GATE
                 │
                 ▼
             PACKAGE TARGET
                 │
                 ▼
              MANIFEST
                 │
                 ▼
               UNREAL
```

---

# 86. FINAL ACCEPTANCE CRITERIA

UAF-81-CONTRACTS será considerado implementable cuando:

1. todos los contratos anteriores tengan representación formal;
2. exista validación automática de schemas;
3. existan contract tests;
4. exista un ExecutionContext común;
5. exista un Artifact model común;
6. exista un ValidationResult común;
7. exista un GenerationResult común;
8. exista un error model común;
9. exista un checkpoint model común;
10. exista un manifest común;
11. exista versionado de contratos;
12. ningún generator dependa de APIs privadas de otro generator.

---

# 87. FINAL PRINCIPLE

La Universal Asset Factory no deberá construirse alrededor de:

```text
Blender
```

ni alrededor de:

```text
Unreal
```

ni alrededor de:

```text
Characters
```

La arquitectura deberá construirse alrededor de:

```text
SPECIFICATION
        ↓
CAPABILITY
        ↓
GENERATION
        ↓
ARTIFACT
        ↓
VALIDATION
        ↓
OPTIMIZATION
        ↓
TARGET
```

Blender, Unreal y cualquier otra herramienta serán implementaciones de capabilities dentro de este modelo.

Ese principio deberá mantenerse durante todo el desarrollo de UAF-81.
