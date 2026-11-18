# UAF-81.5 — CHARACTER RIGGING, SKINNING & DEFORMATION FABRIC

## UAF-81.5-ARCH

### ARQUITECTURA DE RIGGING, SKINNING Y DEFORMACIÓN DE PERSONAJES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.5 — Character Rigging, Skinning & Deformation Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.5 define el sistema responsable de convertir una geometría de personaje en un personaje:

* estructuralmente riggeado;
* correctamente skineado;
* deformable;
* compatible con animación;
* compatible con retargeting;
* compatible con Unreal Engine;
* validable automáticamente;
* reproducible;
* escalable a personajes de distinta complejidad.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá transformar:

```text
Character Geometry
        ↓
Character Anatomy
        ↓
Skeleton Definition
        ↓
Rig Definition
        ↓
Skinning
        ↓
Deformation
        ↓
Validation
        ↓
Unreal Character Package
```

---

# 3. FUNDAMENTAL PRINCIPLE

El skeleton no deberá derivarse únicamente de nombres de objetos.

Deberá existir una representación semántica independiente:

```text
CharacterSkeletonDefinition
```

que posteriormente podrá traducirse a Blender, Unreal u otros targets.

---

# 4. SKELETON DEFINITION

Deberá contener como mínimo:

```text
skeleton_id
version
root_bone
bones
bone_hierarchy
bone_roles
bind_pose
axis_conventions
scale
symmetry
target_profiles
```

---

# 5. BONE DEFINITION

Cada hueso deberá declarar:

```text
bone_id
name
parent
role
position
rotation
length
orientation
constraints
deformation_enabled
```

---

# 6. BONE ROLES

El sistema deberá distinguir entre identidad semántica y nombre técnico.

Roles mínimos:

```text
ROOT
PELVIS
SPINE
CHEST
NECK
HEAD
CLAVICLE
UPPER_ARM
LOWER_ARM
HAND
THIGH
CALF
FOOT
TOE
```

---

# 7. OPTIONAL BONE ROLES

Deberán poder existir:

```text
FINGER
FACIAL
JAW
EYE
BREAST
CLOTH
ARMOR
WEAPON
PROP
TAIL
WING
TENTACLE
AUXILIARY
```

---

# 8. STANDARD HUMANOID SKELETON

Deberá existir un perfil humanoide canónico.

Ejemplo:

```text
root
└── pelvis
    ├── spine
    │   ├── spine_02
    │   ├── spine_03
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       ├── clavicle_L
    │       │   └── arm_L
    │       └── clavicle_R
    │           └── arm_R
    ├── thigh_L
    │   └── calf_L
    │       └── foot_L
    └── thigh_R
        └── calf_R
            └── foot_R
```

El número exacto de huesos podrá variar por arquetipo.

---

# 9. SKELETON ARCHETYPES

Deberán existir perfiles para:

```text
HUMANOID
QUADRUPED
ROBOT
CREATURE
INSECTOID
SERPENTINE
FLYING
CUSTOM
```

---

# 10. SKELETON GENERATION

El skeleton deberá poder generarse a partir de landmarks anatómicos.

Ejemplo:

```text
pelvis
chest
shoulders
elbows
wrists
hips
knees
ankles
head
```

Los landmarks serán inputs, no huesos.

---

# 11. LANDMARK VALIDATION

Antes de generar huesos deberá validarse:

```text
symmetry
distances
hierarchy
orientation
scale
anatomical plausibility
```

---

# 12. SYMMETRY

El sistema deberá soportar:

```text
left/right symmetry
```

con posibilidad de desviación controlada.

---

# 13. ASYMMETRY

Deberá permitirse asimetría intencional.

Ejemplos:

```text
damaged arm
prosthetic limb
armor difference
mutation
weapon attachment
```

La asimetría deberá ser explícita.

---

# 14. BIND POSE

Cada skeleton deberá definir una bind pose.

No deberá asumirse automáticamente A-pose o T-pose.

---

# 15. CANONICAL POSES

Deberán existir perfiles:

```text
A_POSE
T_POSE
RELAXED
CUSTOM
```

---

# 16. AXIS CONVENTION

El sistema deberá conservar la convención global del proyecto.

La conversión entre:

```text
AOE
Blender
Unreal
```

deberá realizarse mediante adapters.

No deberán existir conversiones dispersas por el código.

---

# 17. BONE CONSTRAINTS

Deberán poder definirse:

```text
rotation limits
translation limits
twist limits
swing limits
preferred axis
```

---

# 18. RIG DEFINITION

Deberá existir:

```text
RigDefinition
```

separado del skeleton.

Esto permitirá que varios rigs utilicen el mismo skeleton.

---

# 19. RIG LAYERS

Mínimo:

```text
DEFORMATION
CONTROL
IK
FACIAL
AUXILIARY
EXPORT
```

---

# 20. DEFORMATION BONES

No todos los huesos deberán ser controles.

Deberá distinguirse:

```text
control bone
deformation bone
helper bone
physics bone
export bone
```

---

# 21. CONTROL RIG

El sistema deberá poder definir controles abstractos:

```text
Root Control
COG
Spine Control
Head Control
Hand IK
Foot IK
Pole Vector
Eye Target
```

---

# 22. IK SYSTEM

Deberá soportarse:

```text
two-bone IK
FABRIK
CCD
foot IK
hand IK
custom chains
```

cuando el backend seleccionado lo permita.

---

# 23. FOOT IK

Para personajes humanoides deberá poder configurarse:

```text
heel
toe
ankle
ground contact
foot roll
bank
```

---

# 24. HAND IK

Las manos deberán poder utilizar targets para:

```text
weapon grip
interaction
aiming
two-hand weapon
```

---

# 25. WEAPON ATTACHMENT

Deberán existir sockets o attachment points semánticos:

```text
weapon_hand_L
weapon_hand_R
back
hip
muzzle
```

según el arquetipo.

---

# 26. SKINNING DEFINITION

Deberá existir:

```text
SkinningDefinition
```

con:

```text
mesh_id
skeleton_id
weight_method
max_influences
normalization
envelopes
weight_rules
```

---

# 27. WEIGHT GENERATION

El sistema deberá soportar múltiples estrategias:

```text
automatic
heat
voxel
distance
envelope
geodesic
semantic
hybrid
```

---

# 28. SEMANTIC SKINNING

La generación de pesos podrá utilizar regiones semánticas:

```text
upper_arm
forearm
hand
thigh
calf
foot
```

Esto permitirá mejorar el resultado cuando la geometría procedural tenga topología irregular.

---

# 29. WEIGHT NORMALIZATION

Los pesos deberán cumplir:

```text
sum(weights(vertex)) = 1
```

dentro de la tolerancia definida.

---

# 30. MAX INFLUENCES

Deberá existir un límite configurable:

```text
max_influences_per_vertex
```

El target deberá determinar el límite final.

---

# 31. WEIGHT CLEANUP

Deberán eliminarse o corregirse:

```text
orphan weights
tiny influences
invalid bones
non-normalized weights
unexpected symmetry errors
```

---

# 32. WEIGHT MIRRORING

Para personajes simétricos deberá existir:

```text
mirror_weights()
```

permitiendo producir el lado opuesto y después aplicar excepciones.

---

# 33. WEIGHT TRANSFER

Deberá soportarse transferencia de weights entre:

```text
high topology
low topology
LOD meshes
updated geometry
variants
```

cuando la correspondencia geométrica sea válida.

---

# 34. DEFORMATION REGIONS

Cada mesh podrá declarar zonas críticas:

```text
shoulder
elbow
wrist
hip
knee
ankle
neck
jaw
```

---

# 35. DEFORMATION TEST POSES

Cada personaje deberá probar automáticamente poses de estrés.

Mínimo:

```text
arm_raise
arm_forward
elbow_bend
knee_bend
leg_raise
spine_bend
spine_twist
head_rotation
```

---

# 36. DEFORMATION QUALITY

El sistema deberá detectar:

```text
collapse
volume loss
volume explosion
intersections
severe stretching
candy-wrapper deformation
weight discontinuity
```

---

# 37. VOLUME PRESERVATION

Las articulaciones críticas deberán disponer de mecanismos de preservación de volumen cuando el perfil de calidad lo requiera.

---

# 38. CORRECTIVE DEFORMATION

Deberá existir soporte para:

```text
corrective blendshape
pose-space deformation
joint correction
twist correction
```

---

# 39. CORRECTIVE SHAPE GENERATION

Los correctives deberán asociarse a condiciones:

```text
joint angle
pose
rotation
distance
```

---

# 40. TWIST BONES

Para miembros que necesiten distribución de torsión deberán poder generarse:

```text
upper_arm_twist
forearm_twist
thigh_twist
calf_twist
```

---

# 41. FACIAL RIG

Los personajes que lo requieran deberán poder generar:

```text
jaw
eyes
eyelids
brows
mouth
lips
cheeks
nose
```

---

# 42. FACIAL REPRESENTATION

Deberán soportarse:

```text
bones
blendshapes
curves
hybrid
```

---

# 43. BLENDSHAPE SYSTEM

Deberán existir definiciones para:

```text
expression
phoneme
viseme
facial corrective
custom deformation
```

---

# 44. EYE SYSTEM

Los ojos deberán poder definir:

```text
left_eye
right_eye
look_target
rotation_limits
```

---

# 45. GAZE VALIDATION

El sistema deberá comprobar que los ojos:

```text
follow target
maintain anatomical orientation
respect rotation limits
```

---

# 46. CLOTH DEFORMATION

La ropa podrá:

```text
follow body skeleton
use additional bones
use simulation
use corrective deformation
```

---

# 47. ARMOR DEFORMATION

Las piezas rígidas deberán poder clasificarse como:

```text
rigid
semi_rigid
deformable
```

---

# 48. RIGID ARMOR

Las piezas rígidas deberán evitar deformación innecesaria.

Podrán utilizar:

```text
bone attachment
socket
rigid skinning
```

---

# 49. SEMI-RIGID ARMOR

Podrá utilizar:

```text
limited weights
helper bones
correctives
```

---

# 50. CREATURE SUPPORT

Las criaturas deberán poder utilizar chains arbitrarias.

Ejemplos:

```text
tail
tentacle
spine extension
antenna
wing
horn
```

---

# 51. TAIL SYSTEM

Deberá existir un generador de cadenas:

```text
TailDefinition
```

con:

```text
segment_count
length
falloff
stiffness
control_density
```

---

# 52. TENTACLE SYSTEM

Deberá soportarse generación de cadenas flexibles.

---

# 53. WING SYSTEM

Las alas deberán poder definir:

```text
root
primary_chain
secondary_chain
membrane_controls
fold_controls
```

---

# 54. PHYSICS ASSET

Deberá existir:

```text
PhysicsDefinition
```

para generar cuerpos y constraints.

---

# 55. PHYSICS BODIES

Podrán definirse:

```text
capsule
sphere
box
convex
custom
```

---

# 56. PHYSICS CONSTRAINTS

Deberán soportarse:

```text
hinge
ball_socket
cone
limited_rotation
```

---

# 57. COLLISION POLICY

Cada cuerpo deberá declarar:

```text
collision_enabled
collision_channel
simulation_mode
```

---

# 58. CLOTH PHYSICS

Cuando sea requerido, el personaje podrá producir metadata para:

```text
cloth
cape
skirt
coat
straps
loose accessories
```

---

# 59. RAGDOLL

Los personajes humanoides deberán poder generar un perfil de ragdoll.

---

# 60. RAGDOLL VALIDATION

Deberá verificarse:

```text
bone coverage
joint limits
collision overlaps
unexpected disconnected bodies
```

---

# 61. ANIMATION COMPATIBILITY

El skeleton graphical deberá poder declarar:

```text
animation_profile
```

que describa compatibilidad con una familia de animaciones.

---

# 62. RETARGETING

Deberá existir:

```text
RetargetDefinition
```

para mapear:

```text
source skeleton
        ↓
semantic bone roles
        ↓
target skeleton
```

---

# 63. RETARGET MAP

El mapping deberá utilizar roles semánticos cuando sea posible.

Ejemplo:

```text
source: upperarm_l
target: arm_L
```

---

# 64. RETARGET VALIDATION

Deberán probarse:

```text
idle
walk
run
jump
crouch
aim
attack
```

o el subconjunto correspondiente al perfil.

---

# 65. ANIMATION POSE VALIDATION

Cada personaje deberá ser probado en poses canónicas.

---

# 66. INTERSECTION TESTING

Deberán detectarse intersecciones graves entre:

```text
body
armor
clothing
weapons
accessories
```

---

# 67. CAPSULE COMPATIBILITY

El sistema deberá validar la cápsula gameplay definida por el proyecto.

La generación del rig no podrá invalidar:

```text
height
radius
root position
ground contact
```

---

# 68. GROUND CONTACT

Los pies deberán poder determinar:

```text
sole position
heel
toe
ground offset
```

---

# 69. ROOT MOTION

Deberá declararse explícitamente si el personaje utiliza:

```text
root motion
in-place
hybrid
```

---

# 70. SCALE VALIDATION

La escala del skeleton deberá ser consistente con:

```text
world units
character height
gameplay capsule
animation system
physics
```

---

# 71. LOD RIGGING

Los LOD podrán utilizar distintos niveles de skeleton/deformation complexity.

---

# 72. LOD POLICY

Deberá existir:

```text
LOD0
LOD1
LOD2
LOD3
```

cuando el perfil lo requiera.

---

# 73. LOD SKINNING

Los LOD deberán conservar deformación válida.

La reducción de influences no deberá producir artefactos inaceptables.

---

# 74. EXPORT SKELETON

El sistema deberá separar:

```text
internal rig
```

de:

```text
export skeleton
```

para evitar contaminar el runtime con controles innecesarios.

---

# 75. EXPORT CLEANUP

Antes de exportar deberán eliminarse o excluirse:

```text
non-export controls
debug helpers
temporary deformers
construction geometry
```

según política.

---

# 76. UNREAL ADAPTER

Deberá existir:

```text
UnrealCharacterAdapter
```

responsable de traducir:

```text
SkeletonDefinition
SkinningDefinition
RigDefinition
PhysicsDefinition
```

al formato correspondiente de Unreal.

---

# 77. UNREAL PACKAGE

El resultado deberá poder representar:

```text
Skeletal Mesh
Skeleton
Physics Asset
Materials
Sockets
Morph Targets
Animation Metadata
LOD Metadata
Validation Report
```

---

# 78. SOCKET SYSTEM

Los sockets deberán definirse semánticamente.

Ejemplos:

```text
weapon_socket
back_socket
head_socket
muzzle_socket
hand_socket
```

---

# 79. SOCKET VALIDATION

Cada socket deberá comprobar:

```text
parent bone
position
rotation
scale
orientation
```

---

# 80. CHARACTER PACKAGE

El output completo deberá poder contener:

```text
CharacterPackage
├── Geometry
├── Skeleton
├── Skinning
├── Rig
├── Deformation
├── Physics
├── Materials
├── Sockets
├── Morphs
├── LODs
├── Animation compatibility
└── Validation
```

---

# 81. DETERMINISM

La generación deberá ser reproducible mediante:

```text
character_spec_hash
skeleton_version
rig_version
skinning_version
generator_version
seed
```

---

# 82. PROVENANCE

Cada resultado deberá registrar:

```text
input geometry hash
skeleton hash
rig hash
weight generation method
settings
generator version
target profile
quality profile
```

---

# 83. INCREMENTAL REBUILD

El sistema deberá determinar qué debe regenerarse.

Ejemplo:

```text
Material changed
→ no rig rebuild

Skeleton changed
→ rig + skinning may rebuild

Geometry topology changed
→ skinning validation required

Landmark changed
→ skeleton + rig + skinning rebuild

Physics setting changed
→ physics only
```

---

# 84. CACHE

Deberán poder cachearse:

```text
skeleton
rig
weights
correctives
physics
retarget maps
```

---

# 85. FAILURE MODES

Mínimo:

```text
INVALID_SKELETON
INVALID_HIERARCHY
LANDMARK_FAILURE
BIND_POSE_FAILURE
SKINNING_FAILURE
WEIGHT_NORMALIZATION_FAILURE
DEFORMATION_FAILURE
CORRECTIVE_FAILURE
PHYSICS_FAILURE
RETARGET_FAILURE
SOCKET_FAILURE
EXPORT_FAILURE
```

---

# 86. FAILURE SEVERITY

Cada error deberá clasificarse:

```text
INFO
WARNING
ERROR
BLOCKING
```

---

# 87. AUTOMATIC REPAIR

Cuando sea seguro, el sistema podrá intentar:

```text
weight normalization
weight cleanup
symmetry repair
bone orientation correction
minor intersection correction
socket alignment
```

Toda reparación deberá quedar registrada.

---

# 88. HUMAN-LEVEL QUALITY GATE

Un personaje no podrá considerarse terminado únicamente porque:

```text
FBX exported successfully
```

Deberá superar:

```text
geometry validation
skeleton validation
skinning validation
deformation validation
physics validation
animation compatibility
visual validation
```

---

# 89. DEFORMATION SCORE

Deberá existir una métrica de deformación.

Podrá considerar:

```text
volume preservation
intersection count
stretch
weight smoothness
joint stability
```

---

# 90. RIG QUALITY SCORE

Deberá existir una métrica compuesta:

```text
Rig Quality =
Skeleton Validity
+ Skinning Quality
+ Deformation Quality
+ Animation Compatibility
+ Physics Validity
```

Los pesos deberán ser configurables.

---

# 91. GOLDEN CHARACTER

Deberá existir al menos un personaje golden utilizado para regresión.

El golden character deberá probar:

```text
humanoid skeleton
skin weights
IK
facial deformation
armor
cloth
weapon socket
physics
LOD
export
```

---

# 92. REGRESSION TESTING

Cualquier cambio en:

```text
skeleton generator
weight generator
deformation system
export adapter
```

deberá ejecutar automáticamente la suite de regresión correspondiente.

---

# 93. PERFORMANCE

El sistema deberá registrar:

```text
skeleton generation time
weight generation time
deformation test time
physics generation time
export time
```

---

# 94. RESOURCE BUDGET

Deberán poder definirse límites para:

```text
bone count
influences
morph count
physics bodies
physics constraints
animation complexity
```

---

# 95. COMPLEX CHARACTER SUPPORT

La arquitectura deberá permitir personajes que superen el humanoide básico:

```text
multi-limbed
mechanical
organic
hybrid
modular
asymmetric
non-humanoid
```

sin modificar el núcleo del sistema.

---

# 96. MODULAR CHARACTER PARTS

Un personaje podrá ensamblarse mediante:

```text
head
torso
arms
legs
hands
feet
armor
clothing
accessories
```

Cada módulo deberá declarar sus conexiones.

---

# 97. MODULE COMPATIBILITY

Cada módulo deberá declarar:

```text
attachment points
required bones
provided bones
scale constraints
material regions
deformation rules
```

---

# 98. SKELETON COMPATIBILITY

Dos módulos podrán combinarse únicamente si cumplen su contrato de skeleton.

---

# 99. CHARACTER VARIANTS

Deberán poder generarse variantes sin reconstruir componentes invariantes.

Ejemplo:

```text
same skeleton
different armor
different material
different head
different weapon
```

---

# 100. FINAL ACCEPTANCE CRITERIA

UAF-81.5 estará completa cuando el sistema pueda generar un personaje que:

```text
1. posea skeleton semántico;
2. posea bind pose válida;
3. posea skin weights válidos;
4. mantenga pesos normalizados;
5. soporte IK;
6. soporte sockets;
7. soporte deformación;
8. soporte correctives;
9. soporte LOD;
10. soporte física;
11. soporte ragdoll;
12. soporte retargeting;
13. soporte variantes modulares;
14. soporte piezas rígidas;
15. soporte ropa;
16. soporte criaturas;
17. soporte personajes asimétricos;
18. pueda validarse automáticamente;
19. pueda exportarse a Unreal;
20. pueda reconstruirse incrementalmente;
21. conserve provenance;
22. sea reproducible;
23. respete los presupuestos definidos;
24. supere las pruebas de deformación;
25. sea utilizable en producción sin depender de correcciones manuales obligatorias.
```

---

# 101. NON-NEGOTIABLE RULE

La salida de UAF-81.5 no será considerada un personaje terminado si requiere que un artista:

```text
repare weights
reoriente huesos
corrija sockets
reconstruya el Physics Asset
corrija deformaciones críticas
reconfigure manualmente el skeleton
```

para poder entrar en el pipeline estándar.

Las excepciones deberán registrarse como:

```text
MANUAL_REVIEW_REQUIRED
```

y nunca ocultarse como éxito automático.

---

# 102. NEXT PHASE

# UAF-81.6 — WORLD GEOMETRY, MODULAR BLOCKOUT & PROCEDURAL LEVEL FABRIC

Esta fase trasladará la misma filosofía desde assets individuales hacia el mundo.

Deberá resolver:

```text
Modular Architecture
Building Blocks
Walls
Floors
Doors
Windows
Stairs
Corridors
Rooms
Buildings
Props Placement
Biome Systems
Terrain
Roads
Landscapes
Procedural POIs
Gameplay Spaces
Navigation
Collision
World Partition
Level Streaming
PCG
Instancing
HLOD
LOD
Lighting Metadata
Gameplay Metadata
Spawn Points
Cover Systems
AI Navigation
Map Validation
```

El objetivo será que AOE pueda pasar de:

```text
"crear un personaje"
```

a:

```text
"crear un espacio jugable completo,
estructuralmente válido,
optimizado,
navegable y preparado para Unreal."
```
