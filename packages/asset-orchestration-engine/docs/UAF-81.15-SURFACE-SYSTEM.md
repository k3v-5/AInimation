# UAF-81.15 — MATERIAL, TEXTURE & SURFACE FABRICATION SYSTEM

## UAF-81.15-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN DE MATERIALES, TEXTURAS Y SUPERFICIES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.15 — Material, Texture & Surface Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.14  
**Next Phase:** UAF-81.16  

---

# 1. PURPOSE

UAF-81.15 define el sistema responsable de fabricar, procesar, validar, optimizar, versionar y exportar superficies visuales para assets destinados a Unreal Engine.

El sistema deberá cubrir:

```text
MATERIALS
TEXTURES
UVS
MASKS
DECALS
SURFACE DETAILS
BAKING
PROCEDURAL GENERATION
VARIANTS
MATERIAL INSTANCES
CHANNEL PACKING
TEXTURE ATLASES
UDIMS
VIRTUAL TEXTURES
LOD MATERIALS
VALIDATION
OPTIMIZATION
EXPORT
```

---

# 2. PRIMARY OBJECTIVE

El objetivo es que cualquier asset fabricado por AOE pueda recibir una superficie profesional sin depender de un único sistema de materiales.

Debe ser posible fabricar:

```text
SKIN
METAL
WOOD
STONE
CONCRETE
PLASTIC
RUBBER
FABRIC
LEATHER
GLASS
CERAMIC
LIQUID
ORGANIC
VEGETATION
TERRAIN
ICE
SNOW
SAND
MUD
ENERGY
HOLOGRAM
DAMAGED_SURFACE
```

---

# 3. SURFACE FABRICATION MODEL

Toda superficie deberá conceptualizarse como:

```text
SURFACE
=
GEOMETRY INTERACTION
+
BASE MATERIAL
+
MICRODETAIL
+
MACRODETAIL
+
WEAR
+
DAMAGE
+
VARIATION
+
ENVIRONMENTAL RESPONSE
```

---

# 4. SURFACE PROFILE

Deberá existir:

```text
SurfaceProfile
```

---

# 5. SURFACE PROFILE CONTENT

Mínimo:

```text
surface_id
surface_type
material_class
shader_model
base_color_profile
roughness_profile
metallic_profile
normal_profile
height_profile
ao_profile
emissive_profile
opacity_profile
subsurface_profile
detail_profile
wear_profile
damage_profile
uv_profile
texture_profile
optimization_profile
```

---

# 6. MATERIAL CLASSIFICATION

Deberán existir como mínimo:

```text
OPAQUE
MASKED
TRANSLUCENT
ADDITIVE
SUBSURFACE
FOLIAGE
HAIR
DECAL
WATER
VFX
```

---

# 7. MATERIAL DOMAIN

Cada material deberá declarar explícitamente su dominio.

---

# 8. SHADING MODEL

El sistema deberá permitir seleccionar el modelo de shading requerido por el target.

---

# 9. MATERIAL GRAPH

Deberá existir:

```text
MaterialGraph
```

que represente los nodos de superficie antes de generar el material final.

---

# 10. MATERIAL GRAPH REQUIREMENTS

Cada graph deberá declarar:

```text
inputs
parameters
textures
functions
outputs
dependencies
version
```

---

# 11. MATERIAL PARAMETERS

Los parámetros deberán estar separados en:

```text
STATIC
DYNAMIC
INSTANCE
GLOBAL
```

---

# 12. STATIC PARAMETERS

Los parámetros estáticos podrán alterar la compilación del material.

Deberán utilizarse únicamente cuando exista una razón técnica.

---

# 13. INSTANCE PARAMETERS

Los cambios visuales frecuentes deberán resolverse preferentemente mediante Material Instances.

---

# 14. GLOBAL PARAMETERS

Deberán existir parámetros globales para:

```text
weather
time
damage
dirt
snow
wetness
environment
```

cuando el target lo permita.

---

# 15. BASE COLOR

El sistema deberá soportar:

```text
SOLID_COLOR
TEXTURE
PROCEDURAL
VERTEX_COLOR
ATTRIBUTE
HYBRID
```

---

# 16. ROUGHNESS

La roughness deberá poder derivarse de:

```text
CONSTANT
TEXTURE
PROCEDURAL
MASK
HYBRID
```

---

# 17. METALLIC

El metallic deberá poder derivarse de:

```text
CONSTANT
TEXTURE
MASK
ATTRIBUTE
```

---

# 18. NORMAL

El sistema deberá soportar:

```text
NORMAL_TEXTURE
PROCEDURAL_NORMAL
DETAIL_NORMAL
BLENDED_NORMAL
```

---

# 19. HEIGHT

Deberá soportar:

```text
HEIGHT_TEXTURE
PARALLAX
DISPLACEMENT
WORLD_POSITION
PROCEDURAL_HEIGHT
```

según target.

---

# 20. AMBIENT OCCLUSION

El AO podrá proceder de:

```text
BAKED
PROCEDURAL
GENERATED
VERTEX
TEXTURE
```

---

# 21. EMISSIVE

El emissive deberá tener límites por quality profile.

El sistema deberá evitar valores que provoquen resultados visualmente inválidos en el target.

---

# 22. OPACITY

Deberá soportar:

```text
OPAQUE
MASKED
TRANSLUCENT
```

según material domain.

---

# 23. SUBSURFACE

Deberá existir soporte para:

```text
SKIN
WAX
FLESH
LEAVES
ORGANIC
```

cuando corresponda.

---

# 24. MATERIAL FUNCTIONS

Los bloques reutilizables deberán poder convertirse en:

```text
MaterialFunction
```

---

# 25. STANDARD MATERIAL FUNCTIONS

Mínimo:

```text
Triplanar
DetailBlend
Noise
Wear
Dirt
EdgeWear
Damage
ColorVariation
RoughnessVariation
NormalBlend
WorldAligned
```

---

# 26. PROCEDURAL NOISE

Deberán existir generadores reproducibles de ruido.

---

# 27. NOISE PARAMETERS

Mínimo:

```text
seed
scale
octaves
roughness
lacunarity
distortion
```

---

# 28. SEED DETERMINISM

La misma combinación de:

```text
profile
seed
generator_version
```

deberá producir el mismo resultado.

---

# 29. MACRO VARIATION

Las superficies deberán soportar variación a gran escala.

---

# 30. MICRO VARIATION

Las superficies deberán soportar variación a pequeña escala.

---

# 31. DETAIL LAYERS

Deberán existir al menos:

```text
MACRO
MEDIUM
MICRO
```

---

# 32. DETAIL BLENDING

Las capas de detalle deberán poder mezclarse sin destruir la información base.

---

# 33. WEAR SYSTEM

Deberá existir:

```text
SurfaceWearSystem
```

---

# 34. WEAR TYPES

Mínimo:

```text
EDGE_WEAR
SCRATCH
ABRASION
DUST
DIRT
OIL
OXIDATION
FADING
```

---

# 35. DAMAGE SYSTEM

Deberá existir:

```text
SurfaceDamageSystem
```

---

# 36. DAMAGE TYPES

Mínimo:

```text
SCRATCH
DENT
CRACK
BURN
IMPACT
CORROSION
BULLET_MARK
CUT
FRACTURE
```

---

# 37. DAMAGE MASKS

El daño deberá poder controlarse mediante máscaras.

---

# 38. DAMAGE NON-DESTRUCTIVE

El daño visual deberá ser no destructivo siempre que sea posible.

---

# 39. MATERIAL VARIANTS

Deberá existir:

```text
MaterialVariant
```

---

# 40. VARIANT PARAMETERS

Una variante podrá modificar:

```text
color
roughness
metallic
wear
damage
dirt
emissive
opacity
detail
```

sin duplicar el material base innecesariamente.

---

# 41. PALETTE SYSTEM

Deberá existir:

```text
ColorPalette
```

---

# 42. PALETTE CONTENT

Mínimo:

```text
primary
secondary
accent
neutral
damage
emissive
```

---

# 43. FACTION PALETTES

Las facciones podrán definir palettes reutilizables.

---

# 44. CHARACTER MATERIAL INTEGRATION

Los personajes de UAF-81.14 deberán consumir SurfaceProfiles.

---

# 45. WEAPON MATERIAL INTEGRATION

Las armas deberán consumir SurfaceProfiles.

---

# 46. ENVIRONMENT MATERIAL INTEGRATION

Los entornos deberán consumir SurfaceProfiles.

---

# 47. TERRAIN MATERIAL INTEGRATION

El terrain deberá consumir SurfaceProfiles especializados.

---

# 48. UV SYSTEM

Deberá existir:

```text
SurfaceUVSystem
```

---

# 49. UV CHANNELS

El sistema deberá soportar múltiples canales UV.

---

# 50. UV CHANNEL PURPOSES

Los canales podrán representar:

```text
TEXTURE
LIGHTMAP
DETAIL
MASK
CUSTOM
```

---

# 51. UV VALIDATION

Deberá comprobar:

```text
OVERLAP
STRETCH
DISTORTION
PADDING
ORIENTATION
COVERAGE
```

---

# 52. TEXEL DENSITY

Cada asset deberá poder declarar un target de texel density.

---

# 53. TEXEL DENSITY VALIDATION

Deberán detectarse zonas que estén fuera del rango permitido.

---

# 54. UV STRATEGIES

Mínimo:

```text
SMART_UNWRAP
PACK
SEAM_GUIDED
TRIPLANAR
WORLD_ALIGNED
UDIM
```

---

# 55. TRIPLANAR MATERIALS

Los materiales que no requieran UV explícito podrán utilizar proyección triplanar.

---

# 56. WORLD ALIGNED MATERIALS

Los assets arquitectónicos y terrain podrán utilizar world-aligned projection cuando sea apropiado.

---

# 57. UDIM SYSTEM

Deberá existir:

```text
UDIMProfile
```

---

# 58. UDIM VALIDATION

Deberá comprobarse:

```text
tile_number
continuity
resolution
padding
```

---

# 59. TEXTURE GENERATION

Deberá existir:

```text
TextureFabricationSystem
```

---

# 60. TEXTURE TYPES

Mínimo:

```text
BASE_COLOR
NORMAL
ROUGHNESS
METALLIC
AO
HEIGHT
OPACITY
EMISSIVE
MASK
CURVATURE
THICKNESS
```

---

# 61. TEXTURE SOURCES

Mínimo:

```text
PROCEDURAL
BAKED
IMPORTED
PAINTED
GENERATED
HYBRID
```

---

# 62. TEXTURE RESOLUTION PROFILES

Mínimo:

```text
256
512
1024
2048
4096
8192
```

---

# 63. RESOLUTION POLICY

La resolución deberá ser determinada por:

```text
asset_class
camera_importance
surface_area
quality_tier
memory_budget
platform
```

---

# 64. TEXTURE FORMAT

El sistema deberá seleccionar formatos adecuados al target.

---

# 65. COMPRESSION

Cada texture deberá tener:

```text
compression_profile
alpha_policy
mipmap_policy
```

---

# 66. MIPMAPS

Las texturas de runtime deberán soportar mipmaps cuando corresponda.

---

# 67. MIP BIAS

El sistema podrá definir mip bias por profile.

---

# 68. VIRTUAL TEXTURE

Deberá soportarse virtual texturing cuando el target lo requiera.

---

# 69. TEXTURE STREAMING

Deberá declararse si una textura participa en streaming.

---

# 70. CHANNEL PACKING

Deberá existir:

```text
TexturePackingSystem
```

---

# 71. PACKING EXAMPLE

Podrá existir un mapa:

```text
R = AO
G = ROUGHNESS
B = METALLIC
A = MASK
```

---

# 72. PACKING VALIDATION

Deberá garantizarse que ningún canal requerido sea sobrescrito accidentalmente.

---

# 73. BAKE SYSTEM

Deberá existir:

```text
SurfaceBakeSystem
```

---

# 74. BAKE TYPES

Mínimo:

```text
NORMAL
AO
CURVATURE
THICKNESS
POSITION
ID
WORLD_SPACE_NORMAL
```

---

# 75. HIGH TO LOW BAKE

Deberá soportarse:

```text
HIGH_MESH
↓
BAKE
↓
LOW_MESH
```

---

# 76. CAGE

El bake deberá soportar cage configurable.

---

# 77. BAKE VALIDATION

Deberá detectar:

```text
ray_miss
projection_error
seams
artifacts
invalid_normals
```

---

# 78. TEXTURE SEAMS

El sistema deberá minimizar discontinuidades visibles.

---

# 79. NORMAL VALIDATION

Deberá comprobarse la consistencia de tangentes y normales.

---

# 80. TANGENT POLICY

El proyecto deberá definir un único convenio de tangentes por target.

---

# 81. DECAL SYSTEM

Deberá existir:

```text
DecalFabricationSystem
```

---

# 82. DECAL TYPES

Mínimo:

```text
LOGO
FACTION
DAMAGE
WARNING
TEXT
GRAFFITI
DIRT
BLOOD
IDENTIFICATION
```

---

# 83. DECAL PARAMETERS

Mínimo:

```text
texture
color
opacity
roughness
normal
scale
rotation
projection
```

---

# 84. DECAL VARIANTS

Los decals deberán poder variar sin duplicar recursos.

---

# 85. SURFACE MASK SYSTEM

Deberá existir:

```text
SurfaceMaskSystem
```

---

# 86. MASK SOURCES

Mínimo:

```text
VERTEX_COLOR
ATTRIBUTE
TEXTURE
CURVATURE
AO
POSITION
NORMAL
NOISE
ID
```

---

# 87. MASK COMPOSITION

Las máscaras deberán poder combinarse mediante:

```text
ADD
SUBTRACT
MULTIPLY
MIN
MAX
REMAP
INVERT
```

---

# 88. WORLD MASKS

Deberán poder generarse máscaras por posición mundial.

---

# 89. SLOPE MASK

Deberá existir soporte para máscaras basadas en pendiente.

---

# 90. HEIGHT MASK

Deberá existir soporte para máscaras basadas en altura.

---

# 91. WEATHER RESPONSE

Los materiales deberán poder responder a:

```text
RAIN
SNOW
DUST
MUD
WETNESS
```

cuando el target lo permita.

---

# 92. WETNESS SYSTEM

Deberá existir un parámetro de wetness global o por instancia.

---

# 93. SNOW ACCUMULATION

Las superficies compatibles podrán generar acumulación de nieve mediante máscaras.

---

# 94. DIRT ACCUMULATION

Las superficies podrán generar suciedad basada en orientación y posición.

---

# 95. EDGE WEAR

El desgaste de bordes podrá derivarse de curvature o geometría.

---

# 96. MATERIAL INSTANCE SYSTEM

Deberá existir:

```text
MaterialInstanceSystem
```

---

# 97. INSTANCE SHARING

Múltiples assets deberán poder compartir un material padre.

---

# 98. INSTANCE OVERRIDES

Cada instancia podrá modificar únicamente los parámetros permitidos.

---

# 99. MATERIAL PARENTING

Deberá existir:

```text
MasterMaterial
↓
MaterialFunction
↓
MaterialInstance
```

---

# 100. MASTER MATERIAL COUNT

El sistema deberá evitar proliferación innecesaria de Master Materials.

---

# 101. SHADER COMPLEXITY

Deberá existir validación de complejidad del shader.

---

# 102. SHADER BUDGET

El profile deberá declarar:

```text
instruction_budget
texture_sample_budget
sampler_budget
feature_budget
```

---

# 103. FEATURE SWITCHING

Características costosas deberán poder desactivarse por quality tier.

---

# 104. PLATFORM PROFILES

Mínimo:

```text
PC_LOW
PC_HIGH
CONSOLE
MOBILE
CINEMATIC
```

---

# 105. MATERIAL LOD

El material podrá simplificarse con distancia.

---

# 106. MATERIAL QUALITY LEVELS

Mínimo:

```text
LOW
MEDIUM
HIGH
ULTRA
```

---

# 107. TEXTURE QUALITY LEVELS

Mínimo:

```text
LOW
MEDIUM
HIGH
ULTRA
```

---

# 108. SURFACE COST MODEL

Cada superficie deberá estimar:

```text
texture_memory
shader_cost
sampler_count
material_slots
runtime_cost
```

---

# 109. MATERIAL SLOT OPTIMIZATION

El sistema deberá detectar material slots innecesarios.

---

# 110. MATERIAL MERGING

Cuando sea seguro, podrán combinarse materiales compatibles.

---

# 111. ATLAS SYSTEM

Deberá existir:

```text
TextureAtlasSystem
```

---

# 112. ATLAS USE CASES

Principalmente:

```text
NPC_VARIANTS
PROPS
ENVIRONMENT
MODULAR_KITS
```

---

# 113. ATLAS CONSTRAINTS

No deberá utilizarse atlas cuando destruya:

```text
UV_quality
streaming
material_variation
```

---

# 114. SURFACE REUSE

El sistema deberá favorecer reutilización de texturas y materiales.

---

# 115. DUPLICATION DETECTION

Deberá detectar recursos visualmente o estructuralmente duplicados cuando sea posible.

---

# 116. ASSET HASHING

Cada textura deberá poseer un hash de contenido.

---

# 117. DEDUPLICATION

Texturas idénticas deberán almacenarse una sola vez.

---

# 118. NEAR-DUPLICATE DETECTION

El sistema podrá detectar texturas prácticamente idénticas para revisión.

---

# 119. MATERIAL VERSIONING

Cada material deberá tener:

```text
material_id
version
generator_version
profile_version
```

---

# 120. TEXTURE VERSIONING

Cada textura deberá tener:

```text
texture_id
version
source_hash
generator_version
```

---

# 121. REPRODUCIBILITY

La fabricación deberá ser reproducible.

---

# 122. MATERIAL BUILD MANIFEST

Deberá existir:

```text
MaterialBuildManifest
```

---

# 123. MANIFEST CONTENT

Mínimo:

```text
material_id
surface_profile
textures
functions
parameters
dependencies
target
quality
compression
validation
generator_version
```

---

# 124. SURFACE GRAPH INTEGRATION

Las superficies deberán integrarse con SemanticAssetGraph.

---

# 125. DEPENDENCY TRACKING

Deberá poder determinarse:

```text
material
→ texture
→ source
→ generator
```

---

# 126. INVALIDATION

Modificar una textura deberá invalidar únicamente los materiales dependientes.

---

# 127. MATERIAL CACHE

Los resultados deberán poder almacenarse en cache.

---

# 128. CACHE KEY

La cache deberá depender de:

```text
profile
seed
generator_version
input_hash
dependencies
target
quality
```

---

# 129. ERROR ISOLATION

Un fallo en una textura no deberá destruir automáticamente otros materiales independientes.

---

# 130. PREVIEW SYSTEM

Cada material deberá poder generar previews.

---

# 131. PREVIEW ANGLES

Mínimo:

```text
sphere
plane
cube
asset_preview
```

---

# 132. PREVIEW LIGHTING

Las previews deberán utilizar iluminación estandarizada.

---

# 133. VISUAL REGRESSION

Los materiales deberán poder compararse contra golden references.

---

# 134. MATERIAL QA

Deberá comprobar:

```text
base_color
roughness
metallic
normal
opacity
emissive
```

según material type.

---

# 135. TEXTURE QA

Deberá comprobar:

```text
resolution
format
compression
mipmap
color_space
alpha
```

---

# 136. COLOR SPACE

Cada textura deberá declarar explícitamente su color space.

---

# 137. DATA TEXTURES

Los mapas no visuales deberán tratarse como datos y no como color cuando corresponda.

---

# 138. NORMAL MAP COLOR SPACE

Los normal maps deberán recibir tratamiento específico y nunca interpretarse accidentalmente como color.

---

# 139. ALPHA POLICY

Cada textura deberá declarar:

```text
NO_ALPHA
MASK
GRAYSCALE_ALPHA
RGBA
```

---

# 140. TEXTURE NAMING

Deberá existir nomenclatura determinista.

Ejemplo:

```text
T_<Asset>_<Surface>_<Channel>
```

---

# 141. MATERIAL NAMING

Ejemplo:

```text
M_<Category>_<Surface>
MI_<Asset>_<Variant>
```

---

# 142. MASTER MATERIAL NAMING

Ejemplo:

```text
M_Master_<Domain>
```

---

# 143. DIRECTORY POLICY

Los recursos deberán organizarse por:

```text
category
asset
surface
quality
```

---

# 144. UNREAL PATH POLICY

Los paths de Unreal deberán ser configurables.

No deberán existir rutas absolutas dependientes de una máquina específica.

---

# 145. EXPORT TARGET

El exportador deberá generar recursos compatibles con la estructura del proyecto Unreal objetivo.

---

# 146. IMPORT SETTINGS

Los settings de importación deberán formar parte del manifest.

---

# 147. AUTOMATED IMPORT VALIDATION

Deberá poder validarse que los settings esperados coinciden con el manifest.

---

# 148. MATERIAL INSTANCE VALIDATION

Deberá detectar:

```text
missing_parameter
invalid_texture
wrong_domain
wrong_parent
```

---

# 149. TEXTURE REFERENCE VALIDATION

No deberá existir una referencia rota.

---

# 150. ORPHAN DETECTION

Deberán detectarse:

```text
orphan_materials
orphan_textures
orphan_functions
```

---

# 151. CLEANUP

El sistema deberá poder producir un reporte de recursos no utilizados.

---

# 152. MEMORY BUDGET

Cada asset deberá declarar su presupuesto de memoria visual.

---

# 153. MEMORY REPORT

El reporte deberá mostrar:

```text
texture_memory
material_memory_estimate
mipmap_cost
virtual_texture_cost
```

---

# 154. CHARACTER SURFACE PROFILE

Los personajes podrán utilizar:

```text
skin_profile
eye_profile
hair_profile
fabric_profile
armor_profile
metal_profile
```

---

# 155. WEAPON SURFACE PROFILE

Las armas podrán utilizar:

```text
metal
ceramic
plastic
rubber
glass
energy
```

---

# 156. ENVIRONMENT SURFACE PROFILE

Los entornos podrán utilizar:

```text
concrete
stone
wood
metal
dirt
mud
sand
snow
```

---

# 157. TERRAIN SURFACE PROFILE

El terrain deberá soportar:

```text
slope
height
biome
wetness
vegetation
snow
```

---

# 158. VEGETATION SURFACE PROFILE

La vegetación deberá soportar:

```text
leaf
stem
bark
flower
fruit
```

---

# 159. ORGANIC SURFACE PROFILE

Deberá soportar:

```text
flesh
skin
scale
shell
mucus
bone
```

---

# 160. SPECIAL EFFECT SURFACE PROFILE

Deberá soportar:

```text
energy
hologram
forcefield
electric
plasma
```

---

# 161. SURFACE LIBRARY

Todos los SurfaceProfiles reutilizables deberán registrarse en AssetLibrary.

---

# 162. SURFACE COMPATIBILITY

Cada SurfaceProfile deberá declarar:

```text
supported_geometry
supported_domain
supported_targets
supported_quality_levels
```

---

# 163. SURFACE GENERATOR

Deberá existir:

```text
SurfaceGenerator
```

---

# 164. GENERATOR INPUT

Mínimo:

```text
SurfaceProfile
AssetContext
Seed
QualityProfile
TargetProfile
```

---

# 165. GENERATOR OUTPUT

Mínimo:

```text
Material
Textures
Masks
Manifest
ValidationReport
```

---

# 166. BATCH FABRICATION

Deberá ser posible fabricar múltiples superficies en una ejecución.

---

# 167. BATCH DETERMINISM

El resultado de un batch deberá ser independiente del orden de ejecución.

---

# 168. PARALLEL FABRICATION

Las superficies independientes deberán poder fabricarse en paralelo.

---

# 169. CHECKPOINTS

Mínimo:

```text
UV
BASE_TEXTURES
DETAIL_TEXTURES
BAKES
MATERIAL
VARIANTS
OPTIMIZATION
VALIDATION
EXPORT
```

---

# 170. RECOVERY

Un fallo deberá permitir continuar desde el último checkpoint válido.

---

# 171. TRANSACTION SAFETY

La escritura de recursos deberá utilizar transacciones o mecanismos equivalentes para evitar estados parciales.

---

# 172. GOLDEN MATERIALS

Deberán existir golden materials:

```text
SKIN
METAL
FABRIC
CONCRETE
WOOD
STONE
GLASS
VEGETATION
WATER
ENERGY
```

---

# 173. GOLDEN TEXTURES

Deberán existir referencias golden para los principales canales.

---

# 174. REGRESSION TESTING

Cambios en generadores deberán compararse contra golden outputs.

---

# 175. PERFORMANCE REGRESSION

Deberán detectarse incrementos no autorizados de:

```text
texture_memory
shader_complexity
sampler_count
material_slots
```

---

# 176. ARTISTIC REGRESSION

También deberán detectarse alteraciones visuales significativas.

---

# 177. QUALITY GATES

Cada material deberá superar:

```text
STRUCTURAL
VISUAL
PERFORMANCE
EXPORT
```

---

# 178. STRUCTURAL PASS

Debe comprobar integridad de archivos, referencias y parámetros.

---

# 179. VISUAL PASS

Debe comprobar la apariencia esperada.

---

# 180. PERFORMANCE PASS

Debe comprobar presupuestos.

---

# 181. EXPORT PASS

Debe comprobar compatibilidad con el target.

---

# 182. FAILURE STATES

Mínimo:

```text
INVALID_PROFILE
INVALID_TEXTURE
INVALID_UV
INVALID_BAKE
INVALID_SHADER
INVALID_REFERENCE
BUDGET_EXCEEDED
EXPORT_FAILED
```

---

# 183. ERROR SEVERITY

Cada error deberá clasificarse:

```text
INFO
WARNING
ERROR
FATAL
```

---

# 184. AUTO-REPAIR

Cuando sea seguro podrán repararse automáticamente:

```text
missing_mipmaps
invalid_padding
channel_packing
naming
minor_uv_issues
```

---

# 185. AUTO-REPAIR SAFETY

Toda reparación deberá quedar registrada.

---

# 186. AUDIT LOG

Deberá registrarse:

```text
input
change
reason
generator
version
timestamp
result
```

---

# 187. SECURITY

Los procesos de generación deberán respetar PermissionFirewall y ScopeFirewall.

---

# 188. MODIFICATION SCOPE

Una ejecución de SurfaceGenerator deberá declarar exactamente qué recursos puede modificar.

---

# 189. FORBIDDEN MODIFICATION

No podrá modificar assets fuera de su scope declarado.

---

# 190. DRY RUN

Todo proceso destructivo deberá soportar dry-run cuando sea técnicamente posible.

---

# 191. PREVIEW BEFORE COMMIT

Los cambios podrán previsualizarse antes de confirmar la escritura final.

---

# 192. ROLLBACK

Los cambios deberán poder revertirse cuando formen parte de una operación transaccional.

---

# 193. VERSION COMPATIBILITY

Los materiales deberán declarar la versión mínima del sistema requerida.

---

# 194. MIGRATION

Los cambios incompatibles de MaterialProfile deberán disponer de migración.

---

# 195. DOCUMENTATION

Cada SurfaceProfile deberá disponer de documentación de:

```text
purpose
inputs
outputs
parameters
limitations
target
quality
```

---

# 196. API CONTRACT

Deberán existir interfaces equivalentes a:

```text
SurfaceGenerator
TextureGenerator
MaterialGenerator
BakeGenerator
UVGenerator
MaskGenerator
DecalGenerator
MaterialValidator
TextureValidator
SurfaceOptimizer
SurfaceExporter
```

---

# 197. SEPARATION OF RESPONSIBILITY

Ningún generador deberá asumir responsabilidades completas de otro subsistema.

---

# 198. ORCHESTRATION

ProductionOrchestrator deberá poder ejecutar:

```text
SurfaceBuildJob
```

---

# 199. JOB STATES

Mínimo:

```text
QUEUED
RUNNING
CHECKPOINTED
VALIDATING
COMPLETED
FAILED
ROLLED_BACK
```

---

# 200. FINAL ACCEPTANCE

UAF-81.15 será considerada implementada cuando pueda fabricar y validar automáticamente como mínimo:

```text
1 SKIN MATERIAL
1 METAL MATERIAL
1 FABRIC MATERIAL
1 CONCRETE MATERIAL
1 WOOD MATERIAL
1 STONE MATERIAL
1 GLASS MATERIAL
1 VEGETATION MATERIAL
1 TERRAIN MATERIAL
1 ENERGY MATERIAL
```

y cada uno produzca:

```text
MATERIAL
TEXTURES
MASKS
MANIFEST
VALIDATION REPORT
UNREAL-READY OUTPUT
```

---

# 201. GLOBAL ACCEPTANCE

El sistema deberá poder aplicar las superficies fabricadas a:

```text
CHARACTER
WEAPON
PROP
MODULAR_STRUCTURE
TERRAIN
VEGETATION
ENVIRONMENT
```

sin crear implementaciones específicas independientes para cada categoría.

---

# 202. NON-NEGOTIABLE

El sistema no deberá depender de texturas únicas generadas manualmente para cada asset.

---

# 203. NON-NEGOTIABLE

Los materiales deberán ser reutilizables.

---

# 204. NON-NEGOTIABLE

Las variantes deberán poder utilizar Material Instances y máscaras.

---

# 205. NON-NEGOTIABLE

La generación deberá ser determinista.

---

# 206. NON-NEGOTIABLE

No deberán existir rutas absolutas específicas de una máquina.

---

# 207. NON-NEGOTIABLE

Los recursos deberán estar versionados.

---

# 208. NON-NEGOTIABLE

Toda referencia rota deberá producir un fallo de validación.

---

# 209. NON-NEGOTIABLE

Un material visualmente correcto pero incompatible con el presupuesto del target deberá poder ser rechazado.

---

# 210. NON-NEGOTIABLE

Un material técnicamente correcto pero visualmente deficiente deberá poder ser rechazado por QA artístico.

---

# 211. FINAL ARCHITECTURAL RESULT

UAF-81.15 deberá convertir:

```text
PROCEDURAL SHADER GENERATION
```

en:

```text
PROFESSIONAL SURFACE FABRICATION PLATFORM
```

La plataforma deberá proporcionar:

```text
SURFACE
├── Material
├── Textures
├── UV
├── Masks
├── Decals
├── Microdetail
├── Macrodetail
├── Wear
├── Damage
├── Variants
├── Optimization
├── Validation
├── Cache
├── Manifest
└── Unreal Export
```

---

# 212. INTEGRATION RESULT

Al finalizar UAF-81.15:

```text
UAF-81.14 CHARACTER
        │
        ▼
UAF-81.15 SURFACE
        │
        ▼
UNREAL-READY CHARACTER
```

El mismo sistema deberá poder utilizarse para:

```text
CHARACTER
WEAPON
PROP
BUILDING
TERRAIN
VEGETATION
ENVIRONMENT
```

---

# 213. NEXT PHASE

La siguiente fase será:

```text
UAF-81.16 — WORLD, TERRAIN & ENVIRONMENT FABRICATION SYSTEM
```

Su responsabilidad será fabricar:

```text
TERRAIN
BIOMES
LANDSCAPES
ROADS
RIVERS
CLIFFS
CAVES
VEGETATION DISTRIBUTION
WORLD MATERIAL ASSIGNMENT
WORLD PARTITION
LEVEL STRUCTURE
```

sin romper la compatibilidad con los sistemas de assets existentes.
