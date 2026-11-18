# UAF-81.46 — MATERIAL, TEXTURE, SURFACE AUTHORING & PROCEDURAL LOOK-DEVELOPMENT SYSTEM

## UAF-81.46-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA UNIVERSAL DE CREACIÓN, MODIFICACIÓN, VALIDACIÓN, OPTIMIZACIÓN Y EMPAQUETADO DE SUPERFICIES PARA TODOS LOS ASSETS DE AOE

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.46 — Material, Texture, Surface Authoring & Procedural Look-Development System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.45  
**Next Phase:** UAF-81.47  

---

# 1. PURPOSE

UAF-81.46 establece el sistema universal de creación, modificación, validación, optimización y empaquetado de superficies para todos los assets soportados por AOE.

El sistema deberá producir materiales y texturas aptos para:

```text
CHARACTERS
CREATURES
ROBOTS
WEAPONS
VEHICLES
PROPS
ARCHITECTURE
MODULAR_KITS
ENVIRONMENTS
VEGETATION
VFX
```

La salida deberá ser compatible con el pipeline de Unreal Engine.

---

# 2. CORE OBJECTIVE

El sistema deberá transformar una intención de superficie:

```text
SurfaceIntent
```

en:

```text
SurfacePackage
```

conteniendo:

```text
MATERIAL
TEXTURES
UV
BAKES
MASKS
DECALS
PARAMETERS
UNREAL_MATERIAL
UNREAL_INSTANCE
VALIDATION
PERFORMANCE_DATA
```

---

# 3. SURFACE PIPELINE

Pipeline normativo:

```text
SURFACE INTENT
↓
SURFACE CLASSIFICATION
↓
MATERIAL DEFINITION
↓
GEOMETRY ANALYSIS
↓
UV STRATEGY
↓
PROCEDURAL GENERATION
↓
BAKING
↓
TEXTURE PROCESSING
↓
MATERIAL ASSEMBLY
↓
UNREAL TRANSLATION
↓
OPTIMIZATION
↓
VALIDATION
↓
PACKAGE
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
name
category
material_family
shader_model
texture_profile
resolution_profile
uv_profile
wear_profile
damage_profile
color_profile
scale
seed
target_profile
quality_tier
```

---

# 5. MATERIAL FAMILIES

Mínimo:

```text
SKIN
FABRIC
LEATHER
METAL
PAINTED_METAL
RUBBER
PLASTIC
GLASS
CERAMIC
CONCRETE
STONE
WOOD
SOIL
SAND
GRAVEL
WATER
ICE
EMISSIVE
HOLOGRAM
ENERGY
ORGANIC
MECHANICAL
```

---

# 6. PBR MODEL

El sistema deberá utilizar un modelo PBR físicamente coherente.

Canales mínimos:

```text
BASE_COLOR
METALLIC
ROUGHNESS
NORMAL
AO
```

Canales opcionales:

```text
HEIGHT
DISPLACEMENT
EMISSION
OPACITY
SUBSURFACE
SPECULAR
CLEAR_COAT
CLEAR_COAT_ROUGHNESS
ANISOTROPY
TINT
MASK
```

---

# 7. MATERIAL PARAMETER DEFINITION

Cada material deberá declarar parámetros explícitos:

```text
MaterialParameter
```

con:

```text
name
type
default
minimum
maximum
group
description
runtime_editable
```

---

# 8. PARAMETER TYPES

Mínimo:

```text
FLOAT
INTEGER
BOOLEAN
COLOR
VECTOR2
VECTOR3
TEXTURE
MASK
ENUM
```

---

# 9. MATERIAL INSTANCE MODEL

Deberá existir:

```text
MaterialInstanceDefinition
```

Una instancia deberá modificar parámetros sin duplicar innecesariamente el material maestro.

---

# 10. MASTER MATERIAL SYSTEM

Deberá existir:

```text
MasterMaterialDefinition
MasterMaterialRegistry
```

Los materiales maestros deberán agruparse por familia.

---

# 11. MASTER MATERIAL LIMIT

No deberá generarse un master material independiente para cada asset si puede reutilizarse uno existente.

---

# 12. MATERIAL GRAPH

Deberá existir una representación intermedia:

```text
MaterialGraph
```

con nodos y conexiones deterministas.

---

# 13. MATERIAL NODE TYPES

Mínimo:

```text
TEXTURE
COLOR
VALUE
MULTIPLY
ADD
SUBTRACT
LERP
MASK
NORMAL
FRESNEL
NOISE
CONSTANT
REMAP
POWER
CLAMP
```

---

# 14. MATERIAL GRAPH VALIDATION

Deberá detectar:

```text
UNCONNECTED_INPUT
INVALID_CONNECTION
TYPE_MISMATCH
CYCLE
UNUSED_NODE
INVALID_PARAMETER
MISSING_TEXTURE
```

---

# 15. PROCEDURAL TEXTURE SYSTEM

Deberá existir:

```text
ProceduralTextureDefinition
ProceduralTextureGenerator
```

---

# 16. PROCEDURAL SOURCES

Mínimo:

```text
PERLIN
SIMPLEX
VORONOI
CELLULAR
WAVE
GRADIENT
RANDOM
MUSGRAVE
FRACTAL
IMAGE
CURVE
POSITION
NORMAL
OBJECT_COORDINATE
UV_COORDINATE
```

---

# 17. NOISE DETERMINISM

Todo ruido procedural deberá utilizar un seed explícito.

No se permitirá dependencia de random global.

---

# 18. NOISE PARAMETERS

Mínimo:

```text
seed
scale
octaves
lacunarity
gain
roughness
distortion
contrast
rotation
offset
```

---

# 19. TEXTURE LAYERS

Deberá existir:

```text
TextureLayer
```

permitiendo:

```text
base
variation
wear
dirt
dust
scratches
damage
stains
rust
moss
blood
burn
edge_wear
```

---

# 20. LAYER BLENDING

Deberán soportarse:

```text
NORMAL
MULTIPLY
ADD
SCREEN
OVERLAY
SOFT_LIGHT
COLOR
MASKED
```

---

# 21. MASK GENERATION

Deberá existir:

```text
MaskGenerator
```

para generar máscaras basadas en:

```text
POSITION
NORMAL
CURVATURE
AO
THICKNESS
EDGE
DIRECTION
HEIGHT
NOISE
UV
VERTEX_COLOR
```

---

# 22. CURVATURE MAP

El sistema deberá poder generar:

```text
CURVATURE_CONVEX
CURVATURE_CONCAVE
CURVATURE_COMBINED
```

---

# 23. EDGE WEAR

Deberá existir un generador de desgaste de bordes basado en geometría.

Parámetros mínimos:

```text
intensity
radius
noise
direction
threshold
```

---

# 24. DIRT SYSTEM

Deberá existir:

```text
DirtGenerator
```

con distribución basada en:

```text
AO
NORMAL
POSITION
GRAVITY
EXPOSURE
CURVATURE
```

---

# 25. GRAVITY-AWARE DIRT

El sistema deberá permitir acumulación dependiente de orientación.

Ejemplo conceptual:

```text
UP
DOWN
VERTICAL
UNDER_SURFACE
```

---

# 26. RUST SYSTEM

Deberá existir:

```text
RustGenerator
```

aplicable únicamente a materiales compatibles.

Deberá considerar:

```text
moisture
exposure
curvature
scratches
age
```

---

# 27. SCRATCH SYSTEM

Deberá existir:

```text
ScratchGenerator
```

con:

```text
density
length
width
direction
depth
randomness
```

---

# 28. DAMAGE SYSTEM

Deberá existir:

```text
SurfaceDamageDefinition
```

tipos:

```text
SCRATCH
DENT
CRACK
CHIP
BURN
ABRASION
CORROSION
IMPACT
BULLET
CUT
```

---

# 29. DAMAGE REPRESENTATION

El daño podrá representarse mediante:

```text
GEOMETRY
HEIGHT
NORMAL
ROUGHNESS
BASE_COLOR
MASK
DECAL
```

según el nivel de calidad.

---

# 30. SCALE-AWARE TEXTURING

Toda generación procedural deberá conocer la escala física del objeto.

Una textura no deberá producir un patrón idéntico sobre:

```text
1 cm
1 m
10 m
100 m
```

sin compensación de escala.

---

# 31. PHYSICAL SCALE

Deberá existir:

```text
SurfaceScaleDefinition
```

con:

```text
world_scale
pattern_scale
micro_scale
macro_scale
```

---

# 32. MICRODETAIL

Deberá existir una capa específica para:

```text
pores
fibers
micro_scratches
grain
surface_noise
```

---

# 33. MACRO VARIATION

Deberá existir una capa para evitar superficies visualmente uniformes:

```text
large_color_variation
large_roughness_variation
large_damage
large_stains
```

---

# 34. MULTI-SCALE SURFACE

La superficie final deberá poder combinar:

```text
MACRO
+
MEDIUM
+
MICRO
```

sin depender exclusivamente de geometría.

---

# 35. UV STRATEGY

Deberá existir:

```text
SurfaceUVStrategy
```

seleccionable entre:

```text
UV_UNWRAP
TRIPLANAR
WORLD_ALIGNED
OBJECT_ALIGNED
BOX
CYLINDER
CUSTOM
```

---

# 36. UV AUTO UNWRAP

Deberá soportar:

```text
seam_detection
island_generation
island_packing
rotation
scaling
padding
```

---

# 37. UV SEAM STRATEGY

Las costuras deberán minimizar:

```text
visibility
distortion
material_breaks
```

---

# 38. TEXEL DENSITY

Deberá existir un perfil global:

```text
TexelDensityPolicy
```

Todos los assets de una misma categoría deberán mantener densidad consistente salvo excepción explícita.

---

# 39. UDIM

Deberá existir soporte opcional para:

```text
UDIM
```

especialmente para:

```text
HERO_CHARACTERS
CINEMATIC_ASSETS
LARGE_ARCHITECTURE
```

---

# 40. BAKE SYSTEM

Deberá existir:

```text
BakeDefinition
BakeGenerator
BakeValidator
```

---

# 41. BAKE TYPES

Mínimo:

```text
NORMAL
AO
CURVATURE
POSITION
THICKNESS
ID
WORLD_NORMAL
VERTEX_COLOR
HEIGHT
```

---

# 42. HIGH_TO_LOW BAKE

Deberá soportarse:

```text
HIGH_POLY
↓
LOW_POLY
↓
BAKE
```

---

# 43. BAKE CAGE

Deberá existir:

```text
BakeCageDefinition
```

con:

```text
offset
max_distance
min_distance
custom_cage
```

---

# 44. BAKE VALIDATION

Deberá detectar:

```text
ray_miss
projection_error
cage_intersection
seam_artifact
normal_error
bake_missing
```

---

# 45. NORMAL MAP CONVENTION

El pipeline deberá declarar explícitamente:

```text
TANGENT_SPACE
HANDEDNESS
AXIS_CONVENTION
GREEN_CHANNEL_DIRECTION
```

No se permitirá ambigüedad.

---

# 46. COLOR MANAGEMENT

El pipeline deberá definir:

```text
working_color_space
texture_color_space
display_transform
```

---

# 47. COLOR TEXTURES

Las texturas de color deberán distinguirse de mapas de datos.

Ejemplo:

```text
BASE_COLOR → sRGB
NORMAL → DATA
ROUGHNESS → DATA
METALLIC → DATA
AO → DATA
```

---

# 48. TEXTURE COMPRESSION

Deberá existir:

```text
TextureCompressionProfile
```

por tipo de mapa.

---

# 49. TEXTURE SIZE POLICY

La resolución máxima deberá depender de:

```text
asset_category
quality_tier
target_platform
screen_importance
```

---

# 50. TEXTURE DOWNSCALING

El sistema deberá generar automáticamente versiones inferiores cuando el perfil lo requiera.

---

# 51. MIPMAP POLICY

Todas las texturas utilizadas en runtime deberán tener una política explícita de mipmaps.

---

# 52. VIRTUAL TEXTURE POLICY

Deberá existir soporte configurable para:

```text
VIRTUAL_TEXTURE
STANDARD_TEXTURE
```

---

# 53. CHANNEL PACKING

Deberá existir:

```text
TexturePackingDefinition
```

permitiendo empaquetar:

```text
R = AO
G = ROUGHNESS
B = METALLIC
A = MASK
```

u otra combinación definida por el material.

---

# 54. PACKING VALIDATION

El sistema deberá validar que ningún canal requerido quede sobrescrito accidentalmente.

---

# 55. TEXTURE ATLAS

Deberá existir soporte para:

```text
TextureAtlas
```

cuando el target lo permita.

---

# 56. ATLAS VALIDATION

Deberá comprobar:

```text
padding
bleeding
UV_bounds
island_overlap
mipmap_bleeding
```

---

# 57. DECAL SYSTEM

Deberá existir:

```text
ProceduralDecalGenerator
```

---

# 58. DECAL TYPES

Mínimo:

```text
LOGO
WARNING
NUMBER
GRAFFITI
SCRATCH
BLOOD
BULLET_HOLE
RUST
DAMAGE
INSIGNIA
```

---

# 59. DECAL PLACEMENT

Deberá soportar:

```text
SURFACE_NORMAL
CURVATURE
POSITION
RANDOM
SEMANTIC_REGION
```

---

# 60. MATERIAL VARIANTS

Deberá existir:

```text
MaterialVariantDefinition
```

permitiendo variaciones:

```text
color
roughness
wear
damage
age
dirt
emission
```

---

# 61. VARIANT DETERMINISM

Las variantes deberán utilizar:

```text
base_seed
variant_seed
```

---

# 62. MATERIAL RANDOMIZATION

El sistema deberá evitar variaciones arbitrarias que produzcan resultados físicamente incoherentes.

Cada parámetro deberá tener:

```text
minimum
maximum
distribution
```

---

# 63. DISTRIBUTIONS

Mínimo:

```text
UNIFORM
NORMAL
BIASED
GAUSSIAN
CURVE
FIXED
```

---

# 64. MATERIAL AGE

Deberá existir:

```text
MaterialAgeProfile
```

con:

```text
new
used
worn
old
damaged
destroyed
```

---

# 65. ENVIRONMENTAL EXPOSURE

Deberá poder simularse:

```text
rain
dust
sand
salt
humidity
sun
cold
heat
```

como variables de superficie.

---

# 66. SURFACE CONDITION

Deberá existir:

```text
SurfaceCondition
```

con:

```text
cleanliness
wetness
damage
oxidation
dirt
age
```

---

# 67. WETNESS

La humedad deberá afectar coherentemente:

```text
roughness
base_color
specular_response
```

y no únicamente añadir un color oscuro.

---

# 68. PROCEDURAL FABRIC

El sistema deberá generar:

```text
weave
thread_direction
fuzz
roughness
color_variation
```

---

# 69. PROCEDURAL METAL

Deberá soportar:

```text
base_metal
paint
primer
scratches
exposed_metal
rust
dirt
```

---

# 70. PROCEDURAL WOOD

Deberá soportar:

```text
grain
rings
knots
roughness
color_variation
damage
```

---

# 71. PROCEDURAL CONCRETE

Deberá soportar:

```text
aggregate
pores
cracks
stains
dust
edge_damage
```

---

# 72. PROCEDURAL SKIN

Deberá soportar:

```text
macro_color
blood_flow_variation
pores
roughness
subsurface
microdetail
imperfections
```

---

# 73. PROCEDURAL ORGANIC

Deberá soportar:

```text
growth
veins
membrane
moisture
damage
variation
```

---

# 74. EMISSIVE MATERIAL

Deberá existir un sistema controlado de emisión:

```text
EmissionProfile
```

con límites explícitos.

---

# 75. EMISSION VALIDATION

Deberá detectar:

```text
excessive_emission
invalid_color
bloom_risk
```

---

# 76. TRANSLUCENCY

Deberá soportarse cuando el material lo requiera:

```text
skin
leaves
thin_fabric
glass
organic_membrane
```

---

# 77. OPACITY

Deberá soportar:

```text
MASKED
TRANSLUCENT
OPAQUE
```

según el target.

---

# 78. MATERIAL INSTANCE GENERATION

Para cada material final deberá poder generarse:

```text
MasterMaterial
+
MaterialInstance
```

sin duplicar lógica innecesariamente.

---

# 79. UNREAL MATERIAL TRANSLATION

Deberá existir:

```text
UnrealMaterialTranslator
```

que traduzca el grafo AOE al modelo de materiales del target.

---

# 80. UNREAL MATERIAL PARAMETERS

Los parámetros deberán conservar:

```text
name
type
default
range
group
```

durante la exportación.

---

# 81. UNREAL TEXTURE IMPORT PROFILE

Deberá existir:

```text
UnrealTextureImportProfile
```

con:

```text
compression
sRGB
mipmaps
virtual_texture
filter
lod_bias
address_mode
```

---

# 82. IMPORT PROFILE BY MAP

El perfil deberá distinguir:

```text
BASE_COLOR
NORMAL
MASK
ROUGHNESS
METALLIC
AO
EMISSION
```

---

# 83. SHADER COMPLEXITY

Deberá medirse:

```text
instruction_count
texture_sample_count
branch_count
feature_count
```

---

# 84. MATERIAL PERFORMANCE BUDGET

Cada material deberá declarar:

```text
max_texture_samples
max_instructions
max_virtual_textures
max_layers
```

---

# 85. MATERIAL OPTIMIZATION

Deberá existir:

```text
MaterialOptimizer
```

capaz de:

```text
remove_unused_nodes
merge_constants
pack_channels
reduce_texture_count
simplify_graph
```

---

# 86. OPTIMIZATION SAFETY

Ninguna optimización podrá alterar la apariencia más allá de un umbral definido.

---

# 87. VISUAL MATERIAL REGRESSION

Deberá existir comparación:

```text
REFERENCE_RENDER
vs
GENERATED_RENDER
```

---

# 88. MATERIAL GOLDENS

Mínimo:

```text
GOLDEN_SKIN
GOLDEN_METAL
GOLDEN_FABRIC
GOLDEN_WOOD
GOLDEN_CONCRETE
GOLDEN_GLASS
GOLDEN_ORGANIC
```

---

# 89. TEXTURE HASHING

Toda textura generada deberá tener:

```text
content_hash
generation_hash
source_hash
```

---

# 90. MATERIAL HASHING

Cada material deberá tener un hash determinista derivado de:

```text
definition
parameters
textures
graph
version
```

---

# 91. INCREMENTAL BUILD

Modificar un parámetro de roughness no deberá regenerar:

```text
geometry
UV
unrelated textures
```

salvo dependencia explícita.

---

# 92. DEPENDENCY GRAPH

Deberá existir:

```text
SurfaceDependencyGraph
```

---

# 93. CACHE

Deberá existir cache independiente para:

```text
procedural_noise
masks
bakes
textures
materials
instances
unreal_exports
```

---

# 94. CHECKPOINTS

Mínimo:

```text
SURFACE_DEFINED
MATERIAL_DEFINED
UV_READY
BAKE_COMPLETE
TEXTURES_COMPLETE
MATERIAL_COMPLETE
UNREAL_TRANSLATION_COMPLETE
OPTIMIZATION_COMPLETE
VALIDATION_COMPLETE
PACKAGE_COMPLETE
```

---

# 95. FAILURE RECOVERY

Un fallo durante baking no deberá invalidar automáticamente:

```text
material_definition
UV
procedural_sources
```

---

# 96. SURFACE QA

Deberá comprobar:

```text
material_validity
texture_validity
UV_validity
scale
PBR_consistency
```

---

# 97. TEXTURE QA

Deberá detectar:

```text
missing_texture
wrong_resolution
wrong_color_space
invalid_channels
compression_error
empty_texture
unexpected_alpha
```

---

# 98. PBR QA

Deberá detectar valores físicamente inválidos o sospechosos.

---

# 99. NORMAL QA

Deberá comprobar:

```text
normal_range
orientation
tangent_consistency
seam_consistency
```

---

# 100. ROUGHNESS QA

Deberá detectar:

```text
constant_map
clipping
unexpected_extremes
invalid_range
```

---

# 101. METALLIC QA

Deberá detectar valores fuera del rango permitido.

---

# 102. UV QA

Deberá comprobar:

```text
overlap
stretch
padding
density
bounds
```

---

# 103. BAKE QA

Deberá comprobar:

```text
coverage
ray_hits
seams
artifacts
projection
```

---

# 104. MATERIAL GRAPH TESTS

Mínimo:

```text
test_graph_creation
test_graph_connection
test_graph_type_validation
test_graph_cycle_detection
test_unused_node_detection
test_parameter_validation
test_graph_determinism
```

---

# 105. PROCEDURAL TESTS

Mínimo:

```text
test_noise_determinism
test_noise_scale
test_noise_seed
test_noise_octaves
test_noise_distribution
test_mask_generation
test_curvature_generation
test_edge_wear
test_dirt
test_rust
test_scratches
```

---

# 106. MATERIAL FAMILY TESTS

Mínimo:

```text
test_skin
test_fabric
test_leather
test_metal
test_painted_metal
test_rubber
test_plastic
test_glass
test_ceramic
test_concrete
test_stone
test_wood
test_organic
```

---

# 107. TEXTURE TESTS

Mínimo:

```text
test_base_color
test_normal
test_roughness
test_metallic
test_ao
test_height
test_emission
test_opacity
test_texture_resolution
test_texture_hash
```

---

# 108. UV TESTS

Mínimo:

```text
test_uv_generation
test_uv_unwrap
test_uv_packing
test_uv_padding
test_uv_density
test_uv_overlap
test_udim
```

---

# 109. BAKE TESTS

Mínimo:

```text
test_normal_bake
test_ao_bake
test_curvature_bake
test_position_bake
test_thickness_bake
test_id_bake
test_high_to_low_bake
test_cage
test_bake_failure
```

---

# 110. UNREAL TESTS

Mínimo:

```text
test_material_translation
test_parameter_translation
test_texture_import_profile
test_texture_color_space
test_normal_import
test_channel_packing
test_material_instance
test_shader_budget
```

---

# 111. OPTIMIZATION TESTS

Mínimo:

```text
test_unused_node_removal
test_constant_merge
test_channel_packing
test_texture_reduction
test_graph_simplification
test_visual_error_threshold
```

---

# 112. FAILURE TESTS

Mínimo:

```text
test_missing_texture
test_invalid_texture
test_invalid_uv
test_invalid_material
test_invalid_graph
test_graph_cycle
test_invalid_parameter
test_invalid_bake
test_bake_projection_error
test_invalid_color_space
test_invalid_normal
test_invalid_roughness
test_invalid_metallic
test_texture_budget_exceeded
test_shader_budget_exceeded
test_invalid_unreal_profile
```

---

# 113. DETERMINISM TESTS

Mínimo:

```text
test_material_determinism
test_texture_determinism
test_noise_determinism
test_mask_determinism
test_bake_determinism
test_variant_determinism
test_export_determinism
```

---

# 114. GOLDEN TESTS

Deberán existir golden renders para:

```text
skin
metal
fabric
wood
concrete
glass
organic
```

---

# 115. VISUAL REGRESSION

El sistema deberá almacenar:

```text
surface_hash
material_hash
texture_hash
camera
lighting
resolution
engine_profile
```

---

# 116. PERFORMANCE TESTS

Deberán medirse:

```text
generation_time
bake_time
texture_memory
material_memory
shader_complexity
texture_samples
```

---

# 117. BUDGET TESTS

Deberá fallar si se excede:

```text
texture_budget
shader_budget
memory_budget
generation_budget
```

cuando el perfil lo marque como obligatorio.

---

# 118. END-TO-END TEST

Debe ejecutarse:

```text
SURFACE INTENT
↓
MATERIAL DEFINITION
↓
PROCEDURAL LAYERS
↓
UV
↓
BAKE
↓
TEXTURES
↓
MATERIAL GRAPH
↓
UNREAL MATERIAL
↓
MATERIAL INSTANCE
↓
OPTIMIZATION
↓
VALIDATION
↓
EXPORT
↓
ROUND TRIP
```

---

# 119. ROUND-TRIP TEST

Deberá comprobar que:

```text
AOE MATERIAL
→
EXPORT
→
UNREAL REPRESENTATION
```

conserva la información crítica.

---

# 120. ACCEPTANCE GATES

Mínimo:

```text
DEFINITION_GATE
PBR_GATE
PROCEDURAL_GATE
UV_GATE
BAKE_GATE
TEXTURE_GATE
MATERIAL_GATE
UNREAL_GATE
OPTIMIZATION_GATE
VISUAL_GATE
PERFORMANCE_GATE
DETERMINISM_GATE
EXPORT_GATE
```

---

# 121. DEFINITION GATE

Falla ante:

```text
missing_material_family
missing_profile
invalid_parameter
missing_seed
```

---

# 122. PBR GATE

Falla ante:

```text
invalid_channel
invalid_value
missing_required_channel
```

---

# 123. BAKE GATE

Falla ante:

```text
ray_miss
projection_error
missing_bake
critical_artifact
```

---

# 124. UNREAL GATE

Falla ante:

```text
invalid_material
missing_texture
invalid_import_profile
parameter_loss
shader_budget_exceeded
```

---

# 125. FINAL ACCEPTANCE

UAF-81.46 estará completa únicamente cuando:

```text
SURFACE SCHEMA IMPLEMENTED
MATERIAL SCHEMA IMPLEMENTED
MASTER MATERIAL SYSTEM IMPLEMENTED
MATERIAL INSTANCE SYSTEM IMPLEMENTED
MATERIAL GRAPH IMPLEMENTED
PROCEDURAL TEXTURE SYSTEM IMPLEMENTED
NOISE SYSTEM IMPLEMENTED
MASK SYSTEM IMPLEMENTED
WEAR SYSTEM IMPLEMENTED
DAMAGE SYSTEM IMPLEMENTED
DIRT SYSTEM IMPLEMENTED
RUST SYSTEM IMPLEMENTED
SCRATCH SYSTEM IMPLEMENTED
UV SYSTEM IMPLEMENTED
UDIM SUPPORT IMPLEMENTED
BAKE SYSTEM IMPLEMENTED
BAKE CAGE IMPLEMENTED
PBR VALIDATION IMPLEMENTED
TEXTURE PROCESSING IMPLEMENTED
CHANNEL PACKING IMPLEMENTED
TEXTURE COMPRESSION PROFILES IMPLEMENTED
UNREAL TRANSLATION IMPLEMENTED
MATERIAL OPTIMIZATION IMPLEMENTED
SURFACE CACHE IMPLEMENTED
INCREMENTAL BUILD IMPLEMENTED
VISUAL REGRESSION IMPLEMENTED
GOLDEN MATERIALS IMPLEMENTED
REQUIRED TESTS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 126. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
7 MATERIAL GRAPH TESTS
11 PROCEDURAL TESTS
13 MATERIAL FAMILY TESTS
10 TEXTURE TESTS
7 UV TESTS
9 BAKE TESTS
8 UNREAL TESTS
6 OPTIMIZATION TESTS
16 FAILURE TESTS
7 DETERMINISM TESTS
7 GOLDEN TESTS
1 END_TO_END TEST
```

Total mínimo:

```text
102 TESTS
```

---

# 127. UNIVERSALITY REQUIREMENT

El sistema no deberá contener lógica específica que impida utilizarlo sobre:

```text
characters
weapons
props
architecture
environment
vehicles
creatures
```

---

# 128. CHARACTER INTEGRATION

UAF-81.45 deberá consumir UAF-81.46 para:

```text
skin
eyes
hair
clothing
armor
damage
decals
```

---

# 129. WEAPON INTEGRATION

El sistema deberá permitir:

```text
paint
metal
polymer
carbon
ceramic
glass
wear
scratches
```

sin crear un pipeline paralelo.

---

# 130. ENVIRONMENT INTEGRATION

El sistema deberá permitir superficies:

```text
concrete
stone
soil
wood
metal
glass
vegetation
water
```

a escala de entorno.

---

# 131. FUTURE MATERIAL EXTENSION

La arquitectura deberá permitir incorporar posteriormente:

```text
SUBSTRATE
SNOW
MUD
ICE
LIQUID
FOLIAGE
SKIN_ADVANCED
CLOTH_ADVANCED
HAIR_ADVANCED
```

sin romper el contrato existente.

---

# 132. NEXT PHASE

```text
UAF-81.47 — MODULAR GEOMETRY, BUILDING BLOCKS & PROCEDURAL ENVIRONMENT ASSEMBLY SYSTEM
```

La siguiente fase deberá resolver la otra pieza fundamental del objetivo del proyecto:

```text
BLOCKOUT
↓
MODULAR PIECES
↓
WALLS
↓
FLOORS
↓
CEILINGS
↓
DOORS
↓
WINDOWS
↓
STAIRS
↓
ROOFS
↓
ROOMS
↓
BUILDINGS
↓
FACILITIES
↓
LEVEL BLOCKOUT
↓
PROCEDURAL MAP ASSEMBLY
↓
UNREAL LEVEL PACKAGE
```

El sistema deberá compartir:

```text
SEMANTIC ASSET GRAPH
MATERIAL SYSTEM
LOD SYSTEM
COLLISION SYSTEM
VALIDATION SYSTEM
CACHE
DETERMINISM
```

con las fases anteriores.
