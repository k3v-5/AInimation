# UAF-81.30 — PROCEDURAL MATERIAL, TEXTURE, SURFACE & DECAL PRODUCTION SYSTEM

## UAF-81.30-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE PRODUCCIÓN PROCEDURAL DE MATERIALES, TEXTURAS, SUPERFICIES Y DECALS

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.30 — Procedural Material, Texture, Surface & Decal Production System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.29  
**Next Phase:** UAF-81.31  

---

# 1. PURPOSE

UAF-81.30 establece el sistema profesional de generación, composición, validación, optimización y empaquetado de superficies digitales.

El sistema deberá permitir generar superficies para:

```text
CHARACTERS
CREATURES
ROBOTS
WEAPONS
VEHICLES
PROPS
MODULAR_KITS
ARCHITECTURE
ENVIRONMENTS
VEGETATION
TERRAIN
DECORATION
```

La superficie deberá ser tratada como un asset independiente y reutilizable.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá transformar:

```text
SURFACE INTENT
↓
SURFACE SPECIFICATION
↓
MATERIAL DEFINITION
↓
TEXTURE PROFILE
↓
PROCEDURAL GENERATION
↓
MASK GENERATION
↓
LAYER COMPOSITION
↓
MATERIAL INSTANCE
↓
DECAL GENERATION
↓
VALIDATION
↓
OPTIMIZATION
↓
UNREAL PACKAGING
```

---

# 3. DESIGN PRINCIPLE

La geometría y la superficie deberán estar desacopladas.

Un cambio de:

```text
COLOR
ROUGHNESS
WEAR
DIRT
DAMAGE
NORMAL_DETAIL
EMISSION
```

no deberá obligar a reconstruir la geometría salvo que exista una dependencia explícita.

---

# 4. SURFACE DEFINITION

Deberá existir:

```text
SurfaceDefinition
```

con mínimo:

```text
surface_id
surface_name
surface_type
material_model
texture_profile
resolution_profile
layer_stack
mask_profile
decal_profile
variation_profile
optimization_profile
unreal_profile
seed
version
```

---

# 5. SURFACE TYPES

Mínimo:

```text
ORGANIC
SKIN
FLESH
METAL
PLASTIC
RUBBER
GLASS
CERAMIC
STONE
CONCRETE
WOOD
FABRIC
LEATHER
CARBON
COMPOSITE
ENERGY
HOLOGRAPHIC
LIQUID
ICE
SNOW
SAND
SOIL
VEGETATION
CUSTOM
```

---

# 6. MATERIAL MODELS

Deberán existir perfiles para:

```text
PBR_METALLIC_ROUGHNESS
PBR_SPECULAR
SUBSURFACE
TRANSLUCENT
CLEAR_COAT
EMISSIVE
HAIR
CLOTH
CUSTOM
```

---

# 7. CHANNEL DEFINITION

Cada textura deberá declarar explícitamente su canal.

Mínimo:

```text
BASE_COLOR
NORMAL
ROUGHNESS
METALLIC
SPECULAR
AO
EMISSIVE
OPACITY
HEIGHT
DISPLACEMENT
MASK
```

---

# 8. CHANNEL PACKING

Deberá existir soporte para empaquetamiento.

Ejemplo:

```text
R = AO
G = ROUGHNESS
B = METALLIC
A = MASK
```

La configuración deberá ser explícita.

---

# 9. PACKING VALIDATION

El sistema deberá detectar:

```text
CHANNEL_COLLISION
MISSING_CHANNEL
INVALID_CHANNEL_TYPE
UNUSED_CHANNEL
INCOMPATIBLE_PACKING
```

---

# 10. TEXTURE PROFILE

Deberá existir:

```text
TextureProfile
```

con:

```text
resolution
format
bit_depth
compression
color_space
mip_generation
address_mode
filter_mode
alpha_mode
streaming_group
```

---

# 11. RESOLUTION CLASSES

Mínimo:

```text
256
512
1024
2048
4096
8192
CUSTOM
```

No deberá generarse una resolución superior al presupuesto declarado.

---

# 12. TEXTURE FORMAT

Deberá soportarse un perfil de formatos compatible con el destino Unreal configurado.

El formato final no deberá asumirse únicamente por extensión de archivo.

---

# 13. COLOR SPACE

Cada textura deberá declarar:

```text
SRGB
LINEAR
NORMAL_MAP
HDR
```

según corresponda.

---

# 14. COLOR SPACE VALIDATION

Una textura normal, máscara, roughness o metallic no deberá clasificarse accidentalmente como `SRGB`.

---

# 15. PROCEDURAL NOISE

Deberán existir generadores:

```text
PERLIN
SIMPLEX
VORONOI
WORLEY
FBM
CELLULAR
GRADIENT
RANDOM
CUSTOM
```

---

# 16. NOISE PARAMETERS

Cada ruido deberá controlar:

```text
scale
frequency
octaves
lacunarity
gain
amplitude
seed
```

---

# 17. DETERMINISTIC NOISE

El mismo:

```text
seed
noise_type
parameters
generator_version
```

deberá producir el mismo resultado.

---

# 18. MASK GENERATION

Deberá existir:

```text
ProceduralMaskGenerator
```

---

# 19. MASK TYPES

Mínimo:

```text
CURVATURE
AO
POSITION
HEIGHT
NORMAL_DIRECTION
EDGE
DAMAGE
WEAR
DIRT
RUST
SCRATCH
WETNESS
DUST
MOSS
BLOOD
BURN
CUSTOM
```

---

# 20. MASK OPERATIONS

Deberán soportarse:

```text
ADD
SUBTRACT
MULTIPLY
DIVIDE
MIN
MAX
INVERT
REMAP
BLUR
SHARPEN
THRESHOLD
LEVELS
CONTRAST
```

---

# 21. MASK STACK

Las máscaras deberán poder encadenarse mediante un grafo determinista.

---

# 22. MASK GRAPH

Deberá existir:

```text
MaskGraph
```

con nodos:

```text
INPUT
NOISE
CURVATURE
POSITION
MATH
BLEND
REMAP
FILTER
OUTPUT
```

---

# 23. MATERIAL LAYER SYSTEM

Deberá existir:

```text
MaterialLayer
```

---

# 24. LAYER PARAMETERS

Cada layer podrá modificar:

```text
base_color
metallic
roughness
normal
emission
opacity
specular
```

---

# 25. LAYER BLENDING

Mínimo:

```text
NORMAL
MULTIPLY
ADD
OVERLAY
SCREEN
DARKEN
LIGHTEN
```

---

# 26. MATERIAL LAYER STACK

Ejemplo obligatorio de referencia:

```text
BASE
↓
PRIMARY_COLOR
↓
MICRO_VARIATION
↓
WEAR
↓
DIRT
↓
DAMAGE
↓
DETAIL
↓
EMISSION
```

---

# 27. MATERIAL VARIATION

Deberá existir:

```text
MaterialVariationProfile
```

para producir variantes sin duplicar manualmente el material base.

---

# 28. VARIATION PARAMETERS

Mínimo:

```text
hue
saturation
value
roughness
metallic
noise_scale
damage_amount
wear_amount
dirt_amount
emission_strength
```

---

# 29. VARIANT SEEDS

Cada variante deberá tener un seed independiente.

---

# 30. MATERIAL INSTANCE SYSTEM

Deberá existir:

```text
MaterialInstanceDefinition
```

que referencie un material padre.

---

# 31. MATERIAL INSTANCE OVERRIDES

Deberán permitirse overrides controlados.

No deberá permitirse modificar arbitrariamente parámetros fuera del contrato.

---

# 32. PARAMETER SCHEMA

Cada material deberá declarar:

```text
parameter_name
parameter_type
default_value
min_value
max_value
category
exposed
```

---

# 33. PARAMETER VALIDATION

Los valores fuera de rango deberán:

```text
REJECT
```

o:

```text
CLAMP
```

según política explícita.

---

# 34. PBR VALIDATION

El sistema deberá detectar valores físicamente inválidos o incoherentes.

Ejemplos:

```text
roughness < 0
roughness > 1
metallic < 0
metallic > 1
opacity < 0
opacity > 1
```

---

# 35. METALLIC VALIDATION

Los materiales deberán evitar valores metálicos arbitrarios cuando el perfil requiera clasificación física.

---

# 36. ROUGHNESS VARIATION

La rugosidad deberá poder variar espacialmente mediante máscaras.

---

# 37. MICRODETAIL

Deberá existir un sistema independiente de:

```text
MICRO_NORMAL
MICRO_ROUGHNESS
MICRO_COLOR
```

---

# 38. MACRODETAIL

Deberá existir:

```text
MACRO_DAMAGE
MACRO_WEAR
MACRO_PATTERN
```

sin sustituir el microdetalle.

---

# 39. DETAIL FREQUENCY

El sistema deberá distinguir:

```text
MACRO
MEDIUM
MICRO
```

para evitar texturas visualmente planas.

---

# 40. ORGANIC MATERIALS

Deberá existir soporte específico para:

```text
skin
flesh
scales
exoskeleton
organic_membrane
```

---

# 41. SKIN MATERIAL

El perfil deberá controlar:

```text
subsurface_color
subsurface_strength
roughness
specular
micro_normal
pores
oil
variation
```

---

# 42. FABRIC MATERIAL

Deberá poder controlar:

```text
weave
roughness
fuzz
normal_detail
color_variation
wear
```

---

# 43. METAL MATERIAL

Deberá poder controlar:

```text
metallic
roughness
oxidation
scratches
edge_wear
dirt
```

---

# 44. CONCRETE MATERIAL

Deberá soportar:

```text
aggregate
cracks
roughness_variation
stains
dust
moisture
wear
```

---

# 45. WOOD MATERIAL

Deberá soportar:

```text
grain
rings
color_variation
roughness
damage
splinters
moisture
```

---

# 46. GLASS MATERIAL

Deberá soportar:

```text
transmission
roughness
ior
tint
scratches
dirt
```

---

# 47. ENERGY MATERIAL

Deberá soportar:

```text
emission
color
pulse
noise
fresnel
opacity
```

---

# 48. EMISSION LIMITS

Los perfiles deberán definir límites de emisión para evitar resultados incompatibles con el pipeline visual del proyecto.

---

# 49. DECAL SYSTEM

Deberá existir:

```text
DecalDefinition
```

---

# 50. DECAL TYPES

Mínimo:

```text
DAMAGE
BLOOD
DIRT
WARNING
LOGO
GRAFFITI
NUMBER
SYMBOL
SCRATCH
BURN
LEAK
CUSTOM
```

---

# 51. DECAL PROJECTION

Deberá soportar:

```text
PLANAR
BOX
CYLINDRICAL
CUSTOM
```

---

# 52. DECAL PARAMETERS

Mínimo:

```text
position
rotation
scale
projection_depth
opacity
blend_mode
material
```

---

# 53. DECAL VALIDATION

Deberá detectar:

```text
invalid_projection
excessive_overlap
invalid_scale
invalid_material
out_of_bounds
```

---

# 54. TRIM SHEET SYSTEM

Deberá existir:

```text
TrimSheetDefinition
```

---

# 55. TRIM SEGMENTS

Cada trim deberá declarar:

```text
segment_id
width
height
orientation
material_region
```

---

# 56. TRIM VALIDATION

Deberá comprobar:

```text
UV_ALIGNMENT
SEGMENT_OVERLAP
TILING
PADDING
RESOLUTION
```

---

# 57. TILEABLE SURFACES

Deberá existir:

```text
TileableSurfaceGenerator
```

---

# 58. TILEABILITY TEST

Los bordes:

```text
LEFT ↔ RIGHT
TOP ↔ BOTTOM
```

deberán ser compatibles dentro de una tolerancia configurable.

---

# 59. UNIQUE SURFACES

Deberá existir un pipeline separado para texturas únicas por asset.

---

# 60. UNIQUE TEXTURE SOURCES

Podrán utilizar:

```text
UV_POSITION
OBJECT_SPACE
WORLD_SPACE
CURVATURE
BAKED_MASKS
PROCEDURAL_MASKS
```

---

# 61. TEXTURE BAKING

Deberá existir:

```text
TextureBakePipeline
```

---

# 62. BAKE INPUTS

Mínimo:

```text
HIGH_POLY
LOW_POLY
CAGE
UV
MATERIAL_ID
```

---

# 63. BAKE OUTPUTS

Mínimo:

```text
NORMAL
AO
CURVATURE
POSITION
THICKNESS
ID
```

---

# 64. BAKE VALIDATION

Deberá detectar:

```text
RAY_FAILURE
CAGE_ERROR
SEAM_ARTIFACT
PROJECTION_ERROR
MISSING_UV
INVALID_NORMAL
```

---

# 65. NORMAL MAP VALIDATION

Deberá comprobar:

```text
format
orientation
range
seams
invalid_pixels
```

---

# 66. TEXTURE SEAM ANALYSIS

Deberá existir una prueba automática de seams visibles.

---

# 67. TEXTURE BLEEDING

Deberá existir padding configurable para evitar bleeding entre UV islands.

---

# 68. MIPMAP SYSTEM

Deberá existir política para generación de mipmaps.

---

# 69. MIP VALIDATION

Deberá comprobar:

```text
missing_mips
incorrect_chain
aliasing
unexpected_color_shift
```

---

# 70. TEXTURE STREAMING

Cada textura deberá declarar un perfil de streaming.

---

# 71. MEMORY BUDGET

Deberá calcular:

```text
raw_memory
compressed_memory
runtime_memory
streaming_memory
```

---

# 72. MATERIAL MEMORY BUDGET

Deberá existir un límite configurable por categoría de asset.

---

# 73. MATERIAL COUNT

Cada asset deberá declarar su máximo de materiales permitidos.

---

# 74. MATERIAL CONSOLIDATION

Cuando sea seguro, el sistema deberá detectar materiales equivalentes y proponer o ejecutar consolidación.

---

# 75. SHADER COMPLEXITY

Deberá existir:

```text
ShaderComplexityProfile
```

---

# 76. SHADER VALIDATION

Deberá detectar:

```text
EXCESSIVE_INSTRUCTIONS
EXCESSIVE_TEXTURE_SAMPLES
UNUSED_PARAMETERS
DUPLICATED_LOGIC
INVALID_REFERENCE
```

---

# 77. MASTER MATERIAL

Deberá existir una arquitectura de materiales maestros reutilizables.

---

# 78. MASTER MATERIAL FAMILIES

Mínimo:

```text
M_ORGANIC
M_METAL
M_FABRIC
M_CONCRETE
M_WOOD
M_GLASS
M_ENERGY
M_TERRAIN
M_DECAL
```

---

# 79. MATERIAL INSTANCE POLICY

Los assets deberán utilizar instancias cuando sea posible en lugar de materiales completamente duplicados.

---

# 80. MATERIAL NAMING

Deberá existir un contrato configurable para:

```text
M_
MI_
MF_
```

---

# 81. TEXTURE NAMING

Deberá existir un contrato configurable para:

```text
T_
TEX_
```

y sufijos de canal.

---

# 82. TEXTURE SUFFIXES

Mínimo:

```text
_BC
_N
_R
_M
_AO
_E
_MR
_MASK
_H
```

---

# 83. TEXTURE DIRECTORY STRUCTURE

El sistema deberá producir una estructura determinista:

```text
Assets/
└── <Category>/
    └── <Asset>/
        └── Materials/
        └── Textures/
        └── Decals/
        └── Instances/
```

---

# 84. TEXTURE MANIFEST

Deberá existir:

```text
texture_manifest.json
```

---

# 85. MATERIAL MANIFEST

Deberá existir:

```text
material_manifest.json
```

---

# 86. SURFACE MANIFEST

Deberá existir:

```text
surface_manifest.json
```

---

# 87. HASHING

Cada salida deberá tener:

```text
content_hash
source_hash
generator_hash
```

---

# 88. CACHE

El sistema deberá evitar regenerar texturas idénticas.

---

# 89. CACHE INVALIDATION

El cache deberá invalidarse si cambia:

```text
generator_version
surface_definition
seed
material_graph
texture_profile
resolution
```

---

# 90. PARTIAL REBUILD

Deberá poder reconstruirse individualmente:

```text
MASK
TEXTURE
MATERIAL
DECAL
TRIM
BAKE
```

---

# 91. PROCEDURAL DAMAGE

Deberá existir:

```text
DamageProfile
```

---

# 92. DAMAGE TYPES

Mínimo:

```text
SCRATCH
DENT
CRACK
CHIP
BURN
BULLET
IMPACT
CUT
CORROSION
```

---

# 93. WEAR SYSTEM

Deberá existir:

```text
WearProfile
```

---

# 94. WEAR SOURCES

Mínimo:

```text
EDGES
CONTACT
EXPOSURE
FREQUENCY
RANDOM
DIRECTION
```

---

# 95. DIRT SYSTEM

Deberá existir:

```text
DirtProfile
```

con:

```text
accumulation
direction
density
color
roughness
```

---

# 96. ENVIRONMENTAL ACCUMULATION

Deberá existir soporte para:

```text
dust
mud
snow
moss
moisture
```

---

# 97. SURFACE AGE

Deberá existir:

```text
AgeProfile
```

capaz de controlar envejecimiento procedural.

---

# 98. STYLE PRESERVATION

El sistema deberá separar:

```text
PHYSICAL_REALISM
ART_DIRECTION
```

para permitir superficies realistas, estilizadas o híbridas.

---

# 99. ART DIRECTION PROFILE

Deberá existir:

```text
ArtDirectionSurfaceProfile
```

---

# 100. ART DIRECTION PARAMETERS

Mínimo:

```text
contrast
saturation
roughness_range
color_variation
detail_density
wear_strength
damage_strength
emission_style
```

---

# 101. SURFACE CONSISTENCY

Todos los materiales de un mismo asset deberán poder compartir:

```text
palette
wear_language
damage_language
roughness_language
detail_scale
```

---

# 102. ASSET-WIDE SURFACE PROFILE

Deberá existir:

```text
AssetSurfaceProfile
```

para garantizar coherencia entre múltiples materiales.

---

# 103. CHARACTER SURFACE INTEGRATION

Deberá integrarse con UAF-81.29.

---

# 104. WEAPON SURFACE INTEGRATION

Deberá integrarse con assets de armas.

---

# 105. MODULAR BLOCK INTEGRATION

Deberá permitir materiales reutilizables en:

```text
walls
floors
doors
windows
pipes
panels
stairs
```

---

# 106. ENVIRONMENT INTEGRATION

Deberá permitir superficies compartidas por un entorno completo.

---

# 107. TERRAIN INTEGRATION

Deberá soportar:

```text
terrain_material
layered_material
slope_masks
height_masks
biome_masks
```

---

# 108. BIOME MATERIALS

Deberá permitir perfiles:

```text
DESERT
FOREST
TUNDRA
URBAN
INDUSTRIAL
ALIEN
SCI_FI
CUSTOM
```

---

# 109. SURFACE BLENDING

Los materiales de terreno deberán poder mezclarse mediante:

```text
height
slope
noise
biome
mask
```

---

# 110. DECAL LIBRARY

Deberá existir una biblioteca indexada de decals reutilizables.

---

# 111. MATERIAL LIBRARY

Deberá existir una biblioteca indexada de materiales.

---

# 112. TEXTURE LIBRARY

Deberá existir una biblioteca indexada de texturas.

---

# 113. LIBRARY DEDUPLICATION

Los elementos equivalentes deberán poder identificarse mediante hash.

---

# 114. SEARCH INDEX

Cada recurso deberá indexarse mediante:

```text
id
type
tags
category
style
resolution
format
usage
hash
dependencies
```

---

# 115. DEPENDENCY GRAPH

Deberá registrarse:

```text
Surface
→ Material
→ Texture
→ Mask
→ Generator
```

---

# 116. ORPHAN DETECTION

Deberá detectarse:

```text
orphan_texture
orphan_material
orphan_mask
orphan_decal
```

---

# 117. BROKEN REFERENCE DETECTION

Deberá detectar referencias inexistentes.

---

# 118. UNREAL COMPATIBILITY

Cada surface package deberá declarar:

```text
engine_version
material_model
texture_formats
shader_features
virtual_texture_usage
nanite_compatibility
```

cuando corresponda.

---

# 119. VIRTUAL TEXTURE

Deberá existir soporte configurable para virtual textures.

---

# 120. VIRTUAL TEXTURE VALIDATION

Deberá comprobar que el material y las texturas utilizadas son compatibles con la configuración declarada.

---

# 121. UDIM

Deberá existir soporte explícitamente configurable para:

```text
UDIM_ENABLED
UDIM_DISABLED
```

---

# 122. UDIM VALIDATION

Cuando esté habilitado:

```text
tile_number
tile_sequence
missing_tile
duplicate_tile
```

deberán validarse.

---

# 123. DECAL PERFORMANCE

Deberá existir presupuesto de decals por asset y por escena.

---

# 124. MATERIAL INSTANCE PERFORMANCE

Deberá medirse el coste de variantes.

---

# 125. TEXTURE ATLAS

Deberá existir soporte opcional para atlas.

---

# 126. ATLAS VALIDATION

Deberá comprobar:

```text
padding
UV_mapping
bleeding
resolution
```

---

# 127. SURFACE QA

Deberán producirse visualizaciones:

```text
BASE_COLOR
ROUGHNESS
METALLIC
NORMAL
AO
EMISSION
MASKS
WIREFRAME
UV
```

---

# 128. MATERIAL QA

Deberá existir render de prueba con iluminación estándar.

---

# 129. LIGHTING REGRESSION

La validación deberá utilizar escenarios de iluminación controlados.

---

# 130. EXTREME LIGHT TEST

Cada material deberá evaluarse bajo:

```text
LOW_LIGHT
NEUTRAL_LIGHT
HIGH_LIGHT
COLORED_LIGHT
```

---

# 131. COLOR REGRESSION

Deberá comprobarse que cambios de pipeline no alteren inesperadamente el color.

---

# 132. ROUGHNESS REGRESSION

Deberá comprobarse continuidad y coherencia de roughness.

---

# 133. NORMAL REGRESSION

Deberán detectarse cambios inesperados de orientación o intensidad.

---

# 134. EMISSION REGRESSION

Deberá detectarse emisión excesiva.

---

# 135. TEXTURE ARTIFACT DETECTION

Deberá detectar:

```text
seams
tiling_artifacts
repetition
stretching
compression_artifacts
banding
aliasing
```

---

# 136. PROCEDURAL REPETITION

Deberá existir una métrica para detectar repetición visual excesiva.

---

# 137. RANDOMNESS CONTROL

Toda aleatoriedad deberá provenir de un seed controlado.

---

# 138. REPRODUCIBILITY

Dos builds equivalentes deberán producir resultados equivalentes.

---

# 139. ERROR CLASSIFICATION

Mínimo:

```text
SURFACE_ERROR
TEXTURE_ERROR
MATERIAL_ERROR
MASK_ERROR
BAKE_ERROR
DECAL_ERROR
UV_ERROR
SHADER_ERROR
UNREAL_COMPATIBILITY_ERROR
```

---

# 140. QUALITY SCORE

Deberá existir:

```text
SurfaceQualityReport
```

con:

```text
material_score
texture_score
mask_score
uv_score
visual_score
performance_score
memory_score
unreal_score
consistency_score
```

---

# 141. QUALITY STATES

Mínimo:

```text
DRAFT
GENERATED
VALIDATED
OPTIMIZED
UNREAL_READY
WARNING
FAILED
```

---

# 142. HARD FAIL CONDITIONS

Se deberá rechazar el resultado ante:

```text
missing_required_texture
invalid_texture_format
invalid_color_space
broken_material_reference
invalid_uv_dependency
invalid_shader
critical_bake_failure
invalid_unreal_contract
```

---

# 143. UNIT TESTS

Mínimo:

```text
test_surface_definition
test_texture_profile
test_resolution_profile
test_color_space
test_channel_definition
test_channel_packing
test_noise_generator
test_noise_determinism
test_mask_generator
test_mask_graph
test_mask_operations
test_material_layer
test_material_layer_stack
test_material_variation
test_material_instance
test_parameter_schema
test_pbr_validation
test_microdetail
test_macrodetail
test_organic_material
test_metal_material
test_fabric_material
test_concrete_material
test_wood_material
test_glass_material
test_energy_material
test_decal_definition
test_decal_projection
test_decal_validation
test_trim_sheet
test_trim_validation
test_tileable_surface
test_tileability
test_unique_surface
test_texture_baking
test_bake_validation
test_normal_validation
test_mip_validation
test_texture_memory
test_shader_complexity
test_material_library
test_texture_library
test_deduplication
test_dependency_graph
test_orphan_detection
test_unreal_compatibility
test_virtual_texture
test_udim
test_atlas
test_surface_quality
```

---

# 144. INTEGRATION TESTS

Mínimo:

```text
surface → material
material → texture
texture → mask
mask → material
material → unreal
character → surface
weapon → surface
prop → surface
block → surface
terrain → surface
environment → surface
```

---

# 145. FAILURE TESTS

Mínimo:

```text
invalid_resolution
invalid_format
invalid_color_space
invalid_channel
invalid_packing
broken_mask
broken_material
missing_texture
invalid_uv
bake_failure
normal_failure
mip_failure
shader_failure
invalid_decal
invalid_trim
tileability_failure
udim_failure
atlas_failure
unreal_material_failure
```

---

# 146. DETERMINISM TESTS

Mínimo:

```text
noise
masks
material_layers
material_variations
damage
wear
dirt
texture_generation
baking
decals
trim
terrain_blending
full_surface_generation
```

---

# 147. PERFORMANCE TESTS

Mínimo:

```text
noise_generation
mask_generation
texture_generation
material_generation
baking
decals
atlas_generation
library_search
deduplication
full_surface_build
```

---

# 148. EXPORT TESTS

Mínimo:

```text
material
material_instance
base_color
normal
packed_maps
emission
decals
trim
terrain_material
unreal_package
```

---

# 149. GOLDEN SURFACES

Deberán existir como mínimo:

```text
GOLDEN_SKIN
GOLDEN_METAL
GOLDEN_FABRIC
GOLDEN_CONCRETE
GOLDEN_WOOD
GOLDEN_GLASS
GOLDEN_ENERGY
GOLDEN_TERRAIN
```

---

# 150. REGRESSION TESTS

Los golden surfaces deberán compararse en:

```text
color
roughness
metallic
normal
emission
mask_distribution
texture_memory
shader_complexity
```

---

# 151. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
50 UNIT TESTS
25 INTEGRATION TESTS
20 FAILURE TESTS
15 DETERMINISM TESTS
15 PERFORMANCE TESTS
15 EXPORT TESTS
20 GOLDEN/REGRESSION TESTS
```

Total mínimo:

```text
160 TESTS
```

---

# 152. TEST NON-DUPLICATION

Los tests deberán verificar condiciones independientes.

No se aceptará incrementar el número mediante duplicación semántica.

---

# 153. BUILD CHECKPOINTS

Mínimo:

```text
SURFACE_DEFINED
MATERIAL_DEFINED
MASKS_COMPLETE
TEXTURES_COMPLETE
BAKE_COMPLETE
MATERIAL_VALIDATED
OPTIMIZED
UNREAL_PACKAGED
```

---

# 154. TRANSACTIONAL BUILD

La construcción deberá ser transaccional.

---

# 155. ROLLBACK

Un fallo de cualquier etapa deberá permitir volver al último checkpoint válido.

---

# 156. OBSERVABILITY

Cada operación deberá registrar:

```text
surface_id
stage
duration
input_hash
output_hash
memory_usage
texture_count
material_count
shader_cost
warnings
errors
```

---

# 157. SURFACE MANIFEST

El manifest final deberá registrar:

```text
identity
materials
textures
masks
decals
trim
uv_dependencies
memory
performance
unreal_compatibility
hashes
dependencies
validation
```

---

# 158. CROSS-ASSET REUSE

Un mismo material podrá ser utilizado por:

```text
CHARACTER
WEAPON
PROP
BLOCK
ENVIRONMENT
```

siempre que su contrato sea compatible.

---

# 159. CROSS-ASSET CONSISTENCY

Deberá existir un mecanismo para garantizar que materiales compartidos mantengan la misma definición entre assets.

---

# 160. FINAL DEFINITION OF DONE

UAF-81.30 sólo estará completa cuando:

```text
SURFACE_SCHEMA_IMPLEMENTED
TEXTURE_SCHEMA_IMPLEMENTED
MATERIAL_SCHEMA_IMPLEMENTED
MASK_SCHEMA_IMPLEMENTED
MATERIAL_LAYER_SYSTEM_IMPLEMENTED
PROCEDURAL_NOISE_IMPLEMENTED
PROCEDURAL_MASKS_IMPLEMENTED
MATERIAL_VARIATION_IMPLEMENTED
MATERIAL_INSTANCE_SYSTEM_IMPLEMENTED
PBR_VALIDATION_IMPLEMENTED
ORGANIC_MATERIALS_IMPLEMENTED
METAL_MATERIALS_IMPLEMENTED
FABRIC_MATERIALS_IMPLEMENTED
CONCRETE_MATERIALS_IMPLEMENTED
WOOD_MATERIALS_IMPLEMENTED
GLASS_MATERIALS_IMPLEMENTED
ENERGY_MATERIALS_IMPLEMENTED
DECAL_SYSTEM_IMPLEMENTED
TRIM_SYSTEM_IMPLEMENTED
TILEABLE_SURFACE_SYSTEM_IMPLEMENTED
UNIQUE_TEXTURE_SYSTEM_IMPLEMENTED
TEXTURE_BAKING_IMPLEMENTED
NORMAL_VALIDATION_IMPLEMENTED
MIP_VALIDATION_IMPLEMENTED
MEMORY_ANALYSIS_IMPLEMENTED
SHADER_ANALYSIS_IMPLEMENTED
MATERIAL_LIBRARY_IMPLEMENTED
TEXTURE_LIBRARY_IMPLEMENTED
DEDUPLICATION_IMPLEMENTED
DEPENDENCY_GRAPH_IMPLEMENTED
ORPHAN_DETECTION_IMPLEMENTED
UNREAL_COMPATIBILITY_IMPLEMENTED
VIRTUAL_TEXTURE_SUPPORT_IMPLEMENTED
UDIM_SUPPORT_IMPLEMENTED
ATLAS_SUPPORT_IMPLEMENTED
SURFACE_QA_IMPLEMENTED
VISUAL_REGRESSION_IMPLEMENTED
CACHE_IMPLEMENTED
PARTIAL_REBUILD_IMPLEMENTED
CHECKPOINTS_IMPLEMENTED
ROLLBACK_IMPLEMENTED
MANIFEST_IMPLEMENTED
UNIT_TESTS_IMPLEMENTED
INTEGRATION_TESTS_IMPLEMENTED
FAILURE_TESTS_IMPLEMENTED
DETERMINISM_TESTS_IMPLEMENTED
PERFORMANCE_TESTS_IMPLEMENTED
EXPORT_TESTS_IMPLEMENTED
GOLDEN_TESTS_IMPLEMENTED
REGRESSION_TESTS_IMPLEMENTED
DOCUMENTATION_COMPLETE
```

---

# 161. FINAL OUTPUT CONTRACT

El sistema deberá producir:

```text
SurfacePackage
├── SurfaceDefinition
├── MaterialDefinition
├── MaterialInstances
├── TextureSet
├── Masks
├── Decals
├── TrimSheets
├── UVRequirements
├── ShaderProfile
├── MemoryProfile
├── PerformanceProfile
├── UnrealCompatibility
├── Manifest
└── ValidationReport
```

---

# 162. NEXT PHASE

```text
UAF-81.31 — PROCEDURAL MODULAR ASSET & ARCHITECTURE PRODUCTION SYSTEM
```

Esta fase deberá establecer el sistema profesional para generar:

```text
WALLS
FLOORS
CEILINGS
DOORS
WINDOWS
STAIRS
COLUMNS
PIPES
PANELS
ROOMS
CORRIDORS
BUILDINGS
MODULAR_KITS
INTERIOR_KITS
EXTERIOR_KITS
```

con snapping, sockets, reglas de ensamblaje, variantes, colisiones, LOD, materiales, instanciación y validación automática para Unreal.
