# UAF-81.1 — ASSET INTELLIGENCE & SPECIFICATION

## UAF-81.1-ARCH

### SISTEMA UNIVERSAL DE INTELIGENCIA Y ESPECIFICACIÓN DE ASSETS

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.1 — Asset Intelligence & Specification  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.1 define el lenguaje estructurado mediante el cual UAF describe qué debe producirse.

La fase deberá eliminar la dependencia de specifications específicas de un único tipo de asset.

El sistema deberá poder describir:

```text
CHARACTER
CREATURE
WEAPON
PROP
MATERIAL
TEXTURE
MODULAR_KIT
ARCHITECTURE
ENVIRONMENT
LEVEL
WORLD
VFX
AUDIO
ANIMATION
RIG
BLUEPRINT
```

utilizando una arquitectura semántica común.

---

# 2. CORE OBJECTIVE

El sistema deberá convertir:

```text
INTENT
```

en:

```text
RESOLVED ASSET SPECIFICATION
```

mediante:

```text
Intent
 ↓
Semantic Interpretation
 ↓
Archetype Selection
 ↓
Parameter Resolution
 ↓
Constraint Resolution
 ↓
Dependency Resolution
 ↓
Generation Strategy Requirements
 ↓
Validated Specification
```

---

# 3. IMPORTANT ARCHITECTURAL RULE

UAF-81.1 no deberá decidir directamente qué herramienta utilizar para generar un asset.

La specification podrá expresar:

```text
high detail
realistic skin
complex clothing
modular armor
4K textures
production quality
```

pero no deberá imponer:

```text
use Blender primitive X
use sculpt modifier Y
use software Z
```

La selección de implementación corresponderá a fases posteriores.

---

# 4. SEMANTIC ASSET MODEL

Se deberá crear:

```text
SemanticAsset
```

con las siguientes capas:

```text
Identity
Intent
Structure
Appearance
Behavior
Constraints
Dependencies
Quality
Target
Provenance
```

---

# 5. IDENTITY

La identidad deberá contener:

```text
asset_id
asset_name
asset_type
namespace
version
```

---

# 6. INTENT

Intent deberá representar la intención de diseño.

Ejemplo:

```text
role = heavy_infantry
style = realistic_scifi
visual_language = brutalist_military
mood = intimidating
```

---

# 7. STRUCTURE

Structure describirá cómo está compuesto el asset.

Para un personaje:

```text
body
head
hands
feet
armor
clothing
equipment
weapons
attachments
```

Para un edificio:

```text
foundation
walls
doors
windows
roof
modules
interior
```

Para un mundo:

```text
terrain
regions
biomes
landmarks
roads
structures
gameplay_spaces
```

---

# 8. APPEARANCE

Appearance deberá describir:

```text
shape
proportions
colors
materials
surface properties
wear
damage
detail
visual style
```

---

# 9. BEHAVIOR

Cuando el asset tenga comportamiento, podrá especificarse:

```text
animation
interaction
destruction
physics
gameplay role
navigation
```

La specification no deberá implementar el comportamiento; solamente describirlo.

---

# 10. CONSTRAINTS

Todo asset podrá declarar constraints.

Categorías:

```text
DIMENSIONAL
GEOMETRIC
TOPOLOGICAL
MATERIAL
TEXTURE
PERFORMANCE
ENGINE
GAMEPLAY
STYLE
COMPATIBILITY
```

---

# 11. HARD VS SOFT CONSTRAINTS

Cada constraint deberá declarar:

```text
constraint_type
priority
severity
```

Tipos:

```text
HARD
SOFT
PREFERRED
INFORMATIONAL
```

---

# 12. CONSTRAINT RESOLUTION

Cuando existan conflictos, el sistema deberá resolverlos explícitamente.

Ejemplo:

```text
maximum_triangle_budget
+
required silhouette fidelity
```

El sistema deberá determinar qué condición puede relajarse, si existe una alternativa válida.

Nunca deberá resolver conflictos silenciosamente.

---

# 13. CONSTRAINT GRAPH

Las constraints deberán poder relacionarse:

```text
CharacterHeight
      ↓
BodyProportions
      ↓
ArmorDimensions
      ↓
WeaponScale
      ↓
CollisionCapsule
```

---

# 14. ARCHETYPE SYSTEM

Se deberá crear:

```text
AssetArchetype
```

Un archetype representa una clase funcional de asset.

Ejemplos:

```text
HumanoidCharacter
Creature
MilitaryWeapon
SciFiProp
ModularWall
Building
Terrain
Biome
Material
TextureSet
PlayableLevel
OpenWorldRegion
```

---

# 15. ARCHETYPE REQUIREMENTS

Cada archetype deberá declarar:

```text
required_parameters
optional_parameters
constraints
default_profiles
supported_targets
supported_quality_profiles
```

---

# 16. PARAMETER SYSTEM

Los parámetros deberán ser tipados.

Tipos mínimos:

```text
BOOLEAN
INTEGER
FLOAT
STRING
ENUM
VECTOR2
VECTOR3
COLOR
RANGE
CURVE
REFERENCE
LIST
MAP
OBJECT
```

---

# 17. PARAMETER METADATA

Cada parámetro deberá poder declarar:

```text
name
type
default
minimum
maximum
unit
description
required
exposed
```

---

# 18. UNITS

Las dimensiones físicas deberán tener unidades explícitas.

Internamente UAF deberá utilizar un sistema coherente.

Para producción 3D:

```text
meters
```

será la unidad lógica recomendada.

Las conversiones a centímetros, Unreal Units u otras unidades deberán producirse en adapters de target.

---

# 19. PARAMETER NORMALIZATION

Antes de generar deberá ejecutarse normalización.

Ejemplo:

```text
height = 185cm
```

deberá convertirse a una representación interna canónica equivalente a:

```text
height = 1.85m
```

---

# 20. RANGES

Los parámetros variables deberán poder utilizar:

```text
minimum
maximum
distribution
seed
```

Ejemplo:

```text
shoulder_width:
    min = 0.48
    max = 0.56
    distribution = NORMAL
```

---

# 21. PARAMETER DEPENDENCIES

Los parámetros podrán depender de otros.

Ejemplo:

```text
body_height
      ↓
leg_length
      ↓
knee_position
      ↓
armor_size
```

---

# 22. DERIVED PARAMETERS

El sistema deberá distinguir:

```text
USER_DEFINED
DERIVED
DEFAULTED
INFERRED
```

Esto permitirá conocer de dónde proviene cada valor.

---

# 23. PROVENANCE

Cada parámetro importante deberá poder indicar:

```text
source
origin
confidence
```

Ejemplo:

```text
height
source = explicit
confidence = 1.0
```

---

# 24. SEMANTIC REFERENCES

Una specification podrá referenciar componentes existentes.

Ejemplo:

```text
armor = HeavyArmorSet01
weapon = PlasmaRifle01
material = MilitaryObsidian
```

Estas referencias deberán resolverse antes de generación.

---

# 25. DEPENDENCY RESOLUTION

El sistema deberá construir un dependency graph.

Ejemplo:

```text
Character
├── Armor
│   ├── Material
│   └── TextureSet
├── Weapon
│   └── Material
└── Skeleton
```

---

# 26. CYCLIC DEPENDENCIES

El resolver deberá detectar ciclos.

Ejemplo:

```text
A → B → C → A
```

deberá producir un error explícito.

---

# 27. STYLE PROFILE

Se deberá crear:

```text
StyleProfile
```

con:

```text
visual_language
shape_language
color_language
material_language
detail_language
proportion_language
```

---

# 28. STYLE SEPARATION

El estilo deberá estar separado de la funcionalidad.

Ejemplo:

```text
HumanoidCharacter
```

podrá utilizar:

```text
MilitaryRealistic
FantasyStylized
SciFiHorror
AnimeStylized
Industrial
```

sin modificar el archetype base.

---

# 29. QUALITY PROFILE

Los quality profiles deberán controlar objetivos.

Ejemplo:

```text
STANDARD
```

podrá requerir:

```text
2K textures
optimized materials
game-ready topology
```

mientras:

```text
HERO
```

podrá requerir:

```text
4K/8K source
high-frequency surface detail
advanced material layering
hero silhouette
```

---

# 30. TARGET PROFILE

Se deberá crear:

```text
TargetProfile
```

Ejemplo:

```text
UnrealEngine5Production
```

que podrá declarar:

```text
Nanite
Lumen
VirtualTextures
TextureCompression
Collision
LODs
WorldPartition
```

---

# 31. TARGET ADAPTATION

La specification deberá permanecer independiente del target.

Ejemplo:

```text
texture_resolution = 4096
```

El target resolverá:

```text
source resolution
runtime resolution
compression
mip policy
format
```

---

# 32. CHARACTER SEMANTIC MODEL

El Character deberá poder describirse por regiones anatómicas.

Mínimo:

```text
head
neck
torso
pelvis
upper_arm_L
lower_arm_L
hand_L
upper_arm_R
lower_arm_R
hand_R
upper_leg_L
lower_leg_L
foot_L
upper_leg_R
lower_leg_R
foot_R
```

---

# 33. ADVANCED CHARACTER STRUCTURE

El modelo deberá permitir:

```text
body
face
hair
eyes
teeth
tongue
skin
clothing
armor
accessories
equipment
weapons
```

---

# 34. CHARACTER COMPLEXITY LEVEL

El character deberá declarar:

```text
complexity_level
```

Valores:

```text
C0 — Primitive
C1 — Simple
C2 — Game Character
C3 — Production Character
C4 — Hero Character
C5 — Cinematic Character
```

Esto será fundamental para seleccionar posteriormente estrategias de generación distintas.

---

# 35. CHARACTER GENERATION STRATEGY REQUIREMENT

UAF-81.1 deberá permitir declarar necesidades que una estrategia simple de primitives no pueda satisfacer.

Ejemplo:

```text
facial_fidelity = HIGH
clothing_complexity = HIGH
anatomical_fidelity = HIGH
surface_detail = HIGH
```

El sistema deberá traducir esto en capability requirements.

---

# 36. CAPABILITY REQUIREMENTS

Ejemplo:

```text
requires:
    organic_surface_generation
    advanced_facial_generation
    cloth_geometry
    high_detail_surface
    skeletal_rigging
    skin_weight_generation
```

La specification no deberá decidir qué componente implementará dichas capabilities.

---

# 37. MATERIAL SEMANTIC MODEL

Un material deberá poder describirse mediante:

```text
base_color
metallic
roughness
specular
normal
height
emission
opacity
subsurface
clearcoat
anisotropy
```

además de capas semánticas:

```text
wear
dust
scratches
rust
blood
oil
dirt
damage
```

---

# 38. MATERIAL LAYER SYSTEM

Los materiales deberán soportar composición por capas:

```text
Base
 ↓
Primary Surface
 ↓
Wear
 ↓
Damage
 ↓
Dirt
 ↓
Detail
 ↓
Emission
```

---

# 39. TEXTURE SEMANTIC MODEL

Un TextureSet deberá poder declarar:

```text
albedo
normal
roughness
metallic
ao
height
emission
mask
opacity
```

Cada mapa deberá declarar resolución, formato y propósito.

---

# 40. MODULAR KIT MODEL

Un ModularKit deberá declarar:

```text
grid_size
module_dimensions
connection_rules
snap_points
orientation
variants
material_slots
```

---

# 41. MODULAR COMPATIBILITY

Dos módulos serán compatibles únicamente cuando sus contratos de conexión sean compatibles.

Ejemplo:

```text
WALL_A
```

no deberá conectarse automáticamente a:

```text
ROOF_SOCKET
```

salvo que exista una regla explícita.

---

# 42. ENVIRONMENT MODEL

Un environment deberá soportar:

```text
terrain
vegetation
rocks
structures
roads
water
lighting
atmosphere
biomes
```

---

# 43. WORLD MODEL

Un world deberá poder contener:

```text
regions
biomes
landmarks
gameplay zones
streaming cells
navigation
population rules
```

---

# 44. LEVEL MODEL

Un playable level deberá separar:

```text
visual layout
gameplay layout
navigation
encounters
spawn zones
objectives
streaming
performance budgets
```

---

# 45. SEMANTIC VS PROCEDURAL

La specification deberá decir:

```text
"crear una ciudad industrial abandonada"
```

pero no:

```text
"crear exactamente 143 cubos con bevel"
```

El segundo pertenece al procedural implementation layer.

---

# 46. RESOLUTION PIPELINE

El sistema deberá ejecutar:

```text
Raw Specification
        ↓
Schema Validation
        ↓
Normalization
        ↓
Default Resolution
        ↓
Reference Resolution
        ↓
Dependency Resolution
        ↓
Constraint Resolution
        ↓
Capability Resolution
        ↓
Resolved Specification
```

---

# 47. RESOLVED SPECIFICATION

Se deberá crear:

```text
ResolvedAssetSpecification
```

que contenga:

```text
original_specification
resolved_parameters
resolved_dependencies
resolved_constraints
required_capabilities
effective_quality_profile
effective_target_profile
resolution_trace
```

---

# 48. RESOLUTION TRACE

El sistema deberá poder explicar por qué un valor terminó teniendo determinado resultado.

Ejemplo:

```text
requested:
height = 1.85m

constraint:
character capsule maximum = 1.92m

resolved:
height = 1.85m

status:
accepted
```

---

# 49. CONFLICT REPORT

Si una specification no puede resolverse:

```text
resolution_status = CONFLICT
```

y deberá indicar:

```text
conflicting_parameters
constraints
possible_resolutions
```

---

# 50. NO SILENT CORRECTION

Queda prohibido modificar silenciosamente una intención explícita.

Ejemplo:

```text
user requests:
height = 2.10m

system cannot support:
maximum = 1.92m
```

No deberá simplemente cambiar:

```text
2.10 → 1.92
```

sin registrar la modificación y su motivo.

---

# 51. ASSET BLUEPRINT

La specification resuelta deberá poder producir un:

```text
AssetBlueprint
```

Este blueprint describirá los componentes necesarios antes de generación.

Ejemplo:

```text
Character
├── Body
├── Head
├── Face
├── Clothing
├── Armor
├── Weapon
├── Materials
├── Textures
├── Skeleton
├── Collision
└── Metadata
```

---

# 52. BLUEPRINT NODE

Cada nodo deberá contener:

```text
node_id
node_type
parameters
dependencies
required_capabilities
quality_requirements
```

---

# 53. BLUEPRINT GRAPH

El blueprint será un DAG cuando las dependencias sean acíclicas.

Esto permitirá posteriormente paralelizar generación.

---

# 54. SPECIFICATION HASH

Deberán existir tres hashes:

```text
intent_hash
resolved_specification_hash
blueprint_hash
```

Esto permitirá distinguir:

```text
what was requested
what was resolved
what was planned
```

---

# 55. SPECIFICATION MIGRATION

Las specifications antiguas deberán poder migrarse.

Se deberá crear:

```text
SpecificationMigrator
```

capaz de:

```text
detect_version()
migrate()
validate()
report()
```

---

# 56. BACKWARD COMPATIBILITY

Cuando sea posible:

```text
old specification
      ↓
migration
      ↓
current specification
```

deberá preservar la intención original.

---

# 57. SPECIFICATION VALIDATION

Deberán existir al menos:

```text
SchemaValidator
SemanticValidator
ConstraintValidator
DependencyValidator
CapabilityValidator
TargetValidator
```

---

# 58. ACCEPTANCE TEST — CHARACTER

Debe poder expresarse un personaje complejo sin especificar primitivas de Blender.

Ejemplo conceptual:

```text
Type:
ProductionCharacter

Species:
Humanoid

Height:
1.85m

Complexity:
C4

Style:
Realistic Sci-Fi

Anatomical Fidelity:
High

Face Fidelity:
High

Clothing Complexity:
High

Armor:
Modular Heavy

Surface Detail:
High

Textures:
4K

Rig:
Humanoid Production

Target:
Unreal Engine 5.5
```

La resolución deberá producir las capabilities requeridas.

---

# 59. ACCEPTANCE TEST — MATERIAL

Debe poder expresarse:

```text
Material:
Industrial Painted Metal

Base:
dark gray

Metallic:
high

Roughness:
medium

Wear:
high

Scratches:
medium

Dust:
medium

Target:
Unreal Engine 5.5
```

sin especificar nodos concretos.

---

# 60. ACCEPTANCE TEST — MODULAR KIT

Debe poder expresarse:

```text
Kit:
Industrial Facility

Grid:
1m

Modules:
wall
corner
door
window
floor
roof

Style:
military industrial

Snap:
grid + socket

Target:
Unreal Engine 5.5
```

---

# 61. ACCEPTANCE TEST — WORLD

Debe poder expresarse:

```text
World:
Abandoned Industrial Planet

Scale:
large

Regions:
6

Biome:
industrial wasteland

Terrain:
rocky

Structures:
high

Gameplay:
tactical

Streaming:
required

Target:
Unreal Engine 5.5
```

---

# 62. QUALITY OF SPECIFICATION

Una specification deberá poder clasificarse:

```text
VALID
VALID_WITH_WARNINGS
INCOMPLETE
CONFLICT
UNSUPPORTED
INVALID
```

---

# 63. INCOMPLETE SPECIFICATION

Una specification incompleta no deberá ejecutarse automáticamente si faltan parámetros críticos.

Podrá continuar únicamente si existen defaults explícitos y seguros.

---

# 64. UNSUPPORTED

Si el sistema no dispone de una capability requerida:

```text
UNSUPPORTED
```

deberá ser reportado antes de iniciar una generación costosa.

---

# 65. CAPABILITY GAP

El sistema deberá poder producir un informe:

```text
Capability Gap Report
```

Ejemplo:

```text
Requested:
C4 Hero Character

Available:
primitive_character_generator
basic_rig_generator

Missing:
advanced_face
cloth_geometry
skin_weights
high_detail_surface
```

---

# 66. STRATEGIC VALUE

Este mecanismo permitirá que el proyecto identifique automáticamente cuándo el generador actual ya no es suficiente para la complejidad solicitada.

La solución no será degradar el asset.

La solución será seleccionar otra capability o declarar explícitamente el gap.

---

# 67. EXTENSIBILITY

Los nuevos asset types deberán poder registrarse sin modificar:

```text
ExecutionEngine
ArtifactSystem
ValidationSystem
StorageSystem
```

---

# 68. TESTING REQUIREMENTS

Deberán existir tests para:

```text
schema validation
parameter validation
unit normalization
default resolution
dependency resolution
cycle detection
constraint resolution
conflict detection
capability resolution
style profiles
quality profiles
target profiles
serialization
hashing
migration
```

---

# 69. FOUNDATION INTEGRATION

UAF-81.1 deberá integrarse con:

```text
UAF-81.0 Foundation
```

utilizando:

```text
AssetIdentity
ExecutionContext
Operation
Artifact
Diagnostic
ErrorModel
```

No deberá crear versiones paralelas incompatibles.

---

# 70. DEFINITION OF DONE

UAF-81.1 estará terminada cuando:

1. exista un semantic asset model;
2. existan archetypes;
3. existan parámetros tipados;
4. exista normalización;
5. exista resolución de defaults;
6. exista dependency graph;
7. exista constraint graph;
8. exista capability resolution;
9. exista style system;
10. exista quality system;
11. exista target system;
12. exista AssetBlueprint;
13. exista resolution trace;
14. exista capability gap detection;
15. existan migrations;
16. existan contract tests;
17. un personaje C4 pueda representarse sin mencionar una herramienta de generación;
18. un material pueda representarse;
19. un modular kit pueda representarse;
20. un world pueda representarse.

---

# 71. ARCHITECTURAL OUTCOME

Después de UAF-81.1, el sistema deberá poder entender que:

```text
"quiero un personaje heroico de producción"
```

implica:

```text
anatomy
face
clothing
materials
textures
rig
collision
optimization
validation
```

sin que la specification tenga que describir cómo construir cada uno.

---

# 72. NEXT PHASE

La siguiente fase será:

# UAF-81.2 — CAPABILITY & GENERATION STRATEGY FABRIC

Esta fase decidirá cómo convertir:

```text
ResolvedAssetSpecification
```

en:

```text
GenerationPlan
```

comparando las capabilities disponibles.

Será especialmente importante para resolver el problema actual del proyecto:

```text
simple procedural geometry
```

frente a:

```text
complex production geometry
```

El sistema deberá poder seleccionar dinámicamente entre múltiples estrategias:

```text
primitive procedural
parametric modeling
modular assembly
kitbashing
sculpt/detail workflow
scan/reference workflow
texture-driven detail
hybrid generation
external specialist generator
```

sin cambiar la specification original.
