# UAF-81.11 — PROCEDURAL TEXTURE, MATERIAL & SURFACE AUTHORING FABRIC

## UAF-81.11-ARCH

### ARQUITECTURA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE TEXTURAS, MATERIALES Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.11 — Procedural Texture, Material & Surface Authoring Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Dependency:** UAF-81.10  

---

# 1. PURPOSE

UAF-81.11 establece el sistema responsable de convertir geometría, componentes y superficies en assets visualmente completos mediante:

```text
material definition
+
procedural surface generation
+
texture generation
+
texture baking
+
mask generation
+
material assembly
+
validation
+
Unreal compatibility
```

La fase deberá funcionar tanto para personajes como para:

```text
weapons
props
architecture
modular kits
vehicles
creatures
environments
organic assets
```

---

# 2. PRIMARY OBJECTIVE

El sistema deberá fabricar de forma determinista todos los datos visuales necesarios para representar un asset dentro de Unreal Engine.

El resultado no será únicamente:

```text
Mesh + Material
```

sino:

```text
Mesh
+
UV
+
Material Definition
+
Texture Set
+
Masks
+
Surface Properties
+
LOD Material Strategy
+
Runtime Configuration
+
Validation
+
Manifest
```

---

# 3. ARCHITECTURAL PRINCIPLE

La apariencia visual deberá separarse de la geometría.

```text
GEOMETRY
    ↓
SEMANTIC SURFACE
    ↓
MATERIAL DEFINITION
    ↓
TEXTURE GENERATION
    ↓
MATERIAL ASSEMBLY
    ↓
RUNTIME MATERIAL
```

---

# 4. SURFACE SEMANTICS

Cada superficie deberá poseer una identidad semántica.

Ejemplos:

```text
skin
metal
cloth
leather
rubber
plastic
glass
ceramic
stone
concrete
wood
organic
paint
rust
emissive
```

---

# 5. SURFACE REGION

Deberá existir:

```text
SurfaceRegion
```

Cada región deberá contener como mínimo:

```text
region_id
material_family
material_profile
uv_profile
texture_profile
importance
```

---

# 6. MATERIAL FAMILY

Deberá existir:

```text
MaterialFamily
```

Ejemplos:

```text
SKIN
METAL
FABRIC
LEATHER
PLASTIC
GLASS
STONE
CONCRETE
WOOD
ORGANIC
CERAMIC
ENERGY
```

---

# 7. MATERIAL PROFILE

Cada familia deberá tener un perfil configurable.

Ejemplo:

```text
MetalProfile
    metallic = 1.0
    roughness_range
    oxidation
    scratches
    dirt
    edge_wear
```

---

# 8. MATERIAL PARAMETERIZATION

Los materiales deberán definirse mediante parámetros, no mediante valores arbitrarios incrustados en scripts.

---

# 9. MATERIAL PARAMETER TYPES

Deberán soportarse:

```text
scalar
vector
color
texture
mask
curve
gradient
enum
boolean
```

---

# 10. BASE COLOR

El sistema deberá generar o asignar Base Color mediante:

```text
flat color
gradient
procedural noise
surface masks
baked texture
hybrid
```

---

# 11. METALLIC

Metallic deberá poder definirse:

```text
constant
per-region
texture
procedural
```

---

# 12. ROUGHNESS

Roughness deberá soportar variación espacial.

No deberá producirse una superficie completamente uniforme salvo que el perfil lo solicite explícitamente.

---

# 13. SPECULAR

El sistema deberá soportar control de Specular cuando el material objetivo lo requiera.

---

# 14. NORMAL

Deberán existir fuentes:

```text
geometry bake
procedural normal
detail normal
surface normal
combined normal
```

---

# 15. HEIGHT

Height podrá utilizarse para:

```text
parallax
displacement
baking
surface generation
```

---

# 16. AMBIENT OCCLUSION

AO podrá derivarse de:

```text
geometry
bake
procedural approximation
```

---

# 17. CURVATURE

Deberá existir generación de curvature.

La curvature podrá utilizarse para:

```text
edge wear
dirt accumulation
mask generation
material variation
```

---

# 18. THICKNESS

El sistema deberá soportar mapas de thickness para materiales que requieran:

```text
subsurface
transmission
organic shading
cloth
wax-like materials
```

---

# 19. SUBSURFACE

Deberá existir un perfil de Subsurface independiente.

Aplicaciones:

```text
skin
organic tissue
wax
foliage
special materials
```

---

# 20. EMISSIVE

Emissive deberá poder definirse mediante:

```text
color
intensity
mask
animation parameter
```

---

# 21. EMISSIVE SAFETY

El sistema deberá respetar límites definidos por el perfil de producción para evitar valores que produzcan resultados visuales no deseados en Unreal.

---

# 22. OPACITY

Deberá soportar:

```text
opaque
masked
translucent
```

según el perfil del asset.

---

# 23. MATERIAL DOMAIN

Cada material deberá declarar su dominio de renderizado.

---

# 24. MATERIAL INSTANCE

Deberá existir separación entre:

```text
Master Material
Material Instance
Generated Parameters
```

---

# 25. MASTER MATERIAL POLICY

Los Master Materials deberán ser reutilizables.

No deberá generarse un Master Material completamente independiente por cada asset salvo que sea estrictamente necesario.

---

# 26. MATERIAL INSTANCE POLICY

Las variaciones deberán resolverse preferentemente mediante Material Instances.

---

# 27. MATERIAL GRAPH ABSTRACTION

El sistema deberá mantener una representación independiente del grafo visual antes de traducirlo al formato específico de Unreal.

---

# 28. MATERIAL GRAPH

Deberá existir:

```text
MaterialGraph
```

con nodos semánticos.

Ejemplo:

```text
SurfaceColor
RoughnessVariation
Metallic
NormalDetail
DirtMask
DamageMask
EmissionMask
```

---

# 29. GRAPH COMPILATION

El MaterialGraph deberá poder compilarse hacia el backend correspondiente.

---

# 30. MATERIAL BACKEND

La arquitectura deberá permitir futuros backends sin modificar la definición semántica.

---

# 31. TEXTURE SET

Deberá existir:

```text
TextureSet
```

que agrupe todos los mapas relacionados con un material.

---

# 32. TEXTURE SET IDENTITY

Cada TextureSet deberá poseer:

```text
texture_set_id
material_id
resolution
channels
format
version
```

---

# 33. REQUIRED TEXTURE TYPES

El sistema deberá poder producir:

```text
BaseColor
Normal
Roughness
Metallic
AO
Height
Emissive
Opacity
Thickness
Curvature
ID
Mask
```

No todos serán obligatorios en todos los materiales.

---

# 34. TEXTURE REQUIREMENT MATRIX

Cada MaterialProfile deberá declarar qué mapas son:

```text
REQUIRED
OPTIONAL
UNUSED
DERIVED
```

---

# 35. PROCEDURAL TEXTURE GENERATOR

Deberá existir:

```text
ProceduralTextureGenerator
```

---

# 36. GENERATOR INPUTS

El generador deberá aceptar:

```text
seed
resolution
surface_coordinates
material_profile
noise_profile
mask_profile
quality_level
```

---

# 37. DETERMINISM

La misma combinación de:

```text
material_profile
+
parameters
+
seed
+
generator_version
```

deberá producir el mismo resultado dentro de las tolerancias establecidas.

---

# 38. NOISE SYSTEM

Deberá existir un sistema abstracto de ruido.

Deberá soportar múltiples familias de ruido.

Ejemplos:

```text
perlin
simplex
voronoi
cellular
fractal
gradient
custom
```

---

# 39. NOISE COMPOSITION

Los ruidos podrán combinarse mediante:

```text
add
subtract
multiply
min
max
lerp
remap
power
clamp
```

---

# 40. NOISE PROFILE

Cada ruido deberá poder definirse mediante:

```text
scale
frequency
octaves
lacunarity
gain
contrast
rotation
seed
```

---

# 41. MASK GENERATION

Deberá existir:

```text
SurfaceMaskGenerator
```

---

# 42. MASK SOURCES

Las máscaras podrán derivarse de:

```text
position
normal
curvature
AO
height
material ID
vertex color
UV
noise
distance
semantic region
```

---

# 43. MASK OPERATIONS

Deberán soportarse:

```text
multiply
add
subtract
invert
blur
contrast
threshold
remap
clamp
```

---

# 44. POSITION MASKS

Deberán poder definirse máscaras mediante posición.

Ejemplos:

```text
top
bottom
front
back
left
right
center
```

---

# 45. NORMAL MASKS

Deberán poder seleccionarse superficies según orientación.

---

# 46. CURVATURE MASKS

Deberán poder detectarse:

```text
convex edges
concave regions
sharp edges
smooth regions
```

---

# 47. DAMAGE SYSTEM

Deberá existir:

```text
SurfaceDamageGenerator
```

---

# 48. DAMAGE TYPES

Mínimo:

```text
scratch
dent
crack
chip
burn
corrosion
rust
stain
blood-like contamination
mud
dust
wear
paint loss
```

Los tipos deberán ser perfiles y no lógica fija.

---

# 49. DAMAGE LAYERS

El daño deberá ser no destructivo.

```text
BASE
↓
WEAR
↓
DAMAGE
↓
DIRT
↓
FINAL
```

---

# 50. DAMAGE DISTRIBUTION

La distribución deberá depender de:

```text
surface orientation
curvature
exposure
height
usage
material type
seed
```

---

# 51. EDGE WEAR

Los materiales podrán generar desgaste preferentemente en bordes.

---

# 52. DIRT ACCUMULATION

La suciedad podrá acumularse preferentemente en:

```text
concave areas
bottom regions
contact areas
crevices
```

---

# 53. MATERIAL AGE

Deberá existir un parámetro de edad:

```text
material_age
```

que modifique las capas visuales de manera controlada.

---

# 54. ENVIRONMENTAL EXPOSURE

Podrá existir:

```text
dust
water
salt
corrosion
UV
mud
```

como variables de exposición.

---

# 55. MATERIAL WEAR MODEL

El desgaste deberá poder modelarse como función de:

```text
age
exposure
usage
material
location
```

---

# 56. FABRIC MATERIAL

El sistema deberá disponer de un perfil específico para tejidos.

Deberá soportar:

```text
weave
fiber variation
roughness variation
fold masks
stitch masks
wear
```

---

# 57. LEATHER MATERIAL

Deberá soportar:

```text
grain
roughness
creases
edge wear
color variation
```

---

# 58. SKIN MATERIAL

Deberá soportar:

```text
base tone
subsurface
micro variation
pores
oil variation
redness
roughness variation
```

---

# 59. METAL MATERIAL

Deberá soportar:

```text
metallic
roughness
oxidation
scratches
edge wear
dents
paint layers
```

---

# 60. PAINTED METAL

Deberá soportar capas:

```text
metal
primer
paint
damage
oxidation
```

---

# 61. CONCRETE MATERIAL

Deberá soportar:

```text
aggregate
cracks
stains
roughness
dust
edge damage
```

---

# 62. STONE MATERIAL

Deberá soportar:

```text
strata
fractures
roughness
color variation
erosion
```

---

# 63. WOOD MATERIAL

Deberá soportar:

```text
grain
growth pattern
knots
cracks
age
roughness
```

---

# 64. GLASS MATERIAL

Deberá soportar:

```text
transmission
roughness
tint
scratches
thickness
imperfections
```

---

# 65. ORGANIC MATERIAL

Deberá soportar:

```text
surface variation
growth
moisture
roughness
subsurface
damage
```

---

# 66. MATERIAL LAYER SYSTEM

Deberá existir:

```text
MaterialLayerStack
```

Ejemplo:

```text
Metal
↓
Primer
↓
Paint
↓
Scratches
↓
Rust
↓
Dirt
```

---

# 67. LAYER BLENDING

Cada capa deberá definir:

```text
mask
blend_mode
priority
opacity
```

---

# 68. LAYER PRIORITY

Las capas deberán aplicarse en orden determinista.

---

# 69. MATERIAL MASK SEMANTICS

Las máscaras deberán tener identificadores semánticos.

Ejemplo:

```text
mask.edge_wear
mask.dirt
mask.damage
mask.emissive
mask.skin_redness
```

---

# 70. DECAL SYSTEM

Deberá existir:

```text
ProceduralDecalSystem
```

---

# 71. DECAL TYPES

Mínimo:

```text
logo
warning
serial_number
scratch
graffiti
blood
symbol
damage
technical_label
```

---

# 72. DECAL PLACEMENT

Los decals deberán poder anclarse a:

```text
semantic region
surface point
bone
socket
UV
```

---

# 73. SERIALIZATION

Los decals deberán ser reproducibles.

---

# 74. TEXT GENERATION

El sistema deberá poder producir texto visual para:

```text
serial numbers
warning labels
technical markings
faction symbols
```

cuando el perfil lo permita.

---

# 75. UNIQUE ASSET MARKINGS

Los assets podrán recibir identificadores visuales únicos derivados del asset ID o seed.

---

# 76. UV-BASED GENERATION

Las texturas podrán generarse utilizando UVs.

---

# 77. OBJECT-SPACE GENERATION

Deberá soportarse generación object-space.

---

# 78. WORLD-SPACE GENERATION

Deberá soportarse generación world-space para assets que lo requieran.

---

# 79. TRIPLANAR STRATEGY

Deberá existir soporte para materiales que no dependan exclusivamente de UVs.

---

# 80. UV / PROCEDURAL HYBRID

El sistema deberá poder combinar:

```text
UV textures
+
procedural shading
```

---

# 81. BAKE SYSTEM

Deberá existir:

```text
TextureBakeEngine
```

---

# 82. BAKE INPUT

El bake deberá aceptar:

```text
high_detail_mesh
low_detail_mesh
uv_profile
map_profile
resolution
cage
ray_distance
```

---

# 83. BAKE MAPS

Deberán poder hornearse:

```text
normal
AO
curvature
thickness
height
ID
position
custom
```

---

# 84. BAKE VALIDATION

Después de cada bake deberán validarse:

```text
ray misses
artifacts
seams
empty regions
invalid pixels
```

---

# 85. BAKE REPRODUCIBILITY

El bake deberá registrar:

```text
source_hash
target_hash
settings_hash
generator_version
```

---

# 86. CAGE GENERATION

Deberá existir generación procedural de cages.

---

# 87. CAGE VALIDATION

El cage deberá evitar:

```text
projection misses
wrong surface projection
unintended intersections
```

---

# 88. TEXTURE RESOLUTION POLICY

Las resoluciones válidas deberán ser configurables.

Ejemplo:

```text
512
1024
2048
4096
8192
```

El sistema no deberá asumir una única resolución universal.

---

# 89. RESOLUTION SELECTION

La resolución deberá derivarse de:

```text
asset importance
surface area
camera distance
material importance
platform
budget
```

---

# 90. TEXTURE BUDGET

Cada asset deberá declarar:

```text
max_texture_memory
max_texture_count
max_resolution
```

---

# 91. CHANNEL PACKING

Deberá existir:

```text
TextureChannelPacker
```

---

# 92. CHANNEL PACKING EXAMPLE

Podrá utilizarse:

```text
R = AO
G = Roughness
B = Metallic
A = Mask
```

cuando el MaterialProfile lo permita.

---

# 93. PACKING VALIDATION

No se permitirá pérdida accidental de información por incompatibilidad de canales.

---

# 94. TEXTURE FORMAT

El formato deberá ser parte del perfil de exportación.

---

# 95. COLOR MANAGEMENT

El pipeline deberá diferenciar correctamente:

```text
color data
linear data
mask data
normal data
```

---

# 96. SRGB POLICY

Las texturas deberán marcarse según su naturaleza.

No deberá aplicarse sRGB indiscriminadamente.

---

# 97. NORMAL MAP POLICY

Las normales deberán respetar el formato esperado por el backend de Unreal.

---

# 98. TEXTURE NAMING

Todos los archivos deberán seguir un naming convention determinista.

Ejemplo:

```text
T_<Asset>_<Material>_<Map>
```

---

# 99. MATERIAL NAMING

Ejemplo:

```text
M_<Family>_<Variant>
MI_<Asset>_<Region>
```

---

# 100. TEXTURE VERSIONING

Cada textura deberá estar asociada a una versión del generador.

---

# 101. HASHING

Deberán calcularse hashes para:

```text
source geometry
parameters
material profile
generator version
output texture
```

---

# 102. CACHE SYSTEM

Deberá existir cache de generación.

---

# 103. CACHE KEY

La cache deberá depender de:

```text
input_hash
profile_hash
seed
generator_version
quality_level
```

---

# 104. CACHE INVALIDATION

Un cambio en cualquiera de los componentes relevantes deberá invalidar el resultado correspondiente.

---

# 105. PARTIAL REGENERATION

Cambiar únicamente:

```text
roughness
```

no deberá obligar a regenerar:

```text
normal
height
AO
```

si sus dependencias no cambiaron.

---

# 106. DEPENDENCY GRAPH

Deberá existir:

```text
TextureDependencyGraph
```

---

# 107. DEPENDENCY EXAMPLE

```text
Geometry
 ├── AO
 ├── Curvature
 ├── Thickness
 └── Normal

Material Parameters
 ├── BaseColor
 ├── Roughness
 └── Metallic
```

---

# 108. TEXTURE ATLAS

Deberá soportarse atlas cuando el runtime profile lo requiera.

---

# 109. ATLAS PACKING

El packing deberá considerar:

```text
padding
rotation
resolution
material compatibility
LOD
```

---

# 110. UDIM

Deberá existir soporte para UDIM.

---

# 111. UDIM POLICY

UDIM deberá ser seleccionable por perfil.

No será obligatorio para todos los assets.

---

# 112. VIRTUAL TEXTURE STRATEGY

Deberá existir soporte conceptual para Virtual Textures.

---

# 113. RUNTIME TEXTURE STRATEGY

El sistema deberá distinguir:

```text
source texture
master texture
runtime texture
preview texture
```

---

# 114. PREVIEW QUALITY

Deberá existir un modo de preview de baja resolución para acelerar iteraciones.

---

# 115. FINAL QUALITY

La generación final deberá utilizar el perfil de calidad seleccionado.

---

# 116. MATERIAL PREVIEW

Cada material deberá poder producir un preview estandarizado.

---

# 117. PREVIEW LIGHTING

Los previews deberán utilizar condiciones de iluminación reproducibles.

---

# 118. MATERIAL GOLDEN

Los materiales críticos deberán disponer de golden references.

---

# 119. VISUAL REGRESSION

Deberá existir comparación visual contra golden references.

---

# 120. MATERIAL VALIDATION

Deberá validarse:

```text
missing maps
wrong color space
invalid channels
invalid dimensions
broken references
unsupported features
```

---

# 121. TEXTURE VALIDATION

Deberá validarse:

```text
resolution
format
alpha
mip compatibility
UV coverage
compression suitability
```

---

# 122. SURFACE VALIDATION

Deberá validarse:

```text
texture continuity
material boundaries
surface scale
detail density
```

---

# 123. TEXEL DENSITY VALIDATION

El sistema deberá comprobar que las regiones críticas mantengan una densidad dentro del rango definido.

---

# 124. DETAIL SCALE VALIDATION

Los detalles deberán respetar la escala física del asset.

No deberán existir:

```text
scratches gigantes
pores kilométricos
bolts microscópicos
```

por errores de escala.

---

# 125. PHYSICAL SCALE

El sistema deberá utilizar unidades físicas consistentes.

---

# 126. MATERIAL PHYSICAL PLAUSIBILITY

Los parámetros deberán poder validarse contra rangos plausibles definidos por cada MaterialProfile.

---

# 127. ART-DIRECTION OVERRIDE

La plausibilidad física podrá ser modificada mediante un perfil artístico explícito.

---

# 128. ART-DIRECTION PROFILE

Deberá existir:

```text
ArtDirectionProfile
```

con:

```text
color_palette
contrast
roughness_bias
saturation
detail_density
stylization
```

---

# 129. STYLE ARCHETYPES

Deberán existir perfiles:

```text
REALISTIC
SCI_FI
HORROR
FANTASY
MILITARY
CARTOON
STYLIZED
INDUSTRIAL
CUSTOM
```

---

# 130. STYLE INHERITANCE

Los assets deberán poder heredar un ArtDirectionProfile.

---

# 131. STYLE OVERRIDE

Los parámetros específicos podrán sobrescribir el perfil sin modificarlo globalmente.

---

# 132. MATERIAL CONSISTENCY

Los materiales pertenecientes al mismo asset deberán mantener coherencia visual.

---

# 133. ASSET MATERIAL PALETTE

Deberá existir:

```text
AssetMaterialPalette
```

---

# 134. PALETTE RULES

La paleta deberá poder limitar:

```text
primary colors
secondary colors
accent colors
emissive colors
```

---

# 135. FACTION MATERIAL IDENTITY

Podrán definirse paletas por:

```text
faction
team
biome
manufacturer
culture
```

---

# 136. UNIQUE VARIATION

Las variantes podrán cambiar:

```text
color
wear
damage
decals
roughness
accessories
```

sin romper la identidad de familia.

---

# 137. MATERIAL INSTANCING STRATEGY

Cuando múltiples assets compartan una familia material deberán reutilizar el mismo Master Material.

---

# 138. MATERIAL LIBRARY

Deberá existir una biblioteca semántica:

```text
MaterialLibrary
```

---

# 139. MATERIAL LIBRARY ENTRY

Cada entrada deberá contener:

```text
material_id
family
profile
version
generator
compatibility
quality_profiles
```

---

# 140. MATERIAL LIBRARY VALIDATION

Los materiales deberán probarse antes de poder ser marcados como:

```text
PRODUCTION_READY
```

---

# 141. MATERIAL COMPATIBILITY

Cada material deberá declarar compatibilidad con:

```text
engine_version
rendering_features
platform
asset_type
```

---

# 142. UNREAL MATERIAL TRANSLATION

El backend deberá convertir la definición abstracta a la estructura correspondiente de Unreal.

---

# 143. ENGINE FEATURE CHECK

Antes de exportar deberá comprobarse que las características solicitadas sean compatibles con el perfil objetivo.

---

# 144. UNSUPPORTED FEATURE POLICY

Una característica incompatible deberá producir:

```text
FAIL
WARN
FALLBACK
```

según política.

Nunca deberá desaparecer silenciosamente.

---

# 145. FALLBACK STRATEGY

Cuando exista fallback deberá quedar registrado en el manifest.

---

# 146. MATERIAL OPTIMIZATION

La optimización podrá incluir:

```text
channel packing
texture reduction
material consolidation
instance reuse
map elimination
```

---

# 147. OPTIMIZATION PRIORITY

El sistema deberá preservar primero:

```text
visual identity
silhouette-related surface features
hero details
material separation
```

---

# 148. MATERIAL CONSOLIDATION

Los materiales podrán consolidarse únicamente cuando no se pierda funcionalidad.

---

# 149. TEXTURE DOWNSCALING

Las texturas podrán reducirse según LOD/profile.

---

# 150. TEXTURE QUALITY LEVELS

Mínimo:

```text
DRAFT
STANDARD
HIGH
HERO
CINEMATIC
```

---

# 151. QUALITY CONSISTENCY

Cambiar de calidad no deberá modificar arbitrariamente:

```text
material identity
color palette
material family
surface semantics
```

---

# 152. SURFACE SEED

Cada superficie procedural deberá poseer un seed reproducible.

---

# 153. HIERARCHICAL SEEDS

Deberán existir:

```text
asset_seed
material_seed
texture_seed
damage_seed
detail_seed
```

---

# 154. SEED DERIVATION

Los seeds deberán derivarse jerárquicamente y de forma determinista.

---

# 155. NO UNCONTROLLED RANDOMNESS

No deberá existir generación aleatoria sin seed dentro del pipeline determinista.

---

# 156. MATERIAL MANIFEST

Cada asset deberá producir:

```text
MaterialManifest
```

con:

```text
asset_id
material_ids
texture_sets
profiles
seeds
generator_versions
dependencies
outputs
hashes
validation
budgets
fallbacks
```

---

# 157. AUDIT TRAIL

Deberán registrarse:

```text
material_creation
texture_creation
bake
optimization
validation
export
fallback
```

---

# 158. FAILURE ISOLATION

Un fallo en una textura deberá aislarse del resto del asset cuando sea posible.

---

# 159. RECOVERY

El sistema deberá poder recuperar desde el último resultado válido.

---

# 160. REPRODUCTION

Un material deberá poder reconstruirse desde:

```text
MaterialProfile
+
parameters
+
seed
+
generator_version
```

---

# 161. REPRODUCTION VALIDATION

La reconstrucción deberá producir hashes equivalentes cuando el backend y formato lo permitan.

---

# 162. CROSS-ASSET REUSE

Un MaterialProfile deberá poder reutilizarse entre:

```text
character
weapon
prop
architecture
environment
```

cuando sea semánticamente válido.

---

# 163. SURFACE COMPOSITION

Una superficie podrá componerse de múltiples materiales.

Ejemplo:

```text
armor
├── metal
├── paint
├── rubber
└── dirt
```

---

# 164. MATERIAL REGION GRAPH

Deberá existir:

```text
MaterialRegionGraph
```

para describir dichas relaciones.

---

# 165. REGION INHERITANCE

Una región podrá heredar propiedades de otra.

---

# 166. MATERIAL OVERRIDE

Un componente podrá sobrescribir parámetros sin duplicar todo el material.

---

# 167. GLOBAL ENVIRONMENT MATERIALS

Deberán existir perfiles globales para materiales de entorno.

---

# 168. ENVIRONMENT SURFACE TYPES

Mínimo:

```text
concrete
asphalt
metal
stone
soil
sand
snow
ice
mud
water
wood
vegetation
```

---

# 169. BIOME MATERIAL PROFILE

Deberá existir:

```text
BiomeMaterialProfile
```

---

# 170. BIOME SURFACE VARIATION

Un biome podrá modificar:

```text
color
roughness
damage
growth
wetness
dirt
```

sin duplicar toda la biblioteca.

---

# 171. WETNESS SYSTEM

Deberá existir soporte para variación de humedad.

---

# 172. WETNESS EFFECTS

La humedad podrá modificar:

```text
roughness
color
specular response
darkening
```

---

# 173. SNOW / COVER SYSTEM

Deberá existir un sistema de cobertura superficial.

Podrá utilizar:

```text
height
normal
slope
mask
```

---

# 174. PROCEDURAL COVERAGE

Podrán generarse:

```text
snow
dust
mud
ash
sand
```

mediante reglas de superficie.

---

# 175. ENVIRONMENTAL ACCUMULATION

La acumulación deberá considerar orientación y posición.

---

# 176. MATERIAL LIBRARY GOVERNANCE

Los materiales deberán poseer estados:

```text
DRAFT
VALIDATED
APPROVED
PRODUCTION_READY
DEPRECATED
```

---

# 177. DEPRECATED MATERIAL

Un material deprecated no deberá utilizarse en nuevas generaciones salvo override explícito.

---

# 178. MATERIAL VERSIONING

Cambios incompatibles deberán generar una nueva versión.

---

# 179. BACKWARD COMPATIBILITY

El sistema deberá mantener compatibilidad con assets existentes cuando sea posible.

---

# 180. MIGRATION

Deberán existir mecanismos de migración entre versiones de MaterialProfile.

---

# 181. SECURITY / INTEGRITY

Los outputs deberán poder verificarse mediante hashes.

---

# 182. OUTPUT DIRECTORY STRUCTURE

La estructura deberá ser configurable, pero deberá separar conceptualmente:

```text
Source
Intermediate
Textures
Materials
Bakes
Previews
Runtime
Manifest
```

---

# 183. SOURCE PRESERVATION

Los datos necesarios para reproducir un material no deberán eliminarse durante la optimización.

---

# 184. INTERMEDIATE CLEANUP

Los intermediates podrán limpiarse únicamente cuando:

```text
reproduction requirements
retention policy
checkpoint policy
```

lo permitan.

---

# 185. PREVIEW GENERATION

Cada TextureSet importante deberá producir previews.

---

# 186. PREVIEW CHANNELS

Podrán visualizarse individualmente:

```text
BaseColor
Roughness
Metallic
Normal
AO
Height
Mask
Emissive
```

---

# 187. MATERIAL DEBUG VIEW

Deberá existir una vista diagnóstica capaz de revelar:

```text
UV density
material IDs
curvature
AO
normal direction
mask distribution
```

---

# 188. AUTOMATED QA

La fase deberá disponer de validadores automatizados.

---

# 189. QA CATEGORIES

Mínimo:

```text
STRUCTURAL
SEMANTIC
VISUAL
COLOR
TEXTURE
MATERIAL
ENGINE
PERFORMANCE
DETERMINISM
```

---

# 190. GOLDEN ASSETS

Deberán existir assets golden para:

```text
skin
metal
fabric
leather
concrete
stone
wood
glass
organic
painted metal
```

---

# 191. GOLDEN MATERIAL TEST

Cada cambio del generador deberá compararse contra los golden assets.

---

# 192. REGRESSION POLICY

Un cambio visual significativo deberá producir:

```text
PASS
EXPECTED_CHANGE
FAIL
```

---

# 193. ARTISTIC REVIEW GATE

La validación técnica no será suficiente para aprobar un material.

Deberá existir un estado de revisión artística.

---

# 194. ARTISTIC REJECTION

Un material podrá rechazarse aunque pase todos los tests técnicos.

---

# 195. FINAL MATERIAL PIPELINE

El pipeline normativo será:

```text
SURFACE SEMANTICS
↓
MATERIAL FAMILY
↓
MATERIAL PROFILE
↓
ART DIRECTION
↓
SURFACE MASKS
↓
MATERIAL LAYERS
↓
PROCEDURAL TEXTURES
↓
BAKES
↓
CHANNEL PACKING
↓
TEXTURE VALIDATION
↓
MATERIAL GRAPH
↓
MASTER MATERIAL
↓
MATERIAL INSTANCE
↓
OPTIMIZATION
↓
UNREAL TRANSLATION
↓
ENGINE VALIDATION
↓
VISUAL QA
↓
MANIFEST
↓
PRODUCTION OUTPUT
```

---

# 196. FINAL ACCEPTANCE CRITERIA

UAF-81.11 será considerada completada cuando el sistema pueda fabricar, validar y exportar materiales completos para al menos:

```text
1 humanoide orgánico
1 robot
1 criatura
1 arma
1 pieza de armadura
1 pieza de ropa
1 prop industrial
1 bloque arquitectónico
1 superficie natural
```

Cada caso deberá poder producir, según corresponda:

```text
BaseColor
Normal
Roughness
Metallic
AO
Height
Emissive
Masks
Material Instance
```

---

# 197. NON-NEGOTIABLE REQUIREMENT

No se permitirá que la apariencia final dependa exclusivamente de colores planos asignados desde código.

---

# 198. NON-NEGOTIABLE REQUIREMENT

No se permitirá que una textura generada pierda silenciosamente información por:

```text
color-space mismatch
channel mismatch
unsupported format
resolution mismatch
UV mismatch
```

---

# 199. NON-NEGOTIABLE REQUIREMENT

Toda generación procedural deberá ser reproducible mediante:

```text
input
profile
seed
version
```

---

# 200. NON-NEGOTIABLE REQUIREMENT

El sistema deberá poder distinguir claramente entre:

```text
SOURCE
GENERATED
BAKED
OPTIMIZED
RUNTIME
```

---

# 201. NON-NEGOTIABLE REQUIREMENT

Los materiales deberán diseñarse como infraestructura reutilizable y no como assets aislados.

---

# 202. INTEGRATION WITH UAF-81.10

UAF-81.11 deberá consumir directamente:

```text
CharacterSpecification
SemanticBodyGraph
SurfaceRegion
UVProfile
TopologyProfile
LODProfile
```

de UAF-81.10.

---

# 203. INTEGRATION WITH FUTURE ENVIRONMENT SYSTEM

La arquitectura deberá permitir que el mismo sistema material sea utilizado posteriormente por:

```text
Modular Blocks
Buildings
Terrain
Maps
Biomes
Props
World Assets
```

---

# 204. NEXT PHASE

# UAF-81.12 — PROCEDURAL MODULAR ENVIRONMENT & WORLD FABRICATION

La siguiente fase establecerá la arquitectura para fabricar los elementos físicos que componen un nivel completo de Unreal.

Deberá cubrir como mínimo:

```text
MODULAR BLOCKS
WALLS
FLOORS
CEILINGS
DOORS
WINDOWS
STAIRS
PILLARS
COLUMNS
CORRIDORS
ROOMS
BUILDINGS
PROPS
FURNITURE
INDUSTRIAL KITS
SCI-FI KITS
DUNGEONS
URBAN KITS
INTERIOR KITS
EXTERIOR KITS
TERRAIN
VEGETATION
BIOMES
```

y deberá introducir formalmente:

```text
Grid System
Snap System
Modular Grammar
Spatial Constraints
Architectural Grammar
Room Graph
Building Graph
Biome Graph
World Graph
Procedural Placement
Collision
Navigation
Gameplay Sockets
World Partition Compatibility
Level Streaming
LOD
Nanite Strategy
PCG Integration
Landscape Integration
Data Layers
World Validation
Performance Budgets
```

La meta de UAF-81.12 será pasar de fabricar **assets individuales** a fabricar **sistemas de assets capaces de construir espacios jugables completos**.
