# UAF-81.3 — PROCEDURAL GEOMETRY & ASSET CONSTRUCTION FABRIC

## UAF-81.3-ARCH

### ARQUITECTURA DE CONSTRUCCIÓN GEOMÉTRICA MULTI-RESOLUCIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.3 — Procedural Geometry & Asset Construction Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.3 define la infraestructura responsable de transformar una especificación geométrica en un conjunto de assets 3D estructuralmente válidos, visualmente coherentes y preparados para las etapas posteriores de materiales, rigging, optimización y exportación a Unreal Engine.

Esta fase reemplazará el concepto de:

```text
primitive generation
        ↓
voxel remesh
        ↓
smooth
```

como estrategia general de construcción.

El remesh podrá continuar utilizándose cuando sea apropiado, pero deberá convertirse en una herramienta dentro de una arquitectura mucho más amplia.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá permitir construir geometría mediante múltiples técnicas especializadas:

```text
PARAMETRIC
PROCEDURAL
MODULAR
BOOLEAN
SURFACE-BASED
CURVE-BASED
VOLUME-BASED
ORGANIC
HARD-SURFACE
KITBASH
SCULPT-ASSISTED
DEFORMATION-BASED
TERRAIN
ASSEMBLY
```

Ninguna técnica deberá considerarse universal.

---

# 3. CORE PRINCIPLE

La complejidad geométrica deberá distribuirse por niveles.

```text
L0 — STRUCTURAL
L1 — PRIMARY
L2 — SECONDARY
L3 — TERTIARY
L4 — MICRO
```

Cada nivel podrá utilizar una representación distinta.

---

# 4. GEOMETRY REPRESENTATION

El sistema deberá distinguir entre:

```text
Shape
Mesh
Surface
Volume
Curve
Assembly
Instance
Modifier Stack
Deformation
Detail Map
```

No deberá asumirse que todo elemento geométrico debe convertirse inmediatamente en una malla final.

---

# 5. STRUCTURAL LEVEL — L0

L0 representa la estructura semántica del asset.

Ejemplo de personaje:

```text
Character
├── Root
├── Pelvis
├── Torso
├── Head
├── Arm_L
├── Arm_R
├── Leg_L
├── Leg_R
├── Equipment
└── Accessories
```

L0 no busca detalle visual.

Busca:

```text
identity
hierarchy
placement
scale
relationships
```

---

# 6. PRIMARY GEOMETRY — L1

L1 define la silueta principal.

En un personaje:

```text
head
torso
arms
legs
hands
feet
major armor
major equipment
```

En arquitectura:

```text
walls
floors
ceilings
doors
large structural elements
```

En terreno:

```text
mountains
valleys
plateaus
cliffs
```

---

# 7. SECONDARY GEOMETRY — L2

L2 define formas que afectan significativamente la lectura visual.

Personaje:

```text
muscles
armor plates
joints
belts
pouches
boots
gloves
shoulder structures
helmet components
```

Arquitectura:

```text
frames
columns
windows
stairs
supports
panels
```

---

# 8. TERTIARY GEOMETRY — L3

L3 representa detalles visibles a corta distancia.

Ejemplos:

```text
seams
bolts
vents
small mechanical parts
cloth folds
wrinkles
surface breaks
weapon details
```

---

# 9. MICRO DETAIL — L4

L4 no deberá generarse obligatoriamente como geometría.

El planner deberá decidir entre:

```text
geometry
displacement
normal
height
roughness
material procedural detail
```

dependiendo de:

```text
distance
target platform
camera importance
performance budget
```

---

# 10. DETAIL REPRESENTATION POLICY

La misma característica podrá representarse de diferentes maneras.

Ejemplo:

```text
large armor plate
→ geometry

armor seam
→ geometry or normal

micro scratches
→ material

surface pores
→ normal/height

fabric fibers
→ shader/normal
```

La representación deberá ser una decisión explícita del Generation Plan.

---

# 11. GEOMETRY BUILD GRAPH

La construcción deberá utilizar un DAG.

```text
Semantic Structure
        ↓
Primary Forms
        ↓
Secondary Forms
        ↓
Tertiary Forms
        ↓
Detail Representation
        ↓
Topology Processing
        ↓
UV
        ↓
LOD
        ↓
Collision
```

---

# 12. GEOMETRY COMPONENT

Deberá existir:

```text
GeometryComponent
```

con:

```text
component_id
semantic_role
representation
source
transform
parent
material_slots
visibility
quality_level
lod_policy
collision_policy
```

---

# 13. SEMANTIC ROLE

Cada componente deberá tener un papel semántico.

Ejemplo:

```text
HEAD
TORSO
LIMB
ARMOR
CLOTHING
WEAPON
ACCESSORY
STRUCTURAL
DECORATIVE
FUNCTIONAL
```

Esto permitirá aplicar reglas específicas.

---

# 14. TRANSFORM CONTRACT

Cada componente deberá definir:

```text
position
rotation
scale
pivot
local_axis
parent
```

El sistema deberá evitar transforms ambiguas.

---

# 15. COORDINATE SYSTEM

La geometría deberá respetar el convenio global del proyecto.

El asset deberá declarar:

```text
forward_axis
up_axis
right_axis
unit_scale
```

El adaptador de Unreal deberá encargarse de cualquier conversión necesaria.

---

# 16. UNIT NORMALIZATION

Todo asset deberá normalizarse a una unidad de medida conocida.

La unidad canónica deberá ser:

```text
meters
```

Los generadores podrán trabajar internamente con otras unidades únicamente si declaran explícitamente la conversión.

---

# 17. PARAMETRIC GEOMETRY

Los generadores paramétricos deberán recibir parámetros explícitos.

Ejemplo:

```text
TorsoParameters
├── width
├── depth
├── height
├── shoulder_width
├── waist_width
├── chest_depth
└── curvature
```

Los parámetros deberán estar versionados.

---

# 18. PARAMETER VALIDATION

Los parámetros deberán tener:

```text
type
minimum
maximum
default
units
constraints
```

No deberán aceptarse valores inválidos silenciosamente.

---

# 19. PARAMETER DEPENDENCIES

Los parámetros podrán depender de otros.

Ejemplo:

```text
shoulder_width
depends_on:
    body_scale
    anatomy_profile
```

El sistema deberá resolver dependencias antes de generar geometría.

---

# 20. PROCEDURAL MODIFIERS

Los generadores podrán aplicar operaciones:

```text
bevel
boolean
subdivision
solidify
shrinkwrap
mirror
array
deform
remesh
smooth
decimate
```

Cada modifier deberá ser declarativo.

---

# 21. MODIFIER CONTRACT

Cada modifier deberá declarar:

```text
inputs
outputs
requirements
side_effects
cost
determinism
```

---

# 22. BOOLEAN GEOMETRY

Las operaciones booleanas deberán soportar:

```text
UNION
DIFFERENCE
INTERSECTION
```

Deberán validarse:

```text
manifoldness
self-intersections
degenerate_faces
non-finite_coordinates
```

posteriormente.

---

# 23. HARD-SURFACE GENERATION

Hard-surface deberá utilizar una pipeline propia.

```text
Base Volume
    ↓
Shape Definition
    ↓
Boolean Operations
    ↓
Bevel Strategy
    ↓
Panelization
    ↓
Mechanical Details
    ↓
Topology Cleanup
```

No deberá depender de voxel remesh.

---

# 24. ORGANIC GENERATION

Organic geometry podrá utilizar:

```text
metaballs
volumes
implicit surfaces
subdivision
sculpt-like deformation
procedural curves
surface deformation
```

La técnica será seleccionada según la categoría y calidad requerida.

---

# 25. CHARACTER ANATOMY

La anatomía deberá separarse en componentes.

```text
Skeleton
    ↓
Landmarks
    ↓
Primary Anatomy
    ↓
Secondary Anatomy
    ↓
Muscle/Surface Definition
    ↓
Clothing/Armor
```

---

# 26. LANDMARK SYSTEM

Los landmarks deberán ser datos independientes de la geometría.

Ejemplo:

```text
pelvis
spine
chest
neck
head
shoulder_L/R
elbow_L/R
wrist_L/R
hip_L/R
knee_L/R
ankle_L/R
```

Esto permitirá cambiar de generador sin perder la estructura anatómica.

---

# 27. ANATOMY PROFILE

Se deberá crear:

```text
AnatomyProfile
```

con parámetros como:

```text
height
shoulder_ratio
torso_ratio
limb_ratio
head_ratio
hand_ratio
foot_ratio
muscle_profile
body_mass
```

---

# 28. ANATOMY VALIDATION

La anatomía deberá validarse mediante:

```text
proportion constraints
symmetry constraints
joint constraints
capsule constraints
landmark constraints
```

---

# 29. SYMMETRY

El sistema deberá soportar:

```text
bilateral symmetry
radial symmetry
custom symmetry
asymmetric overrides
```

La asimetría deberá ser explícita.

---

# 30. ASYMMETRY

Ejemplo:

```text
left_arm_armor = type_A
right_arm_armor = type_B
```

El sistema no deberá asumir que una modificación en un lado implica automáticamente la misma modificación en el otro.

---

# 31. CLOTHING

Clothing deberá tratarse como una categoría geométrica independiente.

Pipeline:

```text
Body Surface
    ↓
Garment Pattern
    ↓
Garment Construction
    ↓
Thickness
    ↓
Folds
    ↓
Seams
    ↓
Fasteners
    ↓
Collision
```

---

# 32. CLOTHING REPRESENTATION

Podrá utilizar:

```text
surface meshes
curves
parametric patterns
modular garments
simulation
procedural deformation
```

---

# 33. CLOTHING LAYERS

La ropa deberá soportar capas:

```text
Body
↓
Underwear/Base Layer
↓
Clothing
↓
Armor
↓
Accessories
```

Cada capa deberá declarar:

```text
thickness
clearance
collision_policy
attachment_points
```

---

# 34. ZERO-CLIPPING

El sistema deberá detectar intersecciones no permitidas entre capas.

Deberá distinguir:

```text
EXPECTED_INTERSECTION
FORBIDDEN_INTERSECTION
TOLERATED_INTERSECTION
```

---

# 35. CLEARANCE

Cada componente podrá declarar un margen mínimo.

Ejemplo:

```text
armor_to_body_clearance
cloth_to_body_clearance
weapon_to_body_clearance
```

---

# 36. HAIR

Hair deberá ser independiente del cuerpo.

Representaciones:

```text
curves
cards
mesh
procedural strands
hybrid
```

La strategy determinará cuál utilizar.

---

# 37. ACCESSORIES

Los accesorios deberán utilizar sockets.

Ejemplo:

```text
head_socket
chest_socket
back_socket
hand_L_socket
hand_R_socket
waist_socket
```

---

# 38. SOCKET CONTRACT

Cada socket deberá declarar:

```text
socket_id
position
rotation
allowed_categories
scale_policy
clearance
```

---

# 39. MODULAR ASSEMBLY

Un asset modular deberá poder construirse mediante:

```text
Module
+
Socket
+
Compatibility Rule
+
Placement Rule
```

---

# 40. MODULE COMPATIBILITY

Dos módulos podrán conectarse únicamente si:

```text
socket_type compatible
orientation compatible
scale compatible
clearance valid
semantic compatibility valid
```

---

# 41. INSTANCING

El sistema deberá soportar instancias para reducir coste.

Especialmente:

```text
vegetation
rocks
panels
bolts
architectural modules
props
decoration
```

---

# 42. INSTANCE CONTRACT

Una instancia deberá conservar:

```text
source_asset
transform
variation_seed
material_override
metadata
```

---

# 43. TERRAIN

Terrain deberá utilizar una representación especializada.

Pipeline:

```text
Height/Volume Definition
        ↓
Macro Terrain
        ↓
Erosion
        ↓
Biome Features
        ↓
Secondary Terrain
        ↓
Scatter
        ↓
LOD/Streaming
```

---

# 44. ENVIRONMENT

Environment deberá diferenciar:

```text
terrain
architecture
vegetation
props
atmosphere
gameplay geometry
```

Esto permitirá optimización independiente.

---

# 45. MAP CONSTRUCTION

Un mapa no deberá tratarse como una única malla.

Deberá ser un:

```text
WorldAssembly
```

compuesto por múltiples sistemas.

---

# 46. WORLD COMPONENTS

Mínimo:

```text
terrain
water
architecture
vegetation
props
lighting
fog
VFX
navigation
gameplay volumes
streaming regions
```

---

# 47. TOPOLOGY STAGE

Después de construir la forma deberá existir una etapa explícita de topology processing.

Deberá evaluar:

```text
manifold
normals
face orientation
degenerate geometry
non-manifold edges
self-intersections
density
triangle distribution
```

---

# 48. TOPOLOGY QUALITY

La densidad de polígonos deberá depender del papel del asset.

No se utilizará un único polygon budget universal.

---

# 49. POLYGON BUDGET

El budget deberá considerar:

```text
asset category
importance
camera distance
platform
animation
material complexity
LOD count
```

---

# 50. TRIANGLE BUDGET

El sistema deberá permitir budgets por:

```text
asset
component
LOD
material region
```

---

# 51. TOPOLOGY STRATEGY

La topología podrá optimizarse mediante:

```text
remesh
retopology
decimation
edge-flow preservation
manual topology templates
procedural topology
```

La selección deberá depender del destino.

---

# 52. ANIMATED CHARACTERS

Los personajes animados tendrán requisitos adicionales:

```text
joint deformation
edge flow
deformation zones
weight compatibility
silhouette preservation
```

Una topología válida para un prop estático no deberá considerarse automáticamente válida para un personaje animado.

---

# 53. DEFORMATION ZONES

El personaje deberá poder declarar:

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

como zonas de deformación.

---

# 54. DEFORMATION QUALITY

La validación deberá probar poses de deformación mínimas antes de aprobar un personaje destinado a animación.

---

# 55. UV GENERATION

UV deberá ser una etapa independiente.

Deberá soportar:

```text
automatic unwrap
seams
islands
packing
UDIM
trim sheets
unique UV
shared UV
```

---

# 56. UV POLICY

La estrategia UV deberá depender de:

```text
asset type
material type
texture resolution
target
reusability
```

---

# 57. UV VALIDATION

Deberá comprobarse:

```text
overlap policy
island density
padding
texel density
out-of-bounds
degenerate islands
```

---

# 58. TEXEL DENSITY

Cada asset deberá declarar su objetivo de texel density.

El valor deberá ser configurable por:

```text
platform
asset class
quality profile
camera importance
```

---

# 59. LOD

LOD deberá ser generado desde una política explícita.

```text
LOD0
LOD1
LOD2
LOD3
...
```

---

# 60. LOD RULE

Cada LOD deberá preservar:

```text
silhouette
semantic identity
material regions
collision requirements
animation compatibility
```

según el target.

---

# 61. LOD TRANSITIONS

El sistema deberá definir criterios de transición:

```text
distance
screen_size
performance_budget
platform
```

---

# 62. COLLISION

Collision geometry deberá generarse como output separado.

Tipos:

```text
simple
compound
custom
convex
complex
physics
navigation
```

---

# 63. COLLISION POLICY

La collision strategy dependerá del uso:

```text
world_static
physics
character
weapon
vehicle
projectile
interaction
```

---

# 64. GEOMETRY VALIDATION

Cada asset deberá pasar como mínimo:

```text
scale validation
transform validation
topology validation
normal validation
intersection validation
bounds validation
density validation
material slot validation
UV validation
LOD validation
collision validation
```

---

# 65. VISUAL VALIDATION

Además de validación matemática deberá existir:

```text
silhouette validation
proportion validation
detail preservation
artifact detection
```

La validación visual seguirá siendo independiente de la validación estructural.

---

# 66. ARTIFACT DETECTION

Deberán detectarse problemas como:

```text
floating geometry
unexpected holes
spikes
collapsed geometry
intersections
missing components
broken symmetry
unexpected normals
```

---

# 67. BOUNDING VOLUME

Cada asset deberá generar:

```text
AABB
OBB cuando sea necesario
bounding sphere cuando sea necesario
```

Estos datos alimentarán:

```text
collision
LOD
culling
validation
Unreal import
```

---

# 68. GEOMETRY METADATA

Cada componente deberá conservar:

```text
semantic_id
source_generator
generation_parameters
strategy
version
seed
parent
material_role
LOD_policy
collision_policy
```

---

# 69. REPRODUCIBILITY

Dado:

```text
same specification
same generator version
same parameters
same seed
same tool version
```

el sistema deberá producir resultados equivalentes dentro de la tolerancia definida.

---

# 70. GEOMETRY SNAPSHOT

Antes de operaciones destructivas deberá poder generarse un snapshot.

Esto permitirá:

```text
rollback
comparison
debugging
regression testing
```

---

# 71. NON-DESTRUCTIVE PIPELINE

Siempre que sea viable, las etapas deberán conservar:

```text
source representation
parameters
modifier graph
generated result
```

La conversión destructiva deberá ser explícita.

---

# 72. SOURCE OF TRUTH

La geometría final no será la única fuente de verdad.

La fuente de verdad será:

```text
Specification
+
Parameters
+
Generation Graph
+
Generator Versions
+
Seeds
```

---

# 73. ASSET BUILD RECORD

Cada asset deberá producir:

```text
AssetBuildRecord
```

conteniendo:

```text
asset_id
build_id
specification_hash
generator_versions
parameters
seed
tool_versions
outputs
validation_results
warnings
errors
```

---

# 74. GEOMETRY CACHE

Las etapas geométricas deberán poder cachearse independientemente.

Ejemplo:

```text
AnatomyCache
FaceCache
ClothingCache
ArmorCache
AssemblyCache
TopologyCache
UVCache
LODCache
CollisionCache
```

---

# 75. PARTIAL REBUILD

Si únicamente cambia:

```text
material
```

no deberá reconstruirse necesariamente:

```text
anatomy
clothing
topology
```

El dependency graph deberá determinar qué debe regenerarse.

---

# 76. DIRTY GRAPH

Cada cambio deberá propagar invalidación únicamente a los nodos dependientes.

Ejemplo:

```text
Face parameter changed
        ↓
Face
        ↓
UV
        ↓
Textures
        ↓
Material
```

pero no necesariamente:

```text
Terrain
Weapon
Collision
```

---

# 77. ERROR CLASSIFICATION

Los errores deberán clasificarse:

```text
INPUT_ERROR
PARAMETER_ERROR
CAPABILITY_ERROR
GENERATION_ERROR
TOPOLOGY_ERROR
UV_ERROR
RESOURCE_ERROR
TOOL_ERROR
VALIDATION_ERROR
INTEGRATION_ERROR
```

---

# 78. RECOVERABLE ERRORS

Cada error deberá indicar:

```text
recoverable
retryable
fallback_available
requires_replan
```

---

# 79. RETRY POLICY

Los retries deberán ser limitados y configurables.

No deberá existir retry infinito.

---

# 80. GEOMETRY GENERATOR INTERFACE

Deberá existir una interfaz equivalente a:

```text
GeometryGenerator
```

con responsabilidades para:

```text
validate_input()
plan()
generate()
validate_output()
```

---

# 81. GENERATOR SEPARATION

No deberá permitirse que un generator gestione directamente:

```text
global orchestration
persistent storage
strategy selection
user authorization
```

Estas responsabilidades pertenecen a otras capas.

---

# 82. GENERATOR REGISTRY

Deberá existir:

```text
GeometryGeneratorRegistry
```

para registrar implementaciones.

---

# 83. GENERATOR DISCOVERY

Deberá permitir:

```text
find_generator(
    geometry_type,
    quality_profile,
    target
)
```

---

# 84. CURRENT GENERATOR MIGRATION

El generador existente:

```text
blender_player_skin_dark_fluid.py
```

deberá migrarse progresivamente.

No deberá eliminarse inmediatamente.

Deberá convertirse en una implementación registrada de:

```text
HumanoidProceduralGenerator
```

---

# 85. MIGRATION RULE

La migración deberá preservar:

```text
landmarks
anatomical proportions
materials
axis conventions
capsule validation
deterministic generation
```

cuando estas características sean todavía válidas.

---

# 86. REMESH POLICY

Voxel remesh podrá utilizarse cuando:

```text
organic volume fusion
rapid prototyping
non-deforming organic forms
certain creature archetypes
```

lo justifiquen.

No deberá utilizarse automáticamente para:

```text
face
hands
clothing seams
mechanical assemblies
deformation-critical topology
```

---

# 87. HERO CHARACTER REQUIREMENT

Para personajes heroicos deberá existir la posibilidad de separar:

```text
body
head
face
eyes
teeth
tongue
hair
clothing
armor
equipment
```

en lugar de fusionarlo todo mediante remesh.

---

# 88. COMPONENTIZED CHARACTER

La arquitectura deberá soportar:

```text
Character
├── SkeletalBody
├── Head
│   ├── Face
│   ├── Eyes
│   ├── Teeth
│   └── Tongue
├── Hair
├── Clothing
├── Armor
├── Accessories
└── Equipment
```

---

# 89. FACE REQUIREMENT

Face deberá tener su propia capability y generator.

No deberá depender obligatoriamente del generador corporal.

Esto permitirá introducir posteriormente:

```text
facial topology
facial landmarks
blendshape-ready topology
expression deformation
skin details
```

sin reescribir todo el character generator.

---

# 90. HAND REQUIREMENT

Hands deberán poder generarse mediante una estrategia especializada.

Deberán soportarse:

```text
finger topology
joint deformation
nail geometry
palm structure
individual finger proportions
```

---

# 91. EYE REQUIREMENT

Eyes deberán ser componentes independientes.

Mínimo:

```text
eyeball
iris
pupil
cornea
sclera
tearline
```

cuando el quality profile lo requiera.

---

# 92. TEETH AND MOUTH

El sistema deberá soportar:

```text
upper_teeth
lower_teeth
tongue
gum
mouth_cavity
```

como componentes independientes.

---

# 93. CHARACTER ASSEMBLY

El ensamblador deberá construir:

```text
body
+
head
+
face
+
hair
+
clothing
+
armor
+
equipment
```

respetando:

```text
sockets
hierarchy
clearance
materials
visibility
LOD
collision
```

---

# 94. GEOMETRY QUALITY PROFILES

Deberán existir perfiles configurables.

Mínimo:

```text
PROTOTYPE
GAMEPLAY
PRODUCTION
HERO
CINEMATIC
```

---

# 95. PROFILE EFFECT

El perfil deberá modificar:

```text
geometry density
detail representation
UV strategy
texture dependency
LOD count
collision precision
validation strictness
```

---

# 96. TARGET PROFILES

También deberán existir targets:

```text
UE5_PC
UE5_CONSOLE
UE5_HIGH_END
UE5_MOBILE
CINEMATIC_RENDER
```

Los targets podrán imponer restricciones adicionales.

---

# 97. PLATFORM OPTIMIZATION

El mismo asset lógico podrá producir diferentes builds:

```text
Hero_PC
Hero_Console
Hero_Low
```

sin cambiar necesariamente la specification semántica original.

---

# 98. GEOMETRY BUILD VARIANTS

Una specification podrá generar:

```text
source_master
production
optimized
preview
cinematic
```

variantes derivadas.

---

# 99. MASTER ASSET

El master deberá conservar la máxima información necesaria para derivar variantes.

No deberá optimizarse destructivamente antes de generar los derivados.

---

# 100. FINAL ACCEPTANCE

UAF-81.3 se considerará completada cuando el sistema pueda demostrar:

```text
1. generación primaria;
2. generación secundaria;
3. generación terciaria;
4. representación de microdetalle;
5. composición modular;
6. geometría hard-surface;
7. geometría orgánica;
8. componentes anatómicos;
9. clothing independiente;
10. accessories mediante sockets;
11. topology validation;
12. UV generation;
13. UV validation;
14. LOD generation;
15. collision generation;
16. deterministic builds;
17. cache;
18. partial rebuild;
19. snapshots;
20. visual validation;
21. geometry metadata;
22. quality profiles;
23. target profiles;
24. migration del generador existente;
25. hero character componentization.
```

---

# 101. CRITICAL INTEGRATION TEST

Debe demostrarse la construcción de un personaje que contenga:

```text
Body
Head
Face
Eyes
Teeth
Hair
Clothing
Armor
Weapon
Accessories
```

y que:

```text
Body
≠
Face
≠
Hair
≠
Clothing
≠
Armor
```

sean componentes independientes.

El sistema deberá poder modificar uno de ellos sin reconstruir innecesariamente los demás.

---

# 102. CRITICAL REMESH TEST

Debe demostrarse que:

```text
simple_robot
```

puede utilizar:

```text
procedural + remesh
```

mientras:

```text
hero_character
```

utiliza:

```text
componentized geometry
+
specialized face
+
specialized clothing
+
specialized hair
+
specialized topology
```

sin modificar el núcleo del orquestador.

---

# 103. ARCHITECTURAL RESULT

Después de UAF-81.3, el sistema deberá conceptualizar un asset así:

```text
                    ASSET
                      │
              ┌───────┴────────┐
              │                │
        STRUCTURE          COMPONENTS
              │                │
              └───────┬────────┘
                      ↓
              PRIMARY FORMS
                      ↓
             SECONDARY FORMS
                      ↓
              TERTIARY FORMS
                      ↓
               MICRO DETAIL
                      ↓
              TOPOLOGY / UV
                      ↓
                 LOD / COLLISION
                      ↓
                 VALIDATION
                      ↓
                BUILD ARTIFACT
```

---

# 104. DESIGN CONSEQUENCE

El sistema deja de considerar:

```text
"un personaje = una malla"
```

y pasa a considerar:

```text
"un personaje = un sistema de componentes geométricos relacionados"
```

De la misma manera:

```text
"un mapa = una malla"
```

deja de ser válido.

Un mapa será:

```text
World
├── Terrain
├── Regions
├── Biomes
├── Architecture
├── Props
├── Vegetation
├── Water
├── Lighting
├── VFX
├── Navigation
├── Gameplay
└── Streaming
```

---

# 105. NEXT PHASE

La siguiente fase será:

# UAF-81.4 — MATERIAL, TEXTURE & SURFACE AUTHORING FABRIC

Esta fase deberá resolver el segundo gran problema de producción profesional.

No se limitará a generar materiales PBR.

Deberá establecer una fábrica completa para:

```text
Base Color
Normal
Roughness
Metallic
Specular
AO
Height
Emissive
Opacity
Subsurface
Clear Coat
Anisotropy
Detail Normal
Decals
Masks
Material Layers
Material Instances
Procedural Shaders
Texture Baking
Texture Atlases
UDIM
Trim Sheets
Virtual Textures
```

y deberá definir cómo el mismo asset puede pasar de:

```text
procedural material
```

a:

```text
production material
```

sin perder procedencia, determinismo, variantes, optimización ni compatibilidad con Unreal Engine.
