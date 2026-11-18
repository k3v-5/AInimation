# UAF-81.18 — PROCEDURAL TEXTURE, MATERIAL & SURFACE FABRICATION SYSTEM

## UAF-81.18-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN DE TEXTURAS, MATERIALES Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.18 — Procedural Texture, Material & Surface Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.17  
**Next Phase:** UAF-81.19  

---

# 1. PURPOSE

UAF-81.18 define el sistema responsable de transformar geometría, información semántica y perfiles visuales en superficies completas de producción.

El sistema deberá poder fabricar:

```text
SURFACE
├── UV
├── TEXTURES
├── MATERIAL
├── MATERIAL INSTANCES
├── MASKS
├── DECALS
├── SURFACE DETAILS
├── WEATHERING
├── DAMAGE
├── VARIANTS
├── LODS
└── UNREAL MATERIAL PACKAGE
```

---

# 2. PRIMARY OBJECTIVE

La salida no deberá ser simplemente una textura.

Deberá producir una representación completa:

```text
GEOMETRY
→ UV
→ SURFACE DATA
→ TEXTURES
→ MATERIAL GRAPH
→ MATERIAL INSTANCE
→ VALIDATION
→ OPTIMIZATION
→ UNREAL PACKAGE
```

---

# 3. SURFACE DEFINITION

Deberá existir:

```text
SurfaceDefinition
```

con mínimo:

```text
surface_id
surface_type
material_family
resolution_profile
texel_density
uv_profile
texture_profile
material_profile
weathering_profile
target_profile
```

---

# 4. SURFACE TYPES

Mínimo:

```text
SKIN
FLESH
METAL
ARMOR
FABRIC
LEATHER
RUBBER
PLASTIC
GLASS
CERAMIC
STONE
CONCRETE
WOOD
VEGETATION
SOIL
SAND
SNOW
ICE
WATER
ALIEN
ORGANIC
TECHNOLOGY
HOLOGRAPHIC
CUSTOM
```

---

# 5. MATERIAL FAMILY

Cada superficie deberá pertenecer a una familia material.

Ejemplo:

```text
METAL
├── STEEL
├── ALUMINUM
├── CHROME
├── TITANIUM
├── PAINTED_METAL
├── RUSTED_METAL
└── FUTURISTIC_ALLOY
```

---

# 6. MATERIAL PROFILE

Deberá existir:

```text
MaterialProfile
```

---

# 7. MATERIAL PROFILE PARAMETERS

Mínimo:

```text
base_color
metallic
roughness
specular
normal_strength
emissive
opacity
refraction
subsurface
```

cuando correspondan.

---

# 8. PBR STANDARD

El sistema deberá utilizar un modelo PBR compatible con Unreal Engine.

---

# 9. BASE COLOR

Deberá soportarse:

```text
RGB
RGBA
```

---

# 10. METALLIC

Deberá generarse como:

```text
0.0 – 1.0
```

salvo perfiles especiales.

---

# 11. ROUGHNESS

Deberá generarse como:

```text
0.0 – 1.0
```

---

# 12. NORMAL

Las normales deberán poder generarse desde:

```text
height
high_poly
procedural_noise
sculpt_data
```

---

# 13. AMBIENT OCCLUSION

Deberá poder derivarse de geometría o mapas auxiliares.

---

# 14. HEIGHT

Deberá soportarse como:

```text
height_map
displacement_map
parallax_data
```

según target.

---

# 15. EMISSIVE

Deberá existir control explícito de intensidad y color.

---

# 16. EMISSIVE SAFETY

El sistema deberá respetar los límites visuales establecidos por el TargetProfile.

No deberá producir valores excesivos de forma accidental.

---

# 17. OPACITY

Deberán soportarse:

```text
OPAQUE
MASKED
TRANSLUCENT
```

cuando el target lo permita.

---

# 18. SUBSURFACE

Deberá existir soporte para materiales orgánicos.

---

# 19. MATERIAL MODE

Deberán existir perfiles:

```text
DEFAULT_LIT
SUBSURFACE
TRANSLUCENT
UNLIT
CLEAR_COAT
HAIR
EYE
CUSTOM
```

según compatibilidad con Unreal.

---

# 20. TEXTURE FABRICATOR

Deberá existir:

```text
TextureFabricator
```

---

# 21. TEXTURE DEFINITION

Deberá existir:

```text
TextureDefinition
```

con:

```text
texture_id
channel
resolution
format
bit_depth
color_space
compression
source
generator
```

---

# 22. STANDARD CHANNELS

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
```

---

# 23. CHANNEL PACKING

Deberá soportarse packing:

```text
R = AO
G = ROUGHNESS
B = METALLIC
A = CUSTOM_MASK
```

cuando el TargetProfile lo permita.

---

# 24. PACKING PROFILE

Deberá existir:

```text
TexturePackingProfile
```

---

# 25. PACKING VALIDATION

Deberá comprobar:

```text
channel_range
channel_meaning
alpha_usage
color_space
compression
```

---

# 26. COLOR SPACE

Deberá declararse explícitamente:

```text
SRGB
LINEAR
```

para cada textura.

---

# 27. COLOR SPACE RULE

Los mapas de datos no deberán marcarse accidentalmente como sRGB.

---

# 28. RESOLUTION PROFILE

Deberá existir:

```text
ResolutionProfile
```

---

# 29. RESOLUTION LEVELS

Mínimo:

```text
256
512
1024
2048
4096
8192
```

cuando el hardware y target lo permitan.

---

# 30. ADAPTIVE RESOLUTION

La resolución deberá poder determinarse automáticamente mediante:

```text
screen_importance
asset_size
texel_density
camera_distance
material_importance
```

---

# 31. TEXTURE BUDGET

Cada asset deberá declarar:

```text
texture_memory_budget
```

---

# 32. BUDGET ENFORCEMENT

Superar el presupuesto deberá producir:

```text
TEXTURE_BUDGET_EXCEEDED
```

---

# 33. AUTO DOWNGRADE

El sistema podrá reducir resolución automáticamente si está autorizado.

---

# 34. DOWNSCALE REPORT

Toda reducción deberá registrarse.

---

# 35. TEXEL DENSITY

Deberá existir:

```text
TexelDensityProfile
```

---

# 36. TEXEL DENSITY UNITS

El sistema deberá definir unidades explícitas:

```text
pixels_per_meter
```

---

# 37. TEXEL DENSITY VALIDATION

Deberá detectar:

```text
under_density
over_density
density_inconsistency
```

---

# 38. UV SYSTEM

Deberá existir:

```text
UVFabricator
```

---

# 39. UV CHANNELS

Deberán soportarse múltiples canales.

Mínimo:

```text
UV0
UV1
```

---

# 40. UV0

UV0 deberá estar destinada a texturización salvo configuración distinta.

---

# 41. UV1

UV1 podrá utilizarse para lightmaps cuando el pipeline lo requiera.

---

# 42. UV GENERATION

Deberán soportarse estrategias:

```text
SMART_PROJECT
BOX
CYLINDER
PLANAR
ANGLE_BASED
SEAM_BASED
UDIM
CUSTOM
```

---

# 43. SEAM GENERATION

Deberá existir generación automática de seams.

---

# 44. SEAM CRITERIA

Los seams podrán basarse en:

```text
curvature
angle
material_boundary
anatomical_boundary
hard_surface_boundary
hidden_surface
```

---

# 45. UV DISTORTION

Deberá medirse:

```text
area_distortion
angular_distortion
stretch
```

---

# 46. UV OVERLAP

Deberá detectar overlaps cuando no estén permitidos.

---

# 47. MIRRORED UV

Deberá soportarse UV simétrica cuando el perfil lo permita.

---

# 48. UNIQUE UV

Cuando se requieran decals o damage únicos, deberá poder desactivarse el mirroring.

---

# 49. UV PADDING

El padding deberá depender de:

```text
resolution
mipmap_count
compression
target
```

---

# 50. UV PACKING

Deberá existir:

```text
UVPackProfile
```

---

# 51. UDIM

Deberá existir soporte para UDIM.

---

# 52. UDIM POLICY

El número de tiles deberá limitarse mediante:

```text
max_udim_tiles
memory_budget
asset_importance
```

---

# 53. UDIM NAMING

Los tiles deberán seguir una convención determinista.

---

# 54. TILE VALIDATION

Deberá detectar:

```text
missing_tile
duplicate_tile
empty_tile
invalid_numbering
```

---

# 55. MATERIAL GENERATION

Deberá existir:

```text
MaterialFabricator
```

---

# 56. MATERIAL GRAPH

Los materiales deberán construirse como grafos explícitos.

---

# 57. MATERIAL NODE STANDARDIZATION

Los nodos deberán tener:

```text
stable_name
stable_role
parameters
inputs
outputs
```

---

# 58. MATERIAL PARAMETERS

Los parámetros expuestos deberán estar separados de los valores internos.

---

# 59. MATERIAL INSTANCE

Deberá existir:

```text
MaterialInstanceFabricator
```

---

# 60. INSTANCE PARAMETERS

Deberán poder modificarse sin duplicar el material base:

```text
base_color
roughness
metallic
normal_strength
emissive_color
emissive_intensity
detail_strength
```

---

# 61. MASTER MATERIAL

Deberán existir master materials reutilizables.

Mínimo:

```text
MASTER_SURFACE
MASTER_CHARACTER
MASTER_HARD_SURFACE
MASTER_ORGANIC
MASTER_FX
```

---

# 62. MATERIAL INSTANCING RULE

Las variantes deberán utilizar material instances cuando sea posible.

---

# 63. MATERIAL DUPLICATION CONTROL

El sistema deberá evitar crear materiales duplicados semánticamente equivalentes.

---

# 64. MATERIAL GRAPH COMPLEXITY

Deberá existir:

```text
material_instruction_budget
```

---

# 65. MATERIAL COST VALIDATION

Deberá medirse:

```text
instruction_count
texture_sample_count
static_switch_count
```

---

# 66. STATIC SWITCH POLICY

Los static switches deberán utilizarse únicamente cuando reduzcan coste o permitan una variante necesaria.

---

# 67. TEXTURE SAMPLE BUDGET

Cada TargetProfile deberá definir un máximo recomendado.

---

# 68. MATERIAL FUNCTION LIBRARY

Deberá existir una biblioteca reutilizable:

```text
MaterialFunctionLibrary
```

---

# 69. MATERIAL FUNCTIONS

Mínimo:

```text
TRIPLANAR
UV_TILING
DETAIL_NORMAL
WEAR
DIRT
EDGE_WEAR
DAMAGE
MOSS
RUST
WETNESS
SNOW
EMISSION
FRESNEL
PARALLAX
```

cuando sean compatibles.

---

# 70. PROCEDURAL GENERATION

Las texturas deberán poder generarse proceduralmente.

---

# 71. PROCEDURAL SOURCES

Mínimo:

```text
NOISE
VORONOI
MUSGRAVE
CELLULAR
GRADIENT
CURVATURE
POSITION
NORMAL
AO
HEIGHT
RANDOM
```

---

# 72. PROCEDURAL SEED

Toda generación procedural deberá tener seed.

---

# 73. DETERMINISM

La misma seed y configuración deberán producir resultados equivalentes.

---

# 74. NOISE PROFILES

Deberá existir:

```text
NoiseProfile
```

---

# 75. NOISE PARAMETERS

Mínimo:

```text
scale
detail
roughness
lacunarity
distortion
seed
```

---

# 76. SURFACE MICRODETAIL

Deberá existir un sistema independiente para microdetalle.

---

# 77. MACRO DETAIL

Deberá existir soporte para variación macro.

---

# 78. DETAIL LAYERS

Las superficies deberán poder construirse por capas:

```text
BASE
MACRO
MEDIUM
MICRO
WEATHERING
DAMAGE
ACCENT
```

---

# 79. LAYER BLENDING

Cada capa deberá poseer:

```text
mask
strength
blend_mode
priority
```

---

# 80. DAMAGE SYSTEM

Deberá existir:

```text
DamageSurfaceFabricator
```

---

# 81. DAMAGE TYPES

Mínimo:

```text
SCRATCH
DENT
CRACK
BULLET
BURN
CUT
CHIP
IMPACT
CORROSION
```

---

# 82. DAMAGE MASK

El daño deberá generarse como máscara independiente cuando sea posible.

---

# 83. DAMAGE DEPENDENCY

El daño podrá depender de:

```text
position
curvature
material
exposure
gameplay_state
seed
```

---

# 84. WEAR SYSTEM

Deberá existir:

```text
WearFabricator
```

---

# 85. WEAR SOURCES

Mínimo:

```text
edge
contact
height
exposure
curvature
usage
```

---

# 86. DIRT SYSTEM

Deberá existir:

```text
DirtFabricator
```

---

# 87. DIRT ACCUMULATION

Podrá depender de:

```text
gravity
concavity
exposure
surface_orientation
```

---

# 88. RUST SYSTEM

Deberá existir para materiales compatibles.

---

# 89. WETNESS

Deberá existir:

```text
WetnessProfile
```

---

# 90. WETNESS PARAMETERS

Mínimo:

```text
darkening
roughness_reduction
specular_increase
normal_strength
```

---

# 91. SNOW

Deberá existir:

```text
SnowAccumulationProfile
```

---

# 92. SNOW MASK

La acumulación deberá poder derivarse de:

```text
world_normal
surface_angle
exposure
height
```

---

# 93. ORGANIC SURFACE SYSTEM

Deberá existir un pipeline especializado para:

```text
skin
flesh
plant
alien_flesh
organic_growth
```

---

# 94. SKIN MATERIAL

Deberá soportar:

```text
subsurface
roughness_variation
pores
oil
color_variation
micro_normal
```

---

# 95. ROBOT SURFACE SYSTEM

Los robots deberán poder combinar:

```text
paint
metal
chrome
carbon
glass
emissive
scratches
dirt
damage
```

---

# 96. HARD SURFACE SYSTEM

Deberá existir soporte específico para:

```text
panels
bolts
seams
vents
machined_edges
cut_lines
```

---

# 97. TRIM SHEET SYSTEM

Deberá existir:

```text
TrimSheetFabricator
```

---

# 98. TRIM DEFINITIONS

Cada trim deberá declarar:

```text
trim_id
resolution
width
height
material_family
texel_density
```

---

# 99. TILEABLE MATERIAL SYSTEM

Deberá existir:

```text
TileableMaterialFabricator
```

---

# 100. TILE VALIDATION

La textura deberá comprobar continuidad en:

```text
left-right
top-bottom
```

---

# 101. SEAMLESS VALIDATION

El sistema deberá detectar discontinuidades visibles.

---

# 102. DECAL SYSTEM

Deberá existir:

```text
DecalFabricator
```

---

# 103. DECAL TYPES

Mínimo:

```text
LOGO
WARNING
NUMBER
DAMAGE
BLOOD
DIRT
GRAFFITI
TECH
FACTION
CUSTOM
```

---

# 104. DECAL ATLAS

Los decals deberán poder empaquetarse en atlas.

---

# 105. DECAL UNIQUE DATA

Los decals que requieran identidad única deberán conservar UVs o masks únicas.

---

# 106. MATERIAL VARIANTS

Deberá existir:

```text
MaterialVariantFabricator
```

---

# 107. VARIANT PARAMETERS

Mínimo:

```text
color
roughness
wear
damage
emission
dirt
age
faction
```

---

# 108. FACTION MATERIALS

Deberá poder producirse un mismo asset para múltiples facciones.

---

# 109. COLOR PALETTE

Deberá existir:

```text
ColorPaletteProfile
```

---

# 110. PALETTE CONSTRAINTS

Las paletas deberán declarar:

```text
primary
secondary
accent
emissive
neutral
```

---

# 111. STYLE ARCHETYPE

La generación deberá consumir:

```text
StyleArchetype
```

---

# 112. STYLE PARAMETERS

Mínimo:

```text
contrast
saturation
roughness_bias
metallic_bias
emission_bias
detail_density
damage_density
```

---

# 113. VISUAL CONSISTENCY

Los materiales del mismo asset deberán mantener coherencia estilística.

---

# 114. ASSET-LEVEL CONSISTENCY

Personajes, armas y props de una misma colección deberán poder compartir:

```text
palette
roughness_language
damage_language
material_language
```

---

# 115. MATERIAL SEMANTICS

Cada material deberá declarar su significado físico.

Ejemplo:

```text
semantic_material = painted_steel
```

---

# 116. SEMANTIC MATERIAL LIBRARY

Deberá existir:

```text
SemanticMaterialLibrary
```

---

# 117. LIBRARY MATERIALS

Mínimo:

```text
steel
painted_steel
chrome
rubber
glass
skin
fabric
leather
concrete
stone
wood
mud
snow
ice
```

---

# 118. MATERIAL REUSE

El mismo material semántico deberá poder reutilizarse entre assets.

---

# 119. MATERIAL OVERRIDES

Los assets podrán aplicar overrides controlados.

---

# 120. TEXTURE SOURCE TYPES

Mínimo:

```text
PROCEDURAL
BAKED
IMPORTED
GENERATED
HYBRID
```

---

# 121. BAKE SYSTEM

Deberá existir:

```text
TextureBakePipeline
```

---

# 122. BAKE INPUTS

Podrá utilizar:

```text
high_poly
low_poly
cage
curvature
ao
normal
position
thickness
```

---

# 123. BAKE VALIDATION

Deberá detectar:

```text
ray_failure
projection_error
cage_error
seam_artifact
normal_error
```

---

# 124. NORMAL BAKING

Deberá soportarse:

```text
TANGENT_SPACE
OBJECT_SPACE
```

según target.

---

# 125. TANGENT STANDARD

El método de tangentes deberá ser compatible con Unreal.

---

# 126. NORMAL GREEN CHANNEL

El sistema deberá declarar explícitamente la convención utilizada.

---

# 127. TEXTURE FILTERING

Deberá declararse:

```text
filter_mode
mipmap_policy
anisotropy
```

cuando aplique.

---

# 128. MIPMAP POLICY

Las texturas deberán generar mipmaps salvo excepción explícita.

---

# 129. VIRTUAL TEXTURE

Deberá soportarse Virtual Texturing cuando el target lo requiera.

---

# 130. VIRTUAL TEXTURE VALIDATION

Deberá comprobarse compatibilidad con:

```text
resolution
material
streaming
memory
```

---

# 131. TEXTURE STREAMING

Cada asset deberá poder declarar prioridad de streaming.

---

# 132. STREAMING PRIORITY

Mínimo:

```text
CRITICAL
HIGH
NORMAL
LOW
```

---

# 133. TEXTURE MEMORY ANALYSIS

Deberá calcularse:

```text
raw_memory
compressed_memory
streaming_memory
peak_memory
```

---

# 134. COMPRESSION

Deberá existir un CompressionProfile.

---

# 135. COMPRESSION SELECTION

La compresión deberá depender del canal.

Ejemplo:

```text
COLOR → COLOR_COMPRESSION
NORMAL → NORMAL_COMPRESSION
MASK → DATA_COMPRESSION
```

---

# 136. ALPHA HANDLING

El uso de alpha deberá declararse explícitamente.

---

# 137. TEXTURE FORMAT

El formato deberá depender de:

```text
target
platform
channel
quality
memory_budget
```

---

# 138. PLATFORM PROFILES

Deberán existir perfiles para diferentes plataformas.

Mínimo:

```text
PC
CONSOLE
MOBILE
HIGH_END
LOW_END
```

---

# 139. PLATFORM VARIANTS

Un asset podrá producir diferentes paquetes de texturas por plataforma.

---

# 140. MATERIAL LOD

Deberá existir simplificación de materiales por distancia.

---

# 141. MATERIAL LOD RULES

Podrán reducirse:

```text
detail_normal
macro_detail
texture_resolution
layer_count
```

---

# 142. SHADER COMPLEXITY

Deberá existir validación del coste de shader.

---

# 143. SHADER COMPLEXITY THRESHOLDS

Los límites deberán pertenecer al TargetProfile.

---

# 144. MATERIAL INSTANCE PARAMETER LIMIT

Los parámetros innecesarios no deberán exponerse.

---

# 145. GLOBAL MATERIAL PARAMETERS

Deberá soportarse una colección de parámetros globales.

---

# 146. GLOBAL PARAMETERS

Mínimo:

```text
global_wetness
global_dirt
global_damage
global_emission
global_time
```

cuando el proyecto lo permita.

---

# 147. WORLD-DRIVEN MATERIALS

Los materiales podrán reaccionar a:

```text
world_position
weather
time
biome
faction
game_state
```

---

# 148. DYNAMIC MATERIAL POLICY

Los parámetros dinámicos deberán utilizar Material Parameter Collections o mecanismos equivalentes cuando reduzcan duplicación.

---

# 149. MATERIAL INSTANCE NAMING

Deberá existir una convención determinista.

---

# 150. TEXTURE NAMING

Mínimo:

```text
T_<Asset>_<Surface>_<Channel>
```

---

# 151. MATERIAL NAMING

Mínimo:

```text
M_<Family>_<Variant>
MI_<Asset>_<Variant>
```

---

# 152. UV NAMING

Los canales deberán estar documentados en metadata.

---

# 153. ASSET MATERIAL MANIFEST

Deberá existir:

```text
MaterialManifest
```

---

# 154. MANIFEST CONTENT

Mínimo:

```text
materials
textures
uv_sets
udim_tiles
resolution
memory
compression
dependencies
```

---

# 155. MATERIAL DEPENDENCY GRAPH

El sistema deberá registrar:

```text
Material
→ MaterialFunctions
→ Textures
→ Parameters
```

---

# 156. TEXTURE DEPENDENCY GRAPH

Deberá registrar:

```text
Texture
→ Source
→ Generator
→ Seed
→ Profile
```

---

# 157. INCREMENTAL BUILD

Modificar roughness no deberá regenerar albedo si no existe dependencia.

---

# 158. DEPENDENCY INVALIDATION

Los cambios deberán invalidar únicamente nodos dependientes.

---

# 159. CACHE

Deberá existir:

```text
TextureCache
MaterialCache
UVCache
BakeCache
```

---

# 160. CACHE KEY

La clave deberá incluir:

```text
source_hash
profile_hash
generator_version
seed
target_profile
```

---

# 161. DETERMINISM

La misma configuración deberá producir la misma salida.

---

# 162. RANDOMIZATION

Toda aleatoriedad deberá ser controlada mediante seed.

---

# 163. RANDOM VARIANT GENERATION

Deberá poder generarse:

```text
variant_001
variant_002
variant_003
...
```

manteniendo restricciones del material.

---

# 164. VARIANT UNIQUENESS

Las variantes deberán superar un umbral configurable de diferencia visual.

---

# 165. VISUAL SIMILARITY

Deberá existir una métrica para evitar variantes prácticamente idénticas.

---

# 166. MATERIAL VALIDATOR

Deberá existir:

```text
MaterialValidator
```

---

# 167. TEXTURE VALIDATOR

Deberá existir:

```text
TextureValidator
```

---

# 168. UV VALIDATOR

Deberá existir:

```text
UVValidator
```

---

# 169. VALIDATION RULES

Mínimo:

```text
resolution
color_space
format
compression
uv_overlap
uv_distortion
texel_density
channel_range
missing_texture
broken_reference
```

---

# 170. MATERIAL VALIDATION

Deberá comprobar:

```text
master_material
parameters
texture_references
shader_cost
unsupported_nodes
```

---

# 171. UNREAL VALIDATION

Deberá comprobar:

```text
material_domain
blend_mode
shading_model
texture_import
virtual_texture
parameter_types
```

---

# 172. VISUAL QA

Deberán generarse automáticamente:

```text
ALBEDO_PREVIEW
NORMAL_PREVIEW
ROUGHNESS_PREVIEW
METALLIC_PREVIEW
MATERIAL_PREVIEW
WIREFRAME_UV_PREVIEW
```

---

# 173. MATERIAL PREVIEW

Cada material deberá poder renderizarse sobre un objeto de referencia.

---

# 174. REFERENCE OBJECTS

Mínimo:

```text
SPHERE
PLANE
HARD_SURFACE
CHARACTER_PART
```

---

# 175. LIGHTING QA

Los materiales deberán probarse bajo al menos:

```text
NEUTRAL
HIGH_CONTRAST
DARK
OUTDOOR
```

---

# 176. MATERIAL ARTISTIC VALIDATION

Deberá poder detectarse:

```text
over_uniformity
excessive_noise
over_saturation
incorrect_roughness
flat_surface
repetition
visible_tiling
```

---

# 177. REPETITION DETECTION

Los materiales tileables deberán analizarse para detectar patrones excesivamente evidentes.

---

# 178. DETAIL DENSITY

Deberá existir un límite de frecuencia visual.

---

# 179. NOISE CONTROL

El ruido procedural no deberá utilizarse como sustituto de detalle artístico significativo.

---

# 180. PHYSICAL PLAUSIBILITY

Los valores PBR deberán mantenerse dentro de rangos físicamente razonables salvo perfiles estilizados explícitos.

---

# 181. STYLIZED MATERIALS

Deberán existir perfiles no fotorrealistas.

---

# 182. STYLIZATION PROFILE

Mínimo:

```text
REALISTIC
CINEMATIC
STYLIZED
SCI_FI
HORROR
CARTOON
CUSTOM
```

---

# 183. CHARACTER MATERIAL INTEGRATION

UAF-81.18 deberá integrarse con UAF-81.17.

---

# 184. SKIN MATERIAL INTEGRATION

Los personajes deberán poder consumir materiales de:

```text
skin
hair
eyes
teeth
clothing
armor
```

---

# 185. MATERIAL ASSIGNMENT

Cada submesh deberá declarar su material semántico.

---

# 186. MATERIAL SLOT VALIDATION

No deberán existir slots vacíos sin justificación.

---

# 187. MATERIAL SLOT OPTIMIZATION

Slots equivalentes deberán poder consolidarse.

---

# 188. ATLAS SYSTEM

Deberá existir:

```text
TextureAtlasFabricator
```

---

# 189. ATLAS USE CASES

Mínimo:

```text
decals
small_props
foliage
characters
modular_assets
```

---

# 190. ATLAS PACKING

El packing deberá respetar padding y mip requirements.

---

# 191. ATLAS VALIDATION

Deberá comprobarse:

```text
bleeding
overlap
padding
mipmap_safety
```

---

# 192. SURFACE COLLECTIONS

Deberá existir:

```text
SurfaceCollection
```

para conjuntos coherentes.

---

# 193. COLLECTION EXAMPLE

Una colección podrá definir:

```text
DARX_BRUTALIST
├── steel
├── painted_steel
├── concrete
├── warning_stripes
├── emissive_red
└── dark_rubber
```

---

# 194. COLLECTION CONSISTENCY

Los materiales de una colección deberán compartir reglas visuales.

---

# 195. BIOME MATERIAL SYSTEM

Deberá existir compatibilidad con UAF-81.16.

---

# 196. BIOME PARAMETERS

Los materiales podrán recibir:

```text
biome
temperature
humidity
altitude
weather
```

---

# 197. WEATHERING

El weathering podrá ser estático o dinámico.

---

# 198. STATIC WEATHERING

Se almacenará en texturas/masks.

---

# 199. DYNAMIC WEATHERING

Se controlará mediante parámetros runtime.

---

# 200. DAMAGE PERSISTENCE

Los daños persistentes deberán poder almacenarse en masks o datos equivalentes.

---

# 201. MATERIAL STATE

Deberá existir:

```text
SurfaceState
```

para representar:

```text
clean
worn
damaged
wet
frozen
burned
corroded
```

---

# 202. STATE TRANSITIONS

Las transiciones deberán ser explícitas.

---

# 203. SURFACE STATE VALIDATION

Los estados no deberán producir combinaciones visualmente inválidas.

---

# 204. TEXTURE VARIANT CACHE

Las variantes deberán poder cachearse.

---

# 205. BUILD GRAPH

La fase deberá integrarse al grafo:

```text
Asset
→ Geometry
→ UV
→ Texture
→ Material
→ Variant
→ Target
```

---

# 206. FAILURE RECOVERY

Un fallo en una textura deberá permitir conservar las salidas válidas anteriores.

---

# 207. CHECKPOINTS

Mínimo:

```text
UV_CREATED
TEXTURES_CREATED
MATERIAL_CREATED
MATERIAL_VALIDATED
TEXTURE_VALIDATED
VARIANTS_CREATED
OPTIMIZED
UNREAL_VALIDATED
```

---

# 208. TRANSACTION SAFETY

La publicación deberá utilizar:

```text
MutationTransaction
```

---

# 209. AUDIT

Cada build deberá registrar:

```text
asset_id
surface_id
seed
generator_version
profile_versions
source_hash
outputs
warnings
errors
optimization_actions
```

---

# 210. PERFORMANCE METRICS

Mínimo:

```text
texture_memory
shader_instructions
texture_samples
material_count
material_instance_count
texture_count
udim_count
```

---

# 211. QUALITY SCORE

Deberá existir:

```text
SurfaceQualityScore
```

---

# 212. QUALITY COMPONENTS

Mínimo:

```text
UV_SCORE
PBR_SCORE
DETAIL_SCORE
CONSISTENCY_SCORE
MEMORY_SCORE
SHADER_SCORE
VISUAL_SCORE
```

---

# 213. QUALITY THRESHOLD

Cada TargetProfile deberá definir un mínimo de aceptación.

---

# 214. HARD FAILURE

No podrá publicarse si existe:

```text
missing_texture
invalid_uv
broken_material
invalid_format
unsupported_shader
budget_failure
```

---

# 215. SOFT FAILURE

Podrán existir warnings:

```text
low_texel_density
high_texture_memory
high_shader_cost
minor_uv_distortion
```

siempre que el TargetProfile lo permita.

---

# 216. ARTISTIC REVIEW

El sistema deberá producir previews suficientes para revisión humana.

---

# 217. HUMAN REVIEW DATA

Deberá incluir:

```text
asset_preview
material_preview
channel_previews
UV_preview
memory_report
shader_report
```

---

# 218. EXPORT PACKAGE

La salida deberá poder estructurarse como:

```text
Surface/
├── Textures/
├── Materials/
├── MaterialFunctions/
├── UV/
├── Masks/
├── Decals/
├── Variants/
├── Metadata/
└── Validation/
```

---

# 219. UNREAL PACKAGE

Deberá poder mapearse a:

```text
Textures
Materials
Material Instances
Material Functions
Virtual Textures
Decals
```

según el target.

---

# 220. FINAL ACCEPTANCE

La fase será considerada operativa cuando AOE pueda recibir:

```text
Mesh
+
SurfaceDefinition
+
MaterialProfile
+
TextureProfile
+
TargetProfile
```

y producir:

```text
UV SET
+
COMPLETE PBR TEXTURE SET
+
MASTER MATERIAL
+
MATERIAL INSTANCE
+
VARIANTS
+
VALIDATION REPORT
+
UNREAL-READY PACKAGE
```

de forma reproducible y determinista.

---

# 221. PROFESSIONAL ACCEPTANCE

El sistema deberá poder fabricar superficies aptas para:

```text
CHARACTERS
WEAPONS
PROPS
ARCHITECTURE
ENVIRONMENTS
VEHICLES
CREATURES
MODULAR KITS
```

sin implementar pipelines independientes para cada categoría cuando las capacidades puedan compartirse.

---

# 222. ARCHITECTURAL RESULT

La arquitectura resultante será:

```text
                    SURFACE DEFINITION
                            │
                            ▼
                      MESH ANALYSIS
                            │
                            ▼
                       UV FABRICATOR
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       BAKE PIPELINE                PROCEDURAL ENGINE
             │                             │
             └──────────────┬──────────────┘
                            ▼
                    TEXTURE FABRICATOR
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          DAMAGE          WEAR          WEATHERING
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    MATERIAL FABRICATOR
                            │
                            ▼
                MATERIAL FUNCTION LIBRARY
                            │
                            ▼
                 MATERIAL INSTANCE SYSTEM
                            │
                            ▼
                    VARIANT FABRICATOR
                            │
                            ▼
                    OPTIMIZATION ENGINE
                            │
                            ▼
                     VALIDATION ENGINE
                            │
                            ▼
                      UNREAL PACKAGE
```

---

# 223. RELATIONSHIP WITH UAF

UAF-81.18 deberá integrarse con:

```text
UAF-81.01–81.15
UAF-81.16 World Fabrication
UAF-81.17 Character Rigging & Animation
```

---

# 224. NEXT PHASE

La siguiente fase será:

```text
UAF-81.19 — PROCEDURAL ENVIRONMENT, MODULAR KIT & WORLD FABRICATION SYSTEM
```

Esta fase deberá resolver la fabricación profesional de:

```text
WALLS
FLOORS
CEILINGS
DOORS
WINDOWS
CORRIDORS
ROOMS
BUILDINGS
FACILITIES
INTERIORS
EXTERIORS
MODULAR KITS
PROCEDURAL ROOMS
DUNGEONS
INDUSTRIAL COMPLEXES
SCI-FI FACILITIES
COVER SYSTEMS
PROPS PLACEMENT
VEGETATION
TERRAIN
ROAD NETWORKS
WORLD STREAMING CELLS
LEVEL INSTANCING
COLLISION
NAVIGATION
LIGHTING PROXIES
```
