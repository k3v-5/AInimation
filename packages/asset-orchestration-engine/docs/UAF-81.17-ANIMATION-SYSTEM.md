# UAF-81.17 — CHARACTER RIGGING, SKINNING & ANIMATION FABRICATION SYSTEM

## UAF-81.17-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN DE RIGS, SKINNING, ANIMACIÓN Y COMPORTAMIENTO DE PERSONAJES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.17 — Character Rigging, Skinning & Animation Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.16  
**Next Phase:** UAF-81.18  

---

# 1. PURPOSE

UAF-81.17 define el sistema responsable de convertir una malla de personaje fabricada por AOE en un personaje deformable, animable, físicamente válido y preparado para integración con Unreal Engine.

El resultado final deberá poder representar:

```text
CHARACTER
├── MESH
├── SKELETON
├── RIG
├── SKIN
├── IK
├── PHYSICS
├── ANIMATION
├── POSES
├── LOD
├── MATERIALS
├── SOCKETS
├── COLLISION
├── RETARGETING DATA
├── CONTROL RIG DATA
└── UNREAL CHARACTER PACKAGE
```

---

# 2. PRIMARY OBJECTIVE

El sistema no deberá limitarse a crear un Armature.

Deberá fabricar el conjunto completo:

```text
GEOMETRY
→ SKELETON
→ RIG
→ WEIGHTS
→ DEFORMATION
→ ANIMATION
→ PHYSICS
→ VALIDATION
→ UNREAL EXPORT
```

---

# 3. CHARACTER RIG BUILD

Deberá existir:

```text
CharacterRigBuild
```

---

# 4. CHARACTER INPUT

El sistema deberá aceptar:

```text
CharacterDefinition
CharacterMesh
AnatomicalLandmarks
StyleProfile
RigProfile
AnimationProfile
PhysicsProfile
TargetProfile
```

---

# 5. CHARACTER DEFINITION

Deberá existir:

```text
CharacterDefinition
```

con mínimo:

```text
character_id
character_type
height
scale
anatomy_profile
skeleton_profile
rig_profile
skin_profile
animation_profile
physics_profile
```

---

# 6. CHARACTER TYPES

Mínimo:

```text
HUMANOID
ROBOT
CREATURE
QUADRUPED
INSECTOID
ALIEN
CUSTOM
```

---

# 7. SKELETON SYSTEM

Deberá existir:

```text
SkeletonFabricator
```

---

# 8. SKELETON DEFINITION

Cada skeleton deberá tener:

```text
skeleton_id
root
bones
hierarchy
reference_pose
scale
axis_convention
```

---

# 9. BONE IDENTITY

Cada hueso deberá poseer un identificador estable.

---

# 10. BONE NAME

El nombre del hueso deberá cumplir la convención definida por el TargetProfile.

---

# 11. BONE ROLE

Cada hueso deberá declarar su función:

```text
ROOT
SPINE
CHEST
NECK
HEAD
CLAVICLE
UPPER_ARM
LOWER_ARM
HAND
FINGER
UPPER_LEG
LOWER_LEG
FOOT
TOE
```

---

# 12. EXTENDED BONE ROLES

El sistema deberá permitir:

```text
WEAPON
AUXILIARY
MECHANICAL
TAIL
WING
TENTACLE
ANTENNA
FACIAL
CUSTOM
```

---

# 13. BONE HIERARCHY

La jerarquía deberá ser un árbol válido.

---

# 14. HIERARCHY VALIDATION

No deberá existir:

```text
cyclic_parenting
orphan_bone
duplicate_identity
invalid_parent
```

---

# 15. ROOT BONE

Todo personaje deberá tener exactamente un root lógico.

---

# 16. REFERENCE POSE

Cada skeleton deberá poseer una reference pose explícita.

---

# 17. REFERENCE POSE CONSISTENCY

La pose deberá ser reproducible y compatible con el target de Unreal.

---

# 18. T-POSE / A-POSE

El sistema deberá soportar:

```text
T_POSE
A_POSE
CUSTOM_REFERENCE_POSE
```

---

# 19. LANDMARK TO BONE MAPPING

Las landmarks anatómicas deberán poder mapearse a huesos.

Ejemplo:

```text
pelvis
→ pelvis

chest_core
→ spine/chest

elbow_L
→ lower_arm_L

knee_L
→ lower_leg_L
```

---

# 20. AUTOMATIC SKELETON GENERATION

El skeleton deberá poder generarse automáticamente cuando exista suficiente información anatómica.

---

# 21. MANUAL OVERRIDES

El usuario deberá poder sobrescribir:

```text
bone_position
bone_rotation
bone_parent
bone_length
bone_role
```

---

# 22. SKELETON TEMPLATE

Deberán existir templates reutilizables.

Mínimo:

```text
HUMANOID_STANDARD
HUMANOID_MILITARY
ROBOT_HUMANOID
CREATURE_BIPED
QUADRUPED_STANDARD
CUSTOM
```

---

# 23. SKELETON TEMPLATE VERSIONING

Cada template deberá tener versión.

---

# 24. SKELETON COMPATIBILITY

Dos personajes serán skeleton-compatible únicamente si cumplen el SkeletonCompatibilityProfile.

---

# 25. IK SYSTEM

Deberá existir:

```text
IKFabricator
```

---

# 26. IK CHAINS

Mínimo:

```text
LEFT_ARM
RIGHT_ARM
LEFT_LEG
RIGHT_LEG
SPINE
```

---

# 27. IK END EFFECTORS

Mínimo:

```text
hand_L
hand_R
foot_L
foot_R
```

---

# 28. IK SOLVERS

Deberán soportarse al menos:

```text
CCD
FABRIK
TWO_BONE
```

---

# 29. FOOT IK

Deberá existir soporte para:

```text
foot_placement
ground_alignment
step_height
foot_rotation
```

---

# 30. HAND IK

Deberá existir soporte para:

```text
weapon_grip
object_grip
interaction
```

---

# 31. LOOK-AT IK

Deberá existir soporte para:

```text
head
eyes
upper_body
```

---

# 32. AIM IK

Deberá existir soporte para apuntado.

---

# 33. IK LIMITS

Cada solver deberá respetar:

```text
joint_limits
rotation_limits
translation_limits
```

---

# 34. DEFORMATION SYSTEM

Deberá existir:

```text
DeformationFabricator
```

---

# 35. SKINNING

La malla deberá poder asociarse al skeleton mediante skinning.

---

# 36. WEIGHT GENERATION

Deberá existir:

```text
WeightGenerationSystem
```

---

# 37. WEIGHT SOURCES

Los pesos podrán derivarse de:

```text
bone_distance
voxel_influence
geodesic_distance
heat_method
surface_proximity
landmark_regions
manual_masks
```

---

# 38. WEIGHT GENERATION PIPELINE

Mínimo:

```text
INITIAL_WEIGHTS
→ NORMALIZE
→ SMOOTH
→ LIMIT
→ CLEAN
→ VALIDATE
```

---

# 39. WEIGHT NORMALIZATION

La suma de pesos de cada vértice deberá cumplir:

```text
sum(weights) ≈ 1.0
```

dentro de la tolerancia definida.

---

# 40. MAX INFLUENCES

El TargetProfile deberá definir el número máximo de influencias por vértice.

---

# 41. INFLUENCE PRUNING

Las influencias inferiores al threshold podrán eliminarse.

---

# 42. WEIGHT SMOOTHING

El sistema deberá suavizar transiciones sin destruir límites anatómicos.

---

# 43. WEIGHT PRESERVATION

Los joints mecánicos o rígidos deberán poder utilizar weighting rígido.

---

# 44. RIGID DEFORMATION

Robots y piezas mecánicas deberán soportar:

```text
RIGID
NEAR_RIGID
DEFORMABLE
```

---

# 45. WEIGHT MASKS

Deberán existir máscaras:

```text
ALLOW
DENY
MANDATORY
PREFERRED
```

---

# 46. WEIGHT PAINT VALIDATION

Deberá detectar:

```text
unweighted_vertices
overweighted_vertices
invalid_influences
isolated_weights
weight_spikes
```

---

# 47. DEFORMATION TESTS

El sistema deberá deformar el personaje mediante poses de prueba.

---

# 48. TEST POSES

Mínimo:

```text
REFERENCE
ARM_RAISE
ARM_BEND
ELBOW_BEND
LEG_RAISE
KNEE_BEND
SQUAT
CROUCH
WALK
EXTREME_POSE
```

---

# 49. DEFORMATION ERROR DETECTION

Deberá detectar:

```text
self_intersection
collapse
stretching
volume_loss
volume_explosion
detached_geometry
```

---

# 50. DEFORMATION METRICS

Deberán medirse:

```text
maximum_displacement
volume_change
surface_intersection
joint_error
```

---

# 51. AUTO-CORRECTION

Cuando sea posible, los errores de weighting deberán corregirse automáticamente.

---

# 52. CORRECTION LIMIT

Las correcciones automáticas deberán tener un presupuesto máximo.

---

# 53. NO SILENT CORRECTION

Toda corrección automática deberá registrarse en OperationLog.

---

# 54. RIG SYSTEM

Deberá existir:

```text
RigFabricator
```

---

# 55. CONTROL RIG

Deberá poder generarse un sistema de controles.

---

# 56. CONTROL TYPES

Mínimo:

```text
FK
IK
SPACE_SWITCH
PARENT
AIM
```

---

# 57. CONTROL NAMING

Los controles deberán tener nombres estables.

---

# 58. CONTROL HIERARCHY

La jerarquía de controles no deberá confundirse con la jerarquía de deformación.

---

# 59. RIG SPACE

Deberán existir espacios:

```text
WORLD
CHARACTER
LOCAL
PARENT
```

---

# 60. RIG VALIDATION

Deberá comprobar:

```text
cycles
broken_constraints
invalid_targets
missing_controls
```

---

# 61. SOCKET SYSTEM

Deberá existir:

```text
SocketFabricator
```

---

# 62. STANDARD SOCKETS

Mínimo:

```text
weapon_hand_L
weapon_hand_R
back
head
helmet
muzzle
```

cuando corresponda.

---

# 63. SOCKET ORIENTATION

Cada socket deberá tener orientación determinista.

---

# 64. SOCKET VALIDATION

Deberá comprobar:

```text
parent
position
rotation
scale
```

---

# 65. ANIMATION SYSTEM

Deberá existir:

```text
AnimationFabricator
```

---

# 66. ANIMATION DEFINITION

Mínimo:

```text
animation_id
type
skeleton
duration
fps
root_motion
loop
source
```

---

# 67. ANIMATION TYPES

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
TURN
ATTACK
HIT
DEATH
INTERACT
AIM
RELOAD
CUSTOM
```

---

# 68. PROCEDURAL ANIMATION

El sistema deberá poder fabricar animaciones mediante reglas y keyframes generados.

---

# 69. KEYFRAME GENERATION

Los keyframes deberán poder generarse desde:

```text
poses
IK_targets
curves
motion_profiles
```

---

# 70. MOTION PROFILE

Deberá existir:

```text
MotionProfile
```

---

# 71. MOTION PARAMETERS

Mínimo:

```text
speed
stride_length
step_height
cadence
body_bob
arm_swing
```

---

# 72. LOCOMOTION SYSTEM

Deberá existir:

```text
LocomotionFabricator
```

---

# 73. LOCOMOTION SPEEDS

Mínimo:

```text
idle
walk
jog
run
sprint
```

---

# 74. LOCOMOTION DIRECTION

Deberá soportarse:

```text
forward
backward
left
right
diagonal
```

---

# 75. TURNING

Deberán existir animaciones o procedimientos para:

```text
turn_left
turn_right
pivot
```

---

# 76. STRIDE CONSISTENCY

La longitud de paso deberá ser coherente con la escala del personaje.

---

# 77. ROOT MOTION

Deberá soportarse:

```text
ROOT_MOTION
IN_PLACE
HYBRID
```

---

# 78. ROOT MOTION VALIDATION

Deberá comprobarse que la trayectoria de root coincide con el movimiento esperado.

---

# 79. ANIMATION LOOP VALIDATION

Las animaciones loop deberán evitar saltos perceptibles en la transición.

---

# 80. ANIMATION CURVE VALIDATION

Deberán detectarse:

```text
discontinuities
spikes
invalid_values
```

---

# 81. ANIMATION RETARGETING

Deberá existir:

```text
RetargetProfile
```

---

# 82. RETARGET SOURCE

Deberá poder definirse:

```text
source_skeleton
```

---

# 83. RETARGET TARGET

Deberá poder definirse:

```text
target_skeleton
```

---

# 84. RETARGET MAPPING

El sistema deberá generar:

```text
bone_mapping
translation_rules
rotation_rules
scale_rules
```

---

# 85. RETARGET VALIDATION

Deberá comprobar:

```text
missing_bones
unexpected_bones
scale_mismatch
axis_mismatch
```

---

# 86. RETARGET POSE CORRECTION

Deberán existir offsets de corrección.

---

# 87. RETARGET TEST

Deberá ejecutarse al menos una animación de referencia sobre el target.

---

# 88. ANIMATION VARIANTS

El sistema deberá poder fabricar variantes.

---

# 89. VARIANT PARAMETERS

Mínimo:

```text
speed
aggression
weight
amplitude
style
```

---

# 90. CHARACTER PERSONALITY

Deberá poder expresarse mediante:

```text
MotionStyle
```

---

# 91. MOTION STYLES

Mínimo:

```text
MILITARY
HEAVY
LIGHT
ROBOTIC
ALIEN
INJURED
AGGRESSIVE
STEALTH
CUSTOM
```

---

# 92. PROCEDURAL MOTION MODULATION

Las variaciones deberán conservar restricciones anatómicas.

---

# 93. FACIAL SYSTEM

Cuando el personaje posea rostro deformable deberá existir:

```text
FacialRigFabricator
```

---

# 94. FACIAL METHODS

Deberán soportarse:

```text
BONE
BLENDSHAPE
MORPH_TARGET
HYBRID
```

---

# 95. FACIAL TARGETS

Mínimo:

```text
blink
jaw_open
jaw_left
jaw_right
brow_up
brow_down
mouth_open
```

cuando la anatomía lo permita.

---

# 96. FACIAL VALIDATION

Los morph targets deberán comprobar:

```text
range
naming
compatibility
self_intersection
```

---

# 97. CLOTH SYSTEM

Deberá existir integración con cloth simulation.

---

# 98. CLOTH CATEGORIES

Mínimo:

```text
CLOTHING
CAPE
COAT
STRAP
BAG
SOFT_ARMOR
CUSTOM
```

---

# 99. CLOTH ATTACHMENT

Las prendas deberán poder asociarse al skeleton.

---

# 100. CLOTH WEIGHT MAPS

Deberán generarse o importarse mapas de:

```text
max_distance
backstop
tether
```

cuando sean requeridos por el pipeline.

---

# 101. CLOTH COLLISION

Deberá existir configuración automática de collision bodies.

---

# 102. CLOTH VALIDATION

Deberá detectar:

```text
explosion
penetration
unbounded_vertices
invalid_constraints
```

---

# 103. PHYSICS SYSTEM

Deberá existir:

```text
PhysicsAssetFabricator
```

---

# 104. PHYSICS BODIES

Deberán poder generarse cuerpos para:

```text
head
torso
pelvis
upper_arm
lower_arm
hand
upper_leg
lower_leg
foot
```

según el personaje.

---

# 105. COLLISION SHAPES

Mínimo:

```text
BOX
SPHERE
CAPSULE
CONVEX
```

---

# 106. PHYSICS SIMPLIFICATION

El sistema deberá minimizar el número de cuerpos manteniendo fidelidad suficiente.

---

# 107. PHYSICS CONSTRAINTS

Deberán definirse:

```text
swing_limit
twist_limit
angular_limit
linear_limit
```

cuando corresponda.

---

# 108. RAGDOLL

Deberá existir perfil:

```text
RagdollProfile
```

---

# 109. RAGDOLL VALIDATION

Deberá ejecutarse una simulación de prueba.

---

# 110. RAGDOLL FAILURE

Deberá detectar:

```text
explosion
unstable_body
penetration
detached_body
unrealistic_constraint
```

---

# 111. CHARACTER COLLISION

El personaje deberá poseer una estrategia de collision separada de la malla renderizable.

---

# 112. CAPSULE COMPATIBILITY

Los personajes deberán mantener compatibilidad con las reglas de cápsula definidas por AOE.

---

# 113. SCALE VALIDATION

El sistema deberá verificar:

```text
height
width
limb_length
head_size
foot_size
```

contra el CharacterProfile.

---

# 114. ANATOMICAL VALIDATION

Los joints deberán respetar rangos anatómicos o mecánicos definidos.

---

# 115. ROBOT DEFORMATION MODE

Los robots podrán utilizar sistemas de deformación diferentes de los orgánicos.

---

# 116. ROBOT JOINTS

Deberán poder definirse joints:

```text
HINGE
BALL
SLIDER
ROTATIONAL
CUSTOM
```

---

# 117. MECHANICAL RIG

El sistema deberá permitir rigs mecánicos sin skinning tradicional.

---

# 118. HYBRID CHARACTERS

Deberá soportarse combinación:

```text
RIGID
SKINNED
CLOTH
PHYSICS
```

en un mismo personaje.

---

# 119. ATTACHMENT SYSTEM

Armaduras, armas y accesorios deberán poder asociarse a sockets o huesos.

---

# 120. EQUIPMENT SOCKETS

Deberán existir perfiles para:

```text
weapon
shield
helmet
backpack
shoulder
chest
utility
```

---

# 121. EQUIPMENT VALIDATION

Deberá comprobarse:

```text
socket_alignment
collision
clearance
scale
```

---

# 122. CHARACTER VARIANT SYSTEM

Deberá existir:

```text
CharacterVariantFabricator
```

---

# 123. VARIANT AXES

Mínimo:

```text
height
width
proportion
armor
equipment
material
color
damage
```

---

# 124. SKELETON PRESERVATION

Las variantes deberán conservar el skeleton cuando sea compatible.

---

# 125. ANIMATION COMPATIBILITY

El sistema deberá determinar automáticamente si una variante mantiene compatibilidad con las animaciones existentes.

---

# 126. CHARACTER LOD

Deberán existir LODs específicos para personajes.

---

# 127. LOD LEVELS

Mínimo:

```text
LOD0
LOD1
LOD2
LOD3
LOD4
```

cuando el target lo requiera.

---

# 128. LOD DEFORMATION

Cada LOD deberá conservar una deformación aceptable.

---

# 129. LOD SKINNING

Los LODs deberán conservar o transformar correctamente las influencias del skeleton.

---

# 130. ANIMATION LOD

Deberá existir reducción de coste de animación según distancia.

---

# 131. BONE REDUCTION

Los huesos no críticos podrán eliminarse en LODs compatibles.

---

# 132. BONE RETENTION

Los huesos necesarios para gameplay no deberán eliminarse.

---

# 133. MATERIAL DEFORMATION

Los materiales deberán continuar funcionando bajo deformación.

---

# 134. NORMAL VALIDATION

Deberán comprobarse normales después del skinning y LOD.

---

# 135. TANGENT VALIDATION

Deberán comprobarse tangentes.

---

# 136. EXPORT SKELETON

El skeleton exportado deberá ser estable.

---

# 137. EXPORT FBX

Cuando FBX sea el formato objetivo, deberá existir una política explícita de exportación.

---

# 138. EXPORT GLTF

Cuando corresponda, podrá existir soporte glTF.

---

# 139. UNREAL SKELETON COMPATIBILITY

El paquete deberá declarar explícitamente su skeleton target.

---

# 140. CONTROL RIG INTEGRATION

Deberá existir metadata suficiente para construir o reconstruir Control Rig en Unreal.

---

# 141. ANIMATION BLUEPRINT DATA

Deberán generarse datos suficientes para configurar:

```text
locomotion
state_machine
blend_spaces
aim
IK
```

---

# 142. BLEND SPACE SUPPORT

Deberán definirse parámetros:

```text
speed
direction
```

como mínimo para locomoción multidireccional.

---

# 143. STATE MACHINE

Deberán definirse estados:

```text
IDLE
LOCOMOTION
JUMP
FALL
ATTACK
HIT
DEATH
```

según el CharacterProfile.

---

# 144. TRANSITION RULES

Las transiciones deberán tener condiciones explícitas.

---

# 145. ANIMATION NOTIFY

Deberán poder definirse eventos:

```text
footstep
attack_window
weapon_fire
reload
impact
effect
sound
```

---

# 146. NOTIFY VALIDATION

No deberán existir notifies fuera del rango temporal de la animación.

---

# 147. FOOTSTEP SYSTEM

Las pisadas deberán poder asociarse al tipo de superficie.

---

# 148. SURFACE RESPONSE

Deberá poder mapearse:

```text
surface_type
→ footstep_set
```

---

# 149. DAMAGE REACTIONS

Deberá existir un sistema de reacciones.

---

# 150. HIT REACTION ZONES

Mínimo:

```text
HEAD
CHEST
ARM
LEG
CUSTOM
```

---

# 151. DEATH VARIANTS

Deberán existir variantes según:

```text
direction
damage_type
physics_mode
```

cuando corresponda.

---

# 152. CHARACTER BEHAVIOR PROFILE

Deberá existir:

```text
CharacterBehaviorProfile
```

---

# 153. BEHAVIOR SCOPE

Esta fase no deberá implementar la lógica completa de gameplay, pero deberá exportar información necesaria para:

```text
movement
animation
IK
equipment
physical reactions
```

---

# 154. CHARACTER PACKAGE

Deberá existir:

```text
CharacterPackage
```

---

# 155. PACKAGE CONTENT

Mínimo:

```text
mesh
skeleton
rig
skin
physics
animations
poses
materials
textures
sockets
lods
metadata
validation_report
```

---

# 156. CHARACTER MANIFEST

Deberá existir:

```text
CharacterBuildManifest
```

---

# 157. MANIFEST DEPENDENCIES

Deberá registrar:

```text
source_mesh
skeleton_profile
rig_profile
animation_profile
physics_profile
material_profile
target_profile
```

---

# 158. BUILD CACHE

Rig, skinning y animaciones deberán soportar cache incremental.

---

# 159. CACHE INVALIDATION

Modificar materiales no deberá reconstruir skeleton o animation.

---

# 160. SKELETON CACHE

Si la anatomía y skeleton profile no cambian, el skeleton deberá reutilizarse.

---

# 161. WEIGHT CACHE

Si skeleton y topology no cambian, los weights deberán reutilizarse.

---

# 162. ANIMATION CACHE

Si skeleton compatibility no cambia, las animaciones compatibles deberán reutilizarse.

---

# 163. PARALLEL FABRICATION

Personajes independientes deberán poder fabricarse en paralelo.

---

# 164. FAILURE RECOVERY

El fallo de una animación no deberá destruir el mesh ni el skeleton válidos.

---

# 165. CHECKPOINTS

Mínimo:

```text
MESH_IMPORTED
SKELETON_CREATED
RIG_CREATED
WEIGHTS_CREATED
DEFORMATION_VALIDATED
PHYSICS_CREATED
ANIMATION_CREATED
RETARGET_VALIDATED
LOD_CREATED
EXPORT_VALIDATED
```

---

# 166. CHARACTER VALIDATOR

Deberá existir:

```text
CharacterValidator
```

---

# 167. SKELETON VALIDATION

Debe validar:

```text
hierarchy
names
roles
reference_pose
scale
```

---

# 168. SKIN VALIDATION

Debe validar:

```text
weights
influences
unweighted_vertices
deformation
```

---

# 169. RIG VALIDATION

Debe validar:

```text
constraints
IK
controls
spaces
```

---

# 170. ANIMATION VALIDATION

Debe validar:

```text
duration
fps
curves
root_motion
loop
bone_targets
```

---

# 171. PHYSICS VALIDATION

Debe validar:

```text
bodies
constraints
collision
ragdoll
```

---

# 172. UNREAL VALIDATION

Debe validar:

```text
skeleton_compatibility
socket_integrity
LOD_integrity
animation_compatibility
collision_profile
```

---

# 173. VISUAL CHARACTER QA

Deberán generarse vistas:

```text
FRONT
BACK
SIDE
REFERENCE
POSE
DEFORMATION
RAGDOLL
```

---

# 174. DEFORMATION QA

Las poses extremas deberán renderizarse automáticamente para inspección.

---

# 175. ANIMATION QA

Deberán generarse previews de:

```text
idle
walk
run
attack
death
```

como mínimo cuando estén definidos.

---

# 176. AUTOMATED CHARACTER METRICS

Mínimo:

```text
bone_count
vertex_count
triangle_count
influence_count
animation_count
animation_duration
physics_body_count
LOD_count
```

---

# 177. PERFORMANCE METRICS

Deberá medirse:

```text
skinning_cost
bone_cost
animation_cost
physics_cost
memory_cost
```

---

# 178. CHARACTER BUDGETS

El TargetProfile deberá definir:

```text
max_bones
max_influences
max_triangles
max_material_slots
max_physics_bodies
max_animation_cost
```

---

# 179. BUDGET ENFORCEMENT

Superar un presupuesto crítico deberá bloquear publicación.

---

# 180. AUTO OPTIMIZATION

Deberán existir optimizaciones automáticas cuando sean seguras:

```text
bone_pruning
weight_pruning
LOD_generation
physics_simplification
curve_reduction
```

---

# 181. OPTIMIZATION SAFETY

Ninguna optimización deberá modificar silenciosamente la semántica del personaje.

---

# 182. ANIMATION CURVE REDUCTION

Las curvas podrán simplificarse dentro de una tolerancia configurable.

---

# 183. POSE ERROR TOLERANCE

Cada reducción deberá tener un error máximo permitido.

---

# 184. RETARGET REGRESSION

Los cambios del skeleton deberán probarse contra animaciones golden.

---

# 185. GOLDEN CHARACTER

Deberá existir al menos un personaje golden humanoide.

---

# 186. GOLDEN ROBOT

Deberá existir al menos un robot golden.

---

# 187. GOLDEN CREATURE

Deberá existir al menos una criatura golden.

---

# 188. GOLDEN TESTS

Cada uno deberá probar:

```text
rig
skin
IK
animation
physics
LOD
export
```

---

# 189. DETERMINISM

Los procesos proceduralmente aleatorios deberán utilizar RNG determinista.

---

# 190. REPRODUCIBILITY

El mismo:

```text
CharacterDefinition
+
MeshVersion
+
RigProfile
+
AnimationProfile
+
GeneratorVersion
```

deberá producir resultados equivalentes.

---

# 191. AUDIT

Cada build deberá registrar:

```text
character_id
seed
generator_version
profiles
inputs
outputs
corrections
warnings
errors
```

---

# 192. SECURITY

El sistema deberá respetar:

```text
PermissionFirewall
ScopeFirewall
MutationTransaction
OperationLog
```

---

# 193. MODIFICATION SCOPE

Un CharacterBuildJob deberá declarar los recursos que puede modificar.

---

# 194. NO OUT-OF-SCOPE MUTATION

No podrá modificar assets externos al scope.

---

# 195. CHARACTER BUILD JOB

Deberá existir:

```text
CharacterBuildJob
```

---

# 196. BUILD PIPELINE

Mínimo:

```text
DEFINE
→ ANALYZE_MESH
→ CREATE_SKELETON
→ CREATE_RIG
→ GENERATE_WEIGHTS
→ VALIDATE_DEFORMATION
→ CREATE_PHYSICS
→ CREATE_ANIMATION
→ CREATE_IK
→ CREATE_LODS
→ VALIDATE
→ EXPORT
```

---

# 197. MESH ANALYSIS

Antes del rigging deberán analizarse:

```text
topology
symmetry
scale
landmarks
surface_regions
material_regions
```

---

# 198. MESH TOPOLOGY REQUIREMENT

El sistema deberá determinar si la topología existente es apta para deformación.

---

# 199. TOPOLOGY FAILURE

Si la malla no es apta para skinning, deberá producir:

```text
RIGGING_TOPOLOGY_UNSUITABLE
```

y proporcionar diagnóstico.

---

# 200. AUTO REMESH POLICY

El remesh automático sólo podrá ejecutarse si está permitido por el CharacterProfile.

---

# 201. REMESH SAFETY

El remesh no deberá destruir:

```text
UV
material_regions
landmarks
critical topology
```

sin una estrategia explícita de reconstrucción.

---

# 202. EDGE FLOW

Para personajes deformables deberá analizarse el flujo alrededor de:

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

cuando existan.

---

# 203. DEFORMATION-AWARE TOPOLOGY

El sistema deberá poder recomendar o generar topología orientada a deformación.

---

# 204. CHARACTER CLOTHING LAYERS

La ropa deberá poder existir como capas:

```text
BODY
UNDER_CLOTHING
CLOTHING
ARMOR
ACCESSORY
```

---

# 205. CLOTHING ATTACHMENT

Cada capa deberá declarar si:

```text
SKINNED
RIGID
CLOTH
```

---

# 206. ARMOR SYSTEM

Las piezas rígidas deberán poder seguir huesos sin deformación.

---

# 207. ARMOR CLEARANCE

Deberá verificarse que las piezas no atraviesen el cuerpo durante poses críticas.

---

# 208. CLOTHING DEFORMATION TEST

Las prendas deberán probarse en las mismas poses críticas que el cuerpo.

---

# 209. CHARACTER MATERIAL CONSISTENCY

La deformación no deberá alterar incorrectamente:

```text
UV
tangent_space
material_assignment
```

---

# 210. MULTI-MESH CHARACTER

El personaje podrá estar compuesto por múltiples skeletal meshes.

---

# 211. MESH RELATIONSHIP

Cada submesh deberá declarar:

```text
skeleton
attachment
material
LOD_policy
collision_policy
```

---

# 212. MERGE POLICY

El sistema deberá decidir si los submeshes:

```text
remain_separate
merge
merge_by_material
merge_by_skeleton
```

---

# 213. CHARACTER EXPORT STRUCTURE

El paquete deberá poder producir:

```text
Character/
├── Mesh/
├── Skeleton/
├── Rig/
├── Animation/
├── Physics/
├── Materials/
├── Textures/
├── LOD/
├── Metadata/
└── Validation/
```

---

# 214. FINAL QUALITY GATE

Un personaje sólo podrá publicarse si supera:

```text
GEOMETRY
SCALE
SKELETON
RIG
SKIN
DEFORMATION
IK
PHYSICS
ANIMATION
LOD
MATERIAL
SOCKET
UNREAL
PERFORMANCE
```

---

# 215. REJECTION CONDITIONS

Debe rechazarse el personaje si existe:

```text
invalid_skeleton
unweighted_vertices
catastrophic_deformation
broken_ik
unstable_physics
invalid_animation
invalid_socket
budget_violation
export_failure
```

---

# 216. ARTISTIC REJECTION

También podrá rechazarse por:

```text
poor_deformation
poor_silhouette
unnatural_motion
bad_proportions
visible_clipping
poor_material_behavior
```

---

# 217. FINAL ACCEPTANCE TEST

La fase será considerada operativa cuando AOE pueda recibir un personaje procedural y producir automáticamente:

```text
1 VALID SKELETON
1 VALID RIG
1 VALID SKIN
1 VALID PHYSICS ASSET
1 VALID IK CONFIGURATION
1 IDLE
1 WALK
1 RUN
1 ATTACK
1 DEATH
1 LOD CHAIN
1 EXPORT PACKAGE
```

sin intervención manual obligatoria en el flujo estándar.

---

# 218. PROFESSIONAL CHARACTER ACCEPTANCE

El resultado deberá poder entrar al pipeline de producción sin requerir reconstrucción manual de:

```text
skeleton
weights
rig
physics
basic locomotion
basic animation
LOD
sockets
```

---

# 219. FINAL ARCHITECTURE

La arquitectura resultante será:

```text
                    CHARACTER DEFINITION
                            │
                            ▼
                     MESH ANALYSIS
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
      ANATOMICAL DATA                TOPOLOGY DATA
             │                             │
             └──────────────┬──────────────┘
                            ▼
                    SKELETON FABRICATOR
                            │
                            ▼
                     RIG FABRICATOR
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       IK FABRICATOR                 SOCKET FABRICATOR
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  WEIGHT GENERATION
                            │
                            ▼
                  DEFORMATION VALIDATION
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
      PHYSICS FABRICATOR             CLOTH FABRICATOR
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  ANIMATION FABRICATOR
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        LOCOMOTION       COMBAT        FACIAL
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                       RETARGETING
                            │
                            ▼
                          LODS
                            │
                            ▼
                       VALIDATION
                            │
                            ▼
                    UNREAL PACKAGE
```

---

# 220. RELATIONSHIP WITH PREVIOUS SYSTEMS

UAF-81.17 deberá consumir:

```text
UAF-81.01–81.15
```

especialmente:

```text
AssetSchema
SemanticAssetGraph
AssetLibrary
SpecificationCompiler
GenerationStrategyEngine
ProductionOrchestrator
BlenderCapabilityAPI
Diagnostics
Optimization
```

---

# 221. RELATIONSHIP WITH UAF-81.16

Los personajes podrán ser instanciados dentro de:

```text
WorldDefinition
WorldGraph
GameplayZone
SpawnPoint
CombatZone
BossArena
```

de UAF-81.16.

---

# 222. NEXT PHASE

La siguiente fase será:

```text
UAF-81.18 — PROCEDURAL TEXTURE, MATERIAL & SURFACE FABRICATION SYSTEM
```

Su objetivo será resolver la siguiente capa crítica:

```text
GEOMETRY
+
RIG
+
ANIMATION
↓
SURFACE
```

y deberá cubrir:

```text
TEXTURE GENERATION
PBR
ALBEDO
NORMAL
ROUGHNESS
METALLIC
AO
HEIGHT
MASKS
DECALS
TRIMS
TILEABLE MATERIALS
UNIQUE MATERIALS
PROCEDURAL MATERIALS
WEAR
DAMAGE
DIRT
RUST
WETNESS
SNOW
SKIN
FABRIC
METAL
STONE
CONCRETE
WOOD
GLASS
ALIEN SURFACES
MATERIAL INSTANCING
UDIM
VIRTUAL TEXTURES
TEXTURE MEMORY BUDGET
UNREAL MATERIALS
```
