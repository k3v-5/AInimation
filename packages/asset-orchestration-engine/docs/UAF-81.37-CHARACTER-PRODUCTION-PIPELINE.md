# UAF-81.37 — PROFESSIONAL CHARACTER RIGGING, SKINNING, CLOTHING, HAIR, FACIAL & ANIMATION-READY CHARACTER SYSTEM

## UAF-81.37-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA PROFESIONAL DE RIGGING, SKINNING, VESTIMENTA, CABELLO, ROSTRO Y PREPARACIÓN DE PERSONAJES PARA ANIMACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.37 — Professional Character Rigging, Skinning, Clothing, Hair, Facial & Animation-Ready Character System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.36  
**Next Phase:** UAF-81.38  

---

# 1. PURPOSE

UAF-81.37 establece el sistema profesional para transformar personajes generados proceduralmente en personajes:

```text
RIGGED
SKINNED
CLOTHED
HAIR_READY
FACIAL_READY
ANIMATION_READY
GAMEPLAY_READY
UNREAL_READY
```

La fase deberá cubrir el ciclo completo:

```text
BODY
    ↓
SKELETON
    ↓
RIG
    ↓
SKIN
    ↓
CLOTHING
    ↓
HAIR
    ↓
FACE
    ↓
DEFORMATION
    ↓
LOD
    ↓
VALIDATION
    ↓
EXPORT
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá generar personajes que puedan utilizarse como base para:

```text
PLAYER
NPC
ENEMY
BOSS
CREATURE
ROBOT
ANDROID
ALIEN
HUMANOID
CUSTOM_HUMANOID
```

sin depender de intervención manual obligatoria para completar el pipeline técnico.

---

# 3. CHARACTER DEFINITION

Deberá existir:

```text
CharacterDefinition
CharacterGenerator
CharacterValidator
CharacterRigDefinition
CharacterExportDefinition
```

---

# 4. CHARACTER IDENTITY

Cada personaje deberá tener:

```text
character_id
archetype
body_profile
head_profile
material_profile
rig_profile
clothing_profile
hair_profile
facial_profile
animation_profile
lod_profile
performance_profile
seed
generator_version
```

---

# 5. CHARACTER ARCHETYPES

Mínimo:

```text
HUMAN
HUMANOID
ROBOT
ANDROID
ALIEN
CREATURE
BOSS
HEAVY
LIGHT
CUSTOM
```

---

# 6. BODY PROFILE

Deberá controlar:

```text
height
shoulder_width
chest_width
waist_width
hip_width
arm_length
leg_length
head_size
hand_size
foot_size
neck_length
```

---

# 7. PROPORTION VALIDATION

El sistema deberá detectar:

```text
INVALID_HEIGHT
INVALID_LIMB_RATIO
INVALID_TORSO_RATIO
INVALID_HEAD_RATIO
INVALID_HAND_RATIO
INVALID_FOOT_RATIO
```

---

# 8. LANDMARKS

Deberán existir landmarks semánticos:

```text
root
pelvis
spine
chest
neck
head
clavicle_L
clavicle_R
shoulder_L
shoulder_R
elbow_L
elbow_R
wrist_L
wrist_R
hand_L
hand_R
hip_L
hip_R
knee_L
knee_R
ankle_L
ankle_R
foot_L
foot_R
```

---

# 9. SKELETON DEFINITION

Deberá existir:

```text
SkeletonDefinition
BoneDefinition
SkeletonValidator
```

---

# 10. BONE DEFINITION

Cada hueso deberá contener:

```text
name
parent
local_transform
bind_transform
length
orientation
deformation_role
```

---

# 11. STANDARD SKELETON

Deberá existir un skeleton estándar compatible con las necesidades del proyecto.

---

# 12. SKELETON EXTENSIONS

Deberá poder extenderse con:

```text
tail
horn
wing
tentacle
extra_arm
robot_joint
mechanical_component
custom
```

sin romper el skeleton base.

---

# 13. BONE NAMING

Los nombres deberán ser deterministas.

No se permitirán nombres generados aleatoriamente.

---

# 14. BONE ORIENTATION

Deberán existir reglas explícitas para:

```text
forward_axis
up_axis
roll
local_orientation
```

---

# 15. SKELETON SYMMETRY

Las cadenas simétricas deberán poder validarse:

```text
_L
_R
```

---

# 16. SKELETON SYMMETRY TEST

Deberá verificarse:

```text
bone_count
hierarchy
length
orientation
relative_position
```

entre lados correspondientes.

---

# 17. RIG DEFINITION

Deberá existir:

```text
RigDefinition
RigBuilder
RigValidator
```

---

# 18. RIG TYPES

Mínimo:

```text
HUMANOID
QUADRUPED
ROBOT
CREATURE
CUSTOM
```

---

# 19. CONTROL RIG

Deberá existir una capa de controles separada de los huesos deformadores cuando el profile lo requiera.

---

# 20. CONTROL TYPES

Mínimo:

```text
ROOT
IK
FK
AIM
LOOK_AT
POLE_VECTOR
SPACE_SWITCH
CUSTOM
```

---

# 21. IK SYSTEM

Deberá existir IK para:

```text
ARM_L
ARM_R
LEG_L
LEG_R
```

---

# 22. IK VALIDATION

Deberá comprobar:

```text
reachability
pole_direction
joint_limits
foot_alignment
hand_alignment
```

---

# 23. FOOT IK

Deberá existir soporte para:

```text
GROUND_CONTACT
STEP
SLOPE
STAIR
```

---

# 24. HAND IK

Deberá existir soporte para:

```text
WEAPON
OBJECT
GRIP
TWO_HAND_GRIP
```

---

# 25. LOOK AT

Deberá existir sistema de:

```text
head_look_at
eye_look_at
upper_body_look_at
```

---

# 26. JOINT LIMITS

Cada articulación deberá declarar límites cuando corresponda.

---

# 27. JOINT LIMIT VALIDATION

No deberán producirse poses imposibles dentro del profile permitido.

---

# 28. SKINNING

Deberá existir:

```text
SkinningDefinition
SkinningGenerator
SkinningValidator
```

---

# 29. WEIGHT GENERATION

Los pesos deberán generarse automáticamente a partir de:

```text
distance
volume
bone_influence
topology
anatomical_region
```

---

# 30. WEIGHT NORMALIZATION

Para cada vértice:

```text
sum(weights) == 1.0
```

dentro de una tolerancia definida.

---

# 31. MAXIMUM INFLUENCES

Deberá poder configurarse:

```text
max_influences_per_vertex
```

por profile de plataforma.

---

# 32. ZERO-WEIGHT VERTICES

Deberán detectarse todos los vértices sin influencia válida.

---

# 33. ORPHAN WEIGHTS

Deberán detectarse referencias a huesos inexistentes.

---

# 34. WEIGHT DISTRIBUTION

Deberán detectarse pesos:

```text
NEGATIVE
NAN
INFINITE
OUT_OF_RANGE
```

---

# 35. DEFORMATION TESTING

Cada personaje deberá someterse a poses de deformación automáticas.

Mínimo:

```text
T_POSE
A_POSE
ARM_RAISE
ARM_BEND
ELBOW_BEND
KNEE_BEND
SQUAT
WALK
RUN
CROUCH
```

---

# 36. DEFORMATION ERROR DETECTION

Deberá detectarse:

```text
SELF_INTERSECTION
COLLAPSE
VOLUME_LOSS
VOLUME_EXPLOSION
UNEXPECTED_STRETCH
WEIGHT_POP
```

---

# 37. CORRECTIVE DEFORMATIONS

Deberá existir soporte para:

```text
corrective_shape
pose_space_deformation
joint_corrective
```

---

# 38. CORRECTIVE SHAPES

Mínimo:

```text
ELBOW
KNEE
SHOULDER
HIP
WRIST
ANKLE
```

---

# 39. CLOTHING SYSTEM

Deberá existir:

```text
ClothingDefinition
ClothingGenerator
ClothingValidator
```

---

# 40. CLOTHING TYPES

Mínimo:

```text
SHIRT
PANTS
JACKET
ARMOR
VEST
BOOTS
GLOVES
HELMET
MASK
CAP
ACCESSORY
CUSTOM
```

---

# 41. CLOTHING FIT

La ropa deberá adaptarse al body profile.

---

# 42. CLOTHING CLEARANCE

Deberá existir un clearance mínimo entre:

```text
BODY
CLOTHING
ARMOR
ACCESSORIES
```

según profile.

---

# 43. CLOTHING INTERSECTION

Deberá detectarse intersección no permitida entre cuerpo y ropa.

---

# 44. CLOTH TOPOLOGY

La topología deberá permanecer válida después de adaptación.

---

# 45. CLOTHING RIGGING

La ropa deberá poder:

```text
inherit_skeleton
generate_skin
transfer_weights
```

---

# 46. WEIGHT TRANSFER

Deberá existir transferencia de pesos desde el cuerpo hacia prendas compatibles.

---

# 47. CLOTH DEFORMATION

Deberán probarse las prendas en:

```text
WALK
RUN
CROUCH
JUMP
ARM_RAISE
LEG_BEND
```

---

# 48. CLOTH SIMULATION

Deberá existir soporte opcional para simulación física.

---

# 49. CLOTH SIMULATION CLASSIFICATION

```text
STATIC
RIGID
SKINNED
SIMULATED
HYBRID
```

---

# 50. ARMOR SYSTEM

La armadura deberá soportar:

```text
PLATE
SEGMENT
EXOSKELETON
MECHANICAL
ENERGY
CUSTOM
```

---

# 51. ARMOR DEFORMATION

Las piezas de armadura no deberán atravesar el cuerpo durante poses válidas.

---

# 52. ARMOR SOCKETS

Deberán existir sockets:

```text
helmet
back
chest
shoulder_L
shoulder_R
hip_L
hip_R
hand_L
hand_R
```

---

# 53. EQUIPMENT COMPATIBILITY

Los sockets deberán ser compatibles con el sistema de equipamiento del motor.

---

# 54. HAND / FOOT SYSTEM

Deberá existir soporte para:

```text
finger bones
toe bones
```

cuando el archetype lo requiera.

---

# 55. FINGER RIG

Mínimo:

```text
thumb
index
middle
ring
pinky
```

para ambas manos.

---

# 56. HAND POSES

Deberán existir perfiles:

```text
OPEN
FIST
GRIP
POINT
RELAXED
WEAPON
CUSTOM
```

---

# 57. FACE SYSTEM

Deberá existir:

```text
FaceDefinition
FaceGenerator
FaceValidator
```

---

# 58. FACIAL COMPONENTS

Mínimo:

```text
SKULL
EYES
EYELIDS
EYEBROWS
NOSE
MOUTH
LIPS
TEETH
TONGUE
JAW
```

---

# 59. EYE SYSTEM

Cada ojo deberá soportar:

```text
iris
pupil
sclera
cornea
```

---

# 60. EYE LOOK

Los ojos deberán poder seguir un objetivo independientemente del head rotation cuando el profile lo permita.

---

# 61. EYELID SYSTEM

Los párpados deberán deformarse con el ojo.

---

# 62. MOUTH SYSTEM

Deberá soportar:

```text
OPEN
CLOSE
SMILE
FROWN
JAW_OPEN
JAW_LEFT
JAW_RIGHT
```

---

# 63. TEETH

Deberán existir dientes como geometría independiente o sistema parametrizable.

---

# 64. TONGUE

Deberá existir soporte para lengua en personajes que la requieran.

---

# 65. FACIAL RIG

Deberá soportar:

```text
BONE_BASED
BLENDSHAPE_BASED
HYBRID
```

---

# 66. FACIAL EXPRESSIONS

Mínimo:

```text
NEUTRAL
HAPPY
ANGRY
SAD
FEAR
SURPRISE
DISGUST
PAIN
CUSTOM
```

---

# 67. PHONEMES

Deberá existir soporte mínimo para:

```text
A
E
I
O
U
M
F
V
L
S
SH
TH
```

---

# 68. BLENDSHAPES

Deberán poder generarse:

```text
face_shapes
phoneme_shapes
corrective_shapes
custom_shapes
```

---

# 69. BLENDSHAPE VALIDATION

Deberá comprobarse:

```text
duplicate_names
invalid_ranges
broken_targets
self_intersection
unexpected_geometry
```

---

# 70. HAIR SYSTEM

Deberá existir:

```text
HairDefinition
HairGenerator
HairValidator
```

---

# 71. HAIR TYPES

Mínimo:

```text
CARDS
CURVES
GROOM
MESH
HYBRID
```

---

# 72. HAIR PROFILES

Mínimo:

```text
SHORT
MEDIUM
LONG
BRAID
MOHAWK
MILITARY
ALIEN
CUSTOM
```

---

# 73. HAIR ATTACHMENT

El pelo deberá seguir:

```text
head
scalp
facial_bones
```

cuando corresponda.

---

# 74. HAIR COLLISION

Deberá existir configuración de colisión para:

```text
HEAD
SHOULDER
BACK
ARMOR
CUSTOM
```

---

# 75. HAIR LOD

Deberán existir estrategias de reducción:

```text
LOD0
LOD1
LOD2
LOD3
```

---

# 76. CHARACTER MATERIALS

El sistema deberá soportar materiales separados para:

```text
SKIN
EYES
HAIR
CLOTHING
ARMOR
METAL
RUBBER
TEETH
TONGUE
```

---

# 77. SKIN MATERIAL

Deberá soportar parámetros:

```text
base_color
roughness
subsurface
specular
normal
detail
variation
```

---

# 78. SKIN VARIATION

La variación deberá ser determinista.

---

# 79. CHARACTER DETAIL

Deberá poder generarse detalle procedural:

```text
PORES
SCARS
WRINKLES
TATTOOS
DAMAGE
MECHANICAL_DETAILS
CUSTOM
```

---

# 80. DETAIL LEVEL

Los detalles deberán asociarse al LOD correspondiente.

---

# 81. CHARACTER LOD

Deberá existir:

```text
CharacterLODDefinition
CharacterLODGenerator
CharacterLODValidator
```

---

# 82. LOD COMPONENTS

Cada LOD podrá modificar:

```text
geometry
materials
bones
hair
clothing
facial_detail
collision
```

---

# 83. LOD BONE REDUCTION

Los huesos no esenciales podrán eliminarse progresivamente.

---

# 84. LOD DEFORMATION

Cada LOD deberá mantener deformaciones aceptables.

---

# 85. LOD POP DETECTION

Deberá existir detección de cambios visuales excesivos.

---

# 86. COLLISION

Deberá existir:

```text
CharacterCollisionDefinition
```

---

# 87. COLLISION TYPES

Mínimo:

```text
CAPSULE
BOX
SPHERE
CONVEX
CUSTOM
```

---

# 88. CHARACTER CAPSULE

Deberá permanecer compatible con las reglas globales de gameplay del proyecto.

---

# 89. COLLISION LAYERS

Deberán existir perfiles:

```text
PLAYER
NPC
ENEMY
BOSS
CREATURE
VEHICLE_INTERACTION
```

---

# 90. PHYSICS ASSETS

Deberá poder generarse:

```text
PhysicsAsset
```

a partir del skeleton.

---

# 91. PHYSICS VALIDATION

Deberá detectar:

```text
missing_body
invalid_joint
overlapping_bodies
excessive_body_count
invalid_mass
```

---

# 92. RAGDOLL

Deberá existir soporte para:

```text
ragdoll
partial_ragdoll
hit_reaction
```

---

# 93. HIT REACTION

Deberá poder asociarse reacción con:

```text
head
torso
arm
leg
hand
foot
custom
```

---

# 94. SOCKET SYSTEM

Deberán existir sockets configurables para:

```text
weapon
backpack
grenade
radio
helmet
armor
melee_weapon
attachment
custom
```

---

# 95. ANIMATION PROFILE

Deberá existir:

```text
AnimationProfile
```

---

# 96. ANIMATION COMPATIBILITY

El personaje deberá declarar:

```text
humanoid_class
skeleton_class
retarget_profile
root_motion_mode
```

---

# 97. RETARGETING

Deberá existir soporte para retargeting entre skeletons compatibles.

---

# 98. RETARGET VALIDATION

Deberá comprobar:

```text
bone_mapping
reference_pose
scale
orientation
IK
```

---

# 99. REFERENCE POSE

Cada personaje deberá tener una pose de referencia almacenada.

---

# 100. ANIMATION TESTS

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
AIM
SHOOT
MELEE
DEATH
HIT
```

---

# 101. ANIMATION DEFORMATION QA

Cada animación deberá generar métricas de:

```text
penetration
stretch
collapse
foot_sliding
hand_sliding
joint_error
```

---

# 102. FOOT SLIDING

Deberá detectarse automáticamente.

---

# 103. ROOT MOTION

Deberá existir validación de:

```text
root_translation
root_rotation
trajectory
```

---

# 104. CHARACTER SCALE

La escala deberá validarse contra:

```text
world_units
capsule
skeleton
weapon
environment
```

---

# 105. WEAPON COMPATIBILITY

El personaje deberá poder sostener armas compatibles con el sistema UAF.

---

# 106. WEAPON HAND ALIGNMENT

Deberá validarse la alineación:

```text
hand
weapon_socket
grip
trigger
```

---

# 107. TWO-HAND WEAPON

Deberá soportar armas que requieran:

```text
primary_hand
secondary_hand
```

---

# 108. CHARACTER-ENVIRONMENT TEST

Cada personaje deberá probarse con:

```text
stairs
slopes
doors
cover
vehicles
ladders
walls
```

cuando corresponda.

---

# 109. CHARACTER INTERSECTION TEST

Deberán detectarse intersecciones con elementos ambientales críticos.

---

# 110. PROCEDURAL VARIANTS

El sistema deberá generar variantes mediante:

```text
seed
body_parameters
face_parameters
clothing_parameters
material_parameters
hair_parameters
```

---

# 111. VARIANT DETERMINISM

La misma configuración deberá producir la misma variante lógica.

---

# 112. CHARACTER GENETIC / PARAMETRIC VARIATION

Deberá existir variación controlada para:

```text
height
mass
proportions
face
skin
hair
clothing
armor
materials
```

---

# 113. INVALID COMBINATIONS

Deberán detectarse combinaciones incompatibles:

```text
INVALID_CLOTHING
INVALID_BODY
INVALID_RIG
INVALID_HAIR
INVALID_EQUIPMENT
INVALID_SKELETON
```

---

# 114. CHARACTER ASSEMBLY

Deberá existir un ensamblador:

```text
CharacterAssembler
```

capaz de combinar:

```text
body
head
hair
clothing
armor
weapons
accessories
materials
rig
```

---

# 115. ASSEMBLY ORDER

El orden deberá ser determinista:

```text
BODY
HEAD
SKELETON
SKIN
CLOTHING
ARMOR
HAIR
FACIAL
ACCESSORIES
COLLISION
LOD
EXPORT
```

---

# 116. ASSET REUSE

Las partes compatibles deberán reutilizarse desde Asset Library.

---

# 117. PART COMPATIBILITY

Cada componente deberá declarar:

```text
skeleton_compatibility
scale_compatibility
material_compatibility
attachment_compatibility
```

---

# 118. CHARACTER MANIFEST

Deberá generarse un manifest completo:

```text
character_id
components
skeleton
rig
materials
clothing
hair
face
lods
collision
physics
animation_profile
export_profile
dependencies
hash
```

---

# 119. EXPORT FORMAT

Deberá existir salida compatible con:

```text
FBX
GLTF
GLB
USD
CUSTOM_INTERCHANGE
```

según capabilities disponibles.

---

# 120. UNREAL EXPORT

Deberá generarse información necesaria para:

```text
SKELETAL_MESH
SKELETON
PHYSICS_ASSET
MATERIALS
SOCKETS
LOD
MORPH_TARGETS
ANIMATION_COMPATIBILITY
```

---

# 121. IMPORT VALIDATION

El sistema deberá validar que el resultado exportado conserve:

```text
bone_count
bone_names
skin_weights
materials
morph_targets
sockets
scale
orientation
```

---

# 122. AXIS VALIDATION

Deberá respetarse el convenio global del proyecto:

```text
FORWARD = -Y
```

cuando el profile de Unreal lo requiera.

---

# 123. UNIT VALIDATION

Deberá verificarse conversión correcta a:

```text
CENTIMETERS
```

para Unreal.

---

# 124. CHARACTER PERFORMANCE BUDGET

Cada personaje deberá declarar:

```text
triangle_budget
bone_budget
material_slot_budget
texture_memory_budget
morph_target_budget
physics_body_budget
draw_call_budget
```

---

# 125. PERFORMANCE VALIDATION

Deberá medirse:

```text
triangles
vertices
bones
materials
textures
draw_calls
physics_bodies
morph_targets
memory
```

---

# 126. MOBILE / LOW-END PROFILE

Deberá existir profile opcional:

```text
LOW
MEDIUM
HIGH
CINEMATIC
```

---

# 127. CINEMATIC PROFILE

Podrá superar los budgets gameplay cuando explícitamente se autorice.

---

# 128. GAMEPLAY PROFILE

El profile gameplay deberá tener límites estrictos.

---

# 129. AUTOMATED CHARACTER QA

Cada personaje deberá ejecutar automáticamente:

```text
GEOMETRY_QA
SKELETON_QA
RIG_QA
SKIN_QA
CLOTHING_QA
HAIR_QA
FACIAL_QA
MATERIAL_QA
LOD_QA
COLLISION_QA
PHYSICS_QA
ANIMATION_QA
PERFORMANCE_QA
EXPORT_QA
```

---

# 130. HARD FAIL CONDITIONS

El personaje deberá ser rechazado ante:

```text
MISSING_SKELETON
BROKEN_HIERARCHY
INVALID_WEIGHT
ZERO_WEIGHT_VERTEX
ORPHAN_BONE_REFERENCE
SEVERE_DEFORMATION
CLOTHING_PENETRATION
HAIR_FAILURE
FACIAL_FAILURE
INVALID_LOD
INVALID_COLLISION
INVALID_PHYSICS
INVALID_SOCKET
ANIMATION_FAILURE
FOOT_SLIDING
SCALE_FAILURE
AXIS_FAILURE
EXPORT_FAILURE
PERFORMANCE_BUDGET_FAILURE
```

---

# 131. UNIT TESTS

Mínimo:

```text
test_character_definition
test_character_identity
test_body_profile
test_proportion_validation
test_landmarks
test_skeleton_definition
test_bone_definition
test_standard_skeleton
test_skeleton_extensions
test_bone_naming
test_bone_orientation
test_skeleton_symmetry
test_skeleton_symmetry_validation
test_rig_definition
test_rig_types
test_control_rig
test_ik
test_ik_validation
test_foot_ik
test_hand_ik
test_look_at
test_joint_limits
test_skinning_definition
test_weight_generation
test_weight_normalization
test_max_influences
test_zero_weight_vertices
test_orphan_weights
test_weight_validation
test_deformation_testing
test_deformation_error_detection
test_corrective_deformations
test_clothing_definition
test_clothing_generation
test_clothing_fit
test_clothing_clearance
test_clothing_intersection
test_clothing_topology
test_clothing_rigging
test_weight_transfer
test_cloth_deformation
test_cloth_simulation
test_armor_system
test_armor_deformation
test_armor_sockets
test_equipment_compatibility
test_hand_foot_system
test_finger_rig
test_hand_poses
test_face_definition
test_face_generation
test_face_validation
test_eye_system
test_eye_look
test_eyelid_system
test_mouth_system
test_teeth
test_tongue
test_facial_rig
test_facial_expressions
test_phonemes
test_blendshapes
test_blendshape_validation
test_hair_definition
test_hair_generation
test_hair_types
test_hair_profiles
test_hair_attachment
test_hair_collision
test_hair_lod
test_character_materials
test_skin_material
test_skin_variation
test_character_detail
test_detail_levels
test_character_lod
test_lod_components
test_lod_bone_reduction
test_lod_deformation
test_lod_pop_detection
test_collision
test_collision_types
test_character_capsule
test_collision_layers
test_physics_asset
test_physics_validation
test_ragdoll
test_hit_reaction
test_socket_system
test_animation_profile
test_animation_compatibility
test_retargeting
test_retarget_validation
test_reference_pose
test_animation_tests
test_animation_deformation
test_foot_sliding
test_root_motion
test_character_scale
test_weapon_compatibility
test_weapon_hand_alignment
test_two_hand_weapon
test_character_environment
test_character_intersection
test_procedural_variants
test_variant_determinism
test_parametric_variation
test_invalid_combinations
test_character_assembly
test_assembly_order
test_asset_reuse
test_part_compatibility
test_character_manifest
test_export_formats
test_unreal_export
test_import_validation
test_axis_validation
test_unit_validation
test_performance_budget
test_performance_validation
test_low_end_profile
test_cinematic_profile
test_gameplay_profile
test_automated_character_qa
```

---

# 132. INTEGRATION TESTS

Mínimo:

```text
test_body_to_skeleton
test_skeleton_to_rig
test_rig_to_skin
test_skin_to_clothing
test_clothing_to_rig
test_head_to_face
test_face_to_facial_rig
test_head_to_hair
test_character_to_materials
test_character_to_lod
test_character_to_collision
test_character_to_physics
test_character_to_animation
test_character_to_weapon
test_character_to_environment
test_character_to_asset_library
test_character_to_export
test_export_to_unreal_contract
```

---

# 133. FAILURE TESTS

Mínimo:

```text
test_missing_bone_failure
test_invalid_hierarchy_failure
test_invalid_weight_failure
test_zero_weight_failure
test_orphan_bone_failure
test_deformation_failure
test_clothing_intersection_failure
test_invalid_cloth_failure
test_invalid_armor_failure
test_invalid_socket_failure
test_face_failure
test_blendshape_failure
test_hair_failure
test_lod_failure
test_collision_failure
test_physics_failure
test_animation_failure
test_retarget_failure
test_foot_sliding_failure
test_weapon_alignment_failure
test_scale_failure
test_axis_failure
test_export_failure
test_performance_failure
```

---

# 134. DETERMINISM TESTS

Deberá comprobarse determinismo para:

```text
body_generation
skeleton_generation
rig_generation
weights
clothing
hair
face
materials
lod
collision
physics
assembly
export_manifest
```

---

# 135. PERFORMANCE TESTS

Mínimo:

```text
test_character_generation_time
test_rig_generation_time
test_skinning_time
test_clothing_time
test_hair_time
test_face_generation_time
test_lod_generation_time
test_export_time
test_memory_budget
test_triangle_budget
test_bone_budget
test_material_budget
test_texture_budget
test_physics_budget
test_morph_budget
```

---

# 136. GOLDEN CHARACTERS

Mínimo:

```text
GOLDEN_HUMAN_MALE
GOLDEN_HUMAN_FEMALE
GOLDEN_HEAVY_SOLDIER
GOLDEN_LIGHT_SOLDIER
GOLDEN_ROBOT
GOLDEN_ANDROID
GOLDEN_ALIEN
GOLDEN_CREATURE
GOLDEN_BOSS
GOLDEN_ARMORED_CHARACTER
```

---

# 137. GOLDEN CHARACTER VALIDATION

Deberá comprobar:

```text
geometry_hash
skeleton_hash
rig_hash
weight_hash
material_hash
clothing_hash
hair_hash
face_hash
lod_hash
manifest_hash
```

---

# 138. REGRESSION TESTS

Una modificación del generador no deberá alterar personajes golden sin:

```text
VERSION_CHANGE
MIGRATION
EXPLICIT_APPROVAL
```

---

# 139. CHARACTER VERSIONING

Deberán versionarse:

```text
generator_version
skeleton_version
rig_version
material_version
export_version
```

---

# 140. MIGRATION

Los personajes generados con versiones anteriores deberán poder:

```text
VALIDATE
MIGRATE
REGENERATE
```

cuando sea compatible.

---

# 141. CHECKPOINTS

Mínimo:

```text
BODY_COMPLETE
SKELETON_COMPLETE
RIG_COMPLETE
SKIN_COMPLETE
CLOTHING_COMPLETE
FACE_COMPLETE
HAIR_COMPLETE
MATERIALS_COMPLETE
LOD_COMPLETE
COLLISION_COMPLETE
PHYSICS_COMPLETE
ANIMATION_COMPLETE
QA_COMPLETE
EXPORT_COMPLETE
```

---

# 142. ROLLBACK

Cada checkpoint deberá poder restaurarse sin corromper los anteriores.

---

# 143. NO DESTRUCTIVE PIPELINE

Las etapas deberán conservar artefactos intermedios:

```text
body
skeleton
rig
weights
clothing
face
hair
materials
lod
collision
physics
```

cuando el retention profile lo permita.

---

# 144. CHARACTER REBUILD

Deberá ser posible regenerar únicamente:

```text
BODY
FACE
CLOTHING
HAIR
MATERIALS
RIG
LOD
```

sin reconstruir necesariamente todo el personaje.

---

# 145. DEPENDENCY GRAPH

El sistema deberá conocer las dependencias entre componentes.

Ejemplo:

```text
BODY
 ├── SKELETON
 │    ├── RIG
 │    ├── SKIN
 │    └── PHYSICS
 ├── CLOTHING
 ├── FACE
 └── HAIR
```

---

# 146. INVALIDATION

Cuando un componente cambie, solamente deberán invalidarse sus dependientes.

---

# 147. CHARACTER CACHE

Deberá existir cache para:

```text
body
skeleton
rig
weights
clothing
face
hair
materials
lod
physics
export
```

---

# 148. SECURITY / GOVERNANCE

Ninguna operación deberá modificar assets protegidos fuera del ModificationScope autorizado.

---

# 149. OPERATION LOGGING

Toda operación destructiva deberá registrar:

```text
operation_id
character_id
component
before_hash
after_hash
scope
timestamp
result
```

---

# 150. ARTISTIC QUALITY GATE

Además de validaciones técnicas deberá existir validación artística.

Podrá rechazar:

```text
BAD_SILHOUETTE
UNNATURAL_PROPORTION
VISUAL_ARTIFACT
LOW_DETAIL
MATERIAL_INCONSISTENCY
BAD_FACE
BAD_CLOTHING
BAD_HAIR
```

---

# 151. TECHNICAL QUALITY GATE

Deberá rechazar:

```text
INVALID_TOPOLOGY
INVALID_RIG
INVALID_SKIN
INVALID_LOD
INVALID_COLLISION
INVALID_PHYSICS
INVALID_EXPORT
```

---

# 152. GAMEPLAY QUALITY GATE

Deberá comprobar:

```text
CAPSULE
NAVIGATION
WEAPON_HANDLING
COVER
DOORS
STAIRS
SLOPES
ANIMATION
```

---

# 153. UNREAL QUALITY GATE

Deberá comprobar:

```text
SKELETAL_MESH
SKELETON
PHYSICS_ASSET
MATERIALS
SOCKETS
LODS
MORPHS
SCALE
AXIS
IMPORT_CONTRACT
```

---

# 154. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
140 UNIT TESTS
35 INTEGRATION TESTS
25 FAILURE TESTS
25 DETERMINISM TESTS
20 PERFORMANCE TESTS
15 GOLDEN TESTS
20 REGRESSION TESTS
```

Total mínimo:

```text
280 TESTS
```

---

# 155. DEFINITION OF DONE

La fase estará completa únicamente cuando:

```text
CHARACTER_SCHEMA_IMPLEMENTED
BODY_SYSTEM_IMPLEMENTED
LANDMARK_SYSTEM_IMPLEMENTED
SKELETON_SYSTEM_IMPLEMENTED
RIG_SYSTEM_IMPLEMENTED
IK_SYSTEM_IMPLEMENTED
FK_SYSTEM_IMPLEMENTED
LOOK_AT_IMPLEMENTED
JOINT_LIMITS_IMPLEMENTED
SKINNING_IMPLEMENTED
WEIGHT_GENERATION_IMPLEMENTED
WEIGHT_VALIDATION_IMPLEMENTED
DEFORMATION_QA_IMPLEMENTED
CORRECTIVE_DEFORMATIONS_IMPLEMENTED
CLOTHING_SYSTEM_IMPLEMENTED
CLOTHING_FIT_IMPLEMENTED
CLOTHING_RIGGING_IMPLEMENTED
CLOTH_SUPPORT_IMPLEMENTED
ARMOR_SYSTEM_IMPLEMENTED
SOCKET_SYSTEM_IMPLEMENTED
HAND_SYSTEM_IMPLEMENTED
FACE_SYSTEM_IMPLEMENTED
EYE_SYSTEM_IMPLEMENTED
MOUTH_SYSTEM_IMPLEMENTED
FACIAL_RIG_IMPLEMENTED
BLENDSHAPES_IMPLEMENTED
HAIR_SYSTEM_IMPLEMENTED
CHARACTER_MATERIALS_IMPLEMENTED
CHARACTER_DETAIL_IMPLEMENTED
CHARACTER_LOD_IMPLEMENTED
COLLISION_IMPLEMENTED
PHYSICS_ASSET_IMPLEMENTED
RAGDOLL_IMPLEMENTED
ANIMATION_PROFILE_IMPLEMENTED
RETARGETING_IMPLEMENTED
ANIMATION_QA_IMPLEMENTED
WEAPON_COMPATIBILITY_IMPLEMENTED
ENVIRONMENT_COMPATIBILITY_IMPLEMENTED
PROCEDURAL_VARIANTS_IMPLEMENTED
CHARACTER_ASSEMBLY_IMPLEMENTED
ASSET_REUSE_IMPLEMENTED
CHARACTER_MANIFEST_IMPLEMENTED
UNREAL_EXPORT_IMPLEMENTED
IMPORT_VALIDATION_IMPLEMENTED
PERFORMANCE_BUDGETS_IMPLEMENTED
AUTOMATED_QA_IMPLEMENTED
CHECKPOINTS_IMPLEMENTED
ROLLBACK_IMPLEMENTED
CACHE_IMPLEMENTED
VERSIONING_IMPLEMENTED
MIGRATION_IMPLEMENTED
ARTISTIC_QA_IMPLEMENTED
TECHNICAL_QA_IMPLEMENTED
GAMEPLAY_QA_IMPLEMENTED
UNREAL_QA_IMPLEMENTED
UNIT_TESTS_IMPLEMENTED
INTEGRATION_TESTS_IMPLEMENTED
FAILURE_TESTS_IMPLEMENTED
DETERMINISM_TESTS_IMPLEMENTED
PERFORMANCE_TESTS_IMPLEMENTED
GOLDEN_TESTS_IMPLEMENTED
REGRESSION_TESTS_IMPLEMENTED
DOCUMENTATION_COMPLETE
```

---

# 156. NEXT PHASE

```text
UAF-81.38 — PROFESSIONAL TEXTURE, MATERIAL, SURFACE, DECAL & PROCEDURAL LOOK-DEVELOPMENT SYSTEM
```

Esta fase deberá convertir geometría y assets en superficies de producción mediante:

```text
PBR
MATERIAL_INSTANCES
TEXTURE_GENERATION
BAKE
UDIM
TRIM_SHEETS
DECALS
MASKS
NORMALS
ROUGHNESS
METALLIC
AO
EMISSIVE
SUBSURFACE
TRANSLUCENCY
WEAR
DAMAGE
DIRT
DUST
WETNESS
SNOW
CORRUPTION
PROCEDURAL_VARIATION
TEXTURE_MEMORY_BUDGET
UNREAL_MATERIAL_EXPORT
```

También deberá incluir pruebas automáticas de **consistencia visual, escala física, canales PBR, resolución, compresión, seams, UVs, tiling, mipmaps, material instances y presupuesto de memoria**.
