# UAF-81.52 — UNIVERSAL MATERIAL, TEXTURE & SURFACE AUTHORING SYSTEM

## UAF-81.52-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA UNIVERSAL DE AUTORÍA DE MATERIALES, TEXTURAS Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.52 — Universal Material, Texture & Surface Authoring System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.51  
**Next Phase:** UAF-81.53  

---

# 1. PURPOSE

UAF-81.52 define el sistema universal para crear, transformar, combinar, validar, optimizar, versionar y exportar materiales, texturas y superficies físicas y visuales.

El sistema deberá ser reutilizable por:

```text
CHARACTERS
CREATURES
WEAPONS
PROPS
VEHICLES
ARCHITECTURE
ENVIRONMENTS
TERRAIN
VEGETATION
VFX
UI
```

No deberá existir un sistema de materiales independiente por categoría de asset.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá producir un:

```text
ProductionReadySurfacePackage
```

conteniendo como mínimo:

```text
SURFACE_DEFINITION
MATERIAL_DEFINITION
TEXTURE_DEFINITIONS
PBR_CHANNELS
MATERIAL_INSTANCES
UV_CONFIGURATION
SAMPLING_CONFIGURATION
LAYER_DEFINITION
MASK_DEFINITION
DECAL_DEFINITION
VARIANT_DEFINITION
LOD_CONFIGURATION
MEMORY_ESTIMATE
PERFORMANCE_ESTIMATE
VALIDATION_RESULTS
UNREAL_EXPORT_METADATA
```

---

# 3. CORE PRINCIPLE

El sistema deberá separar:

```text
PHYSICAL SURFACE
        ↓
SURFACE MODEL
        ↓
TEXTURE DATA
        ↓
MATERIAL GRAPH
        ↓
MATERIAL INSTANCE
        ↓
ASSET ASSIGNMENT
```

No se deberá mezclar información de textura con reglas de gameplay.

---

# 4. SURFACE MODEL

Deberá existir:

```text
SurfaceDefinition
```

con:

```text
surface_id
surface_type
physical_properties
visual_properties
texture_set
material_profile
uv_profile
layer_profile
variant_profile
```

---

# 5. SURFACE TYPES

Mínimo:

```text
METAL
WOOD
STONE
CONCRETE
BRICK
CERAMIC
GLASS
PLASTIC
RUBBER
FABRIC
LEATHER
PAPER
SOIL
SAND
MUD
GRASS
ROCK
ICE
SNOW
WATER
FOLIAGE
SKIN
ORGANIC
EMISSIVE
CUSTOM
```

---

# 6. PBR MODEL

El sistema deberá soportar como mínimo:

```text
BASE_COLOR
METALLIC
ROUGHNESS
NORMAL
AMBIENT_OCCLUSION
HEIGHT
EMISSIVE
OPACITY
SPECULAR
```

---

# 7. OPTIONAL CHANNELS

Deberá soportar:

```text
SUBSURFACE
SUBSURFACE_COLOR
CLEAR_COAT
CLEAR_COAT_ROUGHNESS
ANISOTROPY
REFRACTION
TRANSMISSION
SHEEN
CUSTOM_CHANNELS
```

cuando el target renderer lo permita.

---

# 8. CHANNEL DEFINITION

Cada canal deberá declarar:

```text
channel_id
data_type
color_space
resolution
bit_depth
default_value
compression
usage
```

---

# 9. COLOR SPACE

El sistema deberá distinguir explícitamente entre:

```text
SRGB
LINEAR
DATA
NORMAL_MAP
HDR
```

No se permitirá asumir el color space por extensión del archivo.

---

# 10. NORMAL MAP

Las normal maps deberán declarar:

```text
NORMAL_X
NORMAL_Y
NORMAL_Z
```

y el sistema deberá soportar explícitamente:

```text
DIRECTX
OPENGL
```

con conversión validada.

---

# 11. HEIGHT DATA

Deberá soportarse:

```text
HEIGHT_8BIT
HEIGHT_16BIT
HEIGHT_FLOAT
```

cuando el pipeline lo requiera.

---

# 12. TEXTURE DEFINITION

Deberá existir:

```text
TextureDefinition
```

con:

```text
texture_id
source
resolution
format
color_space
compression
mip_policy
tiling
address_mode
channel_usage
```

---

# 13. SOURCE TYPES

Mínimo:

```text
GENERATED
IMPORTED
DERIVED
BAKED
PROCEDURAL
PACKED
ATLAS
UDIM
VIRTUAL_TEXTURE
```

---

# 14. TEXTURE RESOLUTIONS

Deberán soportarse resoluciones configurables:

```text
256
512
1024
2048
4096
8192
CUSTOM
```

El sistema deberá impedir resoluciones no soportadas por el target.

---

# 15. NON-POWER-OF-TWO

Deberá existir soporte explícito para resoluciones no potencia de dos cuando el target lo permita.

---

# 16. MIPMAP SYSTEM

Cada textura deberá declarar:

```text
generate_mips
mip_bias
mip_filter
minimum_mip
maximum_mip
```

---

# 17. MIP VALIDATION

Deberá detectar:

```text
missing_mips
invalid_mip_chain
incorrect_mip_dimensions
```

---

# 18. COMPRESSION

Deberá existir una política configurable por canal:

```text
BC1
BC3
BC4
BC5
BC6H
BC7
ASTC
ETC2
UNCOMPRESSED
CUSTOM
```

según target.

---

# 19. COMPRESSION RULES

No se permitirá seleccionar compresión únicamente por tamaño.

Deberá considerarse:

```text
channel_type
visual_quality
platform
memory_budget
runtime_usage
```

---

# 20. TEXTURE PACKING

Deberá existir:

```text
TexturePackingDefinition
```

permitiendo empaquetar:

```text
R
G
B
A
```

---

# 21. COMMON PACKING

Deberá soportar perfiles como:

```text
ORM
RMA
MASK_RGBA
CUSTOM
```

---

# 22. PACKING VALIDATION

El sistema deberá comprobar que el consumidor espera exactamente el layout generado.

---

# 23. UV SYSTEM

Deberá existir:

```text
UVProfile
UVChannelDefinition
UVValidation
```

---

# 24. UV CHANNELS

Deberán soportarse múltiples canales:

```text
UV0
UV1
UV2
UV3
...
```

hasta el límite del target.

---

# 25. UV PURPOSE

Cada canal deberá declarar:

```text
BASE_TEXTURE
LIGHTMAP
DETAIL
MASK
DECAL
CUSTOM
```

---

# 26. UV TRANSFORM

Deberá soportar:

```text
scale
rotation
offset
pivot
mirror_u
mirror_v
```

---

# 27. WORLD ALIGNED MATERIALS

Deberá existir soporte para:

```text
WORLD_ALIGNED
TRIPLANAR
OBJECT_ALIGNED
SCREEN_ALIGNED
UV_ALIGNED
```

---

# 28. TRIPLANAR

El sistema deberá permitir:

```text
blend_sharpness
projection_scale
projection_offset
axis_weights
```

---

# 29. TILEABLE MATERIALS

Deberá soportar superficies tileables sin seams visibles bajo condiciones definidas por el profile.

---

# 30. SEAM VALIDATION

Deberá existir detector para:

```text
horizontal_seam
vertical_seam
rotation_seam
tile_boundary
```

---

# 31. MATERIAL GRAPH

Deberá existir una representación abstracta:

```text
MaterialGraph
MaterialNode
MaterialConnection
MaterialParameter
```

---

# 32. GRAPH NODES

Mínimo:

```text
CONSTANT
PARAMETER
TEXTURE_SAMPLE
NORMAL
MULTIPLY
ADD
SUBTRACT
DIVIDE
LERP
CLAMP
POWER
REMAP
MASK
FRESNEL
TIME
WORLD_POSITION
OBJECT_POSITION
VERTEX_NORMAL
PIXEL_NORMAL
```

---

# 33. MATERIAL OUTPUT

Deberá soportar:

```text
BASE_COLOR
METALLIC
ROUGHNESS
NORMAL
AO
EMISSIVE
OPACITY
SPECULAR
```

y outputs adicionales según renderer.

---

# 34. GRAPH VALIDATION

Deberá detectar:

```text
missing_input
invalid_connection
type_mismatch
cycle
unused_node
unsupported_node
missing_output
```

---

# 35. GRAPH CYCLES

No deberá existir ningún ciclo inválido en el grafo.

---

# 36. UNUSED NODE DETECTION

Los nodos no utilizados deberán producir:

```text
WARNING
```

o ser eliminados automáticamente si el profile lo permite.

---

# 37. MATERIAL PARAMETERS

Deberán soportarse:

```text
SCALAR
VECTOR
COLOR
TEXTURE
BOOLEAN
ENUM
```

---

# 38. PARAMETER METADATA

Cada parámetro deberá declarar:

```text
name
type
default
minimum
maximum
ui_group
description
runtime_editable
```

---

# 39. PARAMETER VALIDATION

Los valores fuera de rango deberán ser detectados antes del export.

---

# 40. MATERIAL INSTANCES

Deberá existir:

```text
MaterialInstanceDefinition
```

que permita modificar parámetros sin duplicar el material base.

---

# 41. INSTANCE INHERITANCE

Deberá soportarse:

```text
MASTER
PARENT
INSTANCE
CHILD_INSTANCE
```

---

# 42. INSTANCE OVERRIDES

Los overrides deberán registrarse explícitamente.

---

# 43. NO DUPLICATE MATERIALS

Materiales funcionalmente equivalentes deberán reutilizarse cuando sea posible.

---

# 44. MATERIAL FINGERPRINT

Cada material deberá generar:

```text
MaterialFingerprint
```

basado en:

```text
graph
parameters
textures
samplers
settings
```

---

# 45. DEDUPLICATION

Materiales con fingerprint equivalente deberán poder compartir recursos.

---

# 46. SURFACE LAYERS

Deberá existir:

```text
SurfaceLayer
LayerStack
```

---

# 47. LAYER TYPES

Mínimo:

```text
BASE
DIRT
DUST
MUD
SCRATCH
RUST
WEAR
WETNESS
SNOW
ICE
MOSS
BLOOD
DAMAGE
CUSTOM
```

---

# 48. LAYER PARAMETERS

Cada layer deberá declarar:

```text
mask
blend_mode
opacity
priority
material_override
```

---

# 49. LAYER BLENDING

Deberá soportar:

```text
LERP
MULTIPLY
ADD
OVERLAY
SOFT_LIGHT
SCREEN
MAX
MIN
```

según renderer.

---

# 50. LAYER MASKS

Las máscaras podrán proceder de:

```text
TEXTURE
VERTEX_COLOR
WORLD_POSITION
SLOPE
HEIGHT
CURVATURE
NOISE
ATTRIBUTE
CUSTOM
```

---

# 51. PROCEDURAL MASKS

Deberá existir:

```text
ProceduralMaskDefinition
```

---

# 52. PROCEDURAL MASK TYPES

Mínimo:

```text
NOISE
VORONOI
GRADIENT
HEIGHT
SLOPE
CURVATURE
DISTANCE
RANDOM
CELLULAR
CUSTOM
```

---

# 53. PROCEDURAL DETERMINISM

Las máscaras procedurales deberán utilizar seed cuando exista aleatoriedad.

---

# 54. MASK RESOLUTION

Las máscaras deberán poder generarse a diferentes resoluciones según necesidad.

---

# 55. MASK OPTIMIZATION

El sistema deberá evitar generar resolución superior a la necesaria.

---

# 56. DETAIL MATERIAL

Deberá existir soporte para:

```text
DETAIL_ALBEDO
DETAIL_NORMAL
DETAIL_ROUGHNESS
```

---

# 57. DETAIL SCALE

Deberá existir control independiente de:

```text
detail_scale
detail_strength
detail_distance
```

---

# 58. MACRO VARIATION

Deberá soportarse variación de gran escala:

```text
macro_color
macro_roughness
macro_normal
```

para evitar repetición visual.

---

# 59. MICRO VARIATION

Deberá soportarse variación de pequeña escala.

---

# 60. MATERIAL VARIANTS

Deberá existir:

```text
MaterialVariant
```

---

# 61. VARIANT TYPES

Mínimo:

```text
CLEAN
WORN
DIRTY
WET
DRY
DAMAGED
AGED
SNOW_COVERED
BURNED
CORRODED
CUSTOM
```

---

# 62. VARIANT INHERITANCE

Las variantes deberán heredar del material base.

---

# 63. VARIANT CONSISTENCY

Las variantes no deberán romper:

```text
physical_properties
shader_contract
texture_contract
runtime_parameters
```

---

# 64. DECAL SYSTEM

Deberá existir:

```text
DecalDefinition
DecalMaterial
DecalProjection
```

---

# 65. DECAL TYPES

Mínimo:

```text
DAMAGE
DIRT
GRAFFITI
SIGN
WETNESS
BLOOD
WEAR
WEAPON_MARK
ENVIRONMENTAL
CUSTOM
```

---

# 66. DECAL PARAMETERS

```text
projection_type
size
opacity
blend
normal_influence
roughness_influence
lifetime
```

---

# 67. DECAL PERFORMANCE

Deberá existir un presupuesto específico para decals.

---

# 68. VIRTUAL TEXTURE

Deberá soportarse:

```text
VIRTUAL_TEXTURE
```

cuando el target lo requiera.

---

# 69. VT VALIDATION

Deberá comprobar:

```text
page_size
tile_size
format
channel_layout
streaming_policy
```

---

# 70. UDIM

Deberá existir soporte para:

```text
UDIM_SET
UDIM_TILE
UDIM_LAYOUT
```

---

# 71. UDIM VALIDATION

Deberá detectar:

```text
missing_tile
duplicate_tile
invalid_tile
broken_sequence
```

---

# 72. ATLAS SYSTEM

Deberá existir:

```text
TextureAtlas
AtlasRegion
AtlasPackingPolicy
```

---

# 73. ATLAS RULES

El atlas deberá registrar:

```text
source_texture
region
padding
rotation
scale
```

---

# 74. ATLAS PADDING

Deberá existir padding configurable para evitar bleeding.

---

# 75. TEXTURE BLEEDING TEST

El sistema deberá incluir test específico para bleeding entre regiones del atlas.

---

# 76. RESOLUTION SCALING

Deberá existir un sistema para generar versiones:

```text
LOW
MEDIUM
HIGH
ULTRA
CUSTOM
```

---

# 77. QUALITY PROFILE

Cada quality profile deberá declarar:

```text
texture_resolution
normal_resolution
mask_resolution
compression
mip_policy
detail_level
```

---

# 78. PLATFORM PROFILES

Mínimo:

```text
PC
CONSOLE
MOBILE
CINEMATIC
VR
CUSTOM
```

---

# 79. PLATFORM OVERRIDES

Cada plataforma podrá modificar:

```text
resolution
compression
mip_bias
shader_features
virtual_texture
```

sin modificar el material lógico base.

---

# 80. MEMORY ESTIMATION

Deberá calcular:

```text
raw_texture_memory
compressed_texture_memory
runtime_memory
streaming_memory
```

---

# 81. MATERIAL COST

Deberá estimar:

```text
shader_complexity
texture_samples
instruction_count
variant_count
```

cuando la información esté disponible.

---

# 82. SHADER COMPLEXITY

Deberá existir clasificación:

```text
LOW
MEDIUM
HIGH
VERY_HIGH
```

---

# 83. MATERIAL BUDGET

Cada asset deberá poder declarar:

```text
max_materials
max_material_instances
max_texture_memory
max_shader_complexity
```

---

# 84. AUTOMATIC OPTIMIZATION

El sistema podrá aplicar:

```text
texture_downscale
channel_packing
material_deduplication
unused_parameter_removal
unused_texture_removal
instance_reuse
```

únicamente cuando no rompa el quality profile.

---

# 85. LOSSY OPTIMIZATION

Toda optimización con pérdida deberá registrar:

```text
optimization_id
source
target
quality_delta
memory_delta
performance_delta
```

---

# 86. SOURCE OF TRUTH

Los assets derivados no deberán reemplazar silenciosamente la fuente original.

---

# 87. DERIVATION GRAPH

Deberá existir:

```text
SOURCE
 ↓
DERIVED_TEXTURE
 ↓
PACKED_TEXTURE
 ↓
MATERIAL
 ↓
INSTANCE
```

---

# 88. CACHE

Deberá existir cache para recursos derivados.

---

# 89. CACHE KEY

La cache deberá depender de:

```text
source_hash
generator_version
parameters
profile
platform
```

---

# 90. CACHE INVALIDATION

Cambiar cualquiera de los componentes anteriores deberá invalidar únicamente los artefactos afectados.

---

# 91. DETERMINISM

Los procesos procedurales deberán ser deterministas cuando reciban el mismo:

```text
source
seed
parameters
version
profile
```

---

# 92. TEXTURE HASHING

Cada textura deberá disponer de:

```text
source_hash
content_hash
metadata_hash
```

---

# 93. MATERIAL HASHING

Cada material deberá disponer de:

```text
graph_hash
dependency_hash
final_hash
```

---

# 94. IMPORT VALIDATION

Toda textura importada deberá validarse antes de entrar al pipeline.

---

# 95. IMPORT ERRORS

Mínimo:

```text
unsupported_format
corrupt_file
invalid_dimensions
invalid_color_space
missing_alpha
invalid_channels
```

---

# 96. SUPPORTED IMAGE FORMATS

El pipeline deberá definir explícitamente los formatos aceptados.

Como mínimo deberá contemplar:

```text
PNG
TGA
JPG/JPEG
EXR
TIFF
DDS
```

cuando las dependencias del proyecto los soporten.

---

# 97. SOURCE COLOR MANAGEMENT

Deberá existir conversión controlada entre color spaces.

---

# 98. HDR

Deberá existir soporte para texturas HDR cuando sean necesarias.

---

# 99. MATERIAL SEMANTICS

Cada material deberá declarar propiedades semánticas:

```text
surface_type
physical_material
flammability
conductivity
hardness
friction
roughness_class
```

cuando el juego requiera dichas propiedades.

---

# 100. PHYSICAL MATERIAL

Deberá existir:

```text
PhysicalMaterialDefinition
```

separado del material visual.

---

# 101. PHYSICAL MATERIAL PARAMETERS

Mínimo:

```text
friction
restitution
density
penetration_resistance
footstep_type
impact_type
```

---

# 102. AUDIO SURFACE

Deberá existir metadata para:

```text
footstep
bullet_impact
melee_impact
vehicle_contact
environmental_contact
```

---

# 103. GAMEPLAY SURFACE

Deberá existir soporte para:

```text
climbable
slippery
destructible
burnable
wettable
freezable
```

cuando aplique.

---

# 104. SURFACE INTERACTION

Las propiedades físicas y gameplay no deberán depender exclusivamente del material visual.

---

# 105. MATERIAL ASSIGNMENT

Deberá existir:

```text
MaterialAssignment
```

que relacione:

```text
asset
mesh_section
surface
material
physical_material
```

---

# 106. MULTI-MATERIAL ASSETS

Deberá soportarse un asset con múltiples slots.

---

# 107. MATERIAL SLOT VALIDATION

Deberá detectar:

```text
missing_material
unused_slot
duplicate_assignment
invalid_slot
```

---

# 108. MESH-SURFACE COMPATIBILITY

Deberá validar:

```text
UV availability
UV scale
vertex color availability
normal orientation
tangent availability
material slot compatibility
```

---

# 109. TANGENT VALIDATION

Deberá comprobar consistencia entre:

```text
normal_map
tangent_space
mesh_tangents
```

---

# 110. BACKFACE VALIDATION

Cuando el material requiera two-sided rendering deberá declararse explícitamente.

---

# 111. TRANSPARENCY

Deberá distinguir:

```text
OPAQUE
MASKED
TRANSLUCENT
ADDITIVE
MODULATE
```

según target.

---

# 112. TRANSPARENCY VALIDATION

No deberá permitirse activar transparencia costosa sin que el quality/performance profile lo autorice.

---

# 113. EMISSIVE SYSTEM

Deberá soportar:

```text
emissive_color
emissive_intensity
emissive_mask
emissive_animation
```

---

# 114. MATERIAL ANIMATION

Deberá soportarse cuando sea necesario:

```text
UV_SCROLL
PANNER
ROTATION
WAVE
PULSE
DISSOLVE
CUSTOM
```

---

# 115. ANIMATION VALIDATION

Los materiales animados deberán declarar su coste esperado.

---

# 116. DAMAGE MATERIALS

Deberá existir soporte para estados:

```text
HEALTHY
DAMAGED
CRITICAL
DESTROYED
```

cuando el asset sea destructible.

---

# 117. WETNESS SYSTEM

Deberá existir un modelo común para:

```text
wetness
rain_response
puddle_response
roughness_shift
darkening
```

---

# 118. SNOW SYSTEM

Deberá soportar:

```text
snow_amount
snow_mask
snow_roughness
snow_color
snow_normal
```

---

# 119. DIRT SYSTEM

Deberá soportar acumulación de:

```text
dust
mud
dirt
ash
```

---

# 120. WEATHER MATERIAL INTERACTION

Los materiales deberán poder declarar cómo reaccionan ante:

```text
RAIN
SNOW
DUST
HEAT
COLD
```

---

# 121. MATERIAL PREVIEW

Deberá existir un sistema de preview con:

```text
sphere
cube
plane
custom_mesh
```

---

# 122. PREVIEW LIGHTING

Mínimo:

```text
STUDIO
OUTDOOR
DARK
NEUTRAL
CUSTOM
```

---

# 123. PREVIEW REGRESSION

Deberán producirse renders de referencia para materiales críticos.

---

# 124. VISUAL QUALITY TESTS

Deberán comprobar:

```text
base_color
roughness
normal
metallic
emissive
transparency
layer_blending
tiling
```

---

# 125. TEXTURE TESTS

Mínimo:

```text
test_texture_import
test_texture_dimensions
test_texture_color_space
test_texture_compression
test_texture_mips
test_texture_packing
test_texture_hash
test_texture_determinism
```

---

# 126. NORMAL TESTS

Mínimo:

```text
test_opengl_normal
test_directx_normal
test_normal_conversion
test_tangent_compatibility
```

---

# 127. UV TESTS

Mínimo:

```text
test_uv_channels
test_uv_transform
test_world_aligned
test_triplanar
test_tileable_surface
test_seam_detection
```

---

# 128. MATERIAL GRAPH TESTS

Mínimo:

```text
test_material_graph
test_graph_connection
test_graph_type_validation
test_graph_cycle_detection
test_unused_node_detection
test_missing_output
```

---

# 129. MATERIAL INSTANCE TESTS

Mínimo:

```text
test_instance_creation
test_instance_override
test_instance_inheritance
test_instance_deduplication
```

---

# 130. LAYER TESTS

Mínimo:

```text
test_layer_stack
test_layer_priority
test_layer_blending
test_layer_mask
test_procedural_mask
```

---

# 131. VARIANT TESTS

Mínimo:

```text
test_material_variant
test_variant_inheritance
test_variant_consistency
test_variant_hash
```

---

# 132. DECAL TESTS

Mínimo:

```text
test_decal_creation
test_decal_projection
test_decal_budget
test_decal_validation
```

---

# 133. UDIM TESTS

Mínimo:

```text
test_udim_set
test_udim_sequence
test_missing_udim
test_duplicate_udim
```

---

# 134. ATLAS TESTS

Mínimo:

```text
test_atlas_creation
test_atlas_packing
test_atlas_padding
test_atlas_bleeding
```

---

# 135. PERFORMANCE TESTS

Mínimo:

```text
test_texture_memory_budget
test_material_memory_budget
test_shader_complexity
test_texture_sample_budget
test_material_variant_budget
test_transparency_budget
```

---

# 136. OPTIMIZATION TESTS

Mínimo:

```text
test_texture_downscale
test_channel_packing
test_material_deduplication
test_unused_texture_removal
test_instance_reuse
```

---

# 137. CACHE TESTS

Mínimo:

```text
test_cache_hit
test_cache_miss
test_cache_invalidation
test_cache_determinism
```

---

# 138. SEMANTIC TESTS

Mínimo:

```text
test_physical_material
test_surface_semantics
test_audio_surface
test_gameplay_surface
test_material_assignment
```

---

# 139. WEATHER TESTS

Mínimo:

```text
test_wetness
test_snow
test_dirt
test_weather_material_response
```

---

# 140. PREVIEW TESTS

Mínimo:

```text
test_material_preview
test_preview_lighting
test_preview_regression
```

---

# 141. FAILURE TESTS

Mínimo:

```text
test_corrupt_texture
test_invalid_color_space
test_invalid_dimensions
test_invalid_compression
test_invalid_channel_layout
test_invalid_material_graph
test_material_cycle
test_missing_texture
test_missing_output
test_invalid_uv
test_invalid_udim
test_invalid_atlas
test_budget_overflow
test_unsupported_feature
```

---

# 142. DETERMINISM TESTS

Deberán comprobar determinismo de:

```text
procedural_texture
procedural_mask
material_generation
texture_packing
atlas_generation
variant_generation
material_hash
cache
```

---

# 143. GOLDEN MATERIALS

Deberán existir como mínimo:

```text
GOLDEN_METAL
GOLDEN_WOOD
GOLDEN_STONE
GOLDEN_CONCRETE
GOLDEN_FABRIC
GOLDEN_GLASS
GOLDEN_LEATHER
GOLDEN_TERRAIN
GOLDEN_VEGETATION
GOLDEN_WATER
```

---

# 144. GOLDEN VALIDATION

Cada golden material deberá validar:

```text
TEXTURE
PBR
GRAPH
INSTANCE
PERFORMANCE
PREVIEW
EXPORT
```

---

# 145. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
8 TEXTURE
4 NORMAL
6 UV
6 MATERIAL_GRAPH
4 MATERIAL_INSTANCE
5 LAYER
4 VARIANT
4 DECAL
4 UDIM
4 ATLAS
6 PERFORMANCE
5 OPTIMIZATION
4 CACHE
5 SEMANTIC
4 WEATHER
3 PREVIEW
13 FAILURE
8 DETERMINISM
10 GOLDEN
1 END_TO_END
```

Total mínimo:

```text
108 TESTS
```

---

# 146. END-TO-END TEST

Deberá ejecutarse:

```text
SURFACE DEFINITION
        ↓
TEXTURE GENERATION / IMPORT
        ↓
CHANNEL PROCESSING
        ↓
MASK GENERATION
        ↓
MATERIAL GRAPH
        ↓
MATERIAL INSTANCE
        ↓
OPTIMIZATION
        ↓
VALIDATION
        ↓
UNREAL EXPORT
        ↓
READBACK
        ↓
FINAL VALIDATION
```

---

# 147. UNREAL EXPORT CONTRACT

Deberá existir:

```text
MaterialExportContract
```

incluyendo:

```text
material_definition
material_instance
texture_assets
texture_settings
sampler_settings
physical_material
parameter_metadata
virtual_texture_metadata
udim_metadata
decal_metadata
```

---

# 148. UNREAL MATERIAL COMPATIBILITY

El sistema deberá validar compatibilidad con:

```text
MATERIAL DOMAIN
BLEND MODE
SHADING MODEL
TWO SIDED
OPAQUE/MASKED/TRANSLUCENT
```

---

# 149. READBACK

Después del export deberá poder verificarse:

```text
material_exists
textures_exist
parameters_match
slots_match
physical_material_exists
```

---

# 150. PACKAGE STRUCTURE

El paquete final deberá contener:

```text
surface/
material/
textures/
masks/
layers/
variants/
decals/
uv/
physical/
audio/
gameplay/
optimization/
preview/
validation/
unreal/
```

---

# 151. NO ORPHAN TEXTURES

Ninguna textura derivada deberá quedar sin consumidor salvo que esté marcada explícitamente como recurso reusable.

---

# 152. NO MISSING DEPENDENCIES

Todo material deberá resolver:

```text
textures
parameters
graphs
physical_material
shader_dependencies
```

---

# 153. NO SILENT FALLBACKS

Cuando una textura, nodo o feature no pueda utilizarse, el sistema deberá producir:

```text
ERROR
```

salvo que exista un fallback declarado.

---

# 154. FALLBACK POLICY

Los fallbacks deberán ser explícitos:

```text
fallback_id
reason
source
replacement
quality_impact
```

---

# 155. VERSIONING

Deberá registrar:

```text
schema_version
material_version
texture_version
generator_version
shader_version
platform_profile
quality_profile
```

---

# 156. CHANGE IMPACT ANALYSIS

Un cambio en:

```text
base_color_texture
```

no deberá reconstruir automáticamente recursos no dependientes.

Un cambio en:

```text
material_graph
```

deberá invalidar las instancias dependientes cuando corresponda.

---

# 157. CROSS-PHASE INTEGRATION

UAF-81.52 deberá integrarse con:

```text
UAF-81.46 — MATERIAL & TEXTURE SYSTEM
UAF-81.50 — ENVIRONMENT, ARCHITECTURE & MODULAR WORLD ASSEMBLY
UAF-81.51 — WORLD TERRAIN, BIOME, VEGETATION & NATURAL ECOSYSTEM SYSTEM
```

Si una capacidad ya existe, esta fase deberá extender su contrato en lugar de crear una segunda implementación incompatible.

---

# 158. CROSS-ASSET REQUIREMENT

El sistema deberá poder recibir material assignments desde:

```text
CHARACTER_FACTORY
CREATURE_FACTORY
WEAPON_FACTORY
PROP_FACTORY
VEHICLE_FACTORY
ARCHITECTURE_FACTORY
ENVIRONMENT_FACTORY
TERRAIN_FACTORY
VEGETATION_FACTORY
VFX_FACTORY
```

---

# 159. FINAL ACCEPTANCE CRITERIA

UAF-81.52 estará completa únicamente cuando:

```text
SURFACE MODEL IMPLEMENTED
PBR MODEL IMPLEMENTED
TEXTURE PIPELINE IMPLEMENTED
COLOR MANAGEMENT IMPLEMENTED
NORMAL PIPELINE IMPLEMENTED
HEIGHT PIPELINE IMPLEMENTED
COMPRESSION IMPLEMENTED
TEXTURE PACKING IMPLEMENTED
MIP SYSTEM IMPLEMENTED
UV SYSTEM IMPLEMENTED
WORLD ALIGNED MATERIALS IMPLEMENTED
TRIPLANAR IMPLEMENTED
TILEABLE SURFACES IMPLEMENTED
MATERIAL GRAPH IMPLEMENTED
GRAPH VALIDATION IMPLEMENTED
MATERIAL PARAMETERS IMPLEMENTED
MATERIAL INSTANCES IMPLEMENTED
MATERIAL DEDUPLICATION IMPLEMENTED
SURFACE LAYERS IMPLEMENTED
PROCEDURAL MASKS IMPLEMENTED
DETAIL SYSTEM IMPLEMENTED
MACRO VARIATION IMPLEMENTED
MICRO VARIATION IMPLEMENTED
MATERIAL VARIANTS IMPLEMENTED
DECAL SYSTEM IMPLEMENTED
VIRTUAL TEXTURE SUPPORT IMPLEMENTED
UDIM SUPPORT IMPLEMENTED
ATLAS SYSTEM IMPLEMENTED
QUALITY PROFILES IMPLEMENTED
PLATFORM PROFILES IMPLEMENTED
MEMORY ESTIMATION IMPLEMENTED
SHADER COST ESTIMATION IMPLEMENTED
OPTIMIZATION IMPLEMENTED
DERIVATION GRAPH IMPLEMENTED
CACHE IMPLEMENTED
CACHE INVALIDATION IMPLEMENTED
PHYSICAL MATERIAL SYSTEM IMPLEMENTED
AUDIO SURFACE IMPLEMENTED
GAMEPLAY SURFACE IMPLEMENTED
WEATHER INTERACTION IMPLEMENTED
MATERIAL PREVIEW IMPLEMENTED
VISUAL REGRESSION IMPLEMENTED
GOLDEN MATERIALS IMPLEMENTED
MINIMUM 108 TESTS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
UNREAL EXPORT IMPLEMENTED
UNREAL READBACK VALIDATION IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 160. NEXT PHASE

```text
UAF-81.53 — UNIVERSAL GEOMETRY, MESH PROCESSING & PROCEDURAL MODELING SYSTEM
```

La siguiente fase deberá establecer el sistema transversal de:

```text
MESH GENERATION
MESH IMPORT
TOPOLOGY
RETARGETING
DECIMATION
REMESHING
BOOLEAN OPERATIONS
LOOPS
CUTS
EXTRUSION
BEVEL
NORMALS
TANGENTS
UV UNWRAP
UV PACKING
VERTEX COLORS
WELDING
SEAM MANAGEMENT
LOD GEOMETRY
COLLISION GEOMETRY
NANITE READINESS
HLOD GEOMETRY
GEOMETRY VALIDATION
```

Este sistema deberá convertirse en la base geométrica común para personajes, criaturas, armas, props, vehículos, arquitectura, naturaleza y cualquier asset tridimensional.
