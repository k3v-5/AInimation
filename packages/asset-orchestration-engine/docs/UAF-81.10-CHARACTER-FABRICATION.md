# UAF-81.10 — PROCEDURAL CHARACTER FABRICATION & HIGH-COMPLEXITY GEOMETRY

## UAF-81.10-ARCH

### ARQUITECTURA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE PERSONAJES COMPLEJOS

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.10 — Procedural Character Fabrication & High-Complexity Geometry  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.10 establece la arquitectura para fabricar personajes y criaturas de alta complejidad geométrica mediante un sistema procedural compuesto.

La fase sustituye el concepto:

```text
primitives
→
single voxel remesh
→
smooth
→
final mesh
```

por:

```text
Character Specification
↓
Semantic Anatomy
↓
Primary Forms
↓
Secondary Forms
↓
Specialized Components
↓
Clothing / Armor
↓
Surface Detail
↓
Topology Strategy
↓
UV Strategy
↓
Material Regions
↓
Deformation Compatibility
↓
LOD Strategy
↓
Runtime Asset
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá ser capaz de fabricar personajes complejos sin exigir que toda la geometría pertenezca a una única superficie continua.

Deberá soportar simultáneamente:

```text
organic anatomy
hard surface
soft tissue
clothing
armor
mechanical components
accessories
hair
facial structures
weapons
embedded technology
surface detail
```

---

# 3. CORE ARCHITECTURAL PRINCIPLE

La geometría deberá dividirse en niveles semánticos.

```text
PRIMARY
SECONDARY
TERTIARY
SURFACE
DEFORMATION
RUNTIME
```

Cada nivel tendrá reglas propias.

---

# 4. PRIMARY FORMS

Las Primary Forms representan la silueta y masa principal.

Ejemplos:

```text
head
torso
pelvis
upper arm
forearm
thigh
calf
hands
feet
tail
wing
body shell
```

---

# 5. PRIMARY FORM REQUIREMENTS

Las formas primarias deberán priorizar:

```text
silhouette
proportion
volume
landmark placement
global topology
```

No deberán contener detalles superficiales innecesarios.

---

# 6. SECONDARY FORMS

Representan estructuras anatómicas o constructivas que modifican la silueta.

Ejemplos:

```text
muscles
joints
shoulder masses
knee structure
jaw
cheek bones
armor plates
mechanical housings
boots
gloves
belts
```

---

# 7. TERTIARY FORMS

Representan detalles de escala intermedia:

```text
seams
vents
panels
wrinkles
folds
bolts
fasteners
scars
mechanical joints
surface breaks
```

---

# 8. SURFACE DETAIL

Los detalles superficiales deberán poder representarse mediante:

```text
geometry
normal
height
roughness
mask
procedural shader
```

La geometría no deberá utilizarse cuando un mapa sea suficiente.

---

# 9. DETAIL REPRESENTATION DECISION

Cada detalle deberá pasar por una decisión:

```text
GEOMETRY
NORMAL
HEIGHT
MATERIAL
PROCEDURAL
```

La decisión deberá considerar:

```text
visual importance
camera distance
deformation
silhouette contribution
runtime cost
```

---

# 10. SEMANTIC BODY GRAPH

Deberá existir:

```text
SemanticBodyGraph
```

Ejemplo:

```text
Character
├── Head
│   ├── Skull
│   ├── Face
│   ├── Eyes
│   ├── Jaw
│   └── Mouth
├── Torso
│   ├── Chest
│   ├── Abdomen
│   └── Pelvis
├── Arm_L
├── Arm_R
├── Leg_L
└── Leg_R
```

---

# 11. BODY COMPONENT IDENTITY

Cada componente deberá tener un identificador estable.

Ejemplo:

```text
body.head
body.torso
body.arm.left.upper
body.arm.left.forearm
```

---

# 12. COMPONENT OWNERSHIP

Cada geometría deberá pertenecer a un componente semántico.

No deberá existir geometría sin propietario lógico.

---

# 13. COMPONENT GENERATORS

Cada componente podrá tener su propio generador.

Ejemplo:

```text
HeadGenerator
TorsoGenerator
HandGenerator
FootGenerator
ArmorGenerator
ClothingGenerator
```

---

# 14. GENERATOR CONTRACT

Todo generador deberá declarar:

```text
inputs
outputs
parameters
dependencies
seed
quality_level
topology_policy
material_policy
```

---

# 15. PARAMETRIC BODY MODEL

Los cuerpos humanoides deberán utilizar parámetros anatómicos.

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

# 16. PROPORTION PROFILE

Deberá existir:

```text
ProportionProfile
```

que permita definir estilos:

```text
REALISTIC
HEROIC
ATHLETIC
SLENDER
HEAVY
STYLIZED
MONSTROUS
CUSTOM
```

---

# 17. PROPORTION VALIDATION

Los parámetros deberán validarse antes de generar geometría.

---

# 18. ANATOMICAL LANDMARKS

El sistema deberá mantener landmarks consistentes entre:

```text
geometry
skeleton
clothing
armor
animation
```

---

# 19. LANDMARK PROPAGATION

Cuando cambie un landmark primario deberán actualizarse automáticamente los componentes dependientes.

---

# 20. BODY SPACE

Todos los componentes deberán generarse inicialmente en un espacio semántico común.

---

# 21. TRANSFORM CONTRACT

Cada componente deberá almacenar:

```text
position
rotation
scale
local_space
parent_component
```

---

# 22. MIRROR SYSTEM

Deberá existir un sistema de simetría procedural.

```text
MirrorProfile
```

---

# 23. MIRROR AXIS

La simetría deberá poder configurarse.

Para humanoides deberá existir un perfil estándar de simetría izquierda/derecha.

---

# 24. ASYMMETRY LAYER

Después de construir una base simétrica deberá existir una capa de variación asimétrica.

Ejemplos:

```text
scar
missing armor
different eye
damaged limb
asymmetric equipment
```

---

# 25. ASYMMETRY SEED

La asimetría procedural deberá depender de un seed determinista.

---

# 26. TOPOLOGY STRATEGY

No deberá existir una única estrategia topológica.

Deberán existir:

```text
TopologyProfile
```

con posibles modos:

```text
DEFORMATION
HARD_SURFACE
ORGANIC
HYBRID
CINEMATIC
GAMEPLAY
NANITE
CUSTOM
```

---

# 27. DEFORMATION TOPOLOGY

Las regiones deformables deberán recibir una topología apropiada para skinning.

---

# 28. HARD-SURFACE TOPOLOGY

Las piezas mecánicas deberán poder mantener geometría independiente.

---

# 29. HYBRID TOPOLOGY

Los personajes híbridos deberán combinar:

```text
deformation meshes
rigid meshes
attachment meshes
```

---

# 30. NO GLOBAL REMESH RULE

No deberá ejecutarse un remesh global sobre todo el personaje como operación obligatoria.

---

# 31. LOCAL REMESH

El remesh podrá utilizarse únicamente en regiones donde aporte valor.

Ejemplos:

```text
organic torso
muscle transition
creature tissue
```

---

# 32. REGION REMESH

Cada región deberá declarar:

```text
remesh_allowed
voxel_size
smooth_iterations
preserve_boundaries
```

---

# 33. BOUNDARY PRESERVATION

Las operaciones locales no deberán destruir:

```text
material boundaries
UV boundaries
skeleton boundaries
attachment boundaries
```

sin autorización explícita.

---

# 34. BOOLEAN POLICY

Las operaciones booleanas deberán ser regionales y controladas.

---

# 35. BOOLEAN VALIDATION

Después de una operación booleana deberá comprobarse:

```text
non_manifold geometry
self intersections
zero-area faces
broken normals
```

---

# 36. SURFACE CONTINUITY

El sistema deberá distinguir entre:

```text
visual continuity
geometric continuity
deformation continuity
```

No deberá exigir continuidad geométrica donde no sea necesaria.

---

# 37. COMPONENT JOINING

Un conjunto de piezas no deberá convertirse automáticamente en una sola malla.

---

# 38. JOIN POLICY

Cada unión deberá declarar:

```text
JOINED
SEPARATE
INSTANCE
ATTACHED
SKINNED
RIGID
```

---

# 39. INSTANCING

Las piezas repetidas deberán poder instanciarse.

Ejemplos:

```text
bolts
armor plates
teeth
scales
vents
panels
```

---

# 40. DETAIL SCATTER

Deberá existir:

```text
ProceduralDetailScatter
```

para distribuir elementos repetitivos.

---

# 41. SCATTER CONSTRAINTS

Los elementos podrán limitarse mediante:

```text
surface
normal
curvature
mask
region
distance
orientation
```

---

# 42. EXCLUSION MASKS

Deberán poder definirse áreas donde no puede aparecer detalle.

---

# 43. DENSITY CONTROL

La densidad deberá ser paramétrica.

---

# 44. DETAIL SEED

El scatter deberá ser determinista.

---

# 45. ORGANIC SURFACE SYSTEM

Las superficies orgánicas deberán soportar:

```text
pores
wrinkles
scars
veins
microstructure
skin breakup
```

---

# 46. ORGANIC DETAIL REPRESENTATION

El sistema deberá decidir entre:

```text
geometry
normal
height
material
```

según escala.

---

# 47. SKIN SYSTEM

Deberá existir:

```text
SkinSurfaceProfile
```

con parámetros como:

```text
roughness
subsurface
specular
microdetail
color variation
```

---

# 48. SKIN COLOR VARIATION

La variación de color deberá ser procedural y controlable mediante seed.

---

# 49. CLOTHING SYSTEM

Deberá existir:

```text
ClothingFabricator
```

---

# 50. CLOTHING TYPES

Mínimo:

```text
shirt
pants
jacket
coat
boots
gloves
belt
backpack
helmet
```

---

# 51. CLOTHING GENERATION

Las prendas deberán poder derivarse de:

```text
body landmarks
body surface
pattern definition
template
```

---

# 52. CLOTHING LAYERS

Deberán soportarse múltiples capas:

```text
body
underwear
clothing
armor
equipment
accessories
```

---

# 53. CLOTHING OFFSET

Cada capa deberá mantener un offset mínimo respecto de la superficie subyacente.

---

# 54. CLOTHING COLLISION

Las prendas deberán evitar penetraciones visibles con:

```text
body
armor
equipment
```

---

# 55. CLOTHING DEFORMATION

Las prendas deformables deberán poder vincularse al skeleton.

---

# 56. CLOTHING RIGID PARTS

Botones, hebillas, placas y componentes rígidos podrán permanecer como objetos independientes.

---

# 57. SEAM GENERATION

El sistema deberá poder generar costuras procedurales.

---

# 58. WRINKLE GENERATION

Las arrugas podrán derivarse de:

```text
joint location
gravity
fabric type
pose-independent deformation
```

---

# 59. FABRIC PROFILE

Deberá existir:

```text
FabricProfile
```

que defina:

```text
thickness
stiffness
roughness
stretch
fold tendency
```

---

# 60. ARMOR SYSTEM

Deberá existir:

```text
ArmorFabricator
```

---

# 61. ARMOR COMPONENTS

Mínimo:

```text
helmet
shoulder
chest
forearm
glove
thigh
knee
shin
boot
back
```

---

# 62. ARMOR ATTACHMENT

Cada pieza deberá declarar:

```text
attachment_bone
socket
offset
rotation
scale
```

---

# 63. ARMOR DEFORMATION

Cada pieza deberá declarar:

```text
RIGID
SOFT
HYBRID
```

---

# 64. ARMOR CLEARANCE

Deberá existir una distancia mínima entre piezas móviles.

---

# 65. MECHANICAL CLEARANCE TEST

Deberá probarse mediante poses extremas.

---

# 66. MECHANICAL COMPONENT GENERATOR

Los robots deberán poder generar:

```text
joints
actuators
pistons
panels
cables
vents
armor shells
mechanical housings
```

---

# 67. MECHANICAL AXIS SYSTEM

Cada componente móvil deberá declarar su eje principal.

---

# 68. MECHANICAL MOTION TEST

Cada articulación mecánica deberá probar:

```text
min angle
neutral
max angle
```

---

# 69. HAND GENERATOR

Las manos deberán disponer de un generador específico.

---

# 70. HAND PARAMETERIZATION

Mínimo:

```text
palm_width
palm_length
finger_length
finger_thickness
thumb_angle
finger_spacing
```

---

# 71. FINGER GENERATION

Los dedos deberán poder generarse individualmente.

---

# 72. FINGER JOINTS

Cada dedo deberá poder producir:

```text
proximal
intermediate
distal
```

cuando corresponda.

---

# 73. HAND DEFORMATION

La geometría de la mano deberá ser compatible con:

```text
grip
fist
open_hand
weapon_hold
```

---

# 74. FOOT GENERATOR

Los pies deberán tener un generador dedicado.

---

# 75. FACE GENERATOR

Deberá existir:

```text
FaceFabricator
```

separado del generador corporal.

---

# 76. FACE LANDMARKS

Mínimo:

```text
eyes
eyebrows
nose
mouth
jaw
cheeks
ears
```

---

# 77. FACE PROPORTIONS

Deberán ser parametrizables.

---

# 78. EYE GENERATION

Los ojos deberán poder generarse como componentes independientes.

---

# 79. EYE SOCKETS

La cabeza deberá mantener sockets/landmarks estables para los ojos.

---

# 80. TEETH SYSTEM

Deberá poder generarse:

```text
upper_teeth
lower_teeth
canines
custom_teeth
```

cuando corresponda.

---

# 81. TONGUE SYSTEM

Los personajes con boca funcional deberán poder utilizar un componente de lengua.

---

# 82. EAR GENERATOR

Las orejas deberán poder ser:

```text
human
pointed
mechanical
animal
custom
```

---

# 83. HAIR SYSTEM

Deberá existir:

```text
HairFabricator
```

---

# 84. HAIR REPRESENTATIONS

Deberá soportar:

```text
mesh cards
curves
geometry
grooms
hybrid
```

según plataforma y perfil.

---

# 85. HAIR LOD

El cabello deberá disponer de LOD independiente.

---

# 86. ACCESSORY FABRICATOR

Deberá existir un sistema genérico para:

```text
glasses
masks
helmets
backpacks
pouches
jewelry
gadgets
```

---

# 87. CHARACTER EQUIPMENT GRAPH

Todos los accesorios deberán integrarse en:

```text
CharacterEquipmentGraph
```

---

# 88. MATERIAL REGION GENERATION

Cada componente deberá declarar regiones materiales.

Ejemplo:

```text
skin
metal
cloth
rubber
glass
emissive
leather
ceramic
```

---

# 89. MATERIAL SEMANTICS

Las regiones materiales no deberán depender únicamente de índices numéricos.

Deberán tener identificadores semánticos.

---

# 90. UV STRATEGY

Cada componente deberá declarar:

```text
UVProfile
```

---

# 91. UV CHANNELS

El sistema deberá soportar múltiples canales cuando sean necesarios.

---

# 92. UV PURPOSE

Cada canal deberá declarar su propósito:

```text
texture
lightmap
mask
custom
```

---

# 93. UV SEAMS

Las costuras deberán priorizar:

```text
deformation
visibility
texture continuity
packing efficiency
```

---

# 94. UV VALIDATION

Deberá comprobar:

```text
overlap
stretch
islands
resolution
padding
```

---

# 95. TEXTURE SPACE

El sistema deberá poder calcular la densidad de texel.

---

# 96. TEXEL DENSITY

Cada componente deberá declarar o heredar:

```text
target_texel_density
```

---

# 97. TEXTURE RESOLUTION

La resolución deberá determinarse mediante:

```text
screen importance
surface area
material importance
LOD
platform
```

---

# 98. HIGH DETAIL SOURCE

Cuando se genere geometría de alta resolución deberá existir una relación:

```text
HighDetailMesh
↓
Bake
↓
RuntimeMesh
```

---

# 99. BAKE DATA

Deberá conservarse metadata del bake:

```text
source_hash
target_hash
resolution
maps
settings
```

---

# 100. BAKED MAPS

Podrán incluir:

```text
normal
AO
curvature
height
thickness
ID
roughness
custom masks
```

---

# 101. PROCEDURAL MATERIAL MASKS

Las máscaras deberán poder generarse desde:

```text
semantic regions
curvature
position
normal
random seed
```

---

# 102. SURFACE DAMAGE

Deberá existir un sistema procedural de daño.

Ejemplos:

```text
scratches
dents
cuts
burns
corrosion
cracks
```

---

# 103. DAMAGE NON-DESTRUCTIVE POLICY

El daño deberá poder aplicarse como capa sin destruir la geometría base.

---

# 104. DAMAGE SEED

El patrón deberá ser reproducible.

---

# 105. CHARACTER VARIATION

Deberá existir:

```text
CharacterVariationProfile
```

---

# 106. VARIATION PARAMETERS

Mínimo:

```text
height
proportions
face
skin
hair
clothing
armor
damage
accessories
colors
```

---

# 107. VARIATION SEED

Cada personaje deberá poder reproducirse mediante un seed.

---

# 108. VARIATION CONSTRAINTS

Las variantes deberán respetar:

```text
skeleton compatibility
gameplay capsule
animation compatibility
material budget
performance budget
```

---

# 109. VARIANT FAMILY

Los personajes derivados de un mismo arquetipo deberán compartir:

```text
base skeleton
compatible materials
compatible animation profile
```

cuando sea posible.

---

# 110. CHARACTER ARCHETYPE

Deberá existir:

```text
CharacterArchetype
```

Ejemplos:

```text
SOLDIER
SCOUT
HEAVY
ENGINEER
MEDIC
BOSS
CIVILIAN
CREATURE
ROBOT
```

---

# 111. ARCHETYPE INHERITANCE

Los arquetipos deberán poder heredar perfiles.

---

# 112. ARCHETYPE OVERRIDE

Un personaje concreto podrá sobrescribir parámetros del arquetipo sin modificar el arquetipo base.

---

# 113. PROCEDURAL ASSEMBLY

El ensamblaje final deberá realizarse mediante un:

```text
CharacterAssemblyGraph
```

---

# 114. ASSEMBLY ORDER

El orden mínimo será:

```text
Primary
↓
Secondary
↓
Clothing
↓
Armor
↓
Accessories
↓
Tertiary
↓
Surface
```

---

# 115. DEPENDENCY VALIDATION

No podrá generarse una capa si sus dependencias no están disponibles.

---

# 116. PARTIAL REGENERATION

Podrá regenerarse únicamente:

```text
face
hair
armor
clothing
surface
accessories
```

sin reconstruir necesariamente todo el personaje.

---

# 117. TOPOLOGY LOCK

Una geometría podrá marcarse:

```text
TopologyLocked
```

para impedir modificaciones destructivas.

---

# 118. UV LOCK

Las UV podrán marcarse:

```text
UVLocked
```

---

# 119. SKIN LOCK

El skinning podrá marcarse:

```text
SkinLocked
```

---

# 120. NON-DESTRUCTIVE PIPELINE

Las transformaciones deberán conservar:

```text
source
intermediate
final
```

cuando el perfil requiera trazabilidad completa.

---

# 121. MODIFIER STACK

Las operaciones deberán conservar un stack lógico:

```text
Base
→
Shape
→
Detail
→
Deformation
→
Optimization
```

---

# 122. MODIFIER OWNERSHIP

Cada modificación deberá declarar su propietario lógico.

---

# 123. PROCEDURAL PARAMETERS

Los parámetros deberán estar separados de la geometría resultante.

---

# 124. PARAMETER VERSIONING

Los parámetros deberán versionarse.

---

# 125. SEED HIERARCHY

Deberán existir seeds:

```text
global_seed
character_seed
component_seed
detail_seed
variation_seed
```

---

# 126. SEED DERIVATION

Los seeds secundarios deberán derivarse determinísticamente del seed padre.

---

# 127. RANDOMNESS POLICY

No se permitirá aleatoriedad no controlada dentro de una generación determinista.

---

# 128. QUALITY LEVELS

Deberán existir:

```text
DRAFT
STANDARD
HIGH
HERO
CINEMATIC
```

---

# 129. QUALITY BEHAVIOR

El cambio de calidad deberá afectar:

```text
geometry detail
texture resolution
surface detail
hair
microdetail
```

sin alterar arbitrariamente la identidad del personaje.

---

# 130. IDENTITY PRESERVATION

Una versión HIGH y una versión STANDARD deberán representar el mismo personaje.

---

# 131. LOD ARCHITECTURE

Deberán existir:

```text
LOD0
LOD1
LOD2
LOD3
```

o un sistema equivalente configurable.

---

# 132. LOD RESPONSIBILITIES

Cada LOD podrá modificar:

```text
geometry
materials
bones
morphs
hair
physics
```

---

# 133. LOD SILHOUETTE

La reducción de LOD no deberá destruir la silueta dentro de la tolerancia definida.

---

# 134. LOD DEFORMATION

Los LOD skinned deberán continuar deformándose correctamente.

---

# 135. NANITE STRATEGY

La arquitectura deberá permitir separar:

```text
Nanite geometry
deformation geometry
```

cuando la configuración de Unreal lo requiera.

---

# 136. RUNTIME MESH STRATEGY

La geometría de runtime deberá ser seleccionada mediante:

```text
platform
asset_role
distance
deformation
performance_budget
```

---

# 137. CHARACTER BUDGET

Cada personaje deberá declarar:

```text
triangle_budget
vertex_budget
material_budget
texture_budget
bone_budget
morph_budget
physics_budget
```

---

# 138. BUDGET ENFORCEMENT

Superar un presupuesto deberá generar:

```text
WARNING
FAIL
AUTO_OPTIMIZE
```

según política.

---

# 139. OPTIMIZATION STRATEGY

Las optimizaciones deberán preservar primero:

```text
silhouette
deformation
identity
material separation
gameplay functionality
```

---

# 140. OPTIMIZATION PRIORITY

Nunca deberá sacrificarse identidad visual antes que detalles terciarios.

---

# 141. CHARACTER IDENTITY SCORE

Deberá calcularse un score basado en:

```text
silhouette
landmarks
proportions
materials
signature features
```

---

# 142. GOLDEN CHARACTER

Deberá existir una versión golden de cada arquetipo importante.

---

# 143. GOLDEN COMPARISON

Las variantes deberán compararse contra su golden.

---

# 144. VISUAL REGRESSION

Deberán generarse vistas:

```text
front
back
left
right
three-quarter
action
close-up
```

---

# 145. DEFORMATION REGRESSION VIEWS

Deberán generarse adicionalmente:

```text
arms_up
arms_forward
crouch
kneel
weapon_pose
extreme_pose
```

cuando correspondan.

---

# 146. GEOMETRIC VALIDATION

Deberá detectarse:

```text
non-manifold
self-intersection
zero-area faces
duplicate vertices
flipped normals
degenerate geometry
```

---

# 147. SEMANTIC VALIDATION

Deberá detectarse:

```text
missing body component
wrong component type
wrong parent
invalid landmark
missing material region
```

---

# 148. ASSEMBLY VALIDATION

Deberá detectarse:

```text
floating parts
penetrating parts
wrong orientation
wrong attachment
broken symmetry
```

---

# 149. CLOTHING VALIDATION

Deberá detectarse:

```text
body penetration
armor penetration
cloth gaps
incorrect layer ordering
```

---

# 150. FACE VALIDATION

Deberá comprobarse:

```text
eye alignment
mouth alignment
jaw alignment
facial symmetry
```

cuando aplique.

---

# 151. HAND VALIDATION

Deberá comprobarse:

```text
finger order
finger spacing
thumb orientation
grip compatibility
```

---

# 152. FOOT VALIDATION

Deberá comprobarse:

```text
left/right
ground contact
orientation
shoe attachment
```

---

# 153. MATERIAL VALIDATION

Cada componente deberá poseer una asignación material válida.

---

# 154. TEXTURE VALIDATION

Deberá comprobarse:

```text
missing textures
incorrect dimensions
invalid formats
UV incompatibility
```

---

# 155. ENGINE VALIDATION

El resultado deberá evaluarse contra el perfil de Unreal objetivo.

---

# 156. EXPORT CONTRACT

Deberá existir:

```text
CharacterExportProfile
```

que defina:

```text
format
skeleton
materials
textures
physics
morphs
LOD
collision
metadata
```

---

# 157. EXPORT DETERMINISM

Dos exports con los mismos inputs deberán generar resultados equivalentes.

---

# 158. ASSET MANIFEST

Cada personaje deberá generar:

```text
CharacterManifest
```

con:

```text
asset_id
version
source
seed
profile
dependencies
outputs
hashes
validation
budgets
```

---

# 159. FAILURE ISOLATION

El fallo de un componente no deberá destruir componentes previamente válidos.

---

# 160. RECOVERY

El sistema deberá poder continuar desde el último checkpoint válido.

---

# 161. AUDIT LOG

Deberán registrarse:

```text
generation
modification
repair
optimization
validation
export
```

---

# 162. REPRODUCTION TEST

El sistema deberá poder reconstruir un personaje exclusivamente desde:

```text
CharacterSpecification
+
profiles
+
seed
+
versioned dependencies
```

---

# 163. REPRODUCTION ACCEPTANCE

La reconstrucción deberá producir:

```text
same semantic graph
same component identities
same deterministic geometry
same material regions
same skeleton compatibility
```

dentro de las tolerancias establecidas.

---

# 164. FINAL CHARACTER FABRICATION PIPELINE

El pipeline normativo será:

```text
SPECIFICATION
↓
ARCHETYPE
↓
PROPORTION PROFILE
↓
SEMANTIC BODY GRAPH
↓
PRIMARY FORMS
↓
SECONDARY FORMS
↓
FACE / HANDS / FEET
↓
CLOTHING
↓
ARMOR
↓
ACCESSORIES
↓
TERTIARY DETAIL
↓
SURFACE DETAIL
↓
MATERIAL REGIONS
↓
UV
↓
HIGH DETAIL
↓
BAKE
↓
TOPOLOGY
↓
SKINNING
↓
RIGGING
↓
LOD
↓
PHYSICS
↓
VALIDATION
↓
OPTIMIZATION
↓
UNREAL EXPORT
```

---

# 165. FINAL ACCEPTANCE CRITERIA

UAF-81.10 será considerada completada cuando el sistema pueda generar al menos:

```text
1 humanoide orgánico
1 humanoide con ropa
1 humanoide con armadura
1 personaje mecánico
1 criatura
1 personaje híbrido
```

y cada uno pueda producir:

```text
primary geometry
secondary geometry
tertiary detail
materials
UVs
LOD
skeleton compatibility
```

sin depender de un remesh global.

---

# 166. NON-NEGOTIABLE REQUIREMENT

La arquitectura no deberá diseñarse alrededor de un único personaje concreto.

Debe existir una fábrica general capaz de producir familias completas de assets.

---

# 167. NON-NEGOTIABLE REQUIREMENT

El sistema deberá distinguir explícitamente:

```text
GEOMETRY GENERATION
ASSET ASSEMBLY
DEFORMATION
TEXTURE GENERATION
MATERIAL GENERATION
RUNTIME OPTIMIZATION
```

Ninguna de estas responsabilidades deberá depender implícitamente de otra.

---

# 168. NON-NEGOTIABLE REQUIREMENT

La generación de alta calidad no deberá significar simplemente:

```text
more polygons
```

Deberá significar:

```text
correct topology
correct proportions
correct deformation
correct materials
correct UVs
correct detail representation
correct runtime behavior
```

---

# 169. NEXT PHASE

# UAF-81.11 — PROCEDURAL TEXTURE, MATERIAL & SURFACE AUTHORING FABRIC

Esta fase deberá construir el subsistema completo para generar los materiales y texturas necesarios para convertir la geometría en assets visualmente terminados.

Deberá cubrir como mínimo:

```text
Base Color
Roughness
Metallic
Normal
Height
Ambient Occlusion
Opacity
Emissive
Subsurface
Thickness
Curvature
Material IDs
Masks
Decals
Surface Damage
Grunge
Fabric
Leather
Skin
Metal
Plastic
Glass
Ceramic
Organic Materials
```

y deberá contemplar:

```text
procedural generation
texture baking
UDIM
multi-resolution
material instances
texture atlases
virtual textures
runtime materials
Unreal material compatibility
deterministic seeds
texture validation
texture budgets
```

El objetivo será que el sistema deje de generar únicamente **“mallas con materiales básicos”** y pase a fabricar **assets visualmente completos y listos para producción**.
