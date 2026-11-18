# UAF-81.21 — PROCEDURAL CHARACTER, CREATURE & DEFORMATION FABRICATION SYSTEM

## UAF-81.21-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE PERSONAJES, CRIATURAS, ROPA, ARMADURA, RIGGING Y DEFORMACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.21 — Procedural Character, Creature & Deformation Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.20  
**Next Phase:** UAF-81.22  

---

# 1. PURPOSE

UAF-81.21 establece el sistema completo para fabricar personajes y criaturas 3D de producción destinados a Unreal Engine.

La fase deberá resolver simultáneamente:

```text
ANATOMY
BODY PROPORTIONS
FACE
HANDS
FEET
HAIR
CLOTHING
ARMOR
ACCESSORIES
MODULAR EQUIPMENT
HIGH POLY
MID POLY
LOW POLY
UV
MATERIALS
TEXTURES
SKELETON
RIG
SKINNING
WEIGHTS
DEFORMATION
LOD
COLLISION
SOCKETS
EXPORT
VALIDATION
```

---

# 2. FUNDAMENTAL DESIGN PRINCIPLE

El sistema no deberá considerar un personaje como una única malla.

Un personaje deberá representarse como:

```text
Character
├── Identity
├── Anatomy
├── Head
├── Face
├── Eyes
├── Mouth
├── Teeth
├── Tongue
├── Hair
├── Body
├── Hands
├── Feet
├── Clothing
├── Armor
├── Accessories
├── Equipment
├── Skeleton
├── Rig
├── Skinning
├── Materials
├── Textures
├── MorphTargets
├── LODs
├── Collision
├── Sockets
└── UnrealMetadata
```

---

# 3. CHARACTER DEFINITION

Deberá existir:

```text
CharacterDefinition
```

con:

```text
character_id
character_class
species
sex_profile
age_profile
height
mass
proportions
anatomy_profile
face_profile
hair_profile
clothing_profile
armor_profile
equipment_profile
material_profile
rig_profile
animation_profile
lod_profile
collision_profile
style_profile
seed
```

---

# 4. CHARACTER IDENTITY

La identidad del personaje deberá ser independiente de su geometría concreta.

Deberá existir:

```text
CharacterIdentity
```

Mínimo:

```text
identity_id
silhouette_profile
proportion_profile
facial_profile
color_profile
equipment_profile
style_profile
```

---

# 5. DETERMINISTIC CHARACTER GENERATION

La generación deberá depender de una semilla explícita.

Entrada:

```text
CharacterDefinition
+
Seed
+
GeneratorVersion
```

Salida:

```text
IdenticalCharacterBuild
```

---

# 6. RANDOM STREAM ISOLATION

Deberán existir streams independientes:

```text
body_seed
face_seed
hair_seed
clothing_seed
armor_seed
material_seed
texture_seed
equipment_seed
```

Cambiar cabello no deberá alterar anatomía.

---

# 7. ANATOMY SYSTEM

Deberá existir:

```text
AnatomyFabricator
```

---

# 8. ANATOMY REPRESENTATION

La anatomía deberá utilizar landmarks semánticos.

Mínimo:

```text
root
pelvis
spine
chest
neck
head
clavicle_L
clavicle_R
upper_arm_L
upper_arm_R
lower_arm_L
lower_arm_R
hand_L
hand_R
upper_leg_L
upper_leg_R
lower_leg_L
lower_leg_R
foot_L
foot_R
```

---

# 9. BODY PARAMETERS

Mínimo:

```text
height
shoulder_width
chest_width
waist_width
hip_width
arm_length
leg_length
neck_length
head_size
hand_size
foot_size
```

---

# 10. PROPORTION MODEL

Las proporciones deberán poder variar sin romper:

```text
skeleton
clothing
armor
equipment
collision
capsule
```

---

# 11. PROPORTION CONSTRAINTS

Deberán existir límites:

```text
minimum_height
maximum_height
minimum_limb_length
maximum_limb_length
minimum_joint_clearance
```

---

# 12. ANATOMICAL CONSISTENCY

El sistema deberá rechazar configuraciones anatómicas imposibles.

Ejemplos:

```text
elbow_above_shoulder_without_profile
knee_inside_pelvis
hand_inside_torso
foot_inverted_without_profile
```

---

# 13. BODY GENERATION STRATEGY

El sistema deberá soportar múltiples estrategias:

```text
PRIMITIVE
MODULAR_MESH
PARAMETRIC_MESH
HYBRID
CUSTOM
```

---

# 14. HYBRID GENERATION

La estrategia recomendada será:

```text
PARAMETRIC_BASE
+
MODULAR_PARTS
+
SURFACE_RECONSTRUCTION
+
DETAIL_LAYERS
```

---

# 15. BASE BODY

El cuerpo base deberá fabricarse independientemente de la ropa.

---

# 16. BODY TOPOLOGY

La topología deberá ser compatible con deformación.

Deberá priorizar:

```text
joint_loops
shoulder_loops
elbow_loops
knee_loops
hip_loops
wrist_loops
neck_loops
facial_loops
```

---

# 17. TOPOLOGY QUALITY

No se aceptará únicamente una métrica de polygon count.

Deberán evaluarse:

```text
edge_flow
pole_distribution
joint_density
surface_continuity
non_manifold
degenerate_faces
```

---

# 18. MODULAR BODY PARTS

Deberá existir:

```text
BodyPartLibrary
```

---

# 19. BODY PART TYPES

Mínimo:

```text
HEAD
TORSO
PELVIS
UPPER_ARM
LOWER_ARM
HAND
UPPER_LEG
LOWER_LEG
FOOT
```

---

# 20. PART COMPATIBILITY

Cada pieza deberá declarar:

```text
attachment_points
compatible_species
compatible_skeleton
compatible_scale
compatible_style
```

---

# 21. PART ATTACHMENT

Las piezas deberán conectarse mediante:

```text
semantic_attachment
socket_attachment
topology_bridge
surface_wrap
```

---

# 22. SEAM MANAGEMENT

Las uniones no deberán producir:

```text
visible_gap
intersection
z_fighting
non_manifold_connection
```

---

# 23. HEAD SYSTEM

Deberá existir:

```text
HeadFabricator
```

---

# 24. FACE SYSTEM

Deberá existir:

```text
FaceFabricator
```

---

# 25. FACIAL PARAMETERS

Mínimo:

```text
jaw_width
jaw_height
cheek_width
brow_height
eye_spacing
eye_size
nose_width
nose_length
mouth_width
lip_volume
chin_height
```

---

# 26. FACIAL LANDMARKS

Mínimo:

```text
eye_L
eye_R
brow_L
brow_R
nose
mouth
jaw
chin
ear_L
ear_R
```

---

# 27. FACIAL TOPOLOGY

El rostro deberá soportar deformaciones de:

```text
blink
smile
frown
jaw_open
jaw_close
brow_raise
brow_lower
squint
```

---

# 28. MORPH TARGET SYSTEM

Deberá existir:

```text
MorphTargetFabricator
```

---

# 29. MORPH TARGET TYPES

Mínimo:

```text
FACIAL
CORRECTIVE
BODY
CLOTHING
CUSTOM
```

---

# 30. CORRECTIVE MORPHS

Deberán poder corregir deformaciones provocadas por:

```text
elbow
knee
shoulder
hip
wrist
neck
```

---

# 31. EYE SYSTEM

Deberá existir:

```text
EyeAssembly
```

con:

```text
cornea
iris
pupil
sclera
```

---

# 32. EYE ORIENTATION

Los ojos deberán permitir:

```text
look_at
independent_rotation
symmetry
```

---

# 33. MOUTH SYSTEM

Deberá existir:

```text
MouthAssembly
```

con:

```text
lips
teeth
tongue
oral_cavity
```

---

# 34. TEETH

Los dientes deberán ser un sistema modular.

---

# 35. TONGUE

Deberá ser compatible con rigging facial básico.

---

# 36. HAIR SYSTEM

Deberá existir:

```text
HairFabricator
```

---

# 37. HAIR STRATEGIES

Mínimo:

```text
MESH_CARDS
CURVES
PARTICLE
PROCEDURAL_MESH
HYBRID
```

---

# 38. HAIR PROFILE

Mínimo:

```text
length
density
curl
direction
volume
color
roughness
```

---

# 39. HAIR COLLISION

Deberá existir configuración para evitar penetración visible con:

```text
head
armor
helmet
clothing
```

---

# 40. CLOTHING SYSTEM

Deberá existir:

```text
ClothingFabricator
```

---

# 41. CLOTHING TYPES

Mínimo:

```text
UNDERWEAR
SHIRT
PANTS
JACKET
COAT
GLOVES
BOOTS
CAPE
BELT
BACKPACK
CUSTOM
```

---

# 42. CLOTHING FITTING

La ropa deberá adaptarse al cuerpo mediante:

```text
scale
wrap
surface_projection
cloth_simulation
parametric_pattern
```

---

# 43. CLOTHING INTERSECTION

Deberán detectarse intersecciones entre:

```text
body
clothing
clothing
armor
equipment
```

---

# 44. CLOTHING LAYERS

Deberán existir prioridades:

```text
BODY
BASE
CLOTHING
ARMOR
EQUIPMENT
ACCESSORY
```

---

# 45. CLOTHING THICKNESS

La ropa deberá poder tener espesor físico.

---

# 46. CLOTHING TOPOLOGY

Las piezas deformables deberán tener densidad suficiente para soportar skinning.

---

# 47. ARMOR SYSTEM

Deberá existir:

```text
ArmorFabricator
```

---

# 48. ARMOR TYPES

Mínimo:

```text
HELMET
SHOULDER
CHEST
BACK
ARM
FOREARM
HAND
THIGH
KNEE
SHIN
FOOT
```

---

# 49. ARMOR ATTACHMENT

Las piezas deberán utilizar sockets o anchors semánticos.

---

# 50. ARMOR CLEARANCE

Deberá comprobarse separación suficiente respecto al cuerpo y ropa.

---

# 51. EQUIPMENT SYSTEM

Deberá existir:

```text
EquipmentFabricator
```

---

# 52. EQUIPMENT SLOTS

Mínimo:

```text
HEAD
FACE
BACK
CHEST
WAIST
HAND_L
HAND_R
THIGH_L
THIGH_R
```

---

# 53. SOCKET SYSTEM

Los sockets deberán tener:

```text
socket_id
bone
location
rotation
scale
purpose
```

---

# 54. STANDARD UNREAL SOCKETS

Deberán poder generarse:

```text
weapon_r
weapon_l
muzzle
back
pelvis
head
hand_r
hand_l
```

---

# 55. WEAPON COMPATIBILITY

Un arma compatible deberá poder equiparse sin modificar manualmente el personaje.

---

# 56. BACKPACK COMPATIBILITY

El backpack deberá permanecer estable durante animación.

---

# 57. SKELETON SYSTEM

Deberá existir:

```text
SkeletonFabricator
```

---

# 58. SKELETON HIERARCHY

Mínimo:

```text
root
└── pelvis
    ├── spine
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       ├── clavicle_L
    │       │   └── arm_L
    │       └── clavicle_R
    │           └── arm_R
    ├── leg_L
    └── leg_R
```

---

# 59. SKELETON NAMING

Los nombres deberán ser estables y configurables mediante un SkeletonProfile.

---

# 60. SKELETON SYMMETRY

Las cadenas izquierda/derecha deberán conservar simetría cuando el profile lo requiera.

---

# 61. BONE ORIENTATION

La orientación deberá ser determinista.

---

# 62. RIG SYSTEM

Deberá existir:

```text
RigFabricator
```

---

# 63. RIG TYPES

Mínimo:

```text
BIPED
QUADRUPED
HUMANOID
CREATURE
ROBOT
CUSTOM
```

---

# 64. CONTROL RIG

Deberá soportarse una capa de controles independiente del skeleton de exportación.

---

# 65. IK SYSTEM

Mínimo:

```text
hand_L
hand_R
foot_L
foot_R
```

---

# 66. IK VALIDATION

Deberá comprobarse:

```text
reachability
pole_direction
joint_limits
```

---

# 67. FOOT PLANT

El rig deberá poder mantener los pies sobre una superficie definida.

---

# 68. HAND PLACEMENT

Las manos deberán poder alcanzar sockets de armas.

---

# 69. LOOK AT

Deberá existir control de:

```text
head
neck
eyes
```

---

# 70. SPINE CONTROL

El rig deberá permitir distribución de rotación sobre la columna.

---

# 71. SKINNING SYSTEM

Deberá existir:

```text
SkinningFabricator
```

---

# 72. WEIGHT GENERATION

Los pesos deberán poder generarse mediante:

```text
AUTO
HEAT
ENVELOPE
DISTANCE
GEODESIC
HYBRID
CUSTOM
```

---

# 73. WEIGHT NORMALIZATION

Cada vértice deberá tener pesos normalizados.

---

# 74. WEIGHT LIMIT

El número máximo de influencias por vértice deberá ser configurable.

Default:

```text
4
```

---

# 75. WEIGHT VALIDATION

Deberá detectar:

```text
unweighted_vertices
overweighted_vertices
invalid_bone
zero_weight
weight_sum_error
```

---

# 76. WEIGHT CONTINUITY

Las zonas articulares deberán presentar transición progresiva de pesos.

---

# 77. DEFORMATION TEST SYSTEM

Deberá existir:

```text
DeformationValidator
```

---

# 78. DEFORMATION POSES

Mínimo:

```text
T_POSE
A_POSE
CROUCH
WALK
RUN
JUMP
SQUAT
ARM_RAISE
ELBOW_BEND
KNEE_BEND
```

---

# 79. EXTREME POSES

Deberán existir tests:

```text
MAX_ARM_FLEX
MAX_LEG_FLEX
MAX_SPINE_FLEX
MAX_NECK_ROTATION
```

---

# 80. DEFORMATION METRICS

Mínimo:

```text
intersection_score
volume_loss
volume_gain
stretch_score
compression_score
texture_distortion
```

---

# 81. DEFORMATION THRESHOLDS

Cada SkeletonProfile deberá declarar límites aceptables.

---

# 82. CLOTHING DEFORMATION

La ropa deberá heredar o generar pesos compatibles con el cuerpo.

---

# 83. ARMOR DEFORMATION

Las piezas rígidas deberán poder:

```text
follow_bone
follow_socket
remain_rigid
```

---

# 84. RIGID ARMOR

Las placas rígidas no deberán sufrir deformaciones orgánicas innecesarias.

---

# 85. FLEXIBLE ARMOR

Los componentes flexibles podrán utilizar skinning.

---

# 86. ACCESSORY DEFORMATION

Los accesorios deberán clasificarse como:

```text
RIGID
FLEXIBLE
SIMULATED
```

---

# 87. CLOTH SIMULATION

Deberá existir soporte opcional para simulación de:

```text
cape
coat
skirt
straps
cloth_panels
```

---

# 88. SIMULATION BAKE

La simulación deberá poder convertirse en una salida determinista compatible con el pipeline.

---

# 89. HIGH POLY

Deberá existir generación opcional de high-poly.

---

# 90. HIGH-POLY PURPOSE

Podrá utilizarse para:

```text
detail
baking
normal_map
displacement
surface_reference
```

---

# 91. MID POLY

Deberá existir una representación intermedia para producción.

---

# 92. LOW POLY

La malla final deberá optimizarse para runtime.

---

# 93. RETOPOLOGY

Deberá existir:

```text
RetopologyFabricator
```

---

# 94. RETOPOLOGY REQUIREMENTS

La retopología deberá preservar:

```text
silhouette
deformation
UV_regions
material_regions
```

---

# 95. POLYGON BUDGET

Cada CharacterProfile deberá declarar:

```text
high_poly_budget
mid_poly_budget
lod0_budget
lod1_budget
lod2_budget
lod3_budget
```

---

# 96. LOD SYSTEM

Deberá existir:

```text
LOD0
LOD1
LOD2
LOD3
```

como mínimo configurable.

---

# 97. LOD VALIDATION

Cada LOD deberá mantener:

```text
silhouette
material_assignment
skeleton_binding
```

según tolerancia.

---

# 98. UV SYSTEM

Deberá existir:

```text
UVFabricator
```

---

# 99. UV CHANNELS

Deberán soportarse:

```text
UV0
UV1
UV2
```

según target.

---

# 100. UV0

UV0 estará destinado principalmente a texturas de superficie.

---

# 101. UV1

UV1 podrá utilizarse para lightmaps cuando sea necesario.

---

# 102. UV VALIDATION

Deberá detectar:

```text
overlap
out_of_bounds
degenerate_islands
tiny_islands
excessive_stretch
```

---

# 103. MATERIAL ASSIGNMENT

Deberá existir:

```text
CharacterMaterialBinder
```

---

# 104. MATERIAL REGIONS

Mínimo:

```text
SKIN
EYES
TEETH
HAIR
CLOTH
LEATHER
METAL
PLASTIC
GLASS
ENERGY
```

---

# 105. MATERIAL INSTANCE STRATEGY

Los personajes deberán preferir material instances parametrizadas sobre materiales duplicados.

---

# 106. TEXTURE COORDINATION

El personaje deberá poder solicitar:

```text
albedo
normal
roughness
metallic
ao
emissive
mask
```

a UAF-81.22.

---

# 107. TEXTURE MASK SYSTEM

Deberán existir masks semánticas:

```text
skin_mask
cloth_mask
metal_mask
wear_mask
dirt_mask
damage_mask
emissive_mask
```

---

# 108. MATERIAL VARIANTS

El mismo personaje deberá poder tener variantes:

```text
clean
damaged
battle_worn
corrupted
alternate_color
```

sin reconstruir la geometría.

---

# 109. DAMAGE STATES

Deberá existir metadata para:

```text
damage_regions
destruction_regions
material_state
```

---

# 110. CHARACTER VARIANTS

Deberán existir variantes independientes de:

```text
body
face
hair
clothing
armor
equipment
material
```

---

# 111. VARIANT COMBINATOR

Deberá poder generar combinaciones válidas sin producir configuraciones incompatibles.

---

# 112. COMPATIBILITY MATRIX

Deberá existir:

```text
CharacterCompatibilityMatrix
```

que valide:

```text
body ↔ clothing
body ↔ armor
skeleton ↔ rig
skeleton ↔ skinning
armor ↔ skeleton
equipment ↔ sockets
materials ↔ mesh
LOD ↔ skeleton
```

---

# 113. COLLISION SYSTEM

Deberá existir:

```text
CharacterCollisionFabricator
```

---

# 114. COLLISION TYPES

Mínimo:

```text
CAPSULE
BOX
SPHERE
CONVEX
CUSTOM
```

---

# 115. PLAYER CAPSULE

El personaje deberá seguir las restricciones globales del TargetProfile.

---

# 116. COLLISION CLEARANCE

La colisión no deberá atravesar visualmente el personaje salvo tolerancias explícitas.

---

# 117. PHYSICS ASSETS

Deberá existir generación de:

```text
PhysicsAsset
```

---

# 118. PHYSICS BODY TYPES

Mínimo:

```text
HEAD
TORSO
PELVIS
UPPER_ARM
LOWER_ARM
HAND
UPPER_LEG
LOWER_LEG
FOOT
```

---

# 119. PHYSICS CONSTRAINTS

Deberán existir límites de:

```text
rotation
swing
twist
```

---

# 120. SOCKET VALIDATION

Todo socket deberá comprobar:

```text
bone_exists
valid_transform
purpose_defined
collision_clearance
```

---

# 121. UNREAL CHARACTER PROFILE

Deberá existir:

```text
UnrealCharacterProfile
```

---

# 122. UNREAL OUTPUT

Mínimo:

```text
SkeletalMesh
Skeleton
PhysicsAsset
Materials
MaterialInstances
Textures
MorphTargets
Sockets
LODs
Collision
Metadata
```

---

# 123. ANIMATION COMPATIBILITY

El personaje deberá declarar:

```text
animation_rig_type
skeleton_profile
retarget_profile
```

---

# 124. RETARGETING

Deberá existir metadata para permitir retargeting cuando sea compatible.

---

# 125. ROOT MOTION

El profile deberá declarar:

```text
ROOT_MOTION
IN_PLACE
HYBRID
```

---

# 126. CHARACTER EXPORT PACKAGE

El paquete deberá contener:

```text
character_manifest
skeletal_mesh
skeleton
physics_asset
materials
textures
morph_targets
sockets
lod_data
validation_report
```

---

# 127. CHARACTER MANIFEST

Mínimo:

```text
character_id
version
generator_version
seed
skeleton_id
mesh_id
material_ids
texture_ids
lod_profile
collision_profile
```

---

# 128. VALIDATION PIPELINE

La validación deberá seguir:

```text
SCHEMA
 ↓
ANATOMY
 ↓
TOPOLOGY
 ↓
MODULAR COMPATIBILITY
 ↓
CLOTHING FIT
 ↓
ARMOR FIT
 ↓
SKELETON
 ↓
RIG
 ↓
SKINNING
 ↓
DEFORMATION
 ↓
UV
 ↓
MATERIALS
 ↓
LOD
 ↓
COLLISION
 ↓
UNREAL COMPATIBILITY
 ↓
EXPORT
```

---

# 129. ANATOMY VALIDATION

Debe detectar:

```text
invalid_proportions
invalid_landmarks
asymmetry_error
joint_invalidity
```

---

# 130. TOPOLOGY VALIDATION

Debe detectar:

```text
non_manifold
degenerate_faces
bad_normals
self_intersection
invalid_edge_flow
```

---

# 131. CLOTHING VALIDATION

Debe detectar:

```text
body_intersection
armor_intersection
floating_cloth
missing_attachment
```

---

# 132. RIG VALIDATION

Debe detectar:

```text
missing_bone
invalid_parent
bad_orientation
broken_chain
```

---

# 133. SKINNING VALIDATION

Debe detectar:

```text
unweighted
invalid_weights
excessive_influence
```

---

# 134. DEFORMATION VALIDATION

Debe detectar:

```text
severe_intersection
extreme_stretch
extreme_compression
joint_collapse
```

---

# 135. EXPORT VALIDATION

Debe detectar:

```text
missing_asset
broken_reference
invalid_socket
missing_material
invalid_lod
```

---

# 136. ARTISTIC VALIDATION

Además de validación técnica deberá existir:

```text
CharacterVisualQualityValidator
```

---

# 137. VISUAL QUALITY METRICS

Mínimo:

```text
silhouette
proportion
material_coherence
detail_coherence
color_coherence
readability
```

---

# 138. SILHOUETTE VALIDATION

El personaje deberá evaluarse desde:

```text
FRONT
BACK
LEFT
RIGHT
THREE_QUARTER
GAMEPLAY_DISTANCE
```

---

# 139. GAMEPLAY READABILITY

Deberá evaluarse a distancia:

```text
near
medium
far
```

---

# 140. CHARACTER CLASS READABILITY

La silueta deberá permitir diferenciar, cuando corresponda:

```text
ASSAULT
TANK
SUPPORT
SNIPER
BOSS
NPC
PLAYER
```

---

# 141. SCALE VALIDATION

El personaje deberá compararse contra:

```text
player_capsule
world_scale
doors
stairs
cover
vehicles
weapons
```

---

# 142. WEAPON POSE VALIDATION

Deberán ejecutarse pruebas de:

```text
weapon_idle
weapon_aim
weapon_fire
weapon_reload
weapon_melee
```

---

# 143. EQUIPMENT VALIDATION

Todo equipamiento deberá permanecer correctamente anclado durante las poses críticas.

---

# 144. AUTOMATED CHARACTER TEST

Deberá existir:

```text
CharacterSimulationTest
```

---

# 145. AUTOMATED POSE SUITE

Cada personaje deberá evaluarse automáticamente en:

```text
idle
walk
run
crouch
jump
aim
reload
melee
death
```

---

# 146. CHARACTER GOLDEN TESTS

Deberán existir personajes golden para:

```text
HUMAN
ROBOT
ALIEN
CREATURE
HEAVY_ARMOR
LIGHT_ARMOR
CLOTH_HEAVY
CLOTH_LIGHT
```

---

# 147. COMPLEX CHARACTER TEST

Deberá existir al menos un personaje que combine:

```text
complex_face
hair
multi_layer_clothing
armor
backpack
weapon
morph_targets
full_rig
skinning
LOD
physics
```

---

# 148. STRESS CHARACTER

Deberá existir un caso extremo que fuerce:

```text
maximum_parts
maximum_materials
maximum_bones
maximum_morphs
maximum_equipment
```

dentro de límites configurados.

---

# 149. VARIANT STRESS TEST

Deberá comprobarse la generación de múltiples variantes con:

```text
same_body
different_face
different_hair
different_clothing
different_armor
different_material
```

---

# 150. REPRODUCIBILITY TEST

La misma definición deberá producir hashes equivalentes en ejecuciones independientes.

---

# 151. CHARACTER BUILD REPORT

Deberá existir:

```text
CharacterBuildReport
```

---

# 152. REPORT CONTENT

Mínimo:

```text
character_id
vertex_count
triangle_count
bone_count
morph_count
material_count
texture_count
lod_count
draw_call_estimate
memory_estimate
deformation_score
visual_score
export_status
```

---

# 153. PERFORMANCE BUDGET

Cada CharacterProfile deberá declarar:

```text
triangle_budget
bone_budget
morph_budget
material_slot_budget
texture_memory_budget
draw_call_budget
```

---

# 154. BUDGET FAILURE

Superar un presupuesto deberá generar:

```text
WARNING
ERROR
REJECT
```

según severidad.

---

# 155. QUALITY GATE

Un personaje será aceptado únicamente si:

```text
ANATOMY_VALID
AND
TOPOLOGY_VALID
AND
CLOTHING_VALID
AND
ARMOR_VALID
AND
RIG_VALID
AND
SKINNING_VALID
AND
DEFORMATION_VALID
AND
UV_VALID
AND
MATERIAL_VALID
AND
LOD_VALID
AND
COLLISION_VALID
AND
UNREAL_VALID
```

---

# 156. NO-HIDDEN-DEPENDENCY RULE

El personaje no deberá depender de:

```text
absolute_paths
machine_specific_paths
manual_scene_state
hidden_blender_objects
external_untracked_files
```

---

# 157. PORTABILITY

Todo asset generado deberá poder reconstruirse en otra máquina a partir de:

```text
definition
seed
generator_version
declared_dependencies
```

---

# 158. INCREMENTAL REBUILD

Deberá soportarse:

```text
ANATOMY_ONLY
FACE_ONLY
HAIR_ONLY
CLOTHING_ONLY
ARMOR_ONLY
MATERIAL_ONLY
RIG_ONLY
SKINNING_ONLY
LOD_ONLY
FULL_CHARACTER
```

---

# 159. INVALIDATION

Modificar anatomía deberá invalidar únicamente componentes dependientes.

Ejemplo:

```text
ANATOMY
 ↓
CLOTHING
 ↓
ARMOR
 ↓
SKINNING
 ↓
DEFORMATION
```

pero no deberá reconstruir innecesariamente assets independientes.

---

# 160. TRANSACTIONAL BUILD

Cada etapa deberá poder:

```text
START
VALIDATE
COMMIT
ROLLBACK
```

---

# 161. CHECKPOINTS

Mínimo:

```text
CHARACTER_SPECIFIED
ANATOMY_BUILT
BODY_BUILT
FACE_BUILT
CLOTHING_BUILT
ARMOR_BUILT
SKELETON_BUILT
RIG_BUILT
SKINNED
DEFORMATION_VALIDATED
UV_VALIDATED
MATERIALS_ASSIGNED
LODS_BUILT
COLLISION_BUILT
UNREAL_VALIDATED
EXPORTED
```

---

# 162. ERROR CLASSIFICATION

Los errores deberán clasificarse como:

```text
SCHEMA_ERROR
ANATOMY_ERROR
TOPOLOGY_ERROR
COMPATIBILITY_ERROR
CLOTHING_ERROR
RIG_ERROR
SKINNING_ERROR
DEFORMATION_ERROR
UV_ERROR
MATERIAL_ERROR
LOD_ERROR
COLLISION_ERROR
EXPORT_ERROR
```

---

# 163. ERROR SEVERITY

Mínimo:

```text
INFO
WARNING
ERROR
FATAL
```

---

# 164. DIAGNOSTIC EVIDENCE

Todo rechazo deberá incluir:

```text
error_code
component
location
metric
threshold
actual_value
expected_value
suggested_resolution
```

---

# 165. GOLDEN ARTIFACTS

Deberán almacenarse referencias golden de:

```text
mesh
skeleton
weights
poses
materials
textures
lods
physics
```

---

# 166. REGRESSION DETECTION

Una modificación del generador no deberá degradar silenciosamente:

```text
silhouette
deformation
topology
performance
```

---

# 167. CHARACTER FACTORY

Deberá existir:

```text
CharacterFactory
```

que coordine:

```text
AnatomyFabricator
HeadFabricator
FaceFabricator
HairFabricator
ClothingFabricator
ArmorFabricator
EquipmentFabricator
SkeletonFabricator
RigFabricator
SkinningFabricator
MorphTargetFabricator
UVFabricator
CharacterMaterialBinder
LODBuilder
CollisionFabricator
UnrealCharacterExporter
```

---

# 168. FACTORY CONTRACT

Entrada:

```text
CharacterDefinition
CharacterProfile
GeneratorContext
Seed
```

Salida:

```text
CharacterBuildResult
```

---

# 169. CHARACTER BUILD RESULT

Mínimo:

```text
success
character_manifest
asset_references
validation_report
performance_report
diagnostics
```

---

# 170. FINAL ARCHITECTURAL MODEL

UAF-81.21 deberá considerar:

```text
CHARACTER
=
IDENTITY
+
ANATOMY
+
SURFACE
+
EQUIPMENT
+
SKELETON
+
RIG
+
SKINNING
+
DEFORMATION
+
MATERIAL
+
LOD
+
COLLISION
+
UNREAL CONTRACT
```

---

# 171. PROFESSIONAL ACCEPTANCE TEST

El sistema deberá ser capaz de producir un personaje que:

```text
1. Tenga anatomía coherente.
2. Posea topología apta para deformación.
3. Admita rostro complejo.
4. Admita manos y dedos correctamente.
5. Admita múltiples capas de ropa.
6. Admita armadura modular.
7. Admita accesorios.
8. Admita armas.
9. Posea skeleton válido.
10. Posea rig funcional.
11. Posea pesos automáticos válidos.
12. Pase pruebas de deformación.
13. Posea UV válidas.
14. Posea materiales.
15. Posea texturas o referencias válidas.
16. Posea LODs.
17. Posea collision.
18. Posea Physics Asset.
19. Posea sockets.
20. Sea exportable a Unreal.
21. Sea reproducible.
22. Sea verificable automáticamente.
23. Respete budgets.
24. Pueda recibir variantes.
25. Pueda reconstruirse incrementalmente.
```

---

# 172. CRITICAL DESIGN REQUIREMENT

El sistema deberá evitar que el voxel remesh sea la única estrategia de fabricación.

El voxel remesh deberá considerarse:

```text
ONE GENERATION TOOL
```

y no:

```text
THE CHARACTER GENERATION ARCHITECTURE
```

La arquitectura deberá permitir seleccionar dinámicamente la estrategia más adecuada para cada componente.

---

# 173. COMPONENT STRATEGY MATRIX

Cada componente podrá seleccionar:

```text
PROCEDURAL
MODULAR
SCULPTED_REFERENCE
PARAMETRIC
SIMULATION
HYBRID
```

---

# 174. STRATEGY SELECTION

La selección deberá depender de:

```text
component_type
target_quality
deformation_requirement
performance_budget
style_profile
platform
```

---

# 175. FINAL OBJECTIVE

El objetivo final de UAF-81.21 será transformar la capacidad actual de:

```text
procedural geometric character generation
```

en:

```text
PRODUCTION CHARACTER FABRICATION
```

capaz de generar personajes:

```text
COMPLEX
MODULAR
DEFORMABLE
ANIMATABLE
TEXTURABLE
EQUIPPABLE
OPTIMIZED
VALIDATED
REPRODUCIBLE
UNREAL-READY
```

---

# 176. DEPENDENCY CONTRACT

UAF-81.21 dependerá de:

```text
UAF-81.01 → Core Factory
UAF-81.02 → Asset Schema
UAF-81.03 → Semantic Asset Graph
UAF-81.04 → Generation Strategy
UAF-81.05 → Deterministic Build
UAF-81.06 → Validation
UAF-81.07 → Performance
UAF-81.08 → Unreal Integration
UAF-81.19 → World/Environment Fabrication
```

y proporcionará servicios a:

```text
UAF-81.20 → Gameplay
UAF-81.22 → Texture Fabrication
UAF-81.23 → Animation Fabrication
UAF-81.24 → VFX
UAF-81.25 → Audio
UAF-81.26 → Unreal Assembly
```

---

# 177. NEXT PHASE

```text
UAF-81.22 — PROCEDURAL MATERIAL, TEXTURE & SURFACE DETAIL FABRICATION SYSTEM
```

Esta fase deberá resolver el segundo gran componente de la fábrica:

```text
BASE MATERIAL
      ↓
UV
      ↓
MASKS
      ↓
ALBEDO
      ↓
NORMAL
      ↓
ROUGHNESS
      ↓
METALLIC
      ↓
AO
      ↓
EMISSIVE
      ↓
WEAR
      ↓
DAMAGE
      ↓
VARIANTS
      ↓
MATERIAL INSTANCES
      ↓
UNREAL TEXTURE PACKAGE
```
