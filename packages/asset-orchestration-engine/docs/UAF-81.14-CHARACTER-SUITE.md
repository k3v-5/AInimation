# UAF-81.14 — CHARACTER FABRICATION & DEFORMATION SYSTEM

## UAF-81.14-ARCH

### ARQUITECTURA DEL SISTEMA PROFESIONAL DE FABRICACIÓN, RIGGING, SKINNING Y VARIACIÓN DE PERSONAJES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.14 — Character Fabrication & Deformation System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.13  
**Next Phase:** UAF-81.15  

---

# 1. PURPOSE

UAF-81.14 define el sistema responsable de fabricar personajes 3D profesionales destinados a videojuegos y experiencias interactivas.

El sistema deberá soportar:

```text
HUMANOID
CREATURE
ROBOT
ANDROID
ALIEN
MUTANT
MONSTER
BOSS
NPC
PLAYER
```

El sistema deberá resolver simultáneamente:

```text
ANATOMY
PROPORTIONS
FACE
HANDS
FEET
BODY
CLOTHING
ARMOR
ACCESSORIES
HAIR
MATERIALS
RIG
SKINNING
DEFORMATION
MORPH TARGETS
LOD
COLLISION
SOCKETS
VARIANTS
EXPORT
VALIDATION
```

---

# 2. PRIMARY OBJECTIVE

El objetivo no es generar una malla compleja.

El objetivo es fabricar un personaje que pueda entrar en producción.

Por tanto:

```text
CHARACTER FABRICATION
=
GEOMETRY
+
MATERIALS
+
RIG
+
SKIN
+
DEFORMATION
+
COLLISION
+
SOCKETS
+
LOD
+
VARIANTS
+
GAMEPLAY METADATA
+
EXPORT
```

---

# 3. CORE PRINCIPLE

El personaje deberá construirse mediante capas independientes.

```text
CHARACTER INTENT
↓
CHARACTER PROFILE
↓
BODY MODEL
↓
FACE MODEL
↓
EXTREMITIES
↓
CLOTHING
↓
ARMOR
↓
ACCESSORIES
↓
HAIR
↓
MATERIALS
↓
RIG
↓
SKINNING
↓
DEFORMATION
↓
MORPHS
↓
LOD
↓
COLLISION
↓
SOCKETS
↓
VARIANTS
↓
VALIDATION
↓
UNREAL EXPORT
```

---

# 4. CHARACTER PROFILE

Deberá existir:

```text
CharacterProfile
```

---

# 5. CHARACTER PROFILE CONTENT

Mínimo:

```text
character_id
character_type
species
sex_presentation
height
body_mass
body_proportions
style
silhouette
face_profile
material_profile
clothing_profile
armor_profile
hair_profile
rig_profile
animation_profile
lod_profile
collision_profile
gameplay_profile
```

---

# 6. CHARACTER CLASSIFICATION

El sistema deberá diferenciar:

```text
HERO
PLAYER
NPC
ENEMY
ELITE
BOSS
CREATURE
PROP_CHARACTER
```

---

# 7. QUALITY TIERS

Deberán existir como mínimo:

```text
PROXY
GAMEPLAY
STANDARD
HIGH
HERO
CINEMATIC
```

---

# 8. QUALITY TIER BEHAVIOR

Cada tier deberá controlar:

```text
geometry
texture_resolution
material_complexity
hair
face_detail
deformation_quality
lod_count
```

---

# 9. BODY ARCHITECTURE

El cuerpo no deberá generarse como una única superficie monolítica obligatoriamente.

Deberá soportarse:

```text
MODULAR BODY
UNIFIED BODY
HYBRID BODY
```

---

# 10. BODY MODULES

Mínimo:

```text
head
neck
torso
pelvis
upper_arm_L
upper_arm_R
forearm_L
forearm_R
hand_L
hand_R
thigh_L
thigh_R
calf_L
calf_R
foot_L
foot_R
```

---

# 11. BODY LANDMARKS

Deberán existir landmarks normalizados:

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
hip_L
hip_R
knee_L
knee_R
ankle_L
ankle_R
```

---

# 12. PROPORTION SYSTEM

Las proporciones deberán ser paramétricas.

Mínimo:

```text
height
shoulder_width
chest_depth
waist_width
hip_width
arm_length
leg_length
head_size
hand_size
foot_size
```

---

# 13. PROPORTION NORMALIZATION

Las dimensiones deberán expresarse preferentemente como ratios respecto a la altura del personaje.

---

# 14. ANATOMICAL CONSTRAINTS

El sistema deberá impedir proporciones inválidas cuando el profile sea humanoide realista.

---

# 15. STYLE PROFILES

Deberán soportarse:

```text
REALISTIC
SEMI_REALISTIC
STYLIZED
EXAGGERATED
INDUSTRIAL
BIO_MECHANICAL
ALIEN
```

---

# 16. BODY GENERATION STRATEGIES

Deberán existir:

```text
PRIMITIVE_ASSEMBLY
MODULAR_MESH
PARAMETRIC_MESH
SCULPTED_BASE
HYBRID
IMPORTED_BASE
```

---

# 17. PRIMITIVE ASSEMBLY

La estrategia actual basada en primitivas deberá permanecer soportada.

No será eliminada.

---

# 18. MODULAR MESH

Permitirá ensamblar cuerpos mediante piezas de mayor resolución.

---

# 19. PARAMETRIC MESH

Permitirá deformar una topología base según parámetros anatómicos.

---

# 20. HYBRID GENERATION

La estrategia recomendada para personajes complejos será:

```text
PARAMETRIC BODY
+
MODULAR PARTS
+
SPECIALIZED DETAIL
```

---

# 21. TOPOLOGY POLICY

La topología deberá clasificarse:

```text
ANATOMICAL
MECHANICAL
CLOTHING
HARD_SURFACE
ORGANIC
HAIR
ACCESSORY
```

---

# 22. DEFORMATION TOPOLOGY

Las zonas sometidas a deformación extrema deberán priorizar topología compatible con deformación.

---

# 23. JOINT TOPOLOGY

Mínimo:

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

deberán tener suficiente resolución para deformación.

---

# 24. FACE SYSTEM

Deberá existir:

```text
FaceFabricationSystem
```

---

# 25. FACE ARCHITECTURE

La cara deberá poder construirse mediante:

```text
FACE_BASE
FEATURE_MODULES
SURFACE_DETAIL
EXPRESSIONS
```

---

# 26. FACE FEATURES

Mínimo:

```text
eyes
eyelids
brows
nose
mouth
lips
ears
jaw
cheeks
forehead
```

---

# 27. FACE VARIATION

Las características faciales deberán poder variar independientemente.

---

# 28. FACE PARAMETERS

Mínimo:

```text
eye_spacing
eye_size
nose_width
nose_length
jaw_width
jaw_height
cheek_volume
lip_width
lip_thickness
ear_size
```

---

# 29. FACE SYMMETRY

La simetría deberá ser configurable:

```text
SYMMETRIC
ASYMMETRIC
CONTROLLED_ASYMMETRY
```

---

# 30. ASYMMETRY

La asimetría deberá generarse mediante parámetros reproducibles.

---

# 31. EYE SYSTEM

Los ojos deberán ser componentes independientes cuando el target lo requiera.

---

# 32. EYE COMPONENTS

Mínimo:

```text
eyeball
iris
pupil
cornea
sclera
```

---

# 33. EYE RIG

Los ojos deberán poder apuntar independientemente.

---

# 34. EYE VALIDATION

Deberá comprobarse:

```text
alignment
occlusion
rotation
socket_fit
```

---

# 35. MOUTH SYSTEM

Deberá existir una arquitectura compatible con deformaciones de habla y expresiones.

---

# 36. TEETH

Los dientes deberán ser un módulo independiente.

---

# 37. TONGUE

La lengua podrá ser un módulo independiente cuando el profile lo requiera.

---

# 38. EAR SYSTEM

Las orejas deberán soportar variantes anatómicas.

---

# 39. HAND SYSTEM

Las manos deberán dejar de depender exclusivamente de primitivas simples.

---

# 40. HAND ARCHITECTURE

Mínimo:

```text
palm
thumb
index
middle
ring
little
```

---

# 41. FINGER SEGMENTS

Cada dedo deberá soportar:

```text
proximal
middle
distal
```

excepto el pulgar cuando la anatomía seleccionada requiera una estructura diferente.

---

# 42. HAND DEFORMATION

Las manos deberán poder cerrarse en:

```text
OPEN
RELAXED
FIST
GRIP
POINT
WEAPON_GRIP
```

---

# 43. FOOT SYSTEM

Los pies deberán ser módulos independientes.

---

# 44. FOOT PARAMETERS

Mínimo:

```text
length
width
arch
toe_length
heel_size
```

---

# 45. CLOTHING SYSTEM

Deberá existir:

```text
ClothingFabricationSystem
```

---

# 46. CLOTHING ARCHITECTURE

La ropa deberá tratarse como geometría funcional, no como simple textura.

---

# 47. CLOTHING LAYERS

Mínimo:

```text
UNDERLAYER
BASE
OUTER
PROTECTIVE
ACCESSORY
```

---

# 48. CLOTHING TYPES

Mínimo:

```text
shirt
pants
jacket
coat
boots
gloves
hood
belt
backpack
uniform
```

---

# 49. CLOTHING FIT

Cada pieza deberá declarar:

```text
target_body_profile
fit_region
clearance
deformation_policy
```

---

# 50. CLOTHING CLEARANCE

La ropa deberá evitar penetración con el cuerpo.

---

# 51. CLOTHING DEFORMATION

La ropa deberá poder deformarse junto con el skeleton.

---

# 52. CLOTHING SIMULATION

Cuando sea necesario deberá soportarse:

```text
CLOTH_SIM
SKINNED_CLOTH
HYBRID
```

---

# 53. CLOTHING COLLISION

La simulación de ropa deberá utilizar collision proxies definidos explícitamente.

---

# 54. ARMOR SYSTEM

Deberá existir:

```text
ArmorFabricationSystem
```

---

# 55. ARMOR MODULES

Mínimo:

```text
helmet
chest
shoulder
forearm
glove
thigh
knee
shin
boot
back
```

---

# 56. ARMOR SOCKETS

Cada pieza podrá declarar sockets.

---

# 57. ARMOR FIT

La armadura deberá adaptarse a:

```text
body_profile
clothing_layers
skeleton
```

---

# 58. HARD SURFACE DEFORMATION

Las piezas rígidas no deberán deformarse como piel.

Deberán utilizar:

```text
rigid_attachment
bone_attachment
weighted_sections
```

según el diseño.

---

# 59. ACCESSORY SYSTEM

Deberá existir:

```text
AccessorySystem
```

---

# 60. ACCESSORY TYPES

Mínimo:

```text
weapon
holster
radio
grenade
backpack
helmet_attachment
visor
utility
ornament
```

---

# 61. SOCKET STANDARD

Los sockets deberán utilizar nombres normalizados.

Mínimo:

```text
socket_weapon_R
socket_weapon_L
socket_back
socket_head
socket_helmet
socket_hip_R
socket_hip_L
socket_spine
socket_hand_R
socket_hand_L
```

---

# 62. SOCKET TRANSFORM

Cada socket deberá contener:

```text
position
rotation
scale
parent_bone
```

---

# 63. HAIR SYSTEM

Deberá existir:

```text
HairFabricationSystem
```

---

# 64. HAIR STRATEGIES

Mínimo:

```text
CARDS
GROOM
MESH
HYBRID
```

---

# 65. HAIR PROFILE

Deberá controlar:

```text
density
length
roughness
curl
color
variation
```

---

# 66. HAIR DEFORMATION

Deberá soportarse deformación básica para movimiento.

---

# 67. MATERIAL SYSTEM

Cada personaje deberá poder utilizar múltiples materiales.

---

# 68. MATERIAL DOMAINS

Mínimo:

```text
skin
metal
plastic
rubber
fabric
leather
glass
ceramic
energy
organic
```

---

# 69. SKIN MATERIAL

La piel deberá soportar:

```text
base_color
roughness
subsurface
normal
microdetail
variation
```

---

# 70. MATERIAL VARIATION

Las variantes deberán poder cambiar:

```text
color
roughness
wear
damage
age
dirt
```

sin duplicar innecesariamente geometría.

---

# 71. DECAL SYSTEM

Deberá existir soporte para:

```text
scars
logos
faction_marks
damage
dirt
identification
```

---

# 72. DAMAGE SYSTEM

El daño visual deberá poder representar:

```text
scratches
dents
burns
cuts
fractures
missing_panels
```

---

# 73. DAMAGE NON-DESTRUCTIVE POLICY

Siempre que sea posible, el daño visual deberá ser representado mediante capas no destructivas.

---

# 74. RIG SYSTEM

Deberá existir:

```text
CharacterRigSystem
```

---

# 75. RIG TYPES

Mínimo:

```text
HUMANOID
CREATURE
QUADRUPED
ROBOT
CUSTOM
```

---

# 76. HUMANOID SKELETON

Deberá existir una convención estable de nombres.

Mínimo:

```text
root
pelvis
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
thigh_R
calf_R
foot_R
```

---

# 77. FINGER BONES

Cuando el target lo requiera:

```text
thumb
index
middle
ring
little
```

con segmentos correspondientes.

---

# 78. FACIAL RIG

Deberá soportarse:

```text
BONE_FACE
BLENDSHAPE_FACE
HYBRID_FACE
```

---

# 79. CONTROL RIG

Deberá existir una separación conceptual entre:

```text
DEFORMATION SKELETON
CONTROL RIG
```

---

# 80. IK

Deberán soportarse:

```text
arm_IK
leg_IK
hand_IK
foot_IK
```

según profile.

---

# 81. FK

El rig deberá permitir control FK donde sea necesario.

---

# 82. IK/FK

Los miembros principales deberán poder cambiar entre IK y FK si el profile lo requiere.

---

# 83. POLE VECTORS

Las cadenas IK deberán tener controles de orientación.

---

# 84. FOOT RIG

Deberá soportarse:

```text
heel
toe
ball
bank
```

cuando el rig lo requiera.

---

# 85. RETARGETING

El skeleton deberá poder mapearse a un skeleton objetivo mediante:

```text
SkeletonMapping
```

---

# 86. SKELETON MAPPING

Deberá registrar:

```text
source_bone
target_bone
translation_policy
rotation_policy
scale_policy
```

---

# 87. SKINNING SYSTEM

Deberá existir:

```text
SkinningSystem
```

---

# 88. WEIGHT GENERATION

Deberá soportarse:

```text
AUTO_WEIGHT
HEAT_WEIGHT
DISTANCE_WEIGHT
GEODESIC_WEIGHT
TRANSFER_WEIGHT
MANUAL_OVERRIDE
```

---

# 89. WEIGHT NORMALIZATION

Los pesos deberán normalizarse por vértice.

---

# 90. MAX INFLUENCES

El profile deberá definir el máximo número de influencias por vértice.

---

# 91. WEIGHT VALIDATION

Deberá detectar:

```text
unweighted_vertices
overweighted_vertices
invalid_bones
isolated_influences
```

---

# 92. DEFORMATION TEST

Cada personaje deberá pasar poses de prueba.

Mínimo:

```text
T_POSE
A_POSE
ARM_RAISE
ELBOW_BEND
KNEE_BEND
SQUAT
CROUCH
WALK_PROXY
```

---

# 93. DEFORMATION METRICS

Se deberán medir:

```text
volume_loss
intersection
stretch
collapse
```

---

# 94. DEFORMATION THRESHOLDS

Cada quality tier deberá definir tolerancias.

---

# 95. CLOTHING DEFORMATION TEST

La ropa deberá probarse en las mismas poses críticas.

---

# 96. ARMOR COLLISION TEST

La armadura deberá comprobar penetraciones contra:

```text
body
clothing
other armor
```

---

# 97. FACE EXPRESSION SYSTEM

Deberá existir:

```text
FacialExpressionSystem
```

---

# 98. EXPRESSION TYPES

Mínimo:

```text
neutral
smile
anger
fear
pain
surprise
blink
jaw_open
```

---

# 99. MORPH TARGETS

Deberán poder generarse:

```text
expression
phoneme
corrective
asymmetry
damage
```

---

# 100. CORRECTIVE MORPHS

Cuando una deformación produzca resultados visualmente deficientes, podrá utilizarse un corrective morph.

---

# 101. MORPH NAMING

Los morph targets deberán seguir una convención estable.

---

# 102. MORPH VALIDATION

Cada morph deberá comprobar:

```text
range
vertex_count
topology_compatibility
visual_result
```

---

# 103. ANIMATION COMPATIBILITY

El personaje deberá generar metadata suficiente para animación.

---

# 104. ANIMATION PROFILE

Mínimo:

```text
locomotion
combat
idle
interaction
facial
```

---

# 105. COLLISION SYSTEM

Deberá existir:

```text
CharacterCollisionSystem
```

---

# 106. COLLISION REPRESENTATION

Deberá soportarse:

```text
capsule
sphere
box
convex
custom_proxy
```

---

# 107. COLLISION LAYERS

Deberán distinguirse:

```text
GAMEPLAY_COLLISION
PHYSICS_COLLISION
RAGDOLL_COLLISION
TRACE_COLLISION
```

---

# 108. RAGDOLL

Cuando el profile lo requiera deberá generarse:

```text
ragdoll_bodies
ragdoll_constraints
```

---

# 109. RAGDOLL VALIDATION

Deberán comprobarse:

```text
bone_alignment
constraint_limits
penetration
stability
```

---

# 110. LOD SYSTEM

Deberá existir:

```text
CharacterLODSystem
```

---

# 111. LOD LEVELS

Mínimo:

```text
LOD0
LOD1
LOD2
LOD3
LOD4
```

---

# 112. LOD STRATEGY

La reducción deberá preservar:

```text
silhouette
recognition
critical deformation
```

---

# 113. HERO LOD

LOD0 de personajes hero deberá priorizar:

```text
face
hands
silhouette
armor
cloth
```

---

# 114. LOD REDUCTION

Deberá reducir progresivamente:

```text
geometry
materials
microdetail
hair
accessories
```

---

# 115. MATERIAL LOD

Los materiales podrán simplificarse en LODs lejanos.

---

# 116. TEXTURE LOD

Las resoluciones deberán adaptarse al distance profile.

---

# 117. NANITE

Los componentes compatibles podrán utilizar Nanite.

---

# 118. NANITE VALIDATION

La utilización de Nanite deberá depender del target profile.

---

# 119. CHARACTER VARIANT SYSTEM

Deberá existir:

```text
CharacterVariantSystem
```

---

# 120. VARIANT DIMENSIONS

Las variantes podrán modificar:

```text
body
face
hair
clothing
armor
materials
accessories
damage
color
faction
```

---

# 121. VARIANT SEED

Cada variante deberá ser reproducible.

---

# 122. VARIANT SHARING

Las variantes deberán compartir recursos cuando sea posible.

---

# 123. NO DUPLICATION

No se deberán duplicar mallas o texturas cuando únicamente cambie un parámetro material.

---

# 124. FACTION SYSTEM

Los personajes podrán pertenecer a una facción.

---

# 125. FACTION VISUAL PROFILE

La facción podrá controlar:

```text
colors
logos
armor
clothing
weapons
materials
decals
```

---

# 126. ROLE SYSTEM

El personaje podrá declarar:

```text
assault
tank
medic
sniper
engineer
support
boss
civilian
```

---

# 127. ROLE VISUALIZATION

El role podrá influir sobre equipamiento y silueta.

---

# 128. EQUIPMENT COMPATIBILITY

El personaje deberá validar que sus sockets aceptan el equipamiento seleccionado.

---

# 129. WEAPON COMPATIBILITY

El sistema deberá comprobar:

```text
hand_socket
grip
weapon_scale
animation_compatibility
```

---

# 130. BACKPACK COMPATIBILITY

Deberá comprobar:

```text
spine_socket
collision
armor_intersection
```

---

# 131. CHARACTER SEMANTICS

Cada componente deberá tener tags.

Ejemplo:

```text
character:human
role:assault
faction:industrial
equipment:rifle
armor:heavy
```

---

# 132. ASSET GRAPH INTEGRATION

Los componentes del personaje deberán registrarse en SemanticAssetGraph.

---

# 133. DEPENDENCY GRAPH

Deberá existir una relación explícita:

```text
body
→ clothing
→ armor
→ accessories
→ rig
→ skin
→ lod
→ export
```

---

# 134. CHANGE INVALIDATION

Cambiar:

```text
body_height
```

deberá invalidar los componentes dependientes.

---

# 135. MATERIAL-ONLY CHANGE

Cambiar únicamente material no deberá regenerar:

```text
rig
skin
geometry
```

salvo dependencia explícita.

---

# 136. ACCESSORY CHANGE

Cambiar un accesorio no deberá regenerar el cuerpo.

---

# 137. FACE CHANGE

Modificar la cara deberá invalidar únicamente lo necesario.

---

# 138. RIG CHANGE

Modificar el skeleton deberá invalidar:

```text
skin
deformation_tests
animation_metadata
export
```

---

# 139. CHARACTER BUILD GRAPH

Deberá existir:

```text
CharacterBuildGraph
```

---

# 140. BUILD NODES

Mínimo:

```text
BodyNode
FaceNode
ClothingNode
ArmorNode
AccessoryNode
HairNode
MaterialNode
RigNode
SkinNode
MorphNode
LODNode
CollisionNode
ExportNode
```

---

# 141. BUILD ORDER

El sistema deberá respetar dependencias topológicas.

---

# 142. PARALLELIZATION

Los nodos independientes podrán ejecutarse en paralelo.

---

# 143. CACHE

Cada nodo deberá poder producir un resultado cacheable.

---

# 144. CACHE KEY

La cache deberá depender de:

```text
node_type
node_version
input_hash
profile_version
asset_versions
seed
```

---

# 145. FAILURE ISOLATION

Un fallo de HairNode no deberá invalidar BodyNode.

---

# 146. CHECKPOINTS

Mínimo:

```text
body
face
clothing
armor
materials
rig
skin
morph
lod
collision
export
```

---

# 147. CHARACTER MANIFEST

Deberá existir:

```text
CharacterManifest
```

---

# 148. MANIFEST CONTENT

Mínimo:

```text
character_id
character_type
profile
seed
body_assets
face_assets
clothing_assets
armor_assets
accessories
materials
skeleton
skin
morphs
lods
collision
sockets
variants
validation
generator_version
```

---

# 149. EXPORT TARGETS

El sistema deberá poder generar artefactos destinados a:

```text
UNREAL
BLENDER
FBX
GLTF
INTERNAL_CACHE
```

según target profile.

---

# 150. UNREAL CHARACTER EXPORT

El export deberá preservar:

```text
skeletal_mesh
skeleton
materials
physics_asset
morph_targets
sockets
LOD
metadata
```

---

# 151. EXPORT VALIDATION

Antes de exportar deberá comprobarse:

```text
skeleton
weights
materials
morphs
sockets
collision
LOD
scale
axis
```

---

# 152. SCALE

El personaje deberá respetar la escala mundial definida por AOE.

---

# 153. AXIS

El exportador deberá aplicar el convenio de ejes definido por el proyecto.

---

# 154. ZERO CLIPPING

El sistema deberá comprobar intersecciones entre:

```text
body
clothing
armor
accessories
hair
```

---

# 155. CLIPPING THRESHOLD

Deberá existir una tolerancia configurable.

---

# 156. SILHOUETTE VALIDATION

Cada personaje deberá generar vistas:

```text
front
back
left
right
three_quarter
gameplay
```

---

# 157. HERO VALIDATION

Los personajes HERO deberán añadir:

```text
face_closeup
hands_closeup
armor_closeup
material_closeup
```

---

# 158. AUTOMATED CHARACTER QA

Deberán existir validadores para:

```text
geometry
topology
scale
orientation
clipping
weights
deformation
materials
LOD
collision
sockets
export
```

---

# 159. ARTISTIC QA

También deberán evaluarse:

```text
silhouette
proportion
visual hierarchy
material readability
color balance
detail distribution
```

---

# 160. PERFORMANCE QA

Deberán medirse:

```text
triangle_count
vertex_count
material_slots
texture_memory
bone_count
morph_count
draw_call_estimate
LOD_cost
```

---

# 161. BUDGET PROFILES

Deberán existir presupuestos específicos para:

```text
MOBILE
LOW
MID
HIGH
AAA
HERO
CINEMATIC
```

---

# 162. BUDGET ENFORCEMENT

Superar un presupuesto deberá producir:

```text
WARNING
ERROR
REJECT
AUTO_OPTIMIZE
```

según profile.

---

# 163. AUTO OPTIMIZATION

Cuando esté habilitado podrá:

```text
reduce_geometry
merge_materials
reduce_texture_resolution
remove_hidden_geometry
simplify_accessories
```

---

# 164. AUTO OPTIMIZATION SAFETY

No podrá modificar silenciosamente:

```text
character_identity
skeleton_semantics
critical_sockets
gameplay_collision
```

---

# 165. HIDDEN GEOMETRY

La geometría completamente oculta podrá eliminarse únicamente cuando no afecte:

```text
deformation
collision
future equipment
```

---

# 166. TEXTURE SYSTEM

El personaje deberá soportar:

```text
base_color
normal
roughness
metallic
ao
subsurface
mask
detail
emissive
```

---

# 167. TEXTURE RESOLUTION

Deberá poder declararse:

```text
512
1024
2048
4096
8192
```

según quality tier.

---

# 168. UDIM

Los personajes HERO/CINEMATIC deberán poder utilizar UDIM cuando el target lo requiera.

---

# 169. TEXTURE PACKING

Deberá poder combinar canales para optimizar memoria.

---

# 170. TEXTURE VARIANTS

Las variantes deberán poder reutilizar mapas mediante máscaras.

---

# 171. MATERIAL INSTANCE STRATEGY

El sistema deberá favorecer Material Instances sobre duplicación de materiales base.

---

# 172. PROCEDURAL DETAIL

El microdetalle podrá generarse proceduralmente siempre que sea reproducible.

---

# 173. BAKE SYSTEM

Deberá existir soporte conceptual para:

```text
high_to_low
normal_bake
ao_bake
curvature_bake
mask_bake
```

---

# 174. BAKE VALIDATION

Deberá detectar:

```text
missing_uv
invalid_cage
projection_error
seams
```

---

# 175. UV SYSTEM

Deberá existir:

```text
CharacterUVSystem
```

---

# 176. UV REQUIREMENTS

Deberá validar:

```text
overlap
stretch
coverage
padding
texel_density
```

---

# 177. TEXEL DENSITY

La densidad deberá ser configurable por quality tier.

---

# 178. CHARACTER IDENTITY

Cada personaje deberá poseer un conjunto de parámetros que defina su identidad.

---

# 179. IDENTITY VECTOR

Conceptualmente:

```text
body
face
hair
clothing
armor
materials
colors
accessories
```

deberán poder representarse como un IdentityProfile.

---

# 180. IDENTITY STABILITY

Una modificación de LOD no deberá alterar la identidad visual fundamental.

---

# 181. CHARACTER RANDOMIZATION

La generación procedural podrá producir variantes, pero deberá utilizar restricciones.

---

# 182. RANDOMIZATION CONSTRAINTS

Ejemplo:

```text
height_range
body_mass_range
face_range
color_palette
equipment_pool
faction_rules
```

---

# 183. INVALID COMBINATIONS

El sistema deberá rechazar combinaciones incompatibles.

Ejemplo:

```text
armor_A
+
body_profile_B
=
INVALID
```

cuando exista conflicto geométrico o funcional.

---

# 184. CHARACTER GENERATION MODES

Mínimo:

```text
EXACT
PARAMETRIC
VARIANT
RANDOMIZED
HYBRID
```

---

# 185. EXACT MODE

Deberá reproducir exactamente el profile solicitado.

---

# 186. PARAMETRIC MODE

Permitirá modificar parámetros explícitos.

---

# 187. VARIANT MODE

Generará una variante a partir de un personaje base.

---

# 188. RANDOMIZED MODE

Generará personajes dentro de constraints.

---

# 189. HYBRID MODE

Combinará componentes importados con componentes generados.

---

# 190. CHARACTER LIBRARY

Todos los componentes reutilizables deberán registrarse en AssetLibrary.

---

# 191. COMPONENT LIBRARY

Deberá existir categorización:

```text
BODY
FACE
EYES
HAIR
CLOTHING
ARMOR
ACCESSORY
WEAPON
MATERIAL
DECAL
```

---

# 192. COMPONENT COMPATIBILITY

Cada componente deberá declarar compatibilidades.

---

# 193. COMPATIBILITY MATRIX

El sistema deberá poder consultar:

```text
component_A
compatible_with
component_B
```

---

# 194. VERSIONING

Cada componente deberá tener:

```text
component_id
version
compatibility_version
```

---

# 195. DEPRECATION

Los componentes obsoletos deberán poder marcarse:

```text
ACTIVE
DEPRECATED
BLOCKED
```

---

# 196. MIGRATION

Deberá existir estrategia de migración cuando cambie la estructura de un componente.

---

# 197. GOLDEN CHARACTERS

Deberán existir personajes golden:

```text
HUMAN_HERO
HUMAN_NPC
HEAVY_ROBOT
LIGHT_ROBOT
ALIEN
CREATURE
BOSS
```

---

# 198. GOLDEN TEST

Cada golden character deberá comprobar todo el pipeline.

---

# 199. REGRESSION TEST

Los cambios de generación deberán compararse contra golden results.

---

# 200. FINAL ACCEPTANCE CRITERIA

UAF-81.14 será considerada implementada cuando pueda fabricar reproduciblemente:

```text
1 HUMAN HERO
1 HUMAN NPC
1 HEAVY ROBOT
1 LIGHT ROBOT
1 CREATURE
1 ALIEN
1 BOSS
```

Cada uno deberá disponer, según su profile, de:

```text
BODY
FACE
CLOTHING
ARMOR
MATERIALS
RIG
SKINNING
DEFORMATION
COLLISION
SOCKETS
LOD
VARIANTS
MANIFEST
UNREAL EXPORT
```

---

# 201. NON-NEGOTIABLE

La generación de personajes no podrá depender exclusivamente de primitivas geométricas.

---

# 202. NON-NEGOTIABLE

El sistema deberá permitir utilizar geometría especializada para:

```text
face
hands
feet
clothing
armor
hair
mechanical parts
```

---

# 203. NON-NEGOTIABLE

El rig no podrá ser considerado opcional para personajes destinados a animación.

---

# 204. NON-NEGOTIABLE

El skinning deberá validarse mediante poses reales de deformación.

---

# 205. NON-NEGOTIABLE

La ropa y armadura deberán tratarse como componentes con dependencias explícitas.

---

# 206. NON-NEGOTIABLE

La modificación de un componente no deberá provocar regeneración global cuando no exista dependencia.

---

# 207. NON-NEGOTIABLE

Todo personaje deberá ser reproducible mediante:

```text
PROFILE
+
SEED
+
GENERATOR VERSION
+
COMPONENT VERSIONS
```

---

# 208. NON-NEGOTIABLE

Todo personaje deberá disponer de un manifest de fabricación.

---

# 209. NON-NEGOTIABLE

Un personaje que visualmente parezca correcto pero falle:

```text
rig
skinning
collision
LOD
sockets
export
```

deberá ser considerado FAILED.

---

# 210. NON-NEGOTIABLE

Un personaje técnicamente correcto pero visualmente deficiente deberá poder ser rechazado por el sistema de calidad artística.

---

# 211. FINAL ARCHITECTURAL RESULT

UAF-81.14 deberá convertir:

```text
PARAMETRIC CHARACTER GENERATOR
```

en:

```text
CHARACTER FABRICATION PLATFORM
```

La plataforma resultante deberá poder producir personajes que no sean únicamente modelos 3D, sino activos completos de producción:

```text
CHARACTER
├── Geometry
├── Materials
├── Textures
├── Skeleton
├── Skin
├── Morphs
├── Animation Metadata
├── Collision
├── Physics
├── Sockets
├── LOD
├── Variants
├── Gameplay Metadata
└── Unreal Export Package
```

---

# 212. DEPENDENCY CONTRACT

UAF-81.14 dependerá de:

```text
UAF-81.01 — Core Architecture
UAF-81.02 — Asset Specification
UAF-81.03 — Semantic Asset Graph
UAF-81.04 — Generation Strategy
UAF-81.05 — Asset Library
UAF-81.06 — Blender Capability Layer
UAF-81.07 — Validation
UAF-81.08 — Materials
UAF-81.09 — Optimization
UAF-81.10 — Production Orchestration
UAF-81.11 — Modular Environment
UAF-81.12 — Structure Fabrication
UAF-81.13 — Terrain / Biome / World Surface
```

---

# 213. NEXT SYSTEM

La siguiente fase deberá abordar la fabricación profesional de superficies visuales:

```text
UAF-81.15
MATERIAL, TEXTURE & SURFACE FABRICATION SYSTEM
```

y deberá conectar:

```text
CHARACTERS
WEAPONS
PROPS
STRUCTURES
TERRAIN
VEGETATION
WORLD
```

con un único sistema profesional de materiales y texturas.
