# UAF-81.9 — ANIMATION, RIGGING, SKINNING & CHARACTER RUNTIME FABRIC

## UAF-81.9-ARCH

### ARQUITECTURA DE RIGGING, DEFORMACIÓN, ANIMACIÓN Y RUNTIME DE PERSONAJES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.9 — Animation, Rigging, Skinning & Character Runtime Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.9 define el sistema completo para transformar una geometría de personaje, criatura, robot o entidad deformable en un asset animable y utilizable en producción.

La fase deberá cubrir:

```text
Character
Creature
Robot
Mechanical Entity
Hybrid Entity
Humanoid
Non-Humanoid
```

y producir:

```text
ProductionReadyAnimatedCharacter
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá producir un personaje que pueda:

```text
ser importado en Unreal Engine;
tener skeleton;
tener skinning;
deformarse correctamente;
recibir animaciones;
ser retargeteado;
utilizar IK;
utilizar FK;
utilizar Control Rig;
utilizar Animation Blueprint;
utilizar ragdoll;
utilizar sockets;
utilizar morph targets;
utilizar facial animation;
ser evaluado automáticamente;
```

---

# 3. CORE PRINCIPLE

La geometría no será considerada terminada hasta que haya sido validada dentro de un ciclo de deformación.

El pipeline deberá considerar:

```text
Geometry
↓
Topology Analysis
↓
Skeleton
↓
Skinning
↓
Deformation
↓
Animation
↓
Validation
↓
Runtime
```

---

# 4. CHARACTER RUNTIME GRAPH

Deberá existir:

```text
CharacterRuntimeGraph
```

representando:

```text
Character
├── Geometry
├── Skeleton
├── Skin
├── Physics
├── Animation
├── Morphs
├── Materials
├── Sockets
├── Gameplay
└── Runtime Metadata
```

---

# 5. CHARACTER CLASSIFICATION

Antes del rigging deberá clasificarse el asset.

Mínimo:

```text
HUMANOID
CREATURE
QUADRUPED
INSECTOID
SERPENTINE
AVIAN
ROBOT
MECHANICAL
HYBRID
CUSTOM
```

---

# 6. RIG STRATEGY

Cada clasificación deberá seleccionar un:

```text
RigProfile
```

que determine:

```text
bone topology
controllers
IK chains
constraints
deformation strategy
retargeting strategy
animation compatibility
```

---

# 7. HUMANOID RIG

El perfil humanoide deberá soportar como mínimo:

```text
root
pelvis
spine
spine_01
spine_02
chest
neck
head
clavicle_L
upperarm_L
lowerarm_L
hand_L
clavicle_R
upperarm_R
lowerarm_R
hand_R
thigh_L
calf_L
foot_L
ball_L
thigh_R
calf_R
foot_R
ball_R
```

---

# 8. OPTIONAL HUMANOID BONES

Podrán existir:

```text
thumb
index
middle
ring
pinky
jaw
eyes
facial
breast
armor
equipment
```

sin romper el skeleton base.

---

# 9. BONE NAMING CONTRACT

Cada skeleton deberá cumplir un contrato de nombres.

El contrato deberá ser:

```text
deterministic
case-consistent
side-consistent
hierarchy-consistent
engine-compatible
```

---

# 10. SIDE CONVENTION

Las extremidades laterales deberán utilizar una convención única:

```text
_L
_R
```

No deberán coexistir arbitrariamente:

```text
left
Left
L
_l
```

para representar el mismo concepto.

---

# 11. BONE HIERARCHY VALIDATION

Deberá verificarse:

```text
single root
no cycles
valid parents
valid transforms
valid orientation
valid scale
```

---

# 12. ROOT BONE

Todo personaje animable deberá tener un root claramente definido.

El root deberá representar el movimiento global del personaje.

---

# 13. PELVIS

El pelvis deberá representar el centro funcional del cuerpo humanoide cuando corresponda.

---

# 14. SPINE CHAIN

La cadena vertebral deberá ser configurable.

Ejemplo:

```text
pelvis
↓
spine
↓
spine_01
↓
spine_02
↓
chest
```

---

# 15. LIMB CHAINS

Cada extremidad deberá declarar:

```text
start
middle
end
```

Ejemplo:

```text
upperarm
↓
lowerarm
↓
hand
```

---

# 16. LEG CHAINS

Mínimo:

```text
thigh
↓
calf
↓
foot
↓
ball
```

---

# 17. IK SYSTEM

Deberá existir:

```text
IKProfile
```

---

# 18. IK CHAINS

Mínimo:

```text
arm_L
arm_R
leg_L
leg_R
```

---

# 19. IK TARGETS

Deberán existir:

```text
hand_target_L
hand_target_R
foot_target_L
foot_target_R
```

---

# 20. POLE TARGETS

Los brazos y piernas deberán poder utilizar:

```text
pole_L
pole_R
```

para estabilizar el plano de deformación.

---

# 21. IK VALIDATION

Deberá comprobar:

```text
reachability
orientation
pole stability
joint limits
```

---

# 22. FK SYSTEM

El skeleton deberá seguir siendo completamente utilizable mediante FK.

---

# 23. IK/FK COMPATIBILITY

Deberá poder alternarse entre:

```text
IK
FK
IK/FK
```

sin romper la pose.

---

# 24. CONTROL RIG PROFILE

Deberá existir:

```text
ControlRigProfile
```

que describa:

```text
controllers
spaces
IK
FK
constraints
switches
```

---

# 25. CONTROLLER TYPES

Mínimo:

```text
ROOT
BODY
HEAD
HAND
FOOT
ELBOW
KNEE
WEAPON
CUSTOM
```

---

# 26. CONTROLLER NAMING

Los controles deberán tener nombres deterministas y no deberán confundirse con bones.

Ejemplo:

```text
CTRL_root
CTRL_hand_L
CTRL_hand_R
CTRL_foot_L
CTRL_foot_R
```

---

# 27. SPACE SYSTEM

Los controles deberán soportar espacios:

```text
WORLD
LOCAL
PARENT
CHARACTER
WEAPON
CAMERA
```

cuando corresponda.

---

# 28. SKINNING SYSTEM

Deberá existir:

```text
SkinningProfile
```

---

# 29. SKIN WEIGHTS

Cada vértice deformable deberá tener pesos asociados a uno o más bones.

---

# 30. WEIGHT NORMALIZATION

Los pesos deberán cumplir:

```text
sum(weights) = 1
```

dentro de la tolerancia configurada.

---

# 31. MAX INFLUENCES

Deberá existir:

```text
max_influences
```

configurable por plataforma y asset.

---

# 32. WEIGHT GENERATION

El sistema deberá soportar:

```text
distance based
heat based
volume based
nearest bone
geodesic
topology aware
custom
```

---

# 33. WEIGHT GENERATION PRIORITY

Cuando existan múltiples estrategias, deberá seleccionarse mediante:

```text
character_type
topology
bone_density
geometry_complexity
profile
```

---

# 34. WEIGHT CLEANUP

Después de generar pesos deberá ejecutarse:

```text
remove tiny weights
normalize
smooth
limit influences
repair islands
```

según perfil.

---

# 35. WEIGHT VALIDATION

Deberá detectar:

```text
unweighted vertices
overweighted vertices
invalid influences
wrong bone assignment
isolated weight islands
```

---

# 36. WEIGHT VISUALIZATION

El sistema deberá poder generar mapas de influencia para inspección automática.

---

# 37. DEFORMATION TEST POSES

Todo personaje deberá someterse como mínimo a:

```text
T_POSE
A_POSE
REST
ARM_RAISE
ARM_FORWARD
ELBOW_BEND
KNEE_BEND
HIP_BEND
CROUCH
WALK_PROXY
```

---

# 38. EXTREME DEFORMATION

Deberán probarse poses extremas para encontrar:

```text
collapse
stretch
volume loss
self intersection
weight bleeding
```

---

# 39. DEFORMATION METRICS

Deberán calcularse:

```text
volume preservation
surface deviation
joint collapse
penetration
stretch ratio
```

---

# 40. DEFORMATION BUDGET

Cada asset podrá declarar:

```text
max_deformation_error
max_volume_loss
max_penetration
max_stretch
```

---

# 41. CORRECTIVE MORPHS

Deberá existir soporte para:

```text
corrective morphs
```

en articulaciones problemáticas.

---

# 42. CORRECTIVE MORPH TRIGGERS

Podrán activarse mediante:

```text
joint angle
pose
driver
animation state
```

---

# 43. MORPH TARGET SYSTEM

Deberá existir:

```text
MorphTargetProfile
```

---

# 44. MORPH TYPES

Mínimo:

```text
FACIAL
CORRECTIVE
BODY
EXPRESSION
CUSTOM
```

---

# 45. MORPH NAMING

Los morph targets deberán tener nombres deterministas.

Ejemplo:

```text
Mouth_Open
Eye_Blink_L
Eye_Blink_R
Jaw_Open
```

---

# 46. MORPH VALIDATION

Deberá comprobar:

```text
vertex count
topology compatibility
delta validity
range
unexpected deformation
```

---

# 47. FACIAL SYSTEM

Los personajes con rostro deberán poder declarar:

```text
FacialRigProfile
```

---

# 48. FACIAL REGIONS

Mínimo:

```text
jaw
eyes
eyelids
brows
mouth
cheeks
nose
```

cuando la geometría lo permita.

---

# 49. FACIAL REPRESENTATION

Deberá soportarse:

```text
bones
morph targets
hybrid
```

---

# 50. EYE SYSTEM

Los ojos deberán poder utilizar:

```text
eye_L
eye_R
```

con controles de mirada.

---

# 51. LOOK-AT SYSTEM

Deberá existir:

```text
LookAtDefinition
```

para controlar:

```text
head
eyes
upper_body
```

según configuración.

---

# 52. BLINK SYSTEM

Los personajes humanoides deberán poder definir:

```text
blink_L
blink_R
blink_both
```

cuando dispongan de morph/facial rig compatible.

---

# 53. MOUTH SYSTEM

Deberá poder definirse:

```text
jaw_open
jaw_forward
jaw_left
jaw_right
lip_controls
```

cuando corresponda.

---

# 54. ROBOT RIG

Los robots deberán soportar un rig específico.

No deberá forzarse un modelo orgánico de deformación sobre geometría mecánica.

---

# 55. MECHANICAL RIG STRATEGY

Los componentes mecánicos deberán preferir:

```text
rigid deformation
bone parenting
constraints
mechanical pivots
```

sobre deformación suave cuando corresponda.

---

# 56. MECHANICAL JOINT VALIDATION

Deberá comprobarse:

```text
rotation axis
joint limits
collision
mechanical interference
```

---

# 57. CREATURE RIG

Las criaturas deberán poder utilizar estructuras variables.

Ejemplos:

```text
quadruped
six_legged
tentacle
tail
wing
multi_arm
```

---

# 58. PROCEDURAL BONE GENERATION

El sistema deberá poder generar bones desde landmarks.

Inputs posibles:

```text
anatomical landmarks
mesh analysis
semantic markers
template
```

---

# 59. LANDMARK CONTRACT

Los landmarks deberán poder representar:

```text
root
pelvis
spine
head
shoulders
elbows
hands
hips
knees
feet
```

y extensiones específicas del organismo.

---

# 60. BONE ORIENTATION

La orientación de bones deberá ser determinista.

No podrá depender de la orientación accidental de la escena.

---

# 61. JOINT LIMITS

Cada articulación podrá definir:

```text
min_rotation
max_rotation
preferred_axis
secondary_axis
```

---

# 62. ANATOMICAL VALIDATION

En humanoides deberá verificarse:

```text
left/right symmetry
limb length
joint order
bone orientation
```

---

# 63. SYMMETRY

La generación deberá poder utilizar simetría como mecanismo de corrección.

---

# 64. ASYMMETRY SUPPORT

La simetría no deberá ser obligatoria.

Los personajes deliberadamente asimétricos deberán poder declararlo.

---

# 65. ARMOR / CLOTHING RIGGING

Las piezas rígidas de armadura deberán poder:

```text
parentarse
seguir bones
utilizar sockets
utilizar rigid weights
```

---

# 66. CLOTH DEFORMATION

La ropa deformable deberá poder declarar:

```text
cloth
skinned
hybrid
rigid
```

---

# 67. CLOTHING COLLISION

La ropa dinámica deberá poder declarar cuerpos de colisión relevantes.

---

# 68. ACCESSORY SYSTEM

Accesorios deberán poder adjuntarse a:

```text
bone
socket
controller
```

---

# 69. WEAPON ATTACHMENT

Las armas deberán poder vincularse mediante:

```text
hand socket
weapon socket
attachment profile
```

---

# 70. EQUIPMENT SYSTEM

El personaje deberá poder definir:

```text
equipment slots
```

como:

```text
primary
secondary
melee
back
head
chest
utility
```

---

# 71. ANIMATION PROFILE

Deberá existir:

```text
AnimationProfile
```

---

# 72. ANIMATION STATES

Mínimo:

```text
IDLE
WALK
RUN
SPRINT
CROUCH
JUMP
FALL
LAND
ATTACK
HIT
DEATH
```

cuando correspondan al tipo de personaje.

---

# 73. ANIMATION COMPATIBILITY

Cada personaje deberá declarar qué animaciones puede recibir.

---

# 74. RETARGET PROFILE

Deberá existir:

```text
RetargetProfile
```

---

# 75. RETARGET MAPPING

Deberá mapear:

```text
source bone
↓
target bone
```

---

# 76. RETARGET VALIDATION

Deberá comprobar:

```text
missing bones
extra bones
axis mismatch
scale mismatch
pose mismatch
```

---

# 77. RETARGET TEST

Una animación estándar deberá utilizarse como prueba.

El personaje deberá poder ejecutar:

```text
idle
walk
run
jump
```

sin deformaciones críticas.

---

# 78. REFERENCE POSE

Cada skeleton deberá declarar:

```text
reference_pose
```

---

# 79. REFERENCE POSE VALIDATION

Deberá detectarse:

```text
wrong arm angle
wrong leg angle
rotated pelvis
incorrect spine
```

---

# 80. ANIMATION IMPORT METADATA

Cada animación deberá declarar:

```text
skeleton
frame_rate
duration
root_motion
loop
compression_profile
```

---

# 81. ROOT MOTION

Deberá existir:

```text
RootMotionPolicy
```

---

# 82. ROOT MOTION MODES

Mínimo:

```text
DISABLED
ENABLED
EXTRACT
IN_PLACE
CUSTOM
```

---

# 83. ANIMATION COMPRESSION

Deberá existir:

```text
AnimationCompressionProfile
```

que controle:

```text
translation
rotation
scale
curves
key reduction
```

---

# 84. ANIMATION QUALITY VALIDATION

La compresión no deberá introducir:

```text
visible jitter
foot sliding
bone popping
timing errors
```

fuera de las tolerancias.

---

# 85. FOOT LOCK

Los personajes humanoides deberán poder utilizar:

```text
FootLockProfile
```

para reducir:

```text
foot sliding
```

durante locomoción.

---

# 86. HAND IK

Deberá poder utilizarse IK para:

```text
weapon grip
two-hand weapons
interaction
ladder
vehicle controls
```

---

# 87. TWO-HAND WEAPON SYSTEM

Deberá soportarse:

```text
primary hand
secondary hand
weapon reference
IK alignment
```

---

# 88. AIM SYSTEM

Los personajes deberán poder definir:

```text
AimProfile
```

con:

```text
spine contribution
neck contribution
head contribution
arm contribution
```

---

# 89. AIM VALIDATION

Deberán comprobarse:

```text
weapon alignment
hand alignment
look direction
joint limits
```

---

# 90. RAGDOLL SYSTEM

Deberá existir:

```text
RagdollProfile
```

---

# 91. RAGDOLL BODY GENERATION

Los cuerpos físicos podrán generarse desde:

```text
bone hierarchy
mesh dimensions
anatomical profile
```

---

# 92. RAGDOLL JOINTS

Deberán existir límites configurables por articulación.

---

# 93. RAGDOLL VALIDATION

Deberá probar:

```text
fall
impact
collapse
recovery
```

cuando corresponda.

---

# 94. PHYSICS/ANIMATION BLENDING

Deberá soportarse mezcla entre:

```text
animation
physics
partial physics
```

---

# 95. PARTIAL RAGDOLL

Deberá poder simularse únicamente:

```text
head
arms
legs
upper body
```

según perfil.

---

# 96. CHARACTER COLLISION

El personaje deberá declarar:

```text
capsule
physics
complex
custom
```

según necesidad.

---

# 97. CAPSULE VALIDATION

La cápsula de gameplay deberá comprobarse contra la geometría final.

No deberá existir una discrepancia significativa entre:

```text
visual body
collision body
movement body
```

---

# 98. CHARACTER HEIGHT

La altura deberá formar parte del metadata runtime.

---

# 99. CHARACTER WIDTH

Deberá registrarse el ancho máximo relevante para navegación y gameplay.

---

# 100. NAVIGATION PROFILE

Los personajes podrán declarar:

```text
radius
height
step_height
slope_limit
movement_mode
```

---

# 101. CHARACTER GROUNDING

Deberá comprobarse:

```text
foot contact
root height
ground offset
```

---

# 102. ANIMATION GROUND TEST

Una animación de locomoción deberá verificarse contra un plano de referencia.

---

# 103. FOOT CONTACT

Deberá detectarse automáticamente:

```text
foot penetration
foot floating
foot sliding
```

---

# 104. CHARACTER CENTER OF MASS

Deberá poder calcularse:

```text
center_of_mass
```

para física y validación.

---

# 105. CHARACTER BOUNDS

Deberán validarse:

```text
rest bounds
animation bounds
combat bounds
ragdoll bounds
```

---

# 106. ANIMATION BOUNDS

El sistema deberá detectar si una animación provoca un incremento inesperado del bounding volume.

---

# 107. PERFORMANCE

Deberán medirse:

```text
bone_count
morph_count
material_count
vertex_count
triangle_count
animation_memory
physics_body_count
```

---

# 108. BONE BUDGET

Cada perfil podrá declarar:

```text
max_bones
```

---

# 109. MORPH BUDGET

Cada perfil podrá declarar:

```text
max_morph_targets
```

---

# 110. MATERIAL BUDGET

Deberá existir un límite configurable de materiales por personaje.

---

# 111. CHARACTER PERFORMANCE SCORE

Deberá calcularse:

```text
GeometryCost
SkinningCost
AnimationCost
MorphCost
PhysicsCost
MaterialCost
```

---

# 112. ANIMATION LOD

Deberá existir:

```text
AnimationLODProfile
```

---

# 113. ANIMATION LOD STRATEGIES

Podrán reducirse:

```text
bone evaluation
facial evaluation
IK evaluation
physics
morph evaluation
```

a distancia.

---

# 114. FACIAL LOD

La evaluación facial podrá reducirse o desactivarse según distancia y perfil.

---

# 115. DISTANCE-BASED RIG COMPLEXITY

El personaje podrá pasar de:

```text
FULL
STANDARD
REDUCED
MINIMAL
```

según contexto.

---

# 116. NPC PROFILE

Los NPC deberán poder utilizar perfiles de animación más económicos que el personaje principal.

---

# 117. HERO CHARACTER PROFILE

Los personajes hero deberán disponer de mayor presupuesto para:

```text
facial
bones
morphs
materials
animation
```

---

# 118. CROWD PROFILE

Los personajes de multitudes deberán priorizar:

```text
low cost
animation sharing
instancing
reduced skeleton
reduced facial
```

---

# 119. ANIMATION SHARING

Deberá ser posible compartir animaciones entre personajes compatibles.

---

# 120. COMPATIBILITY HASH

Dos personajes podrán compartir animaciones cuando su:

```text
SkeletonCompatibilityHash
```

sea compatible.

---

# 121. SKELETON VERSIONING

Los skeletons deberán estar versionados.

---

# 122. BREAKING CHANGES

Un cambio incompatible deberá generar una nueva versión del skeleton.

---

# 123. MIGRATION

Deberá existir:

```text
SkeletonMigrationProfile
```

para cambios compatibles.

---

# 124. CHARACTER BLUEPRINT METADATA

El paquete deberá generar metadata suficiente para construir o configurar el Actor correspondiente en Unreal.

---

# 125. ANIMATION BLUEPRINT CONTRACT

Deberá existir:

```text
AnimationBlueprintContract
```

que describa:

```text
locomotion
aim
IK
states
parameters
montages
```

---

# 126. PARAMETERS

Los parámetros deberán estar tipados.

Ejemplo:

```text
Speed : float
Direction : float
IsCrouched : bool
IsAiming : bool
```

---

# 127. STATE MACHINE CONTRACT

Las máquinas de estados deberán poder declararse como:

```text
state
transition
condition
blend
```

---

# 128. MONTAGE CONTRACT

Los ataques, impactos y acciones deberán poder declararse como:

```text
MontageDefinition
```

---

# 129. ANIMATION EVENTS

Deberán soportarse eventos semánticos:

```text
footstep
attack
impact
reload
weapon_fire
death
interaction
```

---

# 130. EVENT VALIDATION

Los eventos deberán estar dentro del rango válido de la animación.

---

# 131. SOCKET VALIDATION

Durante las pruebas animadas deberá comprobarse que los sockets:

```text
mantienen posición relativa;
siguen correctamente los bones;
no sufren escalado incorrecto;
```

---

# 132. WEAPON ANIMATION TEST

Cada personaje compatible con armas deberá probar al menos:

```text
equip
aim
fire
reload
melee
```

cuando estén disponibles.

---

# 133. CHARACTER INTEGRATION TEST

Deberá existir una prueba de integración:

```text
Spawn
↓
Idle
↓
Walk
↓
Run
↓
Aim
↓
Interact
↓
Attack
↓
Hit
↓
Death
```

según el perfil.

---

# 134. AUTOMATED POSE LIBRARY

Deberá existir una biblioteca de poses de regresión.

---

# 135. POSE REGRESSION

Los cambios de geometría o skeleton deberán compararse contra las poses golden.

---

# 136. DEFORMATION REGRESSION

Los cambios deberán compararse contra:

```text
joint angles
surface deviation
volume preservation
```

---

# 137. VISUAL REGRESSION

Deberán compararse:

```text
silhouette
facial deformation
armor deformation
cloth deformation
weapon alignment
```

---

# 138. TECHNICAL REGRESSION

Deberá compararse:

```text
bone count
weight count
morph count
physics body count
animation memory
```

---

# 139. AUTOMATIC REPAIR

El sistema podrá reparar automáticamente:

```text
tiny weights
weight normalization
symmetry errors
minor bone orientation
minor socket offsets
```

siempre que el perfil lo permita.

---

# 140. REPAIR SAFETY

Toda reparación deberá registrar:

```text
before
after
operation
reason
confidence
```

---

# 141. CONFIDENCE SCORE

Las reparaciones deberán clasificarse:

```text
HIGH
MEDIUM
LOW
```

---

# 142. LOW-CONFIDENCE POLICY

Las correcciones de baja confianza deberán generar un bloqueo o revisión según perfil.

---

# 143. CHARACTER ACCEPTANCE

Un personaje únicamente será aceptado cuando:

```text
Geometry PASS
Skeleton PASS
Skin PASS
Deformation PASS
Animation PASS
Physics PASS
Runtime PASS
Performance PASS
```

según los requisitos de su perfil.

---

# 144. CHARACTER BUILD STATES

```text
SOURCE
RIGGED
SKINNED
ANIMATABLE
VALIDATED
OPTIMIZED
RUNTIME_READY
PUBLISHED
REJECTED
```

---

# 145. CHARACTER PACKAGE

La salida final deberá contener:

```text
CharacterPackage
├── Geometry
├── Skeleton
├── Skin
├── PhysicsAsset
├── MorphTargets
├── AnimationMetadata
├── IK
├── ControlRig
├── Sockets
├── Materials
├── Collision
├── LOD
├── PerformanceProfile
├── GameplayMetadata
├── ValidationReport
└── Provenance
```

---

# 146. DETERMINISM

La generación de:

```text
skeleton
weights
morphs
physics
metadata
```

deberá ser determinista.

---

# 147. REPRODUCIBILITY

El mismo input deberá generar el mismo resultado dentro de las tolerancias definidas.

---

# 148. BUILD HASH

El CharacterPackage deberá contener:

```text
source_hash
rig_profile_hash
skinning_profile_hash
animation_profile_hash
engine_profile_hash
```

---

# 149. PROVENANCE

Todo componente deberá poder rastrearse hasta su origen.

---

# 150. AUDIT

Toda modificación automática deberá quedar registrada.

---

# 151. HUMAN OVERRIDE

Deberán permitirse overrides explícitos de:

```text
bone
weight
constraint
morph
socket
animation
physics
```

---

# 152. OVERRIDE PRESERVATION

Los overrides protegidos no podrán ser destruidos por regeneraciones posteriores.

---

# 153. PARTIAL REBUILD

Si cambia únicamente:

```text
material
```

no deberá reconstruirse:

```text
skeleton
skin
animation
```

salvo dependencia explícita.

---

# 154. DEPENDENCY GRAPH

Deberá existir un grafo:

```text
Geometry
↓
Skeleton
↓
Skin
↓
Animation
↓
Runtime
```

y:

```text
Geometry
↓
Morph
```

y:

```text
Skeleton
↓
Physics
```

---

# 155. INVALIDATION

Un cambio en skeleton deberá invalidar automáticamente los componentes dependientes.

---

# 156. CACHE

Deberán poder cachearse:

```text
skeleton
weights
morphs
physics
animation retarget data
```

---

# 157. FAILURE RECOVERY

Los fallos deberán poder recuperarse sin perder outputs previamente válidos.

---

# 158. TRANSACTION

La publicación final deberá seguir:

```text
Prepare
↓
Validate
↓
Commit
```

---

# 159. REJECTION REASONS

Los rechazos deberán ser estructurados:

```text
RIG_INVALID
SKIN_INVALID
DEFORMATION_FAILURE
ANIMATION_FAILURE
PHYSICS_FAILURE
SOCKET_FAILURE
PERFORMANCE_FAILURE
UNREAL_COMPATIBILITY_FAILURE
```

---

# 160. FINAL ACCEPTANCE TEST

La fase UAF-81.9 estará completa cuando un personaje generado pueda:

```text
1. recibir un skeleton;
2. deformarse;
3. ejecutar una pose;
4. ejecutar locomoción;
5. utilizar IK;
6. utilizar FK;
7. utilizar sockets;
8. utilizar armas;
9. utilizar física;
10. utilizar ragdoll;
11. utilizar morph targets;
12. utilizar facial animation cuando corresponda;
13. recibir animaciones mediante retargeting;
14. superar pruebas de deformación;
15. superar pruebas de colisión;
16. superar pruebas de runtime;
17. respetar presupuestos;
18. generar metadata para Unreal;
19. reproducirse determinísticamente;
20. superar regresión visual y técnica;
21. ser publicado como CharacterPackage.
```

---

# 161. NON-NEGOTIABLE RULE

Un personaje no deberá considerarse:

```text
PRODUCTION_READY
```

si únicamente posee:

```text
mesh + material
```

Deberá existir como mínimo:

```text
mesh
+
skeleton
+
skin
+
deformation validation
+
runtime metadata
```

y, cuando corresponda:

```text
animation
+
physics
+
morphs
+
IK
+
sockets
```

---

# 162. NEXT PHASE

# UAF-81.10 — PROCEDURAL CHARACTER FABRICATION & HIGH-COMPLEXITY GEOMETRY

Esta fase deberá atacar directamente la limitación de la generación geométrica actual.

El objetivo será pasar de:

```text
primitive assembly
+
voxel remesh
```

a una arquitectura capaz de producir:

```text
high-detail humanoids
organic anatomy
faces
hands
feet
clothing
armor
hard-surface attachments
layered garments
mechanical assemblies
surface detail
secondary forms
tertiary detail
```

manteniendo:

```text
topology control
UV control
material regions
deformation compatibility
LOD compatibility
Nanite compatibility
determinism
```

La arquitectura deberá separar explícitamente:

```text
PRIMARY FORM
SECONDARY FORM
TERTIARY FORM
SURFACE DETAIL
DEFORMATION TOPOLOGY
RUNTIME TOPOLOGY
```

para evitar que el voxel remesh siga siendo el único mecanismo de construcción de personajes.
