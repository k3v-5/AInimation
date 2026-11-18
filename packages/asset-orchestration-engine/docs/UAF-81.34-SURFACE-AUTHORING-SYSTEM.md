# UAF-81.34 — PROCEDURAL MATERIAL, TEXTURE, UV, DECAL & SURFACE AUTHORING SYSTEM

## UAF-81.34-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA PROCEDURAL DE AUTORÍA DE MATERIALES, TEXTURAS, UV, DECALS Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.34 — Procedural Material, Texture, UV, Decal & Surface Authoring System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.33  
**Next Phase:** UAF-81.35  

---

# 1. PURPOSE

UAF-81.34 define el sistema profesional de generación, composición, validación, optimización y exportación de superficies para assets destinados a Unreal Engine.

El sistema deberá permitir producir superficies complejas sin depender de texturas pintadas manualmente como único mecanismo de creación.

Deberá soportar:

```text
MATERIALS
TEXTURES
MASKS
UV
DECALS
SURFACE_DETAILS
WEAR
DAMAGE
DIRT
SCRATCHES
RUST
CORROSION
EMISSIVE
SUBSURFACE
TRANSLUCENCY
CLOTH
SKIN
METAL
STONE
CONCRETE
WOOD
GLASS
PLASTIC
CERAMIC
ORGANIC
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá convertir una especificación semántica de superficie en un conjunto reproducible de assets compatibles con el pipeline Unreal.

```text
SurfaceSpecification
        ↓
SurfaceClassification
        ↓
MaterialGraph
        ↓
TexturePlan
        ↓
UVPlan
        ↓
MaskGeneration
        ↓
DetailGeneration
        ↓
Validation
        ↓
Optimization
        ↓
UnrealPackage
```

---

# 3. SURFACE ARCHITECTURE

La superficie deberá estar separada conceptualmente en:

```text
BASE MATERIAL
+
MACRO VARIATION
+
MICRO DETAIL
+
WEAR
+
DAMAGE
+
DECALS
+
SPECIAL EFFECTS
```

---

# 4. SURFACE SPECIFICATION

Deberá existir:

```text
SurfaceSpecification
```

con mínimo:

```text
surface_id
surface_type
material_family
physical_properties
color_profile
roughness_profile
metallic_profile
normal_profile
height_profile
opacity_profile
emissive_profile
subsurface_profile
variation_profile
wear_profile
damage_profile
decal_profile
texture_profile
uv_profile
resolution_profile
performance_profile
seed
```

---

# 5. MATERIAL FAMILIES

Mínimo:

```text
SKIN
FLESH
BONE
METAL
PAINTED_METAL
RUBBER
PLASTIC
CERAMIC
GLASS
CONCRETE
STONE
BRICK
WOOD
FABRIC
LEATHER
PAPER
LIQUID
SLIME
ORGANIC
ENERGY
HOLOGRAM
EMISSIVE
CUSTOM
```

---

# 6. PHYSICAL MATERIAL MODEL

Cada material deberá declarar propiedades físicas aproximadas.

Mínimo:

```text
base_color
metallic
roughness
specular
normal_strength
ior
opacity
subsurface
transmission
clearcoat
```

---

# 7. MATERIAL PRESETS

Deberán existir presets reutilizables.

Ejemplos:

```text
MAT_BRUSHED_STEEL
MAT_DAMAGED_STEEL
MAT_BLACK_RUBBER
MAT_TACTICAL_FABRIC
MAT_HUMAN_SKIN
MAT_ALIEN_SKIN
MAT_CONCRETE
MAT_RUSTED_METAL
MAT_POLISHED_CHROME
MAT_OBSIDIAN
```

---

# 8. PRESET IMMUTABILITY

Los presets base no deberán modificarse directamente durante una generación.

Deberán clonarse o instanciarse.

---

# 9. MATERIAL INSTANCING

Deberá existir:

```text
MaterialInstanceDefinition
```

para permitir variaciones económicas.

---

# 10. PARAMETERIZED MATERIALS

Los parámetros deberán poder modificarse sin regenerar todas las texturas cuando técnicamente no sea necesario.

---

# 11. COLOR SYSTEM

Deberá soportarse:

```text
RGB
HSV
HSL
HEX
LINEAR_RGB
SRGB
```

con conversiones explícitas.

---

# 12. COLOR MANAGEMENT

Todas las conversiones de color deberán declarar espacio de color.

No se permitirán conversiones implícitas ambiguas.

---

# 13. ROUGHNESS SYSTEM

Deberá soportar:

```text
constant
gradient
noise
height_driven
mask_driven
procedural
texture
```

---

# 14. METALLIC SYSTEM

Deberá soportar valores y máscaras por región.

---

# 15. NORMAL SYSTEM

Deberá existir composición de normales:

```text
macro_normal
surface_normal
micro_normal
detail_normal
```

---

# 16. NORMAL BLENDING

La combinación de normales deberá utilizar una estrategia matemáticamente válida.

No deberá realizarse una suma RGB ingenua.

---

# 17. HEIGHT SYSTEM

Deberá soportar:

```text
height
displacement
parallax
surface_offset
```

según el perfil del asset.

---

# 18. PROCEDURAL NOISE

Deberán existir generadores deterministas de:

```text
PERLIN
VORONOI
FBM
CELLULAR
GRADIENT
RANDOM_VALUE
CUSTOM
```

---

# 19. NOISE PARAMETERS

Cada ruido deberá declarar:

```text
seed
scale
frequency
octaves
amplitude
lacunarity
gain
```

cuando corresponda.

---

# 20. DETERMINISM

El mismo:

```text
surface_specification
seed
generator_version
```

deberá producir el mismo resultado dentro de las tolerancias definidas.

---

# 21. MACRO VARIATION

Las superficies deberán poder incorporar variación a gran escala.

Ejemplos:

```text
color_variation
roughness_variation
density_variation
material_age
environmental_exposure
```

---

# 22. MICRO DETAIL

Deberá existir un sistema separado para detalles de alta frecuencia.

Ejemplos:

```text
pores
grain
fibers
scratches
micro_noise
surface_roughness
```

---

# 23. WEAR SYSTEM

Deberá existir:

```text
WearDefinition
WearGenerator
WearValidator
```

---

# 24. WEAR TYPES

Mínimo:

```text
EDGE_WEAR
SURFACE_WEAR
FREQUENCY_WEAR
CONTACT_WEAR
MECHANICAL_WEAR
ENVIRONMENTAL_WEAR
```

---

# 25. EDGE WEAR

El desgaste podrá depender de:

```text
curvature
ambient_occlusion
normal_change
geometry_edges
```

---

# 26. DIRT SYSTEM

Deberá existir generación procedural de suciedad.

Parámetros:

```text
density
direction
accumulation
color
roughness
scale
seed
```

---

# 27. DIRT ACCUMULATION

Deberá poder acumularse según:

```text
gravity
surface_orientation
cavity
contact
environment
```

---

# 28. DAMAGE SYSTEM

Deberá existir:

```text
DamageDefinition
DamageGenerator
DamageValidator
```

---

# 29. DAMAGE TYPES

Mínimo:

```text
SCRATCH
DENT
CRACK
CHIP
BULLET_IMPACT
BURN
CUT
FRACTURE
CORROSION
BIOLOGICAL_DAMAGE
```

---

# 30. DAMAGE MASKS

Los daños deberán poder representarse mediante máscaras reutilizables.

---

# 31. DAMAGE DEPTH

El sistema deberá distinguir:

```text
COLOR_ONLY
NORMAL_ONLY
HEIGHT
GEOMETRY
HYBRID
```

---

# 32. SCRATCH GENERATOR

Deberá soportar:

```text
direction
length
width
depth
density
distribution
seed
```

---

# 33. RUST SYSTEM

Deberá soportar:

```text
oxidation
color_change
roughness_change
surface_damage
edge_accumulation
moisture_bias
```

---

# 34. CORROSION

La corrosión deberá poder afectar simultáneamente:

```text
albedo
roughness
normal
height
metallic
```

---

# 35. MATERIAL LAYER SYSTEM

Deberá existir un compositor de capas:

```text
Layer_0_BASE
Layer_1_VARIATION
Layer_2_DIRT
Layer_3_WEAR
Layer_4_DAMAGE
Layer_5_DECAL
Layer_6_SPECIAL
```

---

# 36. LAYER ORDER

El orden de evaluación deberá ser explícito y determinista.

---

# 37. MASK SYSTEM

Deberá existir:

```text
MaskDefinition
MaskGenerator
MaskComposer
MaskValidator
```

---

# 38. MASK SOURCES

Mínimo:

```text
VERTEX_COLOR
ATTRIBUTE
AO
CURVATURE
POSITION
NORMAL
HEIGHT
UV
NOISE
DISTANCE
PAINTED_MASK
DECAL
CUSTOM
```

---

# 39. MASK OPERATIONS

Mínimo:

```text
ADD
SUBTRACT
MULTIPLY
MIN
MAX
INVERT
REMAP
POWER
SMOOTHSTEP
CLAMP
```

---

# 40. MASK RANGE

Todas las máscaras deberán operar dentro del rango:

```text
0.0 → 1.0
```

salvo que el tipo de máscara declare explícitamente otro rango.

---

# 41. DECAL SYSTEM

Deberá existir:

```text
DecalDefinition
DecalGenerator
DecalValidator
```

---

# 42. DECAL TYPES

Mínimo:

```text
LOGO
WARNING
NUMBER
GRAFFITI
DAMAGE
DIRT
BLOOD
SYMBOL
TEXT
TECHNICAL_MARKING
```

---

# 43. DECAL PROJECTION

Deberá soportar:

```text
PLANAR
BOX
CYLINDRICAL
UV
CUSTOM
```

---

# 44. DECAL ORIENTATION

Deberá poder alinearse con:

```text
surface_normal
world_axis
object_axis
custom_direction
```

---

# 45. DECAL CLIPPING

Deberá existir validación contra:

```text
floating_decal
deep_projection
unintended_projection
self_projection
```

---

# 46. TEXT SYSTEM

Los decals de texto deberán poder utilizar fuentes registradas.

---

# 47. TEXT LOCALIZATION

El sistema deberá permitir generar variantes lingüísticas del mismo decal.

---

# 48. UV SYSTEM

Deberá existir un sistema completo de UV.

```text
UVDefinition
UVGenerator
UVAnalyzer
UVValidator
```

---

# 49. UV CHANNELS

Deberán soportarse múltiples canales:

```text
UV0
UV1
UV2
CUSTOM
```

---

# 50. UV PURPOSE

Cada canal deberá declarar su finalidad:

```text
TEXTURE
LIGHTMAP
MASK
DECAL
CUSTOM
```

---

# 51. UV GENERATION STRATEGIES

Mínimo:

```text
SMART_PROJECT
SEAM_BASED
PLANAR
BOX
CYLINDRICAL
SPHERICAL
UDIM
CUSTOM
```

---

# 52. UV SEAMS

Las costuras deberán poder definirse mediante reglas semánticas.

---

# 53. UV STRETCH

Deberá medirse:

```text
min_stretch
max_stretch
average_stretch
```

---

# 54. UV OVERLAP

Deberá diferenciarse entre:

```text
INTENTIONAL_OVERLAP
UNINTENTIONAL_OVERLAP
```

---

# 55. TEXEL DENSITY

Deberá existir análisis de densidad.

Deberá detectar:

```text
UNDER_DENSITY
OVER_DENSITY
INCONSISTENT_DENSITY
```

---

# 56. UDIM

Deberá existir soporte opcional para UDIM.

---

# 57. UDIM VALIDATION

Deberá validar:

```text
tile_assignment
missing_tiles
unexpected_tiles
island_distribution
```

---

# 58. TEXTURE TYPES

Mínimo:

```text
ALBEDO
NORMAL
ROUGHNESS
METALLIC
AO
HEIGHT
EMISSIVE
OPACITY
MASK
SUBSURFACE
SPECULAR
```

---

# 59. TEXTURE CHANNEL PACKING

Deberá existir:

```text
ORM
RMA
CUSTOM_PACK
```

---

# 60. CHANNEL PACKING VALIDATION

El sistema deberá impedir que dos canales sean intercambiados accidentalmente.

---

# 61. TEXTURE RESOLUTION POLICY

Deberá definirse resolución por:

```text
asset_class
LOD
surface_importance
camera_distance
performance_budget
```

---

# 62. TEXTURE RESOLUTIONS

Mínimo:

```text
256
512
1024
2048
4096
8192
```

cuando el pipeline objetivo lo permita.

---

# 63. MIPMAP POLICY

Las texturas deberán declarar política de mipmaps.

---

# 64. TEXTURE COMPRESSION

Deberá existir configuración para formatos apropiados al destino Unreal.

---

# 65. ALPHA POLICY

Deberá diferenciar:

```text
OPAQUE
MASKED
TRANSLUCENT
ADDITIVE
CUSTOM
```

---

# 66. EMISSIVE SYSTEM

Deberá soportar:

```text
emissive_color
emissive_strength
pulse
flicker
gradient
mask
```

---

# 67. EMISSIVE LIMIT

Deberá respetarse la política global de exposición y evitar valores que produzcan resultados visualmente inválidos.

---

# 68. SUBSURFACE SYSTEM

Deberá soportar perfiles para:

```text
SKIN
FLESH
WAX
ORGANIC
CUSTOM
```

---

# 69. TRANSLUCENCY

Deberá existir soporte explícito cuando el material lo requiera.

---

# 70. GLASS SYSTEM

Deberá soportar:

```text
IOR
transmission
roughness
tint
thickness
opacity
```

---

# 71. FABRIC SYSTEM

Deberá soportar:

```text
fiber_direction
weave_scale
roughness
normal
color_variation
```

---

# 72. METAL SYSTEM

Deberá soportar:

```text
metallic
roughness
oxidation
polish
brushing
scratches
```

---

# 73. WOOD SYSTEM

Deberá soportar:

```text
grain_direction
grain_scale
knots
variation
roughness
age
damage
```

---

# 74. STONE SYSTEM

Deberá soportar:

```text
macro_pattern
micro_pattern
cracks
roughness
color_variation
erosion
```

---

# 75. CONCRETE SYSTEM

Deberá soportar:

```text
aggregate
pores
cracks
stains
water_damage
roughness_variation
```

---

# 76. SKIN SYSTEM

Deberá soportar:

```text
base_tone
color_variation
pores
oiliness
roughness
subsurface
micro_normal
blemishes
```

---

# 77. SKIN VARIATION

La variación deberá ser controlable y determinista.

---

# 78. ORGANIC MATERIALS

Deberá soportar:

```text
flesh
mucus
slime
fungus
plant
shell
carapace
```

---

# 79. MATERIAL GRAPH

Deberá existir una representación intermedia:

```text
MaterialGraph
```

que sea independiente del renderer cuando sea posible.

---

# 80. GRAPH NODES

Los nodos deberán representar:

```text
INPUT
COLOR
VALUE
NOISE
MASK
BLEND
NORMAL
HEIGHT
UTILITY
OUTPUT
```

---

# 81. GRAPH VALIDATION

Deberá detectar:

```text
UNCONNECTED_INPUT
INVALID_NODE
CYCLE
TYPE_MISMATCH
UNUSED_NODE
INVALID_PARAMETER
```

---

# 82. GRAPH OPTIMIZATION

Deberán eliminarse nodos redundantes cuando sea seguro.

---

# 83. GRAPH DETERMINISM

La compilación del mismo graph deberá producir la misma representación final.

---

# 84. MATERIAL COMPLEXITY

Deberá existir una métrica:

```text
material_complexity_score
```

---

# 85. PERFORMANCE BUDGET

Cada material deberá declarar:

```text
instruction_budget
texture_sample_budget
sampler_budget
memory_budget
```

---

# 86. PERFORMANCE VALIDATION

El material deberá rechazarse si excede el presupuesto definido.

---

# 87. INSTANCE OPTIMIZATION

Cuando dos materiales sólo difieran en parámetros, deberán preferirse instancias sobre materiales completamente independientes.

---

# 88. TEXTURE ATLAS

Deberá existir soporte opcional para atlas.

---

# 89. ATLAS VALIDATION

Deberá comprobar:

```text
island_bounds
padding
bleeding
resolution
mapping
```

---

# 90. PADDING

Deberá existir padding configurable entre regiones UV.

---

# 91. TEXTURE BLEEDING

Deberán existir pruebas específicas para detectar bleeding entre islas.

---

# 92. SURFACE DECIMATION

Cuando sea posible, detalles geométricos deberán poder convertirse en:

```text
NORMAL
HEIGHT
MASK
DECAL
```

para reducir coste geométrico.

---

# 93. DETAIL BAKING

Deberá existir:

```text
HighPoly
    ↓
Bake
    ↓
Normal
AO
Curvature
Height
Mask
```

---

# 94. BAKING VALIDATION

Deberá comprobarse:

```text
ray_distance
cage
projection
missing_detail
artifact
seam
```

---

# 95. CAGE SYSTEM

El baking deberá poder generar y validar cages.

---

# 96. BAKING DETERMINISM

Los parámetros de baking deberán formar parte del hash de generación.

---

# 97. SURFACE VARIANTS

Deberán existir variantes:

```text
CLEAN
USED
DAMAGED
HEAVILY_DAMAGED
RUSTED
BLOODIED
BURNED
CORRODED
WET
DRY
```

---

# 98. ENVIRONMENTAL VARIANTS

Deberán existir modificadores:

```text
DESERT
ARCTIC
URBAN
INDUSTRIAL
UNDERGROUND
SPACE
ALIEN
MILITARY
```

---

# 99. SURFACE STYLE

Deberá existir:

```text
REALISTIC
STYLIZED
SCI_FI
HORROR
MILITARY
FANTASY
CARTOON
CUSTOM
```

---

# 100. STYLE CONSISTENCY

Los materiales pertenecientes a una misma familia deberán poder validarse contra un estilo común.

---

# 101. MATERIAL PALETTE

Deberá existir:

```text
MaterialPalette
```

que agrupe:

```text
primary
secondary
accent
neutral
emissive
damage
```

---

# 102. PALETTE VALIDATION

Deberá detectarse:

```text
excessive_contrast
invalid_color_space
style_outlier
emissive_outlier
```

---

# 103. SURFACE SEMANTICS

Cada superficie deberá declarar:

```text
material_family
physical_category
visual_category
gameplay_category
```

---

# 104. MATERIAL METADATA

Deberá registrar:

```text
generator_version
seed
source
preset
parameters
dependencies
hash
```

---

# 105. TEXTURE METADATA

Cada textura deberá registrar:

```text
texture_type
resolution
color_space
compression
mip_policy
source
generator
seed
hash
```

---

# 106. UV METADATA

Deberá registrar:

```text
channel
strategy
density
overlap
stretch
udim_tiles
```

---

# 107. SURFACE MANIFEST

Deberá generarse:

```text
surface_manifest.json
```

---

# 108. MANIFEST DEPENDENCIES

Deberá registrar:

```text
material
textures
masks
decals
uv
bakes
presets
source_assets
```

---

# 109. INCREMENTAL REBUILD

Modificar:

```text
roughness
color
dirt
wear
decal
emissive
```

no deberá regenerar automáticamente geometría ni skeleton.

---

# 110. CACHE

Cada etapa deberá tener cache independiente.

---

# 111. CACHE KEY

Mínimo:

```text
surface_spec_hash
seed
generator_version
schema_version
dependency_hash
```

---

# 112. CHECKPOINTS

Mínimo:

```text
SURFACE_SPECIFIED
MATERIAL_BUILT
MASKS_BUILT
UV_BUILT
TEXTURES_BUILT
BAKES_BUILT
DECALS_BUILT
VALIDATED
OPTIMIZED
UNREAL_READY
```

---

# 113. VALIDATION ENGINE

Deberán existir:

```text
SurfaceSchemaValidator
MaterialValidator
TextureValidator
UVValidator
MaskValidator
DecalValidator
BakeValidator
PerformanceValidator
```

---

# 114. HARD FAILS

Deberá rechazarse una superficie si existe:

```text
INVALID_COLOR_SPACE
BROKEN_UV
INVALID_TEXTURE
MISSING_TEXTURE
INVALID_MATERIAL_GRAPH
GRAPH_CYCLE
INVALID_NORMAL
INVALID_CHANNEL_PACK
INVALID_COMPRESSION
EXCESSIVE_COMPLEXITY
MISSING_REQUIRED_PARAMETER
```

---

# 115. ARTISTIC VALIDATION

Deberá evaluarse:

```text
surface_readability
material_identity
color_coherence
roughness_coherence
detail_scale
style_consistency
```

---

# 116. MATERIAL READABILITY

Un material deberá ser identificable visualmente bajo las condiciones de iluminación definidas.

---

# 117. MULTI-LIGHT VALIDATION

Deberá poder validarse bajo:

```text
NEUTRAL
DAYLIGHT
NIGHT
HARSH
INDOOR
COLORED
```

---

# 118. CAMERA VALIDATION

Deberán existir pruebas:

```text
CLOSE
MEDIUM
GAMEPLAY
DISTANT
```

---

# 119. TEXTURE PREVIEW

Deberá poder producirse una vista previa independiente del asset completo.

---

# 120. MATERIAL PREVIEW

Deberán generarse previews bajo iluminación estándar.

---

# 121. REGRESSION GOLDENS

Mínimo:

```text
GOLDEN_SKIN
GOLDEN_METAL
GOLDEN_FABRIC
GOLDEN_CONCRETE
GOLDEN_WOOD
GOLDEN_GLASS
GOLDEN_ORGANIC
GOLDEN_EMISSIVE
```

---

# 122. UNIT TESTS

Mínimo:

```text
test_surface_specification
test_material_family
test_material_preset
test_material_instance
test_color_conversion
test_roughness
test_metallic
test_normal
test_height
test_noise
test_determinism
test_macro_variation
test_micro_detail
test_wear
test_edge_wear
test_dirt
test_dirt_accumulation
test_damage
test_damage_masks
test_scratch
test_rust
test_corrosion
test_material_layers
test_mask_definition
test_mask_operations
test_decal_definition
test_decal_projection
test_decal_orientation
test_decal_validation
test_text_decal
test_uv_definition
test_uv_generation
test_uv_channels
test_uv_seams
test_uv_stretch
test_uv_overlap
test_texel_density
test_udim
test_texture_types
test_channel_packing
test_texture_resolution
test_mipmaps
test_texture_compression
test_alpha_policy
test_emissive
test_subsurface
test_translucency
test_glass
test_fabric
test_metal
test_wood
test_stone
test_concrete
test_skin
test_organic
test_material_graph
test_graph_validation
test_graph_optimization
test_material_complexity
test_performance_budget
test_instance_optimization
test_texture_atlas
test_texture_padding
test_texture_bleeding
test_detail_baking
test_baking_validation
test_baking_determinism
test_surface_variants
test_environment_variants
test_surface_style
test_material_palette
test_surface_semantics
test_material_metadata
test_texture_metadata
test_uv_metadata
test_surface_manifest
test_incremental_rebuild
test_surface_cache
test_surface_checkpoints
test_surface_validation
```

---

# 123. INTEGRATION TESTS

Mínimo:

```text
test_character_surface_pipeline
test_weapon_surface_pipeline
test_prop_surface_pipeline
test_building_surface_pipeline
test_environment_surface_pipeline
test_vehicle_surface_pipeline
test_organic_surface_pipeline
test_material_to_texture_pipeline
test_uv_to_texture_pipeline
test_bake_pipeline
test_decal_pipeline
test_surface_to_unreal_pipeline
```

---

# 124. FAILURE TESTS

Mínimo:

```text
test_invalid_material
test_invalid_graph
test_graph_cycle
test_invalid_uv
test_uv_overlap
test_invalid_texture
test_wrong_color_space
test_wrong_channel_pack
test_invalid_normal
test_missing_texture
test_invalid_decal
test_bake_failure
test_excessive_complexity
test_memory_budget_failure
test_instruction_budget_failure
test_invalid_manifest
```

---

# 125. DETERMINISM TESTS

Deberán verificarse:

```text
material
noise
masks
wear
damage
decals
uv
textures
bakes
full_surface
```

---

# 126. PERFORMANCE TESTS

Deberán medir:

```text
material_compile_cost
texture_memory
texture_count
sampler_count
instruction_count
atlas_efficiency
generation_time
cache_hit_rate
```

---

# 127. GOLDEN TESTS

Cada golden deberá comparar:

```text
material_graph_hash
texture_hash
uv_metrics
mask_metrics
performance_metrics
manifest_hash
```

---

# 128. NO FAKE VALIDATION

No se aceptarán pruebas que únicamente comprueben:

```text
material_exists
texture_exists
file_exists
node_exists
```

Las pruebas deberán comprobar propiedades reales.

---

# 129. UNREAL EXPORT

El sistema deberá producir recursos preparados para:

```text
MATERIAL
MATERIAL_INSTANCE
TEXTURE
DECAL
PHYSICAL_MATERIAL
SURFACE_METADATA
```

---

# 130. UNREAL COMPATIBILITY

Deberá validarse:

```text
texture_format
color_space
material_domain
blend_mode
shading_model
nanite_compatibility
virtual_texture_policy
```

cuando corresponda.

---

# 131. VIRTUAL TEXTURES

Deberá existir soporte opcional para Virtual Textures.

---

# 132. MATERIAL LOD

Deberán existir estrategias para reducir complejidad según distancia.

---

# 133. TEXTURE LOD

Deberá poder definirse una política de resolución por LOD.

---

# 134. SURFACE QUALITY LEVELS

Mínimo:

```text
CINEMATIC
HIGH
GAMEPLAY
MOBILE
BACKGROUND
```

---

# 135. QUALITY SCALING

La reducción de calidad deberá preservar la identidad visual.

---

# 136. GLOBAL SURFACE LIBRARY

Los materiales y generadores deberán poder registrarse en:

```text
AssetLibrary
```

---

# 137. REUSE

Un mismo material deberá poder reutilizarse entre:

```text
CHARACTER
WEAPON
PROP
ENVIRONMENT
BUILDING
VEHICLE
```

cuando sea semánticamente compatible.

---

# 138. CROSS-ASSET CONSISTENCY

Deberá existir validación para garantizar que assets de un mismo proyecto compartan:

```text
texel_density
color_management
material_conventions
roughness_conventions
texture_formats
naming
```

---

# 139. PROJECT MATERIAL PROFILE

Deberá existir:

```text
ProjectSurfaceProfile
```

que establezca políticas globales.

---

# 140. PROFILE OVERRIDES

Un asset podrá sobrescribir parámetros globales únicamente de forma explícita.

---

# 141. AUDIT TRAIL

Cada superficie generada deberá poder reconstruirse a partir de:

```text
specification
seed
generator_version
preset
parameters
dependencies
```

---

# 142. REPRODUCTION

Dado un manifest válido, deberá ser posible reproducir la superficie sin depender de estado externo no registrado.

---

# 143. SECURITY

Los recursos externos utilizados durante generación deberán quedar registrados.

---

# 144. EXTERNAL RESOURCE VALIDATION

Deberá verificarse:

```text
source_exists
source_hash
source_version
license_metadata
```

cuando corresponda.

---

# 145. QUALITY GATES

Mínimo:

```text
GATE_01_SCHEMA
GATE_02_COLOR
GATE_03_MATERIAL
GATE_04_MASK
GATE_05_UV
GATE_06_TEXTURE
GATE_07_BAKE
GATE_08_DECAL
GATE_09_PERFORMANCE
GATE_10_UNREAL
```

---

# 146. FINAL ACCEPTANCE

Una superficie sólo podrá marcarse:

```text
UNREAL_READY
```

cuando todos los gates obligatorios estén en:

```text
PASS
```

---

# 147. DEFINITION OF DONE

UAF-81.34 estará completa únicamente cuando:

```text
SURFACE_SCHEMA_IMPLEMENTED
MATERIAL_SYSTEM_IMPLEMENTED
MATERIAL_PRESETS_IMPLEMENTED
MATERIAL_INSTANCING_IMPLEMENTED
COLOR_MANAGEMENT_IMPLEMENTED
ROUGHNESS_SYSTEM_IMPLEMENTED
NORMAL_SYSTEM_IMPLEMENTED
HEIGHT_SYSTEM_IMPLEMENTED
NOISE_SYSTEM_IMPLEMENTED
MACRO_VARIATION_IMPLEMENTED
MICRO_DETAIL_IMPLEMENTED
WEAR_SYSTEM_IMPLEMENTED
DIRT_SYSTEM_IMPLEMENTED
DAMAGE_SYSTEM_IMPLEMENTED
RUST_SYSTEM_IMPLEMENTED
CORROSION_SYSTEM_IMPLEMENTED
MATERIAL_LAYER_SYSTEM_IMPLEMENTED
MASK_SYSTEM_IMPLEMENTED
DECAL_SYSTEM_IMPLEMENTED
UV_SYSTEM_IMPLEMENTED
UDIM_SUPPORT_IMPLEMENTED
TEXEL_DENSITY_IMPLEMENTED
TEXTURE_GENERATION_IMPLEMENTED
CHANNEL_PACKING_IMPLEMENTED
TEXTURE_COMPRESSION_IMPLEMENTED
EMISSIVE_SYSTEM_IMPLEMENTED
SUBSURFACE_SYSTEM_IMPLEMENTED
FABRIC_SYSTEM_IMPLEMENTED
METAL_SYSTEM_IMPLEMENTED
WOOD_SYSTEM_IMPLEMENTED
STONE_SYSTEM_IMPLEMENTED
CONCRETE_SYSTEM_IMPLEMENTED
SKIN_SYSTEM_IMPLEMENTED
ORGANIC_SYSTEM_IMPLEMENTED
MATERIAL_GRAPH_IMPLEMENTED
GRAPH_VALIDATION_IMPLEMENTED
GRAPH_OPTIMIZATION_IMPLEMENTED
BAKING_SYSTEM_IMPLEMENTED
SURFACE_VARIANTS_IMPLEMENTED
STYLE_SYSTEM_IMPLEMENTED
MATERIAL_PALETTE_IMPLEMENTED
SURFACE_MANIFEST_IMPLEMENTED
CACHE_IMPLEMENTED
CHECKPOINTS_IMPLEMENTED
INCREMENTAL_REBUILD_IMPLEMENTED
VALIDATION_IMPLEMENTED
PERFORMANCE_VALIDATION_IMPLEMENTED
UNREAL_EXPORT_IMPLEMENTED
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

# 148. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
120 UNIT TESTS
40 INTEGRATION TESTS
30 FAILURE TESTS
30 DETERMINISM TESTS
20 PERFORMANCE TESTS
20 GOLDEN TESTS
```

Total mínimo:

```text
260 TESTS
```

---

# 149. NEXT PHASE

```text
UAF-81.35 — PROCEDURAL ENVIRONMENT, MODULAR BUILDING, BLOCKOUT & WORLD ASSEMBLY SYSTEM
```

La siguiente fase deberá extender el mismo paradigma desde assets individuales hacia estructuras y espacios completos.

Deberá cubrir:

```text
BUILDINGS
ROOMS
CORRIDORS
DOORS
WINDOWS
STAIRS
WALLS
FLOORS
CEILINGS
MODULAR_KITS
PROCEDURAL_BLOCKOUT
LEVEL_ASSEMBLY
INTERIOR_LAYOUT
EXTERIOR_LAYOUT
COVER
SPAWN_POINTS
NAVIGATION
GAMEPLAY_SPACES
ENVIRONMENT_PROPS
```

El objetivo será que el sistema pueda pasar de:

```text
"generar un asset"
```

a:

```text
"generar un espacio jugable completo y validado para Unreal Engine".
```
