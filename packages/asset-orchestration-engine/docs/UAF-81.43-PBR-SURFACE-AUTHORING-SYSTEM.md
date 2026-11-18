# UAF-81.43 — MATERIAL, TEXTURE, UV, PBR, PROCEDURAL SURFACE & UNREAL MATERIAL AUTHORING SYSTEM

## UAF-81.43-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA PROCEDURAL DE MATERIALES, TEXTURAS, UV, PBR, SUPERFICIES PROCEDURALES Y AUTORÍA DE MATERIALES PARA UNREAL

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.43 — Material, Texture, UV, PBR, Procedural Surface & Unreal Material Authoring System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.42  
**Next Phase:** UAF-81.44  

---

# 1. PURPOSE

UAF-81.43 establece el sistema completo para convertir cualquier asset geométrico producido por AOE en un asset con:

* UVs profesionales.
* Materiales físicamente coherentes.
* Texturas PBR.
* Superficies procedurales.
* Materiales multicapa.
* Decals.
* Masks.
* Detail maps.
* Baking.
* Texture atlases.
* Material instances.
* Optimización para Unreal Engine.
* Validación automática técnica y visual.

El sistema deberá funcionar para:

```text
CHARACTERS
CREATURES
ROBOTS
WEAPONS
PROPS
ARCHITECTURE
MODULAR_KITS
ENVIRONMENTS
VEGETATION
VEHICLES
VFX_SUPPORT_ASSETS
```

---

# 2. PRIMARY OBJECTIVE

La entrada podrá ser:

```text
Mesh
MaterialIntent
StyleProfile
SurfaceProfile
TextureProfile
```

La salida deberá poder producir:

```text
UVSet
MaterialDefinition
TextureSet
BakeSet
ShaderDefinition
MaterialInstanceDefinition
UnrealMaterialPackage
ValidationReport
```

---

# 3. COMPLETE MATERIAL PIPELINE

El pipeline deberá ser:

```text
ASSET
↓
SURFACE ANALYSIS
↓
MATERIAL CLASSIFICATION
↓
UV STRATEGY
↓
UV GENERATION
↓
UV VALIDATION
↓
MATERIAL GRAPH GENERATION
↓
TEXTURE GENERATION
↓
BAKING
↓
TEXTURE VALIDATION
↓
PBR VALIDATION
↓
MATERIAL OPTIMIZATION
↓
UNREAL SHADER DEFINITION
↓
MATERIAL INSTANCE
↓
PACKAGING
↓
FINAL QA
```

---

# 4. MATERIAL ARCHITECTURE

Deberán existir como mínimo:

```text
MaterialDefinition
MaterialLayer
MaterialParameter
MaterialGraph
TextureDefinition
TextureSet
UVDefinition
BakeDefinition
SurfaceDefinition
MaterialValidator
TextureValidator
UVValidator
```

---

# 5. MATERIAL DEFINITION

Cada material deberá declarar:

```text
material_id
name
category
shader_model
surface_type
texture_set
uv_requirements
parameters
layers
optimization_profile
target_platform
```

---

# 6. MATERIAL CATEGORIES

Mínimo:

```text
ORGANIC
SKIN
FABRIC
LEATHER
METAL
PAINTED_METAL
PLASTIC
RUBBER
GLASS
CERAMIC
STONE
CONCRETE
WOOD
VEGETATION
LIQUID
ENERGY
EMISSIVE
HOLOGRAPHIC
TECHNICAL
MULTI_LAYER
CUSTOM
```

---

# 7. SURFACE CLASSIFICATION

Cada superficie deberá poder clasificarse mediante:

```text
SurfaceClassifier
```

y producir:

```text
surface_type
confidence
material_candidates
evidence
```

---

# 8. MULTI-MATERIAL MESH

Una malla podrá contener múltiples regiones materiales.

Cada región deberá tener:

```text
region_id
material_id
faces
priority
semantic_role
```

---

# 9. MATERIAL SEMANTICS

Deberán poder definirse regiones:

```text
skin
eyes
mouth
armor
metal
cloth
rubber
glass
emissive
damage
decals
```

---

# 10. UV ARCHITECTURE

Deberán existir:

```text
UVSetDefinition
UVIsland
UVChart
UVUnwrapper
UVOptimizer
UVValidator
```

---

# 11. UV CHANNELS

El sistema deberá soportar como mínimo:

```text
UV0
UV1
UV2
UV3
```

El número real deberá depender del target.

---

# 12. UV0

UV0 deberá utilizarse para texturas principales salvo que el perfil indique otra cosa.

---

# 13. UV1

UV1 podrá utilizarse para:

```text
LIGHTMAP
BAKING
SECONDARY_TEXTURES
```

según el asset.

---

# 14. UV2+

Deberán poder utilizarse para:

```text
DETAIL
DECALS
TRIM
PROCEDURAL_MAPPING
```

---

# 15. UV GENERATION STRATEGIES

Mínimo:

```text
SMART_PROJECT
ANGLE_BASED
CONFORMAL
CUBIC
CYLINDRICAL
SPHERICAL
PLANAR
TRIM_SHEET
UDIM
CUSTOM
```

---

# 16. UV STRATEGY SELECTION

La estrategia deberá considerar:

```text
geometry_type
surface_type
texture_resolution
material_type
deformation
camera_importance
asset_scale
```

---

# 17. UV SEAMS

Los seams deberán minimizar:

```text
distortion
visible_texture_breaks
stretch
unnecessary_islands
```

---

# 18. UV ISLAND VALIDATION

Cada isla deberá validar:

```text
area
orientation
overlap
distortion
padding
density
```

---

# 19. UV OVERLAP

Deberá distinguirse:

```text
INTENTIONAL_OVERLAP
UNINTENTIONAL_OVERLAP
```

---

# 20. UV OVERLAP GATE

El sistema deberá rechazar overlap no autorizado.

---

# 21. UV DISTORTION

Deberá calcularse un índice de distorsión.

Mínimo:

```text
stretch
compression
angular_distortion
area_distortion
```

---

# 22. TEXEL DENSITY

Deberá existir:

```text
TexelDensityAnalyzer
```

---

# 23. TEXEL DENSITY

La densidad deberá expresarse explícitamente en:

```text
pixels_per_meter
```

---

# 24. TEXEL DENSITY PROFILES

Mínimo:

```text
HERO
HIGH
MEDIUM
LOW
BACKGROUND
```

---

# 25. TEXEL DENSITY CONSISTENCY

Assets que formen parte del mismo conjunto visual deberán mantener densidad compatible.

---

# 26. UDIM

El sistema deberá soportar UDIM cuando el perfil lo requiera.

---

# 27. UDIM ASSIGNMENT

Los tiles deberán ser deterministas.

---

# 28. UDIM VALIDATION

Deberá comprobarse:

```text
tile_assignment
missing_tiles
duplicate_tiles
invalid_uv_range
```

---

# 29. TRIM SHEETS

Deberá existir soporte para materiales basados en:

```text
trim_sheet
```

---

# 30. TRIM SHEET VALIDATION

Deberá comprobar:

```text
trim_alignment
texel_density
orientation
padding
material_region
```

---

# 31. MATERIAL GRAPH

Deberá existir una representación intermedia independiente de Blender.

```text
MaterialGraph
```

no deberá depender directamente de nodos específicos de una única aplicación.

---

# 32. MATERIAL GRAPH NODES

Mínimo:

```text
TextureSample
Color
Float
Vector
Multiply
Add
Subtract
Lerp
Clamp
Power
Contrast
Remap
Noise
Mask
Normal
Transform
UV
WorldPosition
ObjectPosition
VertexColor
Parameter
Output
```

---

# 33. MATERIAL OUTPUTS

Deberán soportarse:

```text
BASE_COLOR
METALLIC
ROUGHNESS
SPECULAR
NORMAL
EMISSIVE
OPACITY
OPACITY_MASK
AMBIENT_OCCLUSION
WORLD_POSITION_OFFSET
PIXEL_DEPTH_OFFSET
SUBSURFACE
SUBSURFACE_COLOR
```

cuando el target lo soporte.

---

# 34. PBR CORE

El sistema deberá utilizar un modelo PBR consistente.

---

# 35. BASE COLOR

La textura de base color deberá contener exclusivamente información compatible con color/albedo.

No deberá contener:

```text
lighting
AO
specular highlights
shadows
```

salvo perfiles explícitos que lo requieran.

---

# 36. METALLIC

Deberá ser un mapa escalar.

Los valores deberán estar dentro de:

```text
0.0 → 1.0
```

---

# 37. ROUGHNESS

Deberá ser un mapa escalar normalizado.

---

# 38. NORMAL MAP

Deberá declararse:

```text
tangent_space
channel_convention
compression_profile
```

---

# 39. NORMAL VALIDATION

Deberá detectarse:

```text
invalid_range
wrong_channel_order
incorrect_orientation
excessive_strength
```

---

# 40. AMBIENT OCCLUSION

Deberá poder generarse mediante:

```text
geometry_bake
procedural
vertex
external_source
```

---

# 41. EMISSIVE

Todo emissive deberá declarar:

```text
intensity
color
purpose
```

---

# 42. EMISSIVE LIMIT

Deberá existir un límite configurable para evitar valores visualmente destructivos en el target.

---

# 43. PROCEDURAL TEXTURE SYSTEM

Deberá existir:

```text
ProceduralTextureDefinition
ProceduralTextureGenerator
ProceduralTextureSeed
```

---

# 44. PROCEDURAL GENERATORS

Mínimo:

```text
PERLIN
VORONOI
FRACTAL
CELLULAR
WAVE
GRADIENT
RANDOM
DIRECTIONAL
WEAR
SCRATCH
DUST
DIRT
RUST
CORROSION
```

---

# 45. PROCEDURAL PARAMETERS

Cada generador deberá declarar:

```text
seed
scale
frequency
amplitude
octaves
contrast
rotation
offset
```

cuando aplique.

---

# 46. DETERMINISTIC TEXTURES

La misma combinación:

```text
asset
material
seed
resolution
parameters
```

deberá generar la misma textura.

---

# 47. MATERIAL LAYERS

Deberá existir soporte para:

```text
BASE
DUST
DIRT
SCRATCH
RUST
WETNESS
SNOW
MUD
BLOOD_PROXY
DAMAGE
EDGE_WEAR
DECAL
EMISSIVE
```

---

# 48. LAYER MASKS

Cada layer podrá utilizar:

```text
vertex_color
curvature
AO
world_height
slope
noise
manual_mask
procedural_mask
texture_mask
```

---

# 49. CURVATURE MAP

Deberá poder generarse:

```text
convex
concave
combined
```

---

# 50. EDGE WEAR

Deberá existir un generador basado en:

```text
curvature
normal
AO
position
material_age
```

---

# 51. DIRT SYSTEM

El dirt podrá depender de:

```text
AO
height
orientation
curvature
noise
```

---

# 52. RUST SYSTEM

El rust deberá poder limitarse por:

```text
material_type
exposure
height
curvature
mask
```

---

# 53. DAMAGE SYSTEM

Deberá soportar:

```text
scratches
chips
fractures
burn
impact
deformation_mask
```

---

# 54. WEAR CONSISTENCY

Los efectos de desgaste deberán ser consistentes entre:

```text
BaseColor
Roughness
Normal
Metallic
```

cuando corresponda.

---

# 55. BAKING SYSTEM

Deberá existir:

```text
BakeDefinition
BakeTarget
BakeProfile
BakeExecutor
BakeValidator
```

---

# 56. BAKE TYPES

Mínimo:

```text
NORMAL
AO
CURVATURE
POSITION
THICKNESS
ID
MATERIAL_ID
WORLD_SPACE_NORMAL
COMBINED
```

---

# 57. HIGH → LOW BAKING

Deberá soportarse:

```text
HIGH_POLY
↓
LOW_POLY
↓
BAKE
```

---

# 58. CAGE SYSTEM

Deberá existir:

```text
BakeCageDefinition
```

con:

```text
distance
bias
ray_direction
```

---

# 59. BAKE FAILURE DETECTION

Deberá detectar:

```text
ray_miss
projection_error
cage_intersection
projection_overlap
invalid_normal
```

---

# 60. BAKE QUALITY

Deberá poder configurarse:

```text
resolution
samples
anti_aliasing
ray_distance
cage_distance
```

---

# 61. TEXTURE RESOLUTIONS

Mínimo:

```text
256
512
1024
2048
4096
8192
```

cuando el target y hardware lo permitan.

---

# 62. RESOLUTION SELECTION

La resolución deberá depender de:

```text
asset_importance
surface_area
texel_density
camera_distance
platform_budget
```

---

# 63. TEXTURE FORMATS

Deberán declararse formatos por plataforma.

No se permitirá asumir que el formato de trabajo es el formato final de Unreal.

---

# 64. COLOR MANAGEMENT

Todo pipeline deberá declarar:

```text
working_color_space
texture_color_space
export_color_space
```

---

# 65. SRGB VALIDATION

Deberá validarse individualmente qué mapas utilizan sRGB.

---

# 66. NON-COLOR DATA

Los mapas:

```text
normal
roughness
metallic
AO
mask
height
```

no deberán tratarse accidentalmente como color.

---

# 67. TEXTURE PACKING

Deberá existir:

```text
TextureChannelPacker
```

---

# 68. CHANNEL PACKING

Podrá combinar:

```text
R = AO
G = Roughness
B = Metallic
A = Mask
```

si el perfil lo especifica.

---

# 69. CHANNEL PACKING VALIDATION

Deberá comprobarse que ningún canal requerido haya sido sobrescrito accidentalmente.

---

# 70. TEXTURE COMPRESSION

Deberá existir:

```text
TextureCompressionProfile
```

por plataforma.

---

# 71. COMPRESSION VALIDATION

Deberá analizarse:

```text
quality
artifact_level
normal_integrity
alpha_integrity
```

---

# 72. MIPMAP SYSTEM

Las texturas deberán generar mipmaps cuando corresponda.

---

# 73. MIP VALIDATION

Deberá comprobarse:

```text
mip_count
resolution_chain
filtering
alpha_behavior
```

---

# 74. TEXTURE STREAMING

Deberá existir metadata para:

```text
streaming
priority
group
max_resolution
```

---

# 75. VIRTUAL TEXTURES

Deberá existir soporte opcional para virtual texturing.

---

# 76. MATERIAL INSTANCES

Deberá existir:

```text
MaterialInstanceDefinition
```

---

# 77. INSTANCE PARAMETERS

Podrán sobrescribirse:

```text
base_color
roughness
metallic
normal_strength
emissive_color
emissive_intensity
tiling
offset
detail_strength
wear_amount
damage_amount
```

---

# 78. INSTANCE INHERITANCE

Una MaterialInstance deberá derivar de un MaterialDefinition válido.

---

# 79. INSTANCE VALIDATION

No podrá utilizar parámetros inexistentes.

---

# 80. MATERIAL VARIANTS

Deberán poder generarse variantes:

```text
CLEAN
USED
DAMAGED
HEAVILY_DAMAGED
WET
DIRTY
RUSTED
BLOODIED_PROXY
FROZEN
BURNED
```

---

# 81. CHARACTER MATERIALS

Los personajes deberán poder separar:

```text
skin
hair
eyes
teeth
cloth
armor
metal
rubber
emissive
```

---

# 82. SKIN MATERIAL

El sistema deberá poder generar perfiles para:

```text
human
alien
synthetic
dark_fluid
organic_creature
```

---

# 83. EYE MATERIAL

Deberá soportar:

```text
cornea
iris
pupil
sclera
wetness
emissive
```

cuando aplique.

---

# 84. HAIR MATERIAL

Deberá existir un perfil específico para:

```text
hair_cards
grooms
synthetic_hair
fur
```

---

# 85. CLOTH MATERIAL

Deberá soportar:

```text
fabric
leather
rubberized_fabric
technical_fabric
```

---

# 86. METAL MATERIAL

Deberá soportar:

```text
bare_metal
painted_metal
brushed_metal
oxidized_metal
chrome
industrial_metal
```

---

# 87. GLASS MATERIAL

Deberá definir explícitamente:

```text
transparency
refraction
roughness
ior
thickness
```

cuando aplique.

---

# 88. ORGANIC MATERIAL

Deberá soportar perfiles de:

```text
skin
flesh
bone
chitin
plant
fungal
```

---

# 89. VEGETATION MATERIAL

Deberá poder declarar:

```text
two_sided
subsurface
wind
opacity_mask
season
```

---

# 90. ARCHITECTURAL MATERIAL

Deberá soportar:

```text
concrete
brick
stone
wood
glass
paint
metal
```

---

# 91. DECAL SYSTEM

Deberá existir:

```text
DecalDefinition
DecalMaterial
DecalMask
DecalPlacement
```

---

# 92. DECAL TYPES

Mínimo:

```text
DAMAGE
WARNING
LOGO
NUMBER
GRAFFITI
DIRT
BLOOD_PROXY
TECHNICAL
IDENTIFICATION
```

---

# 93. DECAL PLACEMENT

Deberá poder utilizar:

```text
surface_normal
socket
landmark
bounding_box
manual_transform
```

---

# 94. DECAL VALIDATION

Deberá detectar:

```text
floating_decal
incorrect_projection
z_fighting
excessive_overlap
```

---

# 95. MATERIAL SCALE

Todo material deberá declarar su escala física.

Ejemplo:

```text
concrete_grain_scale
metal_scratches_scale
fabric_weave_scale
```

---

# 96. PHYSICAL PLAUSIBILITY

Los materiales deberán pasar reglas básicas de plausibilidad:

```text
metallic consistency
roughness consistency
normal consistency
scale consistency
```

---

# 97. MATERIAL IDENTITY

Cada material deberá mantener una identidad semántica independiente de su apariencia final.

---

# 98. STYLE PROFILE

Deberá existir:

```text
MaterialStyleProfile
```

para controlar:

```text
color_palette
roughness_range
metallic_range
contrast
detail_density
wear_level
emissive_level
```

---

# 99. STYLE ARCHETYPES

Mínimo:

```text
REALISTIC
SCI_FI
HORROR
MILITARY
INDUSTRIAL
FANTASY
STYLIZED
CARTOON
CYBERPUNK
ALIEN
```

---

# 100. STYLE CONSISTENCY

Un conjunto de assets deberá poder validarse contra un mismo StyleProfile.

---

# 101. MATERIAL BUDGET

Cada material deberá declarar:

```text
texture_count
texture_memory
shader_complexity
instruction_budget
sampler_count
```

---

# 102. SHADER COMPLEXITY

Deberá estimarse:

```text
instruction_count
texture_samples
branches
layers
```

---

# 103. SHADER OPTIMIZATION

Deberá poder realizar:

```text
constant folding
unused parameter removal
layer simplification
texture packing
sample reduction
```

---

# 104. MATERIAL LOD

Deberá existir posibilidad de reducir:

```text
texture_resolution
detail_normal
layer_count
shader_complexity
```

por distancia.

---

# 105. DISTANCE MATERIAL PROFILE

Mínimo:

```text
HERO
NEAR
MID
FAR
```

---

# 106. MATERIAL VALIDATION

Deberá existir:

```text
MaterialValidator
```

---

# 107. TEXTURE VALIDATION

Deberá existir:

```text
TextureValidator
```

---

# 108. UV VALIDATION

Deberá existir:

```text
UVValidator
```

---

# 109. PBR VALIDATION

Deberá existir:

```text
PBRValidator
```

---

# 110. VISUAL VALIDATION

Deberá existir:

```text
MaterialVisualValidator
```

---

# 111. VISUAL TEST SCENES

Deberán existir escenas estándar:

```text
MAT_STUDIO
MAT_OUTDOOR
MAT_LOW_LIGHT
MAT_HIGH_CONTRAST
MAT_NEON
MAT_METAL
MAT_ORGANIC
```

---

# 112. MATERIAL PREVIEW

Cada material deberá poder renderizarse bajo condiciones controladas.

---

# 113. MATERIAL COMPARISON

Deberá poder compararse:

```text
source
generated
optimized
exported
```

---

# 114. TEXTURE PREVIEW

Deberá poder inspeccionarse cada canal individualmente.

---

# 115. CHANNEL QA

Mínimo:

```text
BASE_COLOR
METALLIC
ROUGHNESS
NORMAL
AO
EMISSIVE
MASK
```

---

# 116. NORMAL QA

Deberá renderizarse una esfera y/o superficie de referencia para detectar inversión de normales.

---

# 117. ROUGHNESS QA

Deberá comprobarse el comportamiento visual sobre una esfera estándar.

---

# 118. METALLIC QA

Deberá verificarse diferencia entre:

```text
metal
dielectric
```

---

# 119. COLOR QA

Deberá verificarse consistencia de color management.

---

# 120. MATERIAL MEMORY QA

Deberá calcularse:

```text
raw_texture_memory
compressed_memory_estimate
streaming_memory
total_material_memory
```

---

# 121. MATERIAL PERFORMANCE GATE

Un material deberá fallar si supera el presupuesto definido para su categoría.

---

# 122. TEXTURE MEMORY GATE

Las texturas deberán respetar el presupuesto de memoria del asset.

---

# 123. SAMPLER GATE

El número de samplers deberá estar dentro del límite del target.

---

# 124. MATERIAL INSTANCE GATE

Las instancias no deberán introducir dependencias inválidas.

---

# 125. DETERMINISM

Deberá ser determinista:

```text
UV generation
texture generation
baking configuration
material graph
channel packing
material instance generation
```

---

# 126. SEED REGISTRATION

Toda textura procedural deberá registrar:

```text
seed
generator
parameters
version
```

---

# 127. MATERIAL HASH

Deberá generarse:

```text
material_hash
```

---

# 128. TEXTURE HASH

Cada textura deberá generar:

```text
texture_hash
```

---

# 129. UV HASH

Cada UVSet deberá generar:

```text
uv_hash
```

---

# 130. SHADER HASH

Cada MaterialGraph deberá generar:

```text
shader_graph_hash
```

---

# 131. MATERIAL BUILD HASH

Deberá calcularse:

```text
material_build_hash
```

a partir de:

```text
uv_hash
texture_hashes
material_hash
shader_graph_hash
style_profile_hash
```

---

# 132. ASSET MATERIAL DEPENDENCY GRAPH

Deberá existir:

```text
Asset
 ├── UV
 ├── Material
 │    ├── Shader
 │    ├── Textures
 │    ├── Masks
 │    └── Parameters
 ├── MaterialInstances
 └── Decals
```

---

# 133. FAILURE CODES

Mínimo:

```text
UV_GENERATION_FAILURE
UV_OVERLAP
UV_DISTORTION
UV_DENSITY_INVALID
UV_PADDING_INVALID
UDIM_INVALID
TRIM_INVALID
MATERIAL_INVALID
MATERIAL_GRAPH_INVALID
TEXTURE_INVALID
TEXTURE_COLORSPACE_INVALID
TEXTURE_FORMAT_INVALID
TEXTURE_MEMORY_EXCEEDED
TEXTURE_COMPRESSION_FAILURE
NORMAL_MAP_INVALID
PBR_INVALID
METALLIC_INVALID
ROUGHNESS_INVALID
EMISSIVE_INVALID
BAKE_FAILURE
BAKE_RAY_MISS
BAKE_CAGE_FAILURE
DECAL_INVALID
SHADER_COMPLEXITY_EXCEEDED
SAMPLER_LIMIT_EXCEEDED
MATERIAL_MEMORY_EXCEEDED
INSTANCE_INVALID
ROUNDTRIP_MATERIAL_FAILURE
```

---

# 134. TEST SUITE

La fase deberá contener como mínimo:

```text
UNIT TESTS
UV TESTS
TEXTURE TESTS
MATERIAL TESTS
PBR TESTS
BAKE TESTS
PROCEDURAL TESTS
DECAL TESTS
OPTIMIZATION TESTS
VISUAL TESTS
EXPORT TESTS
ROUNDTRIP TESTS
DETERMINISM TESTS
GOLDEN MATERIAL TESTS
END_TO_END TESTS
```

---

# 135. UNIT TESTS

Mínimo:

```text
test_material_definition
test_material_layer
test_material_parameter
test_material_graph
test_texture_definition
test_texture_set
test_uv_definition
test_uv_island
test_surface_definition
test_material_style_profile
test_texture_profile
test_bake_definition
test_bake_profile
test_material_hash
test_texture_hash
test_uv_hash
test_shader_hash
test_material_build_hash
```

---

# 136. UV TESTS

Mínimo:

```text
test_uv_generation
test_uv_overlap_detection
test_intentional_overlap
test_uv_distortion
test_uv_density
test_uv_padding
test_uv_island_orientation
test_uv_channel_assignment
test_udim_assignment
test_udim_missing_tile
test_trim_sheet
test_trim_alignment
```

---

# 137. TEXTURE TESTS

Mínimo:

```text
test_base_color
test_metallic
test_roughness
test_normal
test_ao
test_emissive
test_mask
test_colorspace
test_srgb
test_non_color_data
test_resolution
test_mipmap
test_texture_packing
test_texture_compression
test_texture_streaming
```

---

# 138. PBR TESTS

Mínimo:

```text
test_metallic_range
test_roughness_range
test_base_color_range
test_normal_range
test_emissive_range
test_metal_dielectric_consistency
test_pbr_channel_consistency
test_material_scale
```

---

# 139. BAKE TESTS

Mínimo:

```text
test_normal_bake
test_ao_bake
test_curvature_bake
test_position_bake
test_thickness_bake
test_id_bake
test_high_to_low_bake
test_bake_cage
test_bake_ray_miss
test_bake_determinism
```

---

# 140. PROCEDURAL TESTS

Mínimo:

```text
test_noise_generator
test_voronoi_generator
test_fractal_generator
test_wear_generator
test_scratch_generator
test_dirt_generator
test_rust_generator
test_corrosion_generator
test_procedural_seed
test_procedural_determinism
```

---

# 141. MATERIAL LAYER TESTS

Mínimo:

```text
test_base_layer
test_dirt_layer
test_scratch_layer
test_rust_layer
test_damage_layer
test_wetness_layer
test_emissive_layer
test_layer_mask
test_layer_order
test_layer_blending
```

---

# 142. DECAL TESTS

Mínimo:

```text
test_decal_definition
test_decal_projection
test_decal_socket
test_decal_surface
test_decal_overlap
test_decal_z_fighting
```

---

# 143. OPTIMIZATION TESTS

Mínimo:

```text
test_texture_resize
test_channel_packing
test_unused_parameter_removal
test_shader_simplification
test_layer_reduction
test_sampler_reduction
test_material_lod
```

---

# 144. FAILURE TESTS

Mínimo:

```text
test_invalid_uv
test_uv_overlap_failure
test_uv_density_failure
test_invalid_texture
test_wrong_colorspace
test_wrong_normal_format
test_invalid_metallic
test_invalid_roughness
test_invalid_emissive
test_bake_failure
test_bake_cage_failure
test_missing_texture
test_missing_material
test_invalid_material_graph
test_sampler_overflow
test_shader_budget_overflow
test_texture_memory_overflow
test_invalid_material_instance
test_invalid_udim
test_invalid_decal
```

---

# 145. VISUAL TESTS

Deberán existir pruebas para:

```text
test_material_preview
test_metal_preview
test_skin_preview
test_fabric_preview
test_glass_preview
test_concrete_preview
test_organic_preview
test_emissive_preview
test_normal_preview
test_roughness_preview
test_texture_channel_preview
test_material_comparison
```

---

# 146. EXPORT TESTS

Mínimo:

```text
test_material_export
test_texture_export
test_material_instance_export
test_parameter_export
test_uv_export
test_texture_reference_export
test_decal_export
```

---

# 147. ROUND-TRIP TESTS

Mínimo:

```text
test_uv_roundtrip
test_material_roundtrip
test_texture_roundtrip
test_normal_roundtrip
test_parameter_roundtrip
test_material_instance_roundtrip
test_full_material_roundtrip
```

---

# 148. DETERMINISM TESTS

Mínimo:

```text
test_uv_determinism
test_texture_determinism
test_bake_determinism
test_material_graph_determinism
test_material_instance_determinism
test_export_determinism
test_material_hash_determinism
```

---

# 149. GOLDEN MATERIAL LIBRARY

Deberán existir como mínimo:

```text
GOLDEN_SKIN
GOLDEN_METAL
GOLDEN_PAINTED_METAL
GOLDEN_FABRIC
GOLDEN_LEATHER
GOLDEN_CONCRETE
GOLDEN_GLASS
GOLDEN_ORGANIC
GOLDEN_EMISSIVE
GOLDEN_TECHNICAL
```

---

# 150. GOLDEN TEXTURE LIBRARY

Deberán existir referencias para:

```text
BASE_COLOR
ROUGHNESS
METALLIC
NORMAL
AO
CURVATURE
EMISSIVE
MASK
```

---

# 151. MATERIAL CONSISTENCY TEST

Un conjunto de materiales deberá poder validarse simultáneamente para:

```text
texel_density
color_space
roughness
scale
style
memory
shader_complexity
```

---

# 152. CHARACTER MATERIAL INTEGRATION TEST

Deberá ejecutarse:

```text
CHARACTER
↓
UV
↓
SKIN MATERIAL
↓
ARMOR MATERIAL
↓
CLOTH MATERIAL
↓
EYE MATERIAL
↓
EMISSIVE
↓
MATERIAL INSTANCES
↓
UNREAL PACKAGE
```

---

# 153. WEAPON MATERIAL INTEGRATION TEST

Deberá ejecutarse:

```text
WEAPON
↓
UV
↓
METAL
↓
PAINT
↓
RUBBER
↓
WEAR
↓
DECALS
↓
EMISSIVE
↓
UNREAL PACKAGE
```

---

# 154. ENVIRONMENT MATERIAL INTEGRATION TEST

Deberá ejecutarse:

```text
ARCHITECTURE
↓
UV
↓
CONCRETE
↓
METAL
↓
DIRT
↓
DAMAGE
↓
DECALS
↓
UNREAL PACKAGE
```

---

# 155. END-TO-END TEST

Deberá ejecutar:

```text
GENERATED MESH
↓
SURFACE CLASSIFICATION
↓
UV GENERATION
↓
UV QA
↓
MATERIAL GENERATION
↓
TEXTURE GENERATION
↓
BAKING
↓
PBR QA
↓
OPTIMIZATION
↓
MATERIAL INSTANCE
↓
UNREAL MATERIAL PACKAGE
↓
ROUNDTRIP
↓
FINAL VALIDATION
```

---

# 156. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
18 UNIT TESTS
12 UV TESTS
15 TEXTURE TESTS
8 PBR TESTS
10 BAKE TESTS
10 PROCEDURAL TESTS
10 MATERIAL-LAYER TESTS
6 DECAL TESTS
7 OPTIMIZATION TESTS
18 FAILURE TESTS
12 VISUAL TESTS
7 EXPORT TESTS
7 ROUNDTRIP TESTS
7 DETERMINISM TESTS
10 GOLDEN MATERIAL TESTS
3 INTEGRATION TESTS
1 END_TO_END TEST
```

Total mínimo:

```text
161 TESTS
```

---

# 157. QUALITY GATES

La fase deberá tener:

```text
UV_GATE
TEXTURE_GATE
PBR_GATE
BAKE_GATE
MATERIAL_GATE
SHADER_GATE
MEMORY_GATE
VISUAL_GATE
EXPORT_GATE
ROUNDTRIP_GATE
DETERMINISM_GATE
```

---

# 158. UV GATE

Debe cumplirse:

```text
NO_UNAUTHORIZED_OVERLAP
VALID_DENSITY
VALID_PADDING
ACCEPTABLE_DISTORTION
VALID_CHANNELS
```

---

# 159. TEXTURE GATE

Debe cumplirse:

```text
VALID_RESOLUTION
VALID_FORMAT
VALID_COLORSPACE
VALID_MIPMAPS
VALID_MEMORY
```

---

# 160. PBR GATE

Debe cumplirse:

```text
VALID_BASE_COLOR
VALID_METALLIC
VALID_ROUGHNESS
VALID_NORMAL
VALID_EMISSIVE
```

---

# 161. BAKE GATE

Debe cumplirse:

```text
NO_CRITICAL_RAY_MISS
NO_CRITICAL_PROJECTION_ERROR
VALID_CAGE
VALID_OUTPUT
```

---

# 162. MATERIAL GATE

Debe cumplirse:

```text
VALID_GRAPH
VALID_PARAMETERS
VALID_TEXTURE_REFERENCES
VALID_LAYERS
```

---

# 163. SHADER GATE

Debe cumplirse:

```text
WITHIN_INSTRUCTION_BUDGET
WITHIN_SAMPLER_BUDGET
NO_UNUSED_EXPENSIVE_OPERATIONS
```

---

# 164. MEMORY GATE

Debe cumplirse:

```text
TEXTURE_MEMORY <= PROFILE_LIMIT
MATERIAL_MEMORY <= PROFILE_LIMIT
```

---

# 165. VISUAL GATE

El material deberá ser visualmente válido bajo las escenas de referencia.

---

# 166. EXPORT GATE

Deberá producir:

```text
material
textures
instances
metadata
dependencies
```

sin referencias rotas.

---

# 167. ROUNDTRIP GATE

Deberá cumplirse:

```text
SOURCE UV ≈ EXPORTED UV
SOURCE MATERIAL ≈ EXPORTED MATERIAL
SOURCE PARAMETERS ≈ EXPORTED PARAMETERS
```

dentro de tolerancias.

---

# 168. NO SILENT FALLBACK

Toda sustitución deberá registrar:

```text
requested_strategy
actual_strategy
reason
impact
```

---

# 169. NO MISSING TEXTURE RULE

Un material final no podrá contener referencias a texturas inexistentes.

---

# 170. NO ORPHAN TEXTURE RULE

Las texturas generadas que no estén referenciadas deberán marcarse como:

```text
ORPHAN
```

y entrar en limpieza controlada.

---

# 171. NO INVALID COLORSPACE RULE

Cada textura deberá tener explícitamente declarado:

```text
color_space
data_type
```

---

# 172. NO HIDDEN MATERIAL PARAMETER RULE

Todo parámetro expuesto deberá formar parte de:

```text
MaterialDefinition
```

o:

```text
MaterialInstanceDefinition
```

---

# 173. NO UNCONTROLLED RANDOMNESS

Toda generación procedural deberá ser reproducible mediante seed.

---

# 174. VERSIONING

Deberán versionarse:

```text
MaterialGraphVersion
TextureGeneratorVersion
BakeProfileVersion
UVStrategyVersion
```

---

# 175. CACHE

Deberá existir cache para:

```text
UV
bakes
textures
material graphs
```

utilizando hashes deterministas.

---

# 176. CACHE INVALIDATION

Un cambio en:

```text
mesh
UV
parameters
seed
generator_version
bake_profile
```

deberá invalidar únicamente los artefactos afectados.

---

# 177. INCREMENTAL BUILD

El pipeline deberá evitar regenerar recursos no modificados.

---

# 178. MATERIAL PACKAGE

Cada material final deberá poder empaquetarse como:

```text
MaterialPackage
```

conteniendo:

```text
manifest
material_definition
shader_definition
textures
uv_requirements
instances
metadata
validation_report
hashes
```

---

# 179. MANIFEST

El manifest deberá declarar:

```text
asset_id
material_id
version
dependencies
files
hashes
target
validation_status
```

---

# 180. FINAL ACCEPTANCE CRITERIA

UAF-81.43 será considerada completa únicamente cuando:

```text
UV SYSTEM IMPLEMENTED
UV VALIDATION IMPLEMENTED
TEXEL DENSITY IMPLEMENTED
UDIM SUPPORT IMPLEMENTED
TRIM SUPPORT IMPLEMENTED
MATERIAL GRAPH IMPLEMENTED
PBR SYSTEM IMPLEMENTED
PROCEDURAL TEXTURE SYSTEM IMPLEMENTED
MATERIAL LAYERS IMPLEMENTED
BAKING SYSTEM IMPLEMENTED
TEXTURE PACKING IMPLEMENTED
TEXTURE COMPRESSION PROFILES IMPLEMENTED
MIP SYSTEM IMPLEMENTED
TEXTURE STREAMING METADATA IMPLEMENTED
MATERIAL INSTANCE SYSTEM IMPLEMENTED
DECAL SYSTEM IMPLEMENTED
STYLE PROFILE SYSTEM IMPLEMENTED
MATERIAL OPTIMIZATION IMPLEMENTED
MATERIAL MEMORY ANALYSIS IMPLEMENTED
SHADER COMPLEXITY ANALYSIS IMPLEMENTED
VISUAL QA IMPLEMENTED
EXPORT IMPLEMENTED
ROUNDTRIP IMPLEMENTED
DETERMINISM IMPLEMENTED
CACHE IMPLEMENTED
INCREMENTAL BUILD IMPLEMENTED
GOLDEN MATERIAL LIBRARY IMPLEMENTED
ALL REQUIRED TESTS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 181. NEXT PHASE

```text
UAF-81.44 — ENVIRONMENT, MODULAR KIT, PROCEDURAL BLOCKOUT, TERRAIN, WORLD BUILDING & UNREAL MAP AUTHORING SYSTEM
```

La siguiente fase deberá ampliar el mismo concepto desde el asset individual hacia el **mundo completo**:

```text
MODULAR BUILDING BLOCKS
↓
WALLS
DOORS
FLOORS
STAIRS
CEILINGS
PIPES
COVER
PROPS
VEGETATION
ROADS
TERRAIN
LANDSCAPE
BIOMES
LIGHTING
NAVIGATION
GAMEPLAY VOLUMES
↓
PROCEDURAL WORLD ASSEMBLY
↓
UNREAL LEVEL
↓
WORLD PARTITION
↓
HLOD
↓
NAVIGATION
↓
COLLISION
↓
STREAMING
↓
WORLD QA
```

La intención es que UAF-81.44 sea el punto donde AOE deje de pensar únicamente en **“generar assets”** y pase a poder construir **espacios jugables completos y reproducibles para Unreal Engine**.
