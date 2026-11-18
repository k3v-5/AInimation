# UAF-81.0 — FOUNDATION

## UAF-81.0-ARCH

### ARQUITECTURA DEL NÚCLEO FUNDACIONAL

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.0 — Foundation  
**Document:** Architecture Specification  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.0 establece el núcleo común sobre el cual deberán construirse todas las capacidades futuras de Universal Asset Factory.

Esta fase no genera assets finales.

Su objetivo es construir la infraestructura que permita generar, validar, transformar, almacenar, recuperar y publicar cualquier tipo de asset mediante contratos comunes.

---

# 2. SCOPE

UAF-81.0 deberá implementar:

```text
ProjectContext
ExecutionContext
AssetIdentity
AssetSpecification
GenerationRequest
GenerationResult
Artifact
ArtifactManifest
Operation
OperationResult
ValidationResult
Diagnostic
ErrorModel
Hashing
Configuration
PathResolution
StateManagement
CheckpointBase
EventModel
ContractValidation
```

---

# 3. NON-GOALS

Esta fase NO deberá implementar todavía:

```text
character generation
texture generation
material generation
terrain generation
world generation
Unreal import automation
Blender procedural generation
AI image generation
AI mesh generation
automatic rigging
LOD generation
```

Estas capacidades serán implementadas en fases posteriores sobre Foundation.

---

# 4. DESIGN PRINCIPLE

Foundation deberá ser:

```text
engine-agnostic
generator-agnostic
backend-agnostic
asset-type-agnostic
deterministic
testable
serializable
recoverable
extensible
```

---

# 5. PROPOSED PACKAGE STRUCTURE

La nueva arquitectura deberá introducir una raíz conceptual:

```text
src/
└── uaf/
    ├── core/
    │   ├── identity/
    │   ├── context/
    │   ├── specification/
    │   ├── operations/
    │   ├── artifacts/
    │   ├── validation/
    │   ├── diagnostics/
    │   ├── hashing/
    │   ├── configuration/
    │   ├── paths/
    │   ├── events/
    │   └── state/
    │
    ├── contracts/
    ├── schemas/
    ├── serialization/
    └── testing/
```

La implementación deberá integrarse progresivamente con la arquitectura existente de AOE sin duplicar innecesariamente modelos que ya sean compatibles.

---

# 6. PROJECT CONTEXT

Se deberá crear:

```text
ProjectContext
```

Responsabilidad:

```text
project identity
project root
workspace root
artifact root
cache root
output root
configuration
target information
environment information
```

Ejemplo conceptual:

```python
ProjectContext(
    project_id="darx",
    project_root=...,
    workspace_root=...,
    artifact_root=...,
    cache_root=...,
    output_root=...,
)
```

---

# 7. PATH RESOLUTION

Toda ruta deberá resolverse mediante `ProjectContext`.

Se deberá eliminar progresivamente cualquier dependencia de rutas absolutas específicas de una máquina.

Las siguientes rutas deberán ser conceptualmente independientes:

```text
project_root
workspace_root
artifact_root
cache_root
output_root
logs_root
checkpoints_root
temp_root
```

---

# 8. PATH SECURITY

Un resolver deberá impedir que una operación destinada a un root escriba fuera de él cuando el contrato no lo permita.

Deberán detectarse:

```text
path traversal
invalid absolute paths
unauthorized roots
symbolic link escapes
```

cuando aplique al entorno.

---

# 9. EXECUTION CONTEXT

Se deberá crear:

```text
ExecutionContext
```

Contendrá:

```text
production_id
operation_id
asset_id
project_context
configuration
seed
target
quality_profile
permissions
resource_budget
logger
```

---

# 10. EXECUTION CONTEXT RULE

El `ExecutionContext` deberá ser inmutable durante una operación salvo por mecanismos explícitos de estado.

No deberá utilizarse como contenedor global mutable.

---

# 11. ASSET IDENTITY

Se deberá crear:

```text
AssetIdentity
```

Campos mínimos:

```text
asset_id
asset_type
namespace
version
```

La identidad deberá ser serializable.

---

# 12. ASSET TYPES

Foundation deberá soportar tipos extensibles.

Tipos iniciales:

```text
CHARACTER
CREATURE
WEAPON
PROP
MODULAR_KIT
ARCHITECTURE
ENVIRONMENT
MATERIAL
TEXTURE
VFX
AUDIO
ANIMATION
RIG
LEVEL
WORLD
BLUEPRINT
OTHER
```

La lista deberá poder ampliarse sin modificar el core de ejecución.

---

# 13. SPECIFICATION BASE

Se deberá crear una specification base:

```text
AssetSpecification
```

Campos:

```text
identity
schema_version
target
quality_profile
generation_profile
parameters
constraints
dependencies
seed
metadata
```

---

# 14. SPECIFICATION IMMUTABILITY

Una specification validada deberá tratarse como inmutable.

Si se modifica cualquier campo relevante deberá producirse una nueva versión o nueva instancia de specification.

---

# 15. SPECIFICATION HASH

Deberá calcularse:

```text
specification_hash
```

utilizando una representación canónica.

El hash deberá ser estable ante diferencias irrelevantes de:

```text
dictionary ordering
serialization formatting
whitespace
```

---

# 16. CANONICAL SERIALIZATION

Las estructuras utilizadas para hashing deberán serializarse de forma canónica.

La serialización deberá definir explícitamente:

```text
ordering
encoding
null handling
number representation
string encoding
version metadata
```

---

# 17. OPERATION MODEL

Se deberá crear:

```text
Operation
```

Campos mínimos:

```text
operation_id
operation_type
asset_id
inputs
configuration
dependencies
status
created_at
```

---

# 18. OPERATION TYPES

Foundation no deberá limitar artificialmente las operaciones.

Deberán existir al menos categorías conceptuales:

```text
GENERATE
TRANSFORM
ASSEMBLE
VALIDATE
OPTIMIZE
PACKAGE
EXPORT
IMPORT
PUBLISH
```

---

# 19. OPERATION STATUS

Estados:

```text
PENDING
READY
RUNNING
SUCCEEDED
FAILED
CANCELLED
PARTIAL
RECOVERABLE
```

Las transiciones deberán validarse.

---

# 20. STATE MACHINE

No se deberá permitir:

```text
SUCCEEDED → RUNNING
CANCELLED → RUNNING
FAILED → SUCCEEDED
```

sin una operación explícita de retry/recovery que cree el contexto correspondiente.

---

# 21. OPERATION RESULT

Se deberá crear:

```text
OperationResult
```

Campos:

```text
operation_id
status
artifacts
diagnostics
metrics
duration
error
```

---

# 22. ARTIFACT MODEL

Se deberá crear:

```text
Artifact
```

Campos mínimos:

```text
artifact_id
artifact_type
asset_id
content_hash
size
location
producer
producer_version
created_at
metadata
```

---

# 23. ARTIFACT LOCATION

`Artifact.location` no deberá depender exclusivamente de una ruta física.

Deberá permitir representar:

```text
filesystem
object storage
database
temporary workspace
external target
```

---

# 24. ARTIFACT INTEGRITY

Todo artifact publicado deberá poder verificarse mediante:

```text
content_hash
size
existence
readability
```

según su backend.

---

# 25. ARTIFACT MANIFEST

Se deberá crear:

```text
ArtifactManifest
```

El manifest deberá permitir reconstruir la relación:

```text
Asset
 ↓
Operations
 ↓
Artifacts
 ↓
Dependencies
```

---

# 26. ARTIFACT DEPENDENCIES

Cada artifact podrá declarar:

```text
depends_on
consumed_by
derived_from
```

Esto permitirá implementar invalidación incremental posteriormente.

---

# 27. DIAGNOSTIC MODEL

Se deberá crear:

```text
Diagnostic
```

Campos:

```text
severity
code
message
component
operation_id
asset_id
details
location
```

---

# 28. DIAGNOSTIC SEVERITY

Valores:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 29. ERROR MODEL

Los errores de dominio deberán ser estructurados.

Base:

```text
UAFError
```

Categorías:

```text
SpecificationError
ConfigurationError
CapabilityError
GenerationError
ValidationError
ArtifactError
PersistenceError
PackagingError
PermissionError
ResourceError
ExternalProcessError
RecoveryError
```

---

# 30. ERROR SERIALIZATION

Todo error deberá poder convertirse en un objeto serializable sin perder:

```text
type
code
message
operation
asset
phase
recoverability
retryability
details
```

---

# 31. RECOVERABILITY

Cada error deberá indicar:

```text
recoverable
retryable
```

No deberán inferirse estas propiedades únicamente por el tipo de excepción.

---

# 32. METRICS MODEL

Toda operación deberá poder producir métricas:

```text
duration_ms
cpu_time_ms
memory_peak_mb
disk_read_bytes
disk_write_bytes
artifact_count
cache_hit
cache_miss
retry_count
```

Las métricas específicas podrán extenderse.

---

# 33. RESOURCE BUDGET

Se deberá crear:

```text
ResourceBudget
```

con:

```text
max_duration
max_memory
max_disk
max_cpu
max_gpu
max_processes
```

---

# 34. CONFIGURATION MODEL

Se deberá crear una configuración centralizada.

Conceptualmente:

```text
UAFConfig
├── project
├── execution
├── storage
├── cache
├── logging
├── validation
├── targets
└── security
```

---

# 35. CONFIGURATION PRECEDENCE

Se deberá implementar:

```text
DEFAULT
    ↓
PROJECT
    ↓
ENVIRONMENT
    ↓
RUNTIME
    ↓
OPERATION
```

La precedencia deberá estar documentada y testeada.

---

# 36. EVENT MODEL

Se deberá crear un sistema de eventos estructurados.

Eventos iniciales:

```text
ProductionStarted
ProductionCompleted
OperationStarted
OperationCompleted
OperationFailed
ArtifactCreated
ArtifactValidated
ArtifactPublished
CheckpointCreated
CheckpointRestored
```

---

# 37. EVENT IMMUTABILITY

Los eventos publicados deberán ser inmutables.

---

# 38. EVENT CORRELATION

Todos los eventos deberán poder correlacionarse mediante:

```text
production_id
operation_id
asset_id
```

---

# 39. CHECKPOINT BASE

Foundation deberá definir:

```text
Checkpoint
```

con:

```text
checkpoint_id
production_id
operation_id
state
artifacts
input_hash
configuration_hash
generator_version
created_at
```

---

# 40. CHECKPOINT VALIDATION

Antes de restaurar un checkpoint se deberá comprobar:

```text
input_hash
configuration_hash
schema_version
dependency compatibility
artifact integrity
```

---

# 41. SERIALIZATION LAYER

Se deberá implementar una capa independiente de serialización.

Debe permitir al menos:

```text
JSON
```

y dejar preparada la arquitectura para:

```text
MessagePack
binary formats
database persistence
```

---

# 42. SCHEMA VERSIONING

Todo objeto persistible deberá incluir:

```text
schema_version
```

---

# 43. FORWARD COMPATIBILITY

Cuando sea posible, versiones futuras deberán poder leer objetos antiguos.

Las migraciones incompatibles deberán ser explícitas.

---

# 44. CONTRACT VALIDATOR

Deberá existir un mecanismo central:

```text
ContractValidator
```

capaz de validar:

```text
specifications
operations
artifacts
results
manifests
configuration
```

---

# 45. TESTING ARCHITECTURE

Foundation deberá incluir:

```text
unit tests
contract tests
serialization tests
hashing tests
state transition tests
path resolution tests
error model tests
determinism tests
```

---

# 46. DETERMINISM TEST

Deberá existir un test que ejecute la misma specification varias veces:

```text
run(spec, seed)
run(spec, seed)
run(spec, seed)
```

y verifique equivalencia según el nivel de determinismo declarado.

---

# 47. PATH PORTABILITY TEST

Deberá existir un test que garantice que el core funciona con diferentes project roots.

Ejemplo:

```text
D:\Project
C:\Project
/tmp/project
```

según plataforma.

No deberán existir dependencias ocultas de una unidad concreta.

---

# 48. NO GLOBAL STATE

Foundation no deberá depender de:

```text
global ProjectContext
global configuration
global production state
global mutable cache
```

---

# 49. DEPENDENCY INJECTION

Los componentes centrales deberán recibir sus dependencias explícitamente.

Ejemplo conceptual:

```python
OperationRunner(
    artifact_store=...,
    validator=...,
    logger=...,
    configuration=...,
)
```

---

# 50. EXTENSION POINTS

Foundation deberá permitir registrar:

```text
AssetTypes
Generators
Validators
Optimizers
Backends
Packagers
ArtifactStores
```

sin modificar el core.

---

# 51. REGISTRY CONTRACT

Los registries deberán soportar:

```text
register()
get()
find()
list()
supports()
```

y deberán rechazar registros incompatibles.

---

# 52. CAPABILITY REGISTRY

Deberá existir:

```text
CapabilityRegistry
```

que permita consultar:

```text
¿Qué puede producir este sistema?
¿Qué generator soporta este asset?
¿Qué backend puede ejecutar esta operación?
¿Qué target acepta este artifact?
```

---

# 53. CAPABILITY DESCRIPTION

Cada capability deberá declarar:

```text
capability_id
version
asset_types
operations
requirements
limitations
quality_profiles
targets
```

---

# 54. FOUNDATION ACCEPTANCE TEST

La fase será aceptada únicamente cuando sea posible ejecutar un flujo mínimo:

```text
Create Project
      ↓
Create Specification
      ↓
Create Operation
      ↓
Execute Mock Generator
      ↓
Create Artifact
      ↓
Validate Artifact
      ↓
Create Manifest
      ↓
Publish
```

sin utilizar Blender ni Unreal.

---

# 55. MOCK GENERATOR

Deberá existir un `MockGenerator` exclusivamente para pruebas.

Su función será demostrar que el core funciona sin depender de herramientas externas.

---

# 56. MINIMUM END-TO-END TEST

El test mínimo deberá demostrar:

```text
Specification
    ↓
ExecutionContext
    ↓
Operation
    ↓
Generator
    ↓
Artifact
    ↓
Validator
    ↓
Manifest
```

y deberá completar correctamente.

---

# 57. PERFORMANCE REQUIREMENT

Foundation deberá minimizar overhead.

El core no deberá convertirse en el cuello de botella de generación.

Las operaciones pesadas deberán ejecutarse fuera del core cuando correspondan.

---

# 58. THREAD / PROCESS SAFETY

Los componentes que puedan ejecutarse concurrentemente deberán declarar sus garantías.

Se deberá evitar estado mutable compartido no protegido.

---

# 59. LOGGING REQUIREMENT

No se permitirá que un componente crítico falle silenciosamente.

Como mínimo deberá producir:

```text
operation started
operation completed
operation failed
artifact created
validation result
```

---

# 60. FOUNDATION DELIVERABLES

UAF-81.0 deberá entregar:

```text
01 — Core models
02 — Contracts
03 — Schemas
04 — Serialization
05 — Hashing
06 — Configuration
07 — Path resolution
08 — Operation state machine
09 — Artifact model
10 — Diagnostics
11 — Checkpoints
12 — Registries
13 — Capability model
14 — Mock generator
15 — Contract tests
16 — End-to-end foundation test
17 — Migration documentation
```

---

# 61. MIGRATION REQUIREMENT

La implementación deberá coexistir inicialmente con el AOE existente.

No se deberá realizar una migración destructiva de todos los módulos actuales.

La migración deberá ser incremental:

```text
AOE existing
      │
      ├── legacy modules
      │
      └── UAF Foundation
              │
              ▼
        migrated modules
```

---

# 62. DEPRECATION POLICY

Un componente existente no deberá eliminarse simplemente porque exista una alternativa UAF.

Deberá pasar por:

```text
ACTIVE
↓
COMPATIBILITY
↓
DEPRECATED
↓
REMOVAL CANDIDATE
↓
REMOVED
```

---

# 63. FOUNDATION DEFINITION OF DONE

UAF-81.0 estará terminada cuando:

* el core pueda ejecutarse sin Blender;
* el core pueda ejecutarse sin Unreal;
* ningún path crítico dependa de una unidad fija;
* exista determinismo verificable;
* existan artifacts identificables;
* exista provenance;
* exista validation;
* exista recovery;
* exista serialization;
* exista capability discovery;
* exista contract testing;
* exista un flujo end-to-end completamente funcional.

---

# 64. ARCHITECTURAL OUTCOME

Al finalizar UAF-81.0, el sistema deberá poder expresar:

```text
"Necesito producir un asset"
```

sin saber todavía:

```text
cómo se modelará
cómo se texturizará
qué software lo generará
cómo se optimizará
cómo se exportará
```

Eso deberá resolverse posteriormente mediante capabilities.

---

# 65. NEXT PHASE

La siguiente fase será:

# UAF-81.1 — ASSET INTELLIGENCE & SPECIFICATION

Su objetivo será convertir una descripción de alto nivel como:

```text
"Soldado táctico sci-fi realista,
1.85 m, pesado, armadura modular,
arma principal, desgaste militar,
optimizado para Unreal Engine 5.5"
```

en una specification completa, validable y ejecutable.

Esta fase será el puente entre la intención humana y la fábrica de assets.

Deberá introducir:

```text
Asset Archetypes
Semantic Parameters
Constraint Resolution
Dependency Resolution
Style Profiles
Anatomical Profiles
Material Profiles
Texture Profiles
Modular Profiles
World Profiles
Quality Profiles
Target Profiles
```

y deberá permitir que **Character, Texture, Material, Modular Kit, Environment, Level y World compartan el mismo lenguaje de especificación**.
