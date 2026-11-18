# UAF-81.22 — PROCEDURAL MATERIAL, TEXTURE & SURFACE DETAIL FABRICATION SYSTEM

## UAF-81.22-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE MATERIALES, TEXTURAS, SUPERFICIES Y DETALLE

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.22 — Procedural Material, Texture & Surface Detail Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.21  
**Next Phase:** UAF-81.23  

---

# 1. PURPOSE

UAF-81.22 establece el sistema completo para fabricar superficies visuales de producción destinadas a Unreal Engine.

El sistema deberá ser capaz de producir:

```text
MATERIALS
TEXTURES
MASKS
DECALS
TRIM SHEETS
ATLASES
SURFACE DETAILS
WEAR
DAMAGE
DIRT
CORROSION
SCRATCHES
RUST
FABRIC
LEATHER
SKIN
METAL
PLASTIC
GLASS
CERAMIC
STONE
CONCRETE
WOOD
ORGANIC
ENERGY
EMISSIVE
```

---

# 2. FUNDAMENTAL PRINCIPLE

Una superficie no deberá representarse como un conjunto arbitrario de imágenes.

Deberá existir una representación semántica:

```text
SurfaceDefinition
├── SurfaceIdentity
├── PhysicalProperties
├── VisualProperties
├── MaterialModel
├── TextureModel
├── MaskModel
├── LayerStack
├── UVStrategy
├── ResolutionProfile
├── PlatformProfile
└── UnrealProfile
```

---

# 3. MATERIAL DEFINITION

Deberá existir:

```text
MaterialDefinition
```

Mínimo:

```text
material_id
material_class
surface_type
shader_model
base_color
roughness
metallic
specular
normal
height
ao
emissive
opacity
subsurface
clearcoat
anisotropy
transmission
```

---

# 4. PHYSICAL MATERIAL CLASSIFICATION

Cada material deberá pertenecer a una clase física.

Mínimo:

```text
METAL
WOOD
STONE
CONCRETE
PLASTIC
RUBBER
GLASS
CERAMIC
FABRIC
LEATHER
SKIN
ORGANIC
LIQUID
ENERGY
CUSTOM
```

---

# 5. MATERIAL SEMANTICS

El sistema deberá distinguir entre:

```text
physical_material
render_material
gameplay_material
```

Estos tres conceptos no deberán mezclarse.

---

# 6. PHYSICAL MATERIAL

Describe propiedades físicas.

Ejemplo:

```text
METAL
WOOD
CONCRETE
FABRIC
```

---

# 7. RENDER MATERIAL

Describe cómo será renderizada la superficie.

---

# 8. GAMEPLAY MATERIAL

Describe comportamiento utilizado por gameplay.

Ejemplo:

```text
bullet_impact
footstep
penetration
destruction
surface_type
```

---

# 9. MATERIAL GRAPH

Deberá existir una representación intermedia:

```text
MaterialGraph
```

con nodos:

```text
Input
Texture
Noise
Mask
Blend
Layer
Transform
Math
Color
Normal
Roughness
Metallic
Emission
Output
```

---

# 10. GRAPH DETERMINISM

El MaterialGraph deberá poder reconstruirse determinísticamente.

---

# 11. MATERIAL LAYER SYSTEM

Las superficies complejas deberán utilizar capas.

Ejemplo:

```text
BASE_METAL
+
PAINT
+
SCRATCHES
+
DIRT
+
OIL
+
DAMAGE
+
EDGE_WEAR
```

---

# 12. LAYER ORDER

Cada capa deberá declarar:

```text
layer_id
priority
blend_mode
mask
strength
color
roughness
metallic
normal_strength
```

---

# 13. LAYER TYPES

Mínimo:

```text
BASE
PAINT
COATING
DIRT
DUST
MUD
RUST
CORROSION
SCRATCH
DAMAGE
BLOOD
OIL
WATER
DECAL
EMISSIVE
CUSTOM
```

---

# 14. PROCEDURAL SURFACE GENERATOR

Deberá existir:

```text
SurfaceGenerator
```

---

# 15. PROCEDURAL INPUTS

Podrá utilizar:

```text
position
normal
curvature
ambient_occlusion
object_id
material_id
vertex_color
uv
world_position
random_seed
```

---

# 16. PROCEDURAL NOISE

Deberán soportarse múltiples familias:

```text
VALUE
PERLIN
SIMPLEX
VORONOI
WORLEY
CELLULAR
FRACTAL
DOMAIN_WARP
CUSTOM
```

---

# 17. NOISE PARAMETERS

Mínimo:

```text
scale
frequency
octaves
lacunarity
gain
roughness
distortion
seed
```

---

# 18. PROCEDURAL MASK GENERATOR

Deberá existir:

```text
MaskGenerator
```

---

# 19. MASK TYPES

Mínimo:

```text
CURVATURE
AO
EDGE
DIRECTION
HEIGHT
POSITION
RANDOM
DAMAGE
WEAR
DIRT
PAINT
MATERIAL
OBJECT
CUSTOM
```

---

# 20. CURVATURE MASK

Deberá permitir separar:

```text
CONVEX
CONCAVE
```

---

# 21. EDGE WEAR

El desgaste de bordes deberá poder calcularse mediante geometría y/o mapas horneados.

---

# 22. DIRT MASK

La suciedad deberá poder depender de:

```text
height
orientation
cavity
curvature
exposure
randomness
```

---

# 23. ORIENTATION MASK

Deberá existir clasificación:

```text
UP
DOWN
FRONT
BACK
LEFT
RIGHT
CUSTOM_DIRECTION
```

---

# 24. WEATHERING MODEL

Deberá existir:

```text
WeatheringGenerator
```

---

# 25. WEATHERING COMPONENTS

Mínimo:

```text
dust
dirt
scratches
paint_loss
oxidation
rust
water_stains
mud
grime
```

---

# 26. DAMAGE MODEL

Deberá existir:

```text
DamageSurfaceGenerator
```

---

# 27. DAMAGE TYPES

Mínimo:

```text
SCRATCH
DENT
CRACK
CHIP
BURN
PUNCTURE
IMPACT
CORROSION
FRACTURE
CUSTOM
```

---

# 28. DAMAGE DISTRIBUTION

El daño deberá poder distribuirse mediante:

```text
uniform
weighted_random
impact_points
semantic_regions
curvature
gameplay_events
```

---

# 29. DAMAGE SEED

El daño procedural deberá ser determinista.

---

# 30. HIGH-TO-LOW BAKING

Deberá existir:

```text
BakingPipeline
```

---

# 31. BAKE INPUT

Mínimo:

```text
high_poly
low_poly
cage
uv
material_assignment
```

---

# 32. BAKE OUTPUTS

Mínimo:

```text
normal
ao
curvature
position
thickness
height
material_id
object_id
```

---

# 33. NORMAL MAP TYPES

Deberá soportarse:

```text
TANGENT_SPACE
OBJECT_SPACE
```

El target deberá determinar cuál corresponde.

---

# 34. NORMAL MAP VALIDATION

Deberá detectarse:

```text
seams
inverted_green_channel
incorrect_tangent_basis
ray_misses
projection_errors
```

---

# 35. CAGE GENERATION

Deberá existir generación automática de cage.

Parámetros:

```text
distance
offset
adaptive_distance
```

---

# 36. BAKE FAILURE HANDLING

Los rayos fallidos deberán producir diagnóstico:

```text
source
target
uv
location
direction
```

---

# 37. TEXTURE DEFINITION

Deberá existir:

```text
TextureDefinition
```

---

# 38. TEXTURE CHANNELS

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
MASK
```

---

# 39. CHANNEL PACKING

Deberá existir:

```text
TexturePackingEngine
```

Ejemplo:

```text
R = AO
G = Roughness
B = Metallic
A = Mask
```

El packing deberá ser configurable por UnrealProfile.

---

# 40. COLOR SPACE

Cada textura deberá declarar:

```text
color_space
```

Mínimo:

```text
SRGB
LINEAR
NORMAL
MASK
```

---

# 41. COLOR MANAGEMENT

La generación deberá respetar el perfil de color configurado.

No deberán existir conversiones implícitas no declaradas.

---

# 42. TEXTURE RESOLUTION

Deberá soportarse:

```text
256
512
1024
2048
4096
8192
CUSTOM
```

---

# 43. RESOLUTION PROFILE

La resolución deberá depender de:

```text
asset_type
screen_size
camera_distance
importance
platform
memory_budget
```

---

# 44. TEXTURE BUDGET

Cada asset deberá declarar:

```text
texture_memory_budget
texture_count_budget
resolution_budget
```

---

# 45. MIPMAP STRATEGY

La salida deberá ser compatible con mipmaps.

---

# 46. TEXTURE FILTERING

Deberá declararse:

```text
filtering
anisotropy
address_mode
```

---

# 47. UV SYSTEM INTEGRATION

UAF-81.22 deberá consumir información de UAF-81.21.

Nunca deberá asumir UV inexistentes.

---

# 48. UV STRATEGIES

Deberá soportar:

```text
UNIQUE_UV
TILEABLE_UV
TRIM_UV
ATLAS_UV
WORLD_ALIGNED
HYBRID
```

---

# 49. UNIQUE TEXTURE WORKFLOW

Para assets hero:

```text
HIGH_POLY
→
LOW_POLY
→
UNWRAP
→
BAKE
→
TEXTURE
```

---

# 50. TILEABLE WORKFLOW

Para superficies repetitivas:

```text
PROCEDURAL
→
TILEABLE_TEXTURE
→
MATERIAL
```

---

# 51. TRIM SHEET SYSTEM

Deberá existir:

```text
TrimSheetFabricator
```

---

# 52. TRIM SHEET REGIONS

Cada región deberá declarar:

```text
trim_id
uv_region
material_type
scale
orientation
```

---

# 53. TRIM SHEET USE CASES

Mínimo:

```text
architecture
weapons
armor
vehicles
props
```

---

# 54. ATLAS SYSTEM

Deberá existir:

```text
TextureAtlasBuilder
```

---

# 55. ATLAS PACKING

Deberá minimizar:

```text
wasted_space
bleeding
padding_loss
```

---

# 56. ATLAS PADDING

El padding deberá ser configurable y compatible con mipmaps.

---

# 57. DECAL SYSTEM

Deberá existir:

```text
DecalFabricator
```

---

# 58. DECAL TYPES

Mínimo:

```text
LOGO
WARNING
DAMAGE
GRAFFITI
NUMBER
SYMBOL
BLOOD
DIRT
GAMEPLAY
CUSTOM
```

---

# 59. DECAL MATERIALS

Los decals deberán utilizar materiales optimizados y parametrizables.

---

# 60. SURFACE DETAIL

Deberán distinguirse:

```text
GEOMETRIC_DETAIL
NORMAL_DETAIL
ROUGHNESS_DETAIL
COLOR_DETAIL
```

---

# 61. DETAIL PRIORITY

El sistema deberá decidir automáticamente si un detalle debe representarse como:

```text
GEOMETRY
NORMAL
HEIGHT
TEXTURE
MATERIAL_FUNCTION
```

según distancia y presupuesto.

---

# 62. DETAIL DISTANCE

Cada detalle deberá declarar:

```text
visibility_distance
importance
```

---

# 63. DETAIL REDUCTION

Los detalles pequeños deberán poder desaparecer progresivamente mediante LOD/material strategy.

---

# 64. MATERIAL INSTANCE SYSTEM

Deberá existir:

```text
MaterialInstanceFactory
```

---

# 65. MATERIAL PARAMETERS

Los parámetros deberán ser explícitos.

Ejemplo:

```text
BaseColor
Roughness
Metallic
NormalStrength
WearAmount
DirtAmount
DamageAmount
EmissionStrength
```

---

# 66. PARAMETER VALIDATION

Cada parámetro deberá tener:

```text
minimum
maximum
default
type
```

---

# 67. MATERIAL VARIANTS

Un mismo material base deberá producir:

```text
clean
dirty
damaged
wet
burned
aged
corroded
```

sin duplicar innecesariamente el material maestro.

---

# 68. MASTER MATERIAL POLICY

Deberán minimizarse los master materials.

---

# 69. MATERIAL FUNCTION SYSTEM

Las funciones reutilizables deberán poder compartirse:

```text
MF_Wear
MF_Dirt
MF_Scratches
MF_Grime
MF_EdgeWear
MF_Damage
MF_Emissive
MF_Fabric
MF_Metal
```

---

# 70. UNREAL MATERIAL CONTRACT

Toda salida deberá declarar:

```text
material_domain
blend_mode
shading_model
two_sided
opacity_mode
```

---

# 71. SHADING MODELS

Deberán soportarse al menos:

```text
DEFAULT_LIT
UNLIT
SUBSURFACE
CLOTH
HAIR
EYE
CUSTOM
```

según disponibilidad del target.

---

# 72. TRANSLUCENCY

Los materiales translúcidos deberán declararse explícitamente.

---

# 73. OPACITY

Deberá distinguirse:

```text
OPAQUE
MASKED
TRANSLUCENT
```

---

# 74. EMISSIVE CONTROL

El emissive deberá estar sujeto a:

```text
maximum_intensity
exposure_profile
bloom_profile
```

---

# 75. PBR VALIDATION

Deberán validarse rangos físicamente razonables para:

```text
roughness
metallic
specular
normal_strength
```

---

# 76. METALLIC VALIDATION

El sistema deberá evitar valores metálicos arbitrarios en materiales no metálicos.

---

# 77. ROUGHNESS VALIDATION

Deberá impedirse la generación accidental de superficies visualmente incompatibles con su clasificación física.

---

# 78. MATERIAL CONSISTENCY

Los valores deberán evaluarse conjuntamente.

No se aceptará validar cada canal de forma aislada.

---

# 79. FABRIC MATERIAL

Deberá existir un modelo específico para:

```text
cloth
canvas
nylon
leather
```

---

# 80. SKIN MATERIAL

Deberá existir soporte para:

```text
subsurface
micro_normal
roughness_variation
pores
color_variation
```

---

# 81. METAL MATERIAL

Deberá soportar:

```text
paint
bare_metal
oxidation
scratches
roughness_variation
```

---

# 82. HARD SURFACE MATERIAL

Deberá soportar:

```text
panels
seams
bolts
scratches
edge_wear
paint_layers
```

---

# 83. ORGANIC MATERIAL

Deberá soportar:

```text
surface_variation
wetness
roughness
growth
damage
```

---

# 84. GLASS MATERIAL

Deberá declarar:

```text
transmission
roughness
tint
thickness
```

---

# 85. ENERGY MATERIAL

Deberá declarar:

```text
emission_color
emission_strength
pattern
animation_source
```

---

# 86. WORLD-SPACE MATERIALS

Deberán existir materiales capaces de utilizar:

```text
world_position
world_normal
object_scale
```

para superficies grandes.

---

# 87. ANTI-TILING SYSTEM

Deberá existir:

```text
AntiTilingGenerator
```

---

# 88. ANTI-TILING STRATEGIES

Mínimo:

```text
UV_OFFSET
ROTATION
MIRROR
MACRO_VARIATION
WORLD_VARIATION
RANDOM_LAYERING
```

---

# 89. SCALE CONSISTENCY

Los patrones procedurales deberán conservar escala física coherente.

---

# 90. TEXEL DENSITY

Deberá existir:

```text
TexelDensityValidator
```

---

# 91. TEXEL DENSITY TARGET

Cada asset deberá declarar:

```text
target_texel_density
minimum_texel_density
maximum_texel_density
```

---

# 92. TEXEL DENSITY VALIDATION

Deberá detectarse:

```text
under_resolution
over_resolution
inconsistent_density
```

---

# 93. MATERIAL SEAM VALIDATION

Deberán detectarse:

```text
visible_seams
UV_seams
normal_seams
color_seams
roughness_seams
```

---

# 94. TEXTURE BLEEDING

Deberá existir validación contra bleeding en:

```text
mipmap
atlas
trim
unique_uv
```

---

# 95. TEXTURE COMPRESSION PROFILE

Cada textura deberá declarar:

```text
compression_profile
platform_profile
importance
alpha_usage
```

---

# 96. PLATFORM PROFILES

Mínimo:

```text
PC
CONSOLE
MOBILE
VR
CUSTOM
```

---

# 97. TEXTURE FORMAT POLICY

La selección de formato deberá depender de:

```text
channel_type
alpha
normal
platform
memory_budget
quality_requirement
```

---

# 98. TEXTURE MEMORY ESTIMATION

Deberá calcularse antes de exportar:

```text
raw_memory
compressed_memory_estimate
mip_memory
total_memory
```

---

# 99. DRAW CALL IMPACT

La arquitectura deberá calcular el impacto aproximado de:

```text
material_slots
unique_materials
decals
```

---

# 100. MATERIAL SLOT OPTIMIZATION

Deberá existir:

```text
MaterialSlotOptimizer
```

---

# 101. SLOT MERGING

Materiales compatibles deberán poder combinarse cuando la calidad no sea afectada.

---

# 102. MATERIAL SPLITTING

Un material podrá dividirse cuando:

```text
shading_model
opacity
performance
visual_requirement
```

lo justifique.

---

# 103. TEXTURE STREAMING

Las texturas deberán declarar:

```text
streaming_priority
never_stream
mip_bias
```

cuando el target lo requiera.

---

# 104. CHARACTER TEXTURE STRATEGY

Para personajes deberá soportarse:

```text
FACE_TEXTURE
BODY_TEXTURE
CLOTHING_TEXTURE
ARMOR_TEXTURE
HAIR_TEXTURE
```

y estrategias atlas/trims cuando resulte beneficioso.

---

# 105. WEAPON TEXTURE STRATEGY

Las armas deberán poder utilizar:

```text
UNIQUE
TRIM
TILEABLE
HYBRID
```

---

# 106. ENVIRONMENT TEXTURE STRATEGY

Los entornos deberán priorizar:

```text
TILEABLE
TRIM
MACRO_VARIATION
DECALS
VERTEX_COLOR
WORLD_ALIGNED
```

según el caso.

---

# 107. VERTEX COLOR MASKS

Deberá existir soporte para máscaras mediante vertex colors:

```text
R
G
B
A
```

---

# 108. VERTEX MASK SEMANTICS

El significado de cada canal deberá estar declarado.

Ejemplo:

```text
R = dirt
G = wear
B = damage
A = emissive
```

---

# 109. PROCEDURAL COLOR VARIATION

El sistema deberá soportar variaciones controladas de color.

---

# 110. COLOR PALETTE

Deberá existir:

```text
PaletteDefinition
```

---

# 111. PALETTE RULES

La paleta deberá poder restringirse mediante:

```text
hue_range
saturation_range
value_range
contrast
```

---

# 112. STYLE CONSISTENCY

Los materiales generados deberán poder heredar:

```text
StyleArchetype
```

---

# 113. GLOBAL STYLE

Un proyecto deberá poder definir:

```text
metal_language
roughness_language
color_language
damage_language
wear_language
emission_language
```

---

# 114. SURFACE LANGUAGE

La apariencia de diferentes assets deberá poder pertenecer a una misma familia visual.

---

# 115. MATERIAL CROSS-ASSET CONSISTENCY

El metal de:

```text
character
weapon
vehicle
environment
```

deberá poder compartir reglas físicas y visuales.

---

# 116. TEXTURE GENERATION MODES

Mínimo:

```text
FULL_PROCEDURAL
BAKED
HYBRID
IMPORTED_REFERENCE
CUSTOM
```

---

# 117. IMPORTED REFERENCE

Las referencias externas deberán poder convertirse en datos controlados del pipeline.

No deberán convertirse automáticamente en dependencias ocultas.

---

# 118. REFERENCE TRACEABILITY

Toda referencia utilizada deberá registrar:

```text
source_id
source_type
version
hash
usage
```

---

# 119. TEXTURE SOURCE HASH

Toda textura deberá tener hash de contenido.

---

# 120. MATERIAL VERSIONING

Cada material deberá tener:

```text
material_id
material_version
generator_version
```

---

# 121. CACHE

Deberá existir caché para:

```text
noise
masks
bakes
textures
material_graphs
atlases
trim_sheets
```

---

# 122. CACHE INVALIDATION

La caché deberá invalidarse mediante dependencias explícitas.

---

# 123. INCREMENTAL MATERIAL BUILD

Deberá soportarse:

```text
MASK_ONLY
BAKE_ONLY
BASE_COLOR_ONLY
NORMAL_ONLY
ROUGHNESS_ONLY
MATERIAL_ONLY
LOD_TEXTURE_ONLY
FULL_SURFACE
```

---

# 124. MATERIAL TRANSACTION

Cada construcción deberá ser transaccional:

```text
CREATE
VALIDATE
COMMIT
ROLLBACK
```

---

# 125. TEXTURE QA

Deberá existir:

```text
TextureValidator
```

---

# 126. TEXTURE VALIDATION

Mínimo:

```text
resolution
format
color_space
alpha
compression
seams
bleeding
tiling
texel_density
```

---

# 127. NORMAL VALIDATION

Mínimo:

```text
orientation
channel_order
intensity
seams
```

---

# 128. ROUGHNESS VALIDATION

Deberá analizar:

```text
range
contrast
noise
material_consistency
```

---

# 129. BASE COLOR VALIDATION

Deberá analizar:

```text
range
clipping
saturation
palette_compliance
```

---

# 130. MATERIAL VISUAL QA

Deberá existir:

```text
MaterialVisualValidator
```

---

# 131. VISUAL TEST LIGHTING

Los materiales deberán probarse bajo:

```text
NEUTRAL_STUDIO
HARSH_LIGHT
SOFT_LIGHT
DARK_LIGHT
GAMEPLAY_LIGHT
```

---

# 132. MATERIAL REFERENCE TEST

El sistema deberá comparar:

```text
expected_profile
generated_material
```

mediante métricas configurables.

---

# 133. MATERIAL REGRESSION

Cambios en el generador deberán compararse contra golden materials.

---

# 134. GOLDEN MATERIALS

Mínimo:

```text
MAT_METAL
MAT_PAINTED_METAL
MAT_FABRIC
MAT_LEATHER
MAT_SKIN
MAT_CONCRETE
MAT_WOOD
MAT_GLASS
MAT_PLASTIC
MAT_EMISSIVE
```

---

# 135. STRESS MATERIAL

Deberá existir un material con:

```text
multiple_layers
multiple_masks
normal_detail
wear
damage
emission
```

---

# 136. LARGE SURFACE TEST

Deberá existir una superficie suficientemente grande para evaluar:

```text
tiling
macro_variation
texel_density
world_alignment
```

---

# 137. MATERIAL PERFORMANCE TEST

Deberá medirse:

```text
instruction_estimate
texture_count
texture_memory
material_instances
```

---

# 138. SHADER COMPLEXITY

Deberá existir un límite configurable de complejidad.

---

# 139. COMPLEXITY FAILURE

Si se supera el límite:

```text
WARNING
OPTIMIZE
REJECT
```

según perfil.

---

# 140. MATERIAL OPTIMIZER

Deberá existir:

```text
MaterialOptimizer
```

---

# 141. OPTIMIZATION STRATEGIES

Mínimo:

```text
texture_packing
layer_baking
mask_packing
material_merge
parameter_reduction
detail_baking
```

---

# 142. MATERIAL BAKE-DOWN

Capas procedurales podrán convertirse en textura cuando resulte más eficiente.

---

# 143. MATERIAL PROMOTION

Una textura podrá reemplazar una operación procedural si reduce coste sin degradar calidad.

---

# 144. QUALITY/PERFORMANCE TRADEOFF

Toda optimización deberá registrar:

```text
quality_before
quality_after
performance_before
performance_after
```

---

# 145. DECISION TRACE

El sistema deberá explicar por qué eligió:

```text
procedural
baked
packed
merged
unique
tileable
trim
atlas
```

---

# 146. UNREAL EXPORT PACKAGE

Deberá producir:

```text
Material
MaterialInstances
Textures
MaterialFunctions
Decals
PhysicalMaterials
Metadata
ValidationReport
```

---

# 147. MATERIAL MANIFEST

Mínimo:

```text
material_id
version
shader_model
texture_ids
parameter_definitions
physical_material
platform_profile
memory_estimate
```

---

# 148. TEXTURE MANIFEST

Mínimo:

```text
texture_id
channel
resolution
format
color_space
compression
mip_policy
memory_estimate
hash
```

---

# 149. PHYSICAL MATERIAL MANIFEST

Mínimo:

```text
physical_material_id
surface_type
footstep_type
impact_type
penetration_type
```

---

# 150. DEPENDENCY GRAPH

Deberá existir relación:

```text
Asset
 ↓
Material
 ↓
Texture
 ↓
Mask
 ↓
Source
```

---

# 151. NO HIDDEN ASSET RULE

Ningún material podrá depender silenciosamente de:

```text
local_files
absolute_paths
temporary_files
manual_blender_state
untracked_images
```

---

# 152. REPRODUCIBILITY

La misma:

```text
MaterialDefinition
+
Seed
+
GeneratorVersion
```

deberá producir una salida equivalente.

---

# 153. SURFACE BUILD RESULT

Deberá existir:

```text
SurfaceBuildResult
```

Mínimo:

```text
success
material_manifest
texture_manifest
generated_assets
validation_report
performance_report
diagnostics
```

---

# 154. ERROR TAXONOMY

Mínimo:

```text
MATERIAL_SCHEMA_ERROR
TEXTURE_SCHEMA_ERROR
UV_ERROR
BAKE_ERROR
MASK_ERROR
COLOR_ERROR
PBR_ERROR
COMPRESSION_ERROR
MEMORY_BUDGET_ERROR
SHADER_COMPLEXITY_ERROR
EXPORT_ERROR
```

---

# 155. DIAGNOSTIC EVIDENCE

Todo error deberá incluir:

```text
error_code
asset_id
component
location
actual_value
expected_value
threshold
severity
resolution
```

---

# 156. SURFACE QUALITY GATE

Una superficie podrá ser aceptada únicamente si:

```text
SCHEMA_VALID
AND
UV_VALID
AND
TEXTURE_VALID
AND
PBR_VALID
AND
MATERIAL_VALID
AND
MEMORY_VALID
AND
PERFORMANCE_VALID
AND
UNREAL_VALID
```

---

# 157. PROFESSIONAL MATERIAL ACCEPTANCE TEST

El sistema deberá producir al menos:

```text
1. Un metal pintado con desgaste.
2. Un metal corroído.
3. Un material de tela.
4. Un material de cuero.
5. Un material de piel.
6. Un material de hormigón.
7. Un material de madera.
8. Un material de cristal.
9. Un material emissive.
10. Un material procedural tileable.
11. Un trim sheet.
12. Un atlas.
13. Un decal set.
14. Un material multicapa.
15. Un material horneado desde high-poly.
```

---

# 158. CROSS-ASSET ACCEPTANCE TEST

Los materiales deberán poder utilizarse en:

```text
CHARACTER
CREATURE
WEAPON
VEHICLE
PROP
ARCHITECTURE
ENVIRONMENT
```

sin modificar la arquitectura fundamental.

---

# 159. CHARACTER INTEGRATION

UAF-81.22 deberá integrarse directamente con UAF-81.21.

Debe permitir:

```text
body_material
skin_material
hair_material
cloth_material
armor_material
equipment_material
```

---

# 160. ENVIRONMENT INTEGRATION

Debe permitir materiales de:

```text
floor
wall
ceiling
metal_structure
wood_structure
rock
vegetation
water
```

---

# 161. MASTER STYLE INTEGRATION

Todos los materiales deberán poder heredar un:

```text
ProjectMaterialStyle
```

---

# 162. PROJECT MATERIAL STYLE

Mínimo:

```text
default_roughness_range
metal_response
damage_language
wear_language
color_palette
emission_policy
normal_detail_scale
```

---

# 163. ARTISTIC OVERRIDE

El artista deberá poder modificar parámetros permitidos sin alterar la arquitectura.

---

# 164. GOVERNANCE

Los parámetros modificables deberán clasificarse:

```text
PUBLIC
CONTROLLED
INTERNAL
LOCKED
```

---

# 165. LOCKED PARAMETERS

No deberán modificarse sin cambiar la versión del profile:

```text
shader_contract
texture_contract
coordinate_system
packing_contract
export_contract
```

---

# 166. AUDIT TRAIL

Toda generación deberá registrar:

```text
material_id
seed
generator_version
profile_version
inputs
outputs
optimization_decisions
validation_results
```

---

# 167. CHECKPOINTS

Mínimo:

```text
SURFACE_SPECIFIED
MATERIAL_GRAPH_BUILT
UV_VALIDATED
BAKE_COMPLETED
MASKS_GENERATED
TEXTURES_GENERATED
MATERIAL_ASSEMBLED
OPTIMIZED
VALIDATED
EXPORTED
```

---

# 168. FINAL ARCHITECTURAL MODEL

UAF-81.22 deberá considerar:

```text
SURFACE
=
PHYSICAL_MODEL
+
MATERIAL_GRAPH
+
LAYERS
+
MASKS
+
TEXTURES
+
UV_STRATEGY
+
DETAIL
+
OPTIMIZATION
+
UNREAL_CONTRACT
```

---

# 169. CRITICAL DESIGN REQUIREMENT

La arquitectura no deberá convertir todos los materiales en texturas únicas.

Deberá seleccionar dinámicamente entre:

```text
UNIQUE_TEXTURE
TILEABLE_TEXTURE
TRIM_SHEET
ATLAS
WORLD_ALIGNED
PROCEDURAL
DECAL
VERTEX_MASK
HYBRID
```

según:

```text
asset_scale
camera_distance
asset_importance
repetition
memory_budget
shader_budget
```

---

# 170. FINAL OBJECTIVE

El objetivo de UAF-81.22 será transformar:

```text
TEXTURE GENERATION
```

en:

```text
PRODUCTION SURFACE FABRICATION
```

capaz de producir superficies:

```text
PHYSICALLY COHERENT
VISUALLY CONSISTENT
PROCEDURAL
BAKED
OPTIMIZED
VARIANT-READY
MEMORY-AWARE
UNREAL-READY
```

---

# 171. DEPENDENCIES

UAF-81.22 dependerá de:

```text
UAF-81.01 → Core Factory
UAF-81.02 → Asset Schema
UAF-81.03 → Semantic Asset Graph
UAF-81.04 → Generation Strategy
UAF-81.05 → Deterministic Build
UAF-81.06 → Validation
UAF-81.07 → Performance
UAF-81.08 → Unreal Integration
UAF-81.21 → Character Fabrication
```

---

# 172. NEXT PHASE

```text
UAF-81.23 — PROCEDURAL ANIMATION, RIGGING & MOTION FABRICATION SYSTEM
```

Esta fase deberá resolver:

```text
SKELETON
      ↓
RIG
      ↓
IK
      ↓
CONTROL RIG
      ↓
POSE GENERATION
      ↓
MOTION GENERATION
      ↓
ANIMATION RETARGETING
      ↓
ROOT MOTION
      ↓
MOTION VALIDATION
      ↓
ANIMATION COMPRESSION
      ↓
UNREAL ANIMATION ASSETS
```
