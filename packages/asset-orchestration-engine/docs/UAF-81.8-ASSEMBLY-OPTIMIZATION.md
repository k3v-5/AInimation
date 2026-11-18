# UAF-81.8 — ASSET ASSEMBLY, LOD, OPTIMIZATION & UNREAL RUNTIME READINESS

## UAF-81.8-ARCH

### ARQUITECTURA DE ENSAMBLAJE, OPTIMIZACIÓN Y PREPARACIÓN RUNTIME PARA UNREAL ENGINE

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.8 — Asset Assembly, LOD, Optimization & Unreal Runtime Readiness  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.8 define la capa responsable de transformar los recursos generados por las fases anteriores en assets preparados para producción dentro de Unreal Engine.

La fase deberá controlar:

```text
Geometry
Materials
Textures
Collision
Physics
LOD
Nanite
Instancing
Bounds
Sockets
Pivot
Scale
Streaming
HLOD
Memory
Draw Calls
Runtime Cost
Export
Import
Validation
```

---

# 2. PRIMARY OBJECTIVE

El objetivo no es únicamente exportar un asset.

El objetivo es producir:

```text
ProductionReadyAsset
```

que cumpla simultáneamente:

```text
Visual Quality
+
Technical Correctness
+
Gameplay Correctness
+
Performance Requirements
+
Unreal Compatibility
+
Deterministic Build
```

---

# 3. ASSET RUNTIME PACKAGE

La salida será:

```text
RuntimeAssetPackage
```

conteniendo:

```text
Geometry
Materials
Textures
Collision
Physics
LOD
Nanite
Sockets
Metadata
GameplayMetadata
StreamingMetadata
OptimizationMetadata
ValidationReport
Provenance
```

---

# 4. ASSET ASSEMBLY GRAPH

Deberá existir:

```text
AssetAssemblyGraph
```

representando:

```text
Asset
├── Geometry
├── Material
├── Texture
├── Collision
├── Physics
├── LOD
├── Sockets
├── Metadata
└── Dependencies
```

---

# 5. ASSEMBLY STAGES

El ensamblaje deberá seguir una secuencia determinista:

```text
Source
↓
Normalize
↓
Validate
↓
Assemble
↓
Optimize
↓
Generate Runtime Data
↓
Validate Runtime Data
↓
Package
↓
Export
```

---

# 6. TRANSFORMATION PRINCIPLE

La optimización nunca deberá modificar silenciosamente la intención artística o funcional.

Toda transformación deberá registrar:

```text
input
operation
parameters
output
reason
```

---

# 7. TRANSFORMATION CATEGORIES

Mínimo:

```text
GEOMETRY
MATERIAL
TEXTURE
COLLISION
PHYSICS
LOD
NANITE
STREAMING
INSTANCING
BOUNDS
SOCKETS
```

---

# 8. NORMALIZATION

Antes de optimizar, el sistema deberá normalizar:

```text
scale
rotation
origin
pivot
axes
units
naming
hierarchy
material references
```

---

# 9. SCALE VALIDATION

Deberá existir:

```text
ScaleProfile
```

que defina las unidades esperadas.

Un asset con escala incorrecta deberá ser rechazado o corregido según política.

---

# 10. PIVOT SYSTEM

Cada asset deberá declarar:

```text
PivotDefinition
```

con:

```text
position
orientation
pivot_type
```

---

# 11. PIVOT TYPES

Mínimo:

```text
CENTER
BOTTOM
ORIGIN
ROOT
CUSTOM
SOCKET
```

---

# 12. PIVOT VALIDATION

Deberá detectar:

```text
unexpected pivot
floating pivot
offset pivot
rotation mismatch
```

---

# 13. ORIGIN POLICY

La posición del origen deberá depender del tipo de asset.

Ejemplo:

```text
Character → feet/root
Weapon → grip
Prop → base
Building → foundation
Vehicle → chassis/root
```

---

# 14. HIERARCHY

Deberá existir una jerarquía normalizada:

```text
AssetRoot
├── Render
├── Collision
├── Physics
├── Attachments
└── Metadata
```

cuando el tipo de asset lo permita.

---

# 15. STATIC ASSET

Los assets estáticos deberán poder reducirse a:

```text
StaticMesh
MaterialSet
CollisionSet
Metadata
```

---

# 16. SKELETAL ASSET

Los personajes y criaturas deberán poder representar:

```text
SkeletalMesh
Skeleton
PhysicsAsset
Materials
Sockets
AnimationMetadata
```

---

# 17. SOCKET SYSTEM

Deberá existir:

```text
SocketDefinition
```

con:

```text
socket_id
parent
position
rotation
scale
semantic_type
```

---

# 18. SOCKET TYPES

Mínimo:

```text
WEAPON
MUZZLE
GRIP
MAGAZINE
HAND
HEAD
BACK
SHOULDER
ROOT
CUSTOM
```

---

# 19. SOCKET VALIDATION

Deberá comprobarse:

```text
orientation
parent
scale
position
naming
compatibility
```

---

# 20. LOD SYSTEM

Deberá existir:

```text
LODProfile
```

que defina:

```text
lod_count
screen_sizes
triangle_targets
material_policy
shadow_policy
```

---

# 21. LOD LEVELS

El sistema deberá soportar:

```text
LOD0
LOD1
LOD2
LOD3
LOD4
```

según el asset.

---

# 22. LOD GENERATION

Los LOD podrán generarse mediante:

```text
mesh simplification
decimation
manual source meshes
procedural reduction
```

---

# 23. LOD TRIANGLE TARGET

Cada nivel deberá poder definir:

```text
target_triangle_ratio
minimum_triangle_count
maximum_deviation
```

---

# 24. LOD SILHOUETTE VALIDATION

La reducción deberá comprobar:

```text
silhouette_error
volume_error
feature_loss
```

---

# 25. LOD MATERIAL POLICY

Deberá poder definirse si cada LOD:

```text
keeps_materials
merges_materials
uses_atlas
uses_simplified_material
```

---

# 26. LOD UV VALIDATION

Después de cualquier reducción deberá verificarse:

```text
UV validity
UV distortion
material assignment
```

---

# 27. LOD COLLISION

La colisión deberá ser independiente de los LOD visuales salvo que el perfil indique lo contrario.

---

# 28. LOD DISTANCE

Los cambios de LOD deberán definirse mediante:

```text
screen_size
distance
quality_profile
```

No deberá depender únicamente de una distancia absoluta cuando el sistema objetivo utilice screen size.

---

# 29. LOD TRANSITION

Deberá evitarse:

```text
visible popping
material popping
shadow popping
silhouette discontinuity
```

dentro de los límites del perfil.

---

# 30. NANITE ELIGIBILITY

Deberá existir:

```text
NaniteEligibilityProfile
```

que determine si un asset es candidato.

---

# 31. NANITE DECISION

La decisión deberá considerar:

```text
geometry_type
material_features
transparency
masked_usage
deformation
runtime_profile
platform_profile
```

---

# 32. NANITE POLICY

El sistema no deberá activar Nanite indiscriminadamente.

Cada asset deberá registrar:

```text
nanite_enabled
decision
reason
profile
```

---

# 33. NANITE VALIDATION

Cuando corresponda, deberá comprobar:

```text
unsupported features
material constraints
geometry constraints
platform constraints
```

---

# 34. DEFORMABLE GEOMETRY

Los assets deformables deberán distinguirse de los estáticos.

Ejemplo:

```text
Skeletal
Morph
World Position Animation
Static
```

---

# 35. COLLISION SYSTEM

Deberá existir:

```text
CollisionProfile
```

---

# 36. COLLISION TYPES

Mínimo:

```text
NONE
SIMPLE
COMPLEX
CUSTOM
HYBRID
```

---

# 37. SIMPLE COLLISION

Deberán poder generarse:

```text
box
sphere
capsule
convex
multi_convex
```

---

# 38. COMPLEX COLLISION

Deberá utilizarse únicamente cuando esté justificado por el gameplay o la física.

---

# 39. COLLISION BUDGET

Cada asset podrá declarar:

```text
max_collision_primitives
max_collision_vertices
max_complexity
```

---

# 40. COLLISION VALIDATION

Deberá comprobar:

```text
missing collision
excessive collision
floating collision
collision outside visual bounds
unexpected gaps
```

---

# 41. PHYSICS ASSET

Para assets físicos complejos deberá existir:

```text
PhysicsAssetDefinition
```

---

# 42. PHYSICS BODIES

Cada cuerpo deberá declarar:

```text
shape
bone_or_parent
mass
collision_profile
constraints
```

---

# 43. PHYSICS CONSTRAINTS

Deberán soportarse:

```text
hinge
ball_socket
fixed
prismatic
custom
```

---

# 44. PHYSICS VALIDATION

Deberá detectar:

```text
unconstrained bodies
invalid hierarchy
excessive body count
interpenetration
unstable configuration
```

---

# 45. MASS PROFILE

Los assets físicos podrán utilizar:

```text
MassProfile
```

con:

```text
mass
density
center_of_mass
```

---

# 46. CENTER OF MASS

Cuando sea relevante deberá calcularse o declararse explícitamente.

---

# 47. BOUNDS

Deberá existir:

```text
BoundsDefinition
```

para:

```text
render bounds
collision bounds
streaming bounds
culling bounds
physics bounds
```

---

# 48. BOUNDS VALIDATION

Deberá detectar:

```text
incorrect bounds
excessively large bounds
bounds not containing geometry
```

---

# 49. INSTANCING SYSTEM

Deberá existir:

```text
InstancingProfile
```

para detectar assets repetitivos.

---

# 50. INSTANCING CANDIDATES

Mínimo:

```text
vegetation
lights
windows
panels
pipes
debris
props
modular pieces
```

---

# 51. INSTANCE COMPATIBILITY

Dos objetos podrán compartir instancing si cumplen:

```text
same mesh
compatible material
compatible transform rules
compatible rendering settings
```

---

# 52. INSTANCE GROUPING

Deberá poder agruparse por:

```text
cell
room
building
district
world
```

---

# 53. DRAW CALL OPTIMIZATION

Deberá existir:

```text
DrawCallProfile
```

---

# 54. DRAW CALL REDUCTION

Podrán utilizarse:

```text
material merging
instancing
atlas
mesh merging
HLOD
LOD
```

cuando sean compatibles.

---

# 55. MATERIAL SLOT OPTIMIZATION

El sistema deberá detectar:

```text
unused materials
duplicate materials
equivalent materials
excessive material slots
```

---

# 56. MATERIAL SLOT MERGING

Los materiales equivalentes podrán consolidarse si:

```text
visual result equivalent
shader compatible
UV compatible
```

---

# 57. TEXTURE MEMORY

Deberá calcularse:

```text
texture_memory_estimate
resident_memory_estimate
streaming_memory_estimate
```

---

# 58. MESH MEMORY

Deberá estimarse:

```text
vertex_memory
index_memory
nanite_memory
collision_memory
physics_memory
```

---

# 59. TOTAL ASSET COST

Deberá existir:

```text
RuntimeCost
```

con:

```text
geometry
textures
materials
shaders
physics
collision
streaming
```

---

# 60. PERFORMANCE PROFILE

Mínimo:

```text
PROTOTYPE
STANDARD
PRODUCTION
HIGH
CINEMATIC
```

---

# 61. PLATFORM PROFILE

Deberá existir:

```text
PlatformProfile
```

para permitir diferentes presupuestos.

Ejemplo conceptual:

```text
PC
CONSOLE
HIGH_END_PC
MOBILE
VR
CUSTOM
```

---

# 62. PLATFORM-SPECIFIC OPTIMIZATION

La misma fuente podrá producir variantes optimizadas por plataforma.

---

# 63. STREAMING PROFILE

Deberá existir:

```text
StreamingProfile
```

con:

```text
priority
group
max_resident_size
distance_policy
```

---

# 64. ASSET STREAMING

El sistema deberá determinar qué recursos necesitan:

```text
always loaded
streamed
on demand
distance streamed
```

---

# 65. DEPENDENCY MANAGEMENT

Deberá existir:

```text
RuntimeDependencyGraph
```

para:

```text
mesh
material
texture
physics
collision
blueprint
world
```

---

# 66. CIRCULAR DEPENDENCY DETECTION

Las dependencias circulares deberán detectarse antes del empaquetado.

---

# 67. BLUEPRINT METADATA

Los assets podrán declarar metadata para integración con Blueprints.

---

# 68. ACTOR DEFINITION

Deberá existir:

```text
ActorDefinition
```

que describa cómo ensamblar un asset dentro del mundo.

---

# 69. ACTOR COMPONENTS

Mínimo:

```text
Transform
Mesh
Collision
Physics
Interaction
GameplayTags
Sockets
Metadata
```

según el asset.

---

# 70. DATA ASSETS

Los assets deberán poder exportar metadata estructurada para ser consumida por sistemas de gameplay.

---

# 71. GAMEPLAY TAGS

Deberán conservarse durante el proceso:

```text
asset tags
surface tags
interaction tags
damage tags
navigation tags
```

---

# 72. INTERACTION SOCKETS

Deberá poder declararse dónde puede interactuar el jugador o gameplay.

Ejemplo:

```text
door_handle
weapon_mount
vehicle_entry
loot_point
interaction_point
```

---

# 73. ROOT MOTION / ANIMATION METADATA

Para assets animados deberá existir metadata para:

```text
skeleton
root
animation compatibility
retargeting
```

---

# 74. SKELETON COMPATIBILITY

Los personajes deberán poder declarar:

```text
skeleton_profile
bone_contract
retarget_profile
```

---

# 75. CHARACTER RUNTIME PACKAGE

Un personaje deberá poder empaquetarse como:

```text
CharacterPackage
├── SkeletalMesh
├── Skeleton
├── PhysicsAsset
├── Materials
├── Textures
├── Sockets
├── Collision
├── LOD
├── NanitePolicy
└── Metadata
```

---

# 76. WEAPON RUNTIME PACKAGE

Un arma deberá poder empaquetarse como:

```text
WeaponPackage
├── Static/SkeletalMesh
├── Materials
├── Collision
├── Sockets
├── LOD
├── Physics
└── Metadata
```

---

# 77. PROP RUNTIME PACKAGE

Un prop deberá poder empaquetarse como:

```text
PropPackage
├── Mesh
├── Materials
├── Collision
├── LOD
├── InstancingMetadata
└── Metadata
```

---

# 78. MODULAR MODULE PACKAGE

Un módulo deberá incluir:

```text
ModulePackage
├── Mesh
├── Materials
├── Collision
├── Connectors
├── LOD
├── HLOD
└── Metadata
```

---

# 79. WORLD RUNTIME PACKAGE

Un mundo deberá poder incorporar:

```text
WorldPackage
├── Cells
├── Actors
├── Geometry
├── Materials
├── Navigation
├── HLOD
├── Streaming
└── GameplayMetadata
```

---

# 80. HLOD SYSTEM

Deberá existir:

```text
HLODProfile
```

---

# 81. HLOD GROUPING

Los objetos podrán agruparse según:

```text
distance
cell
building
district
semantic_region
```

---

# 82. HLOD MATERIAL POLICY

El sistema deberá poder:

```text
merge
simplify
bake
retain
```

materiales durante HLOD.

---

# 83. HLOD VALIDATION

Deberá comprobar:

```text
visual continuity
bounds
material correctness
triangle reduction
memory reduction
```

---

# 84. CULLING

Deberá existir:

```text
CullingProfile
```

para controlar:

```text
distance
screen_size
bounds
semantic importance
```

---

# 85. CULLING EXCEPTIONS

Los elementos críticos podrán declarar:

```text
never_cull
always_loaded
gameplay_critical
```

---

# 86. SHADOW COST

El sistema deberá estimar el coste de sombras de los assets.

---

# 87. SHADOW POLICY

Cada asset podrá declarar:

```text
cast_shadow
receive_shadow
distance_shadow_policy
```

---

# 88. PHYSICS COST

Deberá medirse:

```text
body_count
constraint_count
collision_complexity
simulation_mode
```

---

# 89. NAVIGATION COST

Cuando el asset afecte navegación deberá estimarse:

```text
navmesh_complexity
dynamic_obstacle_cost
navigation_modifier_count
```

---

# 90. AUTOMATED IMPORT

Deberá existir:

```text
UnrealImportDefinition
```

que describa cómo debe importarse cada asset.

---

# 91. IMPORT SETTINGS

Deberán poder controlarse:

```text
mesh_import
material_import
collision_import
normal_import
scale
skeleton
physics
nanite
```

---

# 92. IMPORT DETERMINISM

Los settings de importación deberán estar versionados.

No deberán depender de configuraciones manuales del editor.

---

# 93. REIMPORT

Un asset actualizado deberá poder reimportarse conservando configuraciones declarativas.

---

# 94. IMPORT VALIDATION

Después de importar deberá verificarse:

```text
asset exists
mesh valid
materials assigned
collision valid
scale valid
bounds valid
dependencies valid
```

---

# 95. POST-IMPORT VALIDATION

La validación deberá ejecutarse sobre el resultado real del target cuando sea posible.

---

# 96. EXPORT MANIFEST

Cada build deberá producir:

```text
AssetManifest
```

con:

```text
asset_id
build_id
source_hash
dependencies
outputs
profiles
validation
```

---

# 97. BUILD HASH

El resultado deberá tener un hash derivado de:

```text
source
configuration
generator_version
profiles
dependencies
seed
```

---

# 98. REPRODUCIBLE BUILD

La misma entrada deberá producir el mismo paquete dentro de las tolerancias declaradas.

---

# 99. INCREMENTAL BUILD

El sistema deberá reconstruir únicamente aquello afectado por cambios.

---

# 100. INVALIDATION

La cache deberá invalidarse cuando cambie:

```text
geometry source
material source
texture source
profile
generator version
dependency
```

---

# 101. BUILD CACHE

Deberán cachearse:

```text
optimized meshes
LODs
collision
physics
textures
materials
runtime metadata
```

---

# 102. FAILURE RECOVERY

Si una etapa falla:

```text
no deberá corromper outputs válidos anteriores
```

---

# 103. TRANSACTIONAL BUILD

La publicación deberá realizarse mediante una operación transaccional:

```text
Prepare
↓
Validate
↓
Commit
```

---

# 104. ROLLBACK

Si la validación final falla:

```text
Commit
```

no deberá ejecutarse.

---

# 105. VALIDATION MATRIX

Cada asset deberá evaluarse contra:

```text
Geometry
Materials
Textures
UV
Collision
Physics
LOD
Nanite
Bounds
Sockets
Streaming
Memory
Draw Calls
Dependencies
Unreal Import
Gameplay
```

---

# 106. BLOCKING ERRORS

Deberán bloquear publicación:

```text
invalid geometry
missing material
broken dependency
invalid collision
invalid scale
invalid socket
budget violation
failed import
```

cuando el perfil las considere críticas.

---

# 107. WARNING POLICY

Los warnings deberán clasificarse:

```text
INFORMATIONAL
OPTIMIZATION
QUALITY
PERFORMANCE
COMPATIBILITY
```

---

# 108. ASSET QUALITY SCORE

Deberá existir:

```text
RuntimeAssetQualityScore
```

compuesto por:

```text
Visual
Technical
Gameplay
Performance
Compatibility
```

---

# 109. PERFORMANCE SCORE

El sistema deberá calcular un score específico para:

```text
Memory
Geometry
Shader
DrawCall
Physics
Streaming
```

---

# 110. GOLDEN ASSETS

Deberá existir una biblioteca de assets golden:

```text
character
creature
weapon
prop
vehicle
modular_piece
building
terrain
world
```

---

# 111. GOLDEN REGRESSION

Cada cambio del pipeline deberá compararse contra golden assets.

---

# 112. VISUAL REGRESSION

Deberán compararse:

```text
silhouette
material
color
lighting response
LOD transitions
```

---

# 113. TECHNICAL REGRESSION

Deberán compararse:

```text
triangle count
memory
draw calls
material slots
collision
LOD
dependencies
```

---

# 114. RUNTIME REGRESSION

Cuando exista entorno de ejecución disponible deberán comprobarse:

```text
spawn
render
collision
physics
navigation
streaming
```

---

# 115. REPORTING

Cada build deberá producir:

```text
BuildReport
```

conteniendo:

```text
status
quality_score
performance_score
warnings
errors
outputs
metrics
```

---

# 116. AUDIT TRAIL

Cada transformación deberá quedar registrada.

---

# 117. PROVENANCE

Cada output deberá poder rastrearse hasta:

```text
source
specification
generator
version
seed
profile
dependency
build
```

---

# 118. VERSION COMPATIBILITY

Deberá existir:

```text
CompatibilityMatrix
```

para:

```text
AOE version
Blender version
Unreal version
asset schema version
material schema version
```

---

# 119. ENGINE PROFILE

El sistema deberá utilizar:

```text
UnrealEngineProfile
```

en lugar de asumir una única versión fija.

---

# 120. ENGINE-SPECIFIC ADAPTER

Las diferencias entre versiones deberán estar aisladas en adapters.

El núcleo de AOE no deberá contener lógica dispersa específica de una versión del engine.

---

# 121. PLATFORM PROFILE

Deberá poder combinarse:

```text
EngineProfile
+
PlatformProfile
+
QualityProfile
```

para determinar el resultado final.

---

# 122. BUILD MATRIX

Un mismo asset podrá generar:

```text
PC_HIGH
PC_STANDARD
CONSOLE
CINEMATIC
```

sin duplicar la fuente.

---

# 123. FINAL ASSET STATES

Todo asset deberá encontrarse en uno de estos estados:

```text
DRAFT
GENERATED
VALIDATED
OPTIMIZED
PACKAGED
PUBLISHED
REJECTED
SUPERSEDED
```

---

# 124. PUBLISH RULE

Únicamente un asset:

```text
VALIDATED
+
OPTIMIZED
+
PACKAGED
```

podrá pasar a:

```text
PUBLISHED
```

---

# 125. NO MANUAL FIX PRINCIPLE

El pipeline no deberá considerar terminado un asset que requiera correcciones manuales repetitivas para:

```text
scale
pivot
collision
LOD
material assignment
naming
folder placement
import settings
```

Si una corrección aparece repetidamente, deberá convertirse en una regla automatizada.

---

# 126. HUMAN ARTIST OVERRIDE

Podrán existir overrides explícitos.

Cada override deberá registrar:

```text
asset
field
old_value
new_value
reason
author
timestamp
```

---

# 127. OVERRIDE SAFETY

Un override no deberá modificar silenciosamente la especificación original.

---

# 128. ARTIST LOCK

Un recurso podrá marcar:

```text
locked
```

para impedir regeneración automática de determinados componentes.

---

# 129. LOCKED COMPONENTS

Mínimo:

```text
geometry
material
texture
collision
LOD
socket
```

---

# 130. REGENERATION POLICY

La regeneración deberá respetar componentes bloqueados.

---

# 131. ASSET FACTORY CONTRACT

Todo asset generado por AOE deberá poder responder:

```text
What is it?
Where did it come from?
How was it generated?
Which version generated it?
What does it depend on?
What does it cost?
Can it be rebuilt?
Can it be validated?
Can it be exported?
Can it be reproduced?
```

---

# 132. FINAL ACCEPTANCE CRITERIA

UAF-81.8 estará completa cuando pueda convertir assets generados por las fases anteriores en recursos que:

```text
1. tengan escala correcta;
2. tengan pivots correctos;
3. tengan jerarquía correcta;
4. tengan materiales correctos;
5. tengan colisión correcta;
6. tengan física cuando corresponda;
7. tengan sockets válidos;
8. tengan LODs;
9. tengan Nanite policy;
10. tengan bounds correctos;
11. tengan streaming metadata;
12. tengan HLOD metadata;
13. estén optimizados;
14. respeten presupuestos;
15. tengan dependencias resueltas;
16. puedan importarse automáticamente;
17. puedan reimportarse;
18. puedan validarse después de importar;
19. sean reproducibles;
20. sean incrementalmente reconstruibles;
21. tengan provenance;
22. tengan build hash;
23. tengan regression tests;
24. tengan quality score;
25. estén preparados para runtime.
```

---

# 133. NON-NEGOTIABLE PRINCIPLE

AOE no deberá considerar:

```text
"exportado"
```

como equivalente a:

```text
"production ready"
```

Un asset únicamente será production ready cuando haya superado:

```text
GENERATION
↓
ASSEMBLY
↓
VALIDATION
↓
OPTIMIZATION
↓
RUNTIME PREPARATION
↓
IMPORT VALIDATION
↓
PUBLISH
```

---

# 134. NEXT PHASE

# UAF-81.9 — ANIMATION, RIGGING, SKINNING & CHARACTER RUNTIME FABRIC

La siguiente fase deberá atacar directamente una de las limitaciones actuales más importantes del sistema de personajes.

UAF-81.9 deberá definir:

```text
Skeleton Generation
Bone Hierarchy
Bone Naming
Human-like Rigs
Creature Rigs
Mechanical Rigs
Hybrid Rigs
IK
FK
IK/FK Switching
Control Rig
Skinning
Automatic Weights
Weight Normalization
Weight Painting
Weight Validation
Deformation Testing
Corrective Morphs
Blend Shapes
Facial Rigging
Facial Morph Targets
Finger Rigging
Foot Rigging
Hand Rigging
Retargeting
Animation Profiles
Animation Compatibility
Physics Assets
Ragdoll
Sockets
Weapon Attachments
Animation LOD
Pose Validation
Motion Range Validation
Export
Unreal Skeleton Compatibility
Control Rig Integration
Animation Blueprint Metadata
```

La finalidad será que el sistema deje de producir solamente **“personajes que tienen una geometría correcta”** y pueda producir **personajes que puedan entrar en el ciclo completo de animación y gameplay de Unreal**.
