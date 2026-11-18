# UAF-81.7 — MATERIAL, TEXTURE & SURFACE SYNTHESIS FABRIC

## UAF-81.7-ARCH

### ARQUITECTURA DE SÍNTESIS DE MATERIALES, TEXTURAS Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.7 — Material, Texture & Surface Synthesis Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.7 define el sistema responsable de crear, procesar, validar, optimizar, versionar y empaquetar las superficies visuales utilizadas por todos los assets y mundos generados por AOE.

El sistema deberá cubrir el ciclo:

```text
Surface Intent
↓
Surface Definition
↓
Material Design
↓
Texture Synthesis
↓
UV / Projection
↓
Channel Construction
↓
Material Assembly
↓
Optimization
↓
Unreal Integration
↓
Validation
↓
Surface Package
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá permitir producir superficies profesionales para:

```text
Characters
Creatures
Robots
Weapons
Props
Buildings
Modular Kits
Vehicles
Terrain
Vegetation
Worlds
FX Assets
UI-related world surfaces
```

---

# 3. SURFACE PACKAGE

La salida principal será:

```text
SurfacePackage
```

conteniendo:

```text
SurfaceDefinition
MaterialDefinition
TextureSet
UVDefinition
ChannelDefinition
ShaderDefinition
MaterialInstanceDefinition
VariantDefinitions
OptimizationMetadata
ValidationReport
Provenance
```

---

# 4. SURFACE DEFINITION

Deberá existir:

```text
SurfaceDefinition
```

con:

```text
surface_id
surface_family
style
physical_class
visual_class
material_response
texture_profile
resolution_profile
uv_profile
variation_profile
wear_profile
damage_profile
```

---

# 5. SURFACE FAMILIES

Mínimo:

```text
METAL
PLASTIC
RUBBER
GLASS
STONE
CONCRETE
WOOD
FABRIC
LEATHER
CERAMIC
FLESH
SKIN
BONE
ORGANIC
VEGETATION
WATER
ICE
ENERGY
EMISSIVE_TECH
```

Deberá ser posible registrar nuevas familias sin modificar el núcleo.

---

# 6. PHYSICAL CLASS

La superficie podrá declarar:

```text
metallic
non_metallic
semi_transparent
transparent
subsurface
emissive
two_sided
masked
```

---

# 7. MATERIAL DEFINITION

Deberá existir:

```text
MaterialDefinition
```

con:

```text
material_id
parent_material
surface_family
shader_model
parameters
texture_slots
rendering_features
quality_tier
```

---

# 8. PBR BASE MODEL

El sistema deberá soportar como mínimo:

```text
BaseColor
Metallic
Roughness
Normal
AmbientOcclusion
Emissive
Opacity
```

---

# 9. OPTIONAL CHANNELS

También deberá soportar:

```text
Height
Displacement
Specular
SubsurfaceColor
SubsurfaceAmount
ClearCoat
ClearCoatRoughness
Anisotropy
Tangent
CustomMasks
```

cuando el material lo requiera.

---

# 10. TEXTURE SET

Deberá existir:

```text
TextureSet
```

que agrupe todas las texturas necesarias para una superficie.

Ejemplo:

```text
TextureSet
├── BaseColor
├── Normal
├── ORM
├── Emissive
└── Mask
```

---

# 11. CHANNEL PACKING

El sistema deberá soportar empaquetado de canales.

Ejemplo estándar:

```text
R = AO
G = Roughness
B = Metallic
```

La configuración deberá ser declarativa.

---

# 12. CHANNEL CONTRACT

Cada textura deberá declarar explícitamente:

```text
channel
semantic
color_space
bit_depth
compression
range
```

No deberá inferirse semántica únicamente por nombre de archivo.

---

# 13. COLOR SPACE

El sistema deberá distinguir explícitamente:

```text
sRGB
Linear
NormalMap
Mask
HDR
```

y evitar conversiones incorrectas.

---

# 14. TEXTURE RESOLUTION

Deberán soportarse como mínimo:

```text
256
512
1024
2048
4096
8192
```

La resolución deberá depender del perfil de calidad y del tipo de asset.

---

# 15. TEXTURE BUDGET

Cada asset podrá declarar:

```text
max_texture_memory
max_resolution
max_texture_count
max_material_count
```

---

# 16. TEXEL DENSITY

Deberá existir:

```text
TexelDensityProfile
```

que permita establecer unidades físicas por textura.

---

# 17. TEXEL DENSITY VALIDATION

El sistema deberá detectar:

```text
under_density
over_density
inconsistent_density
```

entre piezas que deban pertenecer visualmente al mismo conjunto.

---

# 18. UV DEFINITION

Deberá existir:

```text
UVDefinition
```

con:

```text
uv_channel
layout_type
resolution
padding
rotation_policy
scale_policy
overlap_policy
```

---

# 19. UV CHANNELS

Deberá soportarse:

```text
UV0
UV1
UV2
UV3
```

cuando el target lo requiera.

---

# 20. UV STRATEGIES

Mínimo:

```text
SMART_PROJECT
BOX
CYLINDRICAL
PLANAR
CUBIC
SEAM_BASED
ATLAS
TRIM
UDIM
CUSTOM
```

---

# 21. UV VALIDATION

Deberá detectar:

```text
overlap
out_of_bounds
distortion
insufficient_padding
flipped_islands
degenerate_islands
```

---

# 22. UV OVERLAP POLICY

Los overlaps podrán clasificarse:

```text
ALLOWED
WARNING
FORBIDDEN
```

según el material y el uso.

---

# 23. TRIM SHEET SUPPORT

Deberá existir soporte para:

```text
TrimSheetDefinition
```

incluyendo:

```text
trim_regions
material_regions
scale_rules
orientation_rules
```

---

# 24. ATLAS SUPPORT

Deberá existir:

```text
TextureAtlasDefinition
```

para agrupar assets compatibles.

---

# 25. UDIM SUPPORT

El sistema deberá poder declarar:

```text
UDIM_LAYOUT
UDIM_TILE_RANGE
UDIM_ASSIGNMENT
```

cuando sea necesario para assets de alta resolución.

---

# 26. PROCEDURAL TEXTURE SYNTHESIS

Deberá existir un sistema capaz de producir patrones mediante:

```text
noise
cellular
voronoi
gradient
wave
mask
curvature
position
normal
ambient_occlusion
```

---

# 27. PROCEDURAL GRAPH

Las texturas procedurales deberán representarse mediante:

```text
TextureGraph
```

donde:

```text
node = operation
edge = data flow
```

---

# 28. TEXTURE GRAPH NODES

Mínimo:

```text
Noise
Voronoi
Gradient
Blur
Levels
Contrast
Multiply
Add
Subtract
Clamp
Remap
Mask
Transform
Warp
Blend
EdgeDetect
Curvature
Position
Normal
```

---

# 29. GRAPH DETERMINISM

El TextureGraph deberá aceptar:

```text
seed
```

y producir resultados reproducibles.

---

# 30. SURFACE LAYERS

Deberá existir:

```text
SurfaceLayer
```

para construir superficies mediante capas.

Ejemplo:

```text
Base Metal
↓
Primer
↓
Paint
↓
Scratches
↓
Dirt
↓
Rust
↓
Dust
↓
Damage
```

---

# 31. LAYER MASKS

Cada capa deberá poder utilizar:

```text
procedural_mask
texture_mask
vertex_color
attribute
curvature
normal
height
position
manual_mask
```

---

# 32. WEAR SYSTEM

Deberá existir:

```text
WearProfile
```

que controle:

```text
edge_wear
surface_wear
paint_loss
micro_scratches
macro_scratches
dirt
dust
```

---

# 33. EDGE WEAR

El desgaste de bordes deberá poder calcularse mediante:

```text
curvature
normal_change
distance_field
procedural_noise
```

---

# 34. DAMAGE SYSTEM

Deberá existir:

```text
DamageProfile
```

con:

```text
scratch
dent
fracture
burn
impact
crack
chipped_paint
```

---

# 35. DAMAGE INTENSITY

Deberán existir niveles:

```text
NONE
LIGHT
MEDIUM
HEAVY
EXTREME
```

---

# 36. DAMAGE DETERMINISM

El daño procedural deberá utilizar:

```text
asset_seed
surface_seed
damage_seed
```

para evitar resultados impredecibles.

---

# 37. ORGANIC SURFACES

Las superficies orgánicas deberán soportar:

```text
pores
veins
wrinkles
fibers
growth
wetness
subsurface
variation
```

---

# 38. SKIN PROFILE

Deberá existir un perfil específico para piel:

```text
SkinSurfaceProfile
```

con soporte para:

```text
base_tone
subsurface
roughness_variation
pores
micro_normal
oil_variation
color_variation
```

---

# 39. FABRIC PROFILE

Deberá existir:

```text
FabricSurfaceProfile
```

para:

```text
weave
thread_direction
roughness
fuzz
wear
fold_response
```

---

# 40. METAL PROFILE

Deberá existir:

```text
MetalSurfaceProfile
```

para:

```text
metallic
roughness
brushed_direction
oxidation
scratches
paint
coating
```

---

# 41. GLASS PROFILE

Deberá existir:

```text
GlassSurfaceProfile
```

para:

```text
transmission
roughness
tint
thickness
imperfections
```

---

# 42. CONCRETE PROFILE

Deberá soportar:

```text
aggregate
cracks
stains
roughness
dust
edge_damage
water_damage
```

---

# 43. WOOD PROFILE

Deberá soportar:

```text
grain
rings
color_variation
roughness
knots
damage
```

---

# 44. MATERIAL VARIANTS

Cada material podrá tener variantes:

```text
Clean
Used
Damaged
Wet
Dusty
Burned
Rusty
Frozen
Bloodied
```

según corresponda al contenido.

---

# 45. VARIANT GENERATION

Las variantes deberán reutilizar la misma definición base cuando sea posible.

No deberá duplicarse innecesariamente todo el material.

---

# 46. MATERIAL INSTANCES

Deberá existir:

```text
MaterialInstanceDefinition
```

para permitir parámetros variables sin duplicar shaders.

---

# 47. PARAMETER TYPES

Mínimo:

```text
Scalar
Vector
Texture
Boolean
Color
Enum
```

---

# 48. PARAMETER RANGES

Cada parámetro deberá declarar:

```text
minimum
maximum
default
recommended
```

---

# 49. PARAMETER VALIDATION

No deberán permitirse valores fuera del rango definido salvo override explícito.

---

# 50. MATERIAL GRAPH

Deberá existir:

```text
MaterialGraph
```

con:

```text
inputs
nodes
connections
outputs
```

---

# 51. SHADER FEATURES

El sistema deberá registrar explícitamente las funcionalidades utilizadas:

```text
transparency
refraction
subsurface
world_position
vertex_animation
parallax
displacement
emission
```

---

# 52. SHADER COMPLEXITY

Deberá existir un:

```text
ShaderComplexityProfile
```

que limite:

```text
instruction_count
texture_samples
dynamic_branches
expensive_features
```

---

# 53. PERFORMANCE TIERS

Mínimo:

```text
MOBILE
LOW
MEDIUM
HIGH
ULTRA
CINEMATIC
```

---

# 54. MATERIAL LOD

Los materiales deberán poder degradarse según distancia o calidad.

Ejemplo:

```text
CLOSE
MEDIUM
FAR
HLOD
```

---

# 55. TEXTURE LOD

Las texturas deberán generar mipmaps apropiados y políticas de streaming.

---

# 56. TEXTURE STREAMING

Cada textura deberá poder declarar:

```text
streaming
priority
group
max_resident_size
```

---

# 57. VIRTUAL TEXTURE

Deberá existir soporte opcional para:

```text
VirtualTexture
```

cuando el perfil Unreal lo requiera.

---

# 58. TEXTURE COMPRESSION

Deberá existir una política explícita por canal.

Ejemplo conceptual:

```text
BaseColor → color compression
Normal → normal compression
Mask → linear mask compression
HDR → HDR compression
```

---

# 59. NORMAL MAP VALIDATION

Deberá comprobar:

```text
normal orientation
channel convention
tangent compatibility
range
compression compatibility
```

---

# 60. TANGENT SPACE

La definición deberá registrar:

```text
tangent_method
normal_convention
mikktspace_compatibility
```

cuando sea aplicable.

---

# 61. HEIGHT / DISPLACEMENT

El sistema deberá distinguir entre:

```text
height
parallax
displacement
```

y no tratarlos como equivalentes.

---

# 62. MASK SYSTEM

Deberá existir un sistema común de máscaras.

Mínimo:

```text
DirtMask
DamageMask
WearMask
WetnessMask
RustMask
PaintMask
EmissionMask
```

---

# 63. MASK PACKING

Varias máscaras podrán empaquetarse en una textura si:

```text
resolution compatible
sampling compatible
compression compatible
```

---

# 64. MATERIAL CONSISTENCY

Los materiales pertenecientes al mismo asset deberán compartir:

```text
color philosophy
roughness philosophy
scale
texel density
physical response
```

---

# 65. STYLE ARCHETYPE

El sistema deberá consumir:

```text
StyleArchetype
```

para garantizar coherencia artística.

---

# 66. STYLE PARAMETERS

Un estilo podrá definir:

```text
color_range
contrast
roughness_range
metallic_range
emission_range
detail_frequency
wear_level
```

---

# 67. EMISSIVE CONTROL

Deberá existir un límite explícito de emisión por perfil para evitar resultados incompatibles con el pipeline de iluminación objetivo.

---

# 68. SURFACE SCALE

Las texturas deberán mantener escala física coherente.

Un ladrillo, tornillo, panel o poro no deberá cambiar arbitrariamente de tamaño entre assets.

---

# 69. MICRODETAIL

Deberá distinguirse:

```text
macro_detail
mid_detail
micro_detail
```

para evitar introducir geometría o texturas excesivamente costosas para detalles que no serán visibles.

---

# 70. DETAIL DISTRIBUTION

El detalle deberá depender de:

```text
camera_distance
asset_size
gameplay_importance
quality_tier
```

---

# 71. DECAL SUPPORT

Los decals deberán poder declararse como:

```text
DecalDefinition
```

con:

```text
type
material
projection
size
opacity
priority
lifetime
```

---

# 72. DECAL CATEGORIES

Mínimo:

```text
DAMAGE
DIRT
WARNING
NUMBER
LOGO
GRAFFITI
BLOOD
TECHNICAL
ENVIRONMENTAL
```

---

# 73. MATERIAL BAKING

Deberá existir un:

```text
BakePipeline
```

para producir mapas derivados de:

```text
high_poly
low_poly
geometry
sculpt
procedural_data
```

---

# 74. BAKE MAPS

Mínimo:

```text
Normal
AO
Curvature
Thickness
Position
ID
Height
```

---

# 75. BAKE VALIDATION

Deberá detectar:

```text
projection errors
ray misses
cage errors
seams
artifacts
incorrect scale
```

---

# 76. LOW-POLY SUPPORT

El sistema deberá poder diferenciar:

```text
source_geometry
render_geometry
collision_geometry
bake_geometry
```

---

# 77. MATERIAL IDs

La geometría podrá declarar IDs semánticos para permitir asignación automática de materiales.

---

# 78. AUTOMATIC MATERIAL ASSIGNMENT

A partir de:

```text
material_id
surface_tag
geometry_region
semantic_tag
```

el sistema podrá asignar materiales automáticamente.

---

# 79. SURFACE SEMANTICS

Deberán existir tags como:

```text
Surface.Metal
Surface.Concrete
Surface.Glass
Surface.Fabric
Surface.Skin
Surface.Wood
Surface.Rubber
```

---

# 80. UNREAL MATERIAL ADAPTER

Deberá existir:

```text
UnrealMaterialAdapter
```

responsable de traducir:

```text
MaterialDefinition
TextureSet
MaterialInstanceDefinition
```

a los recursos correspondientes del proyecto Unreal.

---

# 81. ASSET NAMING

Deberá existir una convención centralizada para:

```text
Textures
Materials
MaterialInstances
Masks
Decals
```

---

# 82. NAMING EXAMPLE

Ejemplo conceptual:

```text
T_<Asset>_<Surface>_<Channel>
M_<Family>_<Surface>
MI_<Asset>_<Variant>
```

La convención deberá ser configurable.

---

# 83. FOLDER STRUCTURE

La exportación deberá poder organizar:

```text
Materials/
Textures/
Masks/
Decals/
Variants/
```

sin depender de rutas absolutas.

---

# 84. MATERIAL DEPENDENCY GRAPH

Deberá existir:

```text
MaterialDependencyGraph
```

para conocer:

```text
material
→ textures
→ masks
→ parent material
→ shader
```

---

# 85. REBUILD

Si cambia únicamente:

```text
BaseColor
```

no deberá reconstruirse:

```text
Normal
Material Graph
```

salvo dependencia explícita.

---

# 86. INCREMENTAL SYNTHESIS

El sistema deberá regenerar únicamente los componentes afectados.

---

# 87. CACHE

Deberá existir cache para:

```text
procedural nodes
bakes
textures
material graphs
compiled definitions
```

---

# 88. CACHE KEY

La cache deberá depender como mínimo de:

```text
input_hash
generator_version
seed
profile
dependencies
```

---

# 89. DETERMINISM

Los mismos inputs deberán producir el mismo resultado dentro de las tolerancias declaradas.

---

# 90. PROVENANCE

Cada textura y material deberá conservar:

```text
source_definition
generator_version
seed
profile
dependencies
build_id
```

---

# 91. TEXTURE VALIDATION

Cada textura deberá comprobar:

```text
resolution
format
bit_depth
color_space
channel_usage
compression
alpha
mipmaps
```

---

# 92. MATERIAL VALIDATION

Cada material deberá comprobar:

```text
required_inputs
parameter_ranges
texture_references
shader_features
performance
```

---

# 93. UV VALIDATION

Cada asset deberá comprobar:

```text
UV presence
UV distortion
UV overlap
texel density
padding
orientation
```

---

# 94. VISUAL VALIDATION

Deberán existir renders de prueba para:

```text
neutral lighting
strong lighting
low lighting
close-up
distance
```

---

# 95. MATERIAL REGRESSION

Los cambios de shader o generador deberán compararse contra imágenes golden.

---

# 96. TEXTURE REGRESSION

Los cambios deberán detectar:

```text
color drift
roughness drift
normal drift
mask drift
missing details
```

---

# 97. PERFORMANCE REGRESSION

Deberán medirse:

```text
texture memory
shader complexity
texture samples
material count
streaming cost
```

---

# 98. GOLDEN MATERIAL LIBRARY

Deberá existir una biblioteca golden que contenga al menos:

```text
metal
painted metal
rusted metal
concrete
glass
fabric
leather
skin
plastic
rubber
wood
organic
emissive sci-fi
```

---

# 99. MATERIAL FAMILY TESTS

Cada familia deberá tener pruebas específicas.

---

# 100. CROSS-ASSET CONSISTENCY

Un material compartido por:

```text
character
weapon
prop
environment
```

deberá conservar comportamiento visual coherente.

---

# 101. WORLD INTEGRATION

UAF-81.7 deberá integrarse directamente con UAF-81.6.

Un WorldPackage deberá poder solicitar:

```text
surface_family
material_profile
variation_profile
```

y recibir un SurfacePackage compatible.

---

# 102. CHARACTER INTEGRATION

UAF-81.7 deberá integrarse con UAF-81.5.

Los personajes deberán poder utilizar:

```text
skin
armor
fabric
rubber
metal
glass
organic materials
```

sin crear pipelines separados.

---

# 103. ASSET-AGNOSTIC DESIGN

El sistema deberá operar sobre una abstracción común:

```text
RenderableSurface
```

y no asumir que el objeto es:

```text
character
weapon
building
terrain
```

---

# 104. SURFACE GRAPH

Deberá existir:

```text
SurfaceGraph
```

que relacione:

```text
Geometry
UV
Material
Textures
Masks
Variants
LOD
```

---

# 105. SURFACE QUALITY SCORE

Deberá existir:

```text
SurfaceQualityScore
```

compuesto como mínimo por:

```text
UVQuality
TextureQuality
MaterialQuality
PhysicalConsistency
VisualQuality
Performance
```

---

# 106. QUALITY GATES

Una superficie podrá clasificarse:

```text
FAILED
PROTOTYPE
PRODUCTION
HIGH_QUALITY
CINEMATIC
```

---

# 107. BLOCKING CONDITIONS

Deberán bloquear la publicación:

```text
missing required texture
invalid UV
broken material dependency
invalid color space
invalid normal
budget violation
missing Unreal mapping
```

cuando el perfil lo marque como crítico.

---

# 108. ARTISTIC REJECTION

Un material podrá ser rechazado aunque técnicamente funcione si:

```text
visual coherence insufficient
scale incorrect
roughness implausible
detail excessive
detail insufficient
style mismatch
```

---

# 109. EXPORT PACKAGE

El paquete final deberá contener:

```text
SurfacePackage
├── Definitions
├── Textures
├── Materials
├── MaterialInstances
├── Masks
├── Decals
├── Metadata
├── Validation
└── Provenance
```

---

# 110. FINAL ACCEPTANCE CRITERIA

UAF-81.7 estará completa cuando pueda:

```text
1. definir superficies;
2. definir familias físicas;
3. generar texturas;
4. generar materiales;
5. generar máscaras;
6. construir PBR;
7. generar variantes;
8. generar UVs;
9. validar UVs;
10. controlar texel density;
11. generar trim sheets;
12. generar atlases;
13. soportar UDIM;
14. realizar baking;
15. validar normal maps;
16. controlar color spaces;
17. controlar compresión;
18. controlar memoria;
19. controlar shader complexity;
20. generar Material Instances;
21. realizar síntesis incremental;
22. utilizar cache;
23. mantener determinismo;
24. mantener provenance;
25. realizar visual regression;
26. integrarse con personajes;
27. integrarse con mundos;
28. integrarse con props;
29. integrarse con armas;
30. exportar recursos compatibles con Unreal.
```

---

# 111. NON-NEGOTIABLE PRINCIPLE

La generación procedural no deberá perseguir únicamente:

```text
"una textura que se vea bien"
```

sino:

```text
CORRECT PHYSICAL RESPONSE
+
CORRECT SCALE
+
CORRECT UV
+
CORRECT COLOR SPACE
+
CORRECT MEMORY PROFILE
+
CORRECT SHADER COST
+
CORRECT UNREAL INTEGRATION
+
CORRECT VISUAL IDENTITY
```

---

# 112. NEXT PHASE

# UAF-81.8 — ASSET ASSEMBLY, LOD, OPTIMIZATION & UNREAL RUNTIME READINESS

La siguiente fase deberá cerrar la brecha entre:

```text
GENERATED ASSET
```

y:

```text
PRODUCTION-READY UNREAL ASSET
```

UAF-81.8 deberá especificar:

```text
Asset Assembly
LOD Generation
LOD Validation
Nanite Eligibility
Nanite Policies
Collision Generation
Physics Assets
Sockets
Pivot Validation
Origin Validation
Scale Validation
Actor Assembly
Blueprint Metadata
Material Assignment
Texture Streaming
Virtual Textures
HLOD
Instancing
Draw Call Optimization
Triangle Optimization
Memory Optimization
Distance Culling
Bounds
Occlusion
Shadow Cost
Physics Cost
Navigation Cost
Asset Dependencies
Unreal Naming
Unreal Folder Mapping
Automated Import
Automated Reimport
Validation
Performance Budgets
Golden Assets
Regression
Packaging
```

La meta de UAF-81.8 será convertir las piezas generadas por **UAF-81.5, UAF-81.6 y UAF-81.7** en assets que puedan entrar directamente al entorno de producción de Unreal.
