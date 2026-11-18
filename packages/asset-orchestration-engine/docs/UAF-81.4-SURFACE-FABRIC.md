# UAF-81.4 — MATERIAL, TEXTURE & SURFACE AUTHORING FABRIC

## UAF-81.4-ARCH

### ARQUITECTURA DE SUPERFICIES, TEXTURAS Y MATERIALES DE PRODUCCIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.4 — Material, Texture & Surface Authoring Fabric  
**Status:** NORMATIVE  
**Version:** 1.0.0  

---

# 1. PURPOSE

UAF-81.4 define el sistema responsable de transformar la descripción superficial de un asset en:

```text
Surface Definition
        ↓
Texture Plan
        ↓
Texture Generation
        ↓
Material Definition
        ↓
Material Instance
        ↓
Target Adapter
        ↓
Unreal-Ready Surface Package
```

La fase deberá cubrir tanto superficies completamente procedurales como superficies dependientes de texturas.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá permitir producir superficies profesionales para:

```text
characters
creatures
weapons
props
architecture
vehicles
terrain
vegetation
VFX surfaces
```

---

# 3. FUNDAMENTAL PRINCIPLE

Material y texture no deberán considerarse el mismo objeto.

```text
Texture:
representación de datos superficiales.

Material:
reglas de interpretación de esos datos.

Material Instance:
configuración concreta de un material.

Surface:
descripción semántica completa de cómo debe verse una superficie.
```

---

# 4. SURFACE MODEL

Deberá existir:

```text
SurfaceDefinition
```

con:

```text
surface_id
semantic_role
material_family
shader_model
texture_policy
channel_policy
resolution_policy
tiling_policy
detail_policy
target_policy
quality_profile
```

---

# 5. SURFACE SEMANTICS

Cada superficie deberá declarar su función.

Ejemplos:

```text
SKIN
METAL
PAINTED_METAL
RUBBER
CLOTH
LEATHER
PLASTIC
GLASS
CERAMIC
STONE
WOOD
CONCRETE
ORGANIC
ENERGY
EMISSIVE
LIQUID
```

---

# 6. MATERIAL FAMILY

Una familia define comportamiento compartido.

Ejemplo:

```text
PAINTED_METAL
├── base metallic response
├── paint layer
├── wear
├── scratches
├── edge exposure
└── dirt
```

Las variantes no deberán duplicar innecesariamente el shader.

---

# 7. MATERIAL MODEL

Deberá existir:

```text
MaterialDefinition
```

con:

```text
material_id
version
shader_model
parameters
texture_bindings
layer_stack
render_settings
target_adapters
```

---

# 8. MATERIAL LAYER SYSTEM

Los materiales complejos deberán poder construirse mediante capas.

Ejemplo:

```text
Base Metal
    ↓
Primer
    ↓
Paint
    ↓
Wear
    ↓
Dirt
    ↓
Scratches
    ↓
Micro Detail
```

---

# 9. LAYER CONTRACT

Cada layer deberá declarar:

```text
layer_id
inputs
outputs
mask
blend_mode
parameters
priority
compatibility
```

---

# 10. LAYER ORDER

El orden de capas deberá ser explícito.

No deberá depender de la implementación accidental del shader.

---

# 11. MASK SYSTEM

Las máscaras deberán ser first-class artifacts.

Tipos:

```text
material mask
wear mask
dirt mask
damage mask
edge mask
region mask
paint mask
selection mask
```

---

# 12. MASK SOURCES

Una máscara podrá proceder de:

```text
geometry
curvature
AO
normal
vertex color
UV
procedural noise
attribute
texture
manual region
semantic metadata
```

---

# 13. SEMANTIC MASKS

Los componentes geométricos podrán proporcionar máscaras semánticas.

Ejemplo:

```text
armor_primary
armor_secondary
cloth_main
cloth_trim
skin
metal_exposed
```

Esto permitirá construir materiales sin depender exclusivamente de texturas pintadas.

---

# 14. PBR BASE CHANNELS

El sistema deberá soportar como mínimo:

```text
Base Color
Metallic
Roughness
Normal
Ambient Occlusion
```

---

# 15. EXTENDED CHANNELS

También deberá soportar cuando el target lo permita:

```text
Specular
Height
Displacement
Emissive
Opacity
Subsurface
Clear Coat
Clear Coat Roughness
Anisotropy
Refraction
Transmission
Custom Masks
```

---

# 16. CHANNEL POLICY

Cada material deberá declarar qué canales necesita.

No deberán generarse mapas innecesarios.

---

# 17. CHANNEL PACKING

El sistema deberá poder empaquetar canales.

Ejemplo:

```text
R = Ambient Occlusion
G = Roughness
B = Metallic
```

La política de packing deberá ser explícita y registrada.

---

# 18. PACKING VALIDATION

Antes de exportar deberá comprobarse:

```text
channel range
color space
bit depth
semantic mapping
compression compatibility
```

---

# 19. COLOR SPACE

Cada textura deberá declarar:

```text
color_space
```

Ejemplos:

```text
sRGB
Linear
NormalMap
HDR
```

No deberá inferirse únicamente por extensión o nombre de archivo.

---

# 20. NORMAL MAP POLICY

Normal maps deberán declarar:

```text
tangent_space
handedness
encoding
strength
```

El sistema deberá soportar la convención requerida por el target.

---

# 21. TEXTURE DEFINITION

Deberá existir:

```text
TextureDefinition
```

con:

```text
texture_id
version
channel
resolution
format
color_space
source
generation_method
compression_policy
mip_policy
tiling_policy
```

---

# 22. TEXTURE SOURCES

Una textura podrá proceder de:

```text
PROCEDURAL
BAKED
REFERENCE
GENERATED
PAINTED
PHOTOGRAPHIC
SCANNED
DERIVED
HYBRID
```

---

# 23. PROCEDURAL TEXTURES

Deberán soportarse patrones:

```text
noise
voronoi
cellular
gradient
mask
fractal
weathering
damage
fabric
stone
metal
organic
```

---

# 24. PROCEDURAL SEEDS

Toda generación procedural que utilice aleatoriedad deberá aceptar:

```text
seed
```

cuando sea técnicamente posible.

---

# 25. PROCEDURAL DETERMINISM

Dado:

```text
same parameters
same seed
same generator version
```

el resultado deberá ser reproducible dentro de la tolerancia definida.

---

# 26. REFERENCE-DRIVEN SURFACES

El sistema podrá utilizar referencias visuales.

La referencia deberá convertirse en datos estructurados cuando sea posible:

```text
dominant colors
material family
roughness characteristics
wear regions
pattern scale
surface variation
```

No deberá depender obligatoriamente de copiar una imagen completa sobre el asset.

---

# 27. TEXTURE GENERATION GRAPH

La generación de texturas deberá utilizar un DAG.

Ejemplo:

```text
Geometry
   ↓
Normal Bake ─────┐
Curvature ───────┤
AO ──────────────┤
Position ────────┤
                 ↓
          Material Masks
                 ↓
       Procedural Layers
                 ↓
         Channel Assembly
                 ↓
             Packing
                 ↓
          Mipmap/Compression
```

---

# 28. BAKING SYSTEM

Deberá existir:

```text
BakePlan
```

para producir mapas derivados de geometría de alta resolución.

---

# 29. BAKE TYPES

Mínimo:

```text
Normal
AO
Curvature
Position
Thickness
ID
Material ID
World Normal
Height
```

---

# 30. HIGH-TO-LOW BAKE

El sistema deberá soportar:

```text
High Resolution Geometry
        ↓
Projection
        ↓
Low Resolution Geometry
        ↓
Texture Maps
```

---

# 31. BAKE VALIDATION

Deberán detectarse:

```text
projection errors
ray misses
cage failures
seams
gradient discontinuities
incorrect normals
unexpected artifacts
```

---

# 32. CAGE SYSTEM

Cuando sea necesario, el bake deberá soportar cage.

La cage deberá tener parámetros versionados.

---

# 33. BAKE DETERMINISM

El bake deberá registrar:

```text
high_mesh_hash
low_mesh_hash
cage_hash
baker_version
settings_hash
```

---

# 34. UV DEPENDENCY

El texture pipeline deberá declarar qué UV set utiliza.

Ejemplo:

```text
UV0 → primary material
UV1 → lightmap
UV2 → detail
```

No deberá asumir siempre UV0.

---

# 35. UDIM

El sistema deberá soportar UDIM para assets que lo requieran.

Deberá registrar:

```text
tile_id
tile_resolution
tile_usage
```

---

# 36. TEXTURE RESOLUTION

La resolución deberá ser una política, no una constante.

Perfiles mínimos:

```text
LOW
MEDIUM
HIGH
HERO
CINEMATIC
```

---

# 37. RESOLUTION DECISION

La resolución deberá considerar:

```text
surface area
camera importance
texel density
material complexity
target platform
memory budget
```

---

# 38. TEXTURE BUDGET

Cada asset podrá declarar:

```text
max_texture_memory
max_texture_count
max_resolution
max_udim_tiles
```

El planner deberá respetar estos límites.

---

# 39. MATERIAL INSTANCE

Deberá existir:

```text
MaterialInstanceDefinition
```

permitiendo modificar parámetros sin duplicar el material base.

---

# 40. INSTANCE PARAMETERS

Ejemplos:

```text
base_color_tint
roughness_multiplier
metallic_value
normal_strength
wear_amount
dirt_amount
emissive_intensity
detail_scale
```

---

# 41. PARAMETER VALIDATION

Cada parámetro deberá tener:

```text
type
range
default
units
allowed_targets
```

---

# 42. MATERIAL VARIANTS

Un mismo material podrá producir:

```text
clean
damaged
dirty
battle_worn
prototype
elite
corrupted
```

mediante instancias o capas.

---

# 43. CHARACTER SURFACE MODEL

Los personajes deberán poder tener regiones independientes:

```text
skin
hair
eyes
teeth
clothing
armor
weapons
accessories
```

Cada región podrá utilizar una familia de materiales distinta.

---

# 44. SKIN MATERIAL

Skin podrá requerir:

```text
base color
roughness
normal
subsurface
micro normal
oil variation
color variation
```

según quality profile.

---

# 45. HAIR MATERIAL

Hair podrá utilizar:

```text
strand/card data
base color
roughness
anisotropy
root variation
tip variation
```

cuando el target lo permita.

---

# 46. CLOTH MATERIAL

Cloth podrá utilizar:

```text
fiber pattern
roughness variation
weave normal
dirt
wear
edge variation
```

---

# 47. METAL MATERIAL

Metal deberá poder representar:

```text
base metal
paint
oxidation
scratches
edge wear
dirt
roughness variation
```

---

# 48. DAMAGE SYSTEM

El sistema deberá soportar daño superficial procedural.

Tipos:

```text
scratch
dent
paint_loss
burn
corrosion
fracture
impact
contamination
```

---

# 49. DAMAGE MASKS

El daño deberá poder utilizar:

```text
semantic region
curvature
impact data
procedural distribution
seed
manual mask
```

---

# 50. WEATHERING

Deberá existir un sistema de weathering capaz de utilizar:

```text
gravity
exposure
contact
water
dirt accumulation
wear
age
environment type
```

---

# 51. ENVIRONMENT-AWARE MATERIALS

Los materiales podrán recibir datos del entorno.

Ejemplo:

```text
desert
snow
rain
industrial
underwater
toxic
```

La misma superficie podrá cambiar de apariencia sin reemplazar el material base.

---

# 52. DECAL SYSTEM

Deberá soportarse:

```text
logos
warning signs
numbers
scratches
blood-like stains
damage markings
team markings
```

como elementos independientes cuando sea apropiado.

---

# 53. DECAL POLICY

Los decals deberán poder configurarse como:

```text
geometry
material layer
texture
runtime decal
baked detail
```

según target y coste.

---

# 54. TRIM SHEETS

El sistema deberá soportar trim sheets para assets modulares.

Deberá existir:

```text
TrimDefinition
```

con regiones semánticas.

---

# 55. MATERIAL REUSE

El sistema deberá maximizar reutilización mediante:

```text
master materials
material families
instances
trim sheets
shared masks
shared procedural functions
```

---

# 56. MATERIAL DUPLICATION CONTROL

No deberán crearse materiales duplicados si:

```text
same shader
same parameters
same texture bindings
same target
```

salvo que exista una razón explícita.

---

# 57. TEXTURE DEDUPLICATION

Texturas idénticas deberán poder detectarse mediante hash.

---

# 58. TEXTURE ATLAS

Deberá soportarse atlas cuando sea beneficioso.

El atlas deberá conservar:

```text
source textures
region mapping
UV transformation
padding
```

---

# 59. VIRTUAL TEXTURE POLICY

Cuando el target lo soporte, el planner podrá seleccionar virtual textures.

La decisión deberá registrarse.

---

# 60. COMPRESSION

Cada textura deberá declarar:

```text
compression_policy
```

según:

```text
channel type
platform
quality
memory budget
```

---

# 61. MIPMAP POLICY

Deberá existir una política explícita para:

```text
mip generation
sharpening
bias
streaming
```

---

# 62. TEXTURE STREAMING

Los assets deberán poder declarar prioridades de streaming.

Ejemplo:

```text
hero
gameplay
background
environment
cosmetic
```

---

# 63. SHADER COMPLEXITY

La superficie deberá tener un presupuesto de shader.

Deberán evaluarse:

```text
instruction count
texture samples
branches
layer count
runtime cost
```

cuando la información esté disponible.

---

# 64. SHADER VARIANTS

El sistema deberá evitar generar variantes innecesarias.

Las features opcionales deberán poder habilitarse mediante configuración.

---

# 65. STATIC SWITCH POLICY

Cuando el target requiera optimización, las features que no necesiten cambiar en runtime podrán convertirse en static configuration.

---

# 66. EMISSIVE POLICY

La intensidad emisiva deberá estar limitada por quality/target profile.

Los valores fuera del rango permitido deberán generar warning o error según severidad.

---

# 67. MATERIAL VALIDATION

Deberán validarse:

```text
missing textures
incorrect color spaces
invalid ranges
missing channels
incorrect normal format
duplicate materials
unsupported shader features
texture budget
shader budget
```

---

# 68. VISUAL MATERIAL VALIDATION

También deberán realizarse pruebas visuales.

Mínimo:

```text
neutral lighting
high contrast lighting
low lighting
close-up
distance view
```

---

# 69. MATERIAL REGISTRY

Deberá existir:

```text
MaterialRegistry
```

con:

```text
register()
get()
find()
find_family()
find_compatible()
```

---

# 70. TEXTURE REGISTRY

Deberá existir:

```text
TextureRegistry
```

permitiendo:

```text
register()
get()
find()
deduplicate()
```

---

# 71. SURFACE REGISTRY

Deberá existir:

```text
SurfaceRegistry
```

para relacionar:

```text
surface
material
textures
masks
target
```

---

# 72. UNREAL ADAPTER

La definición de material deberá ser independiente de Unreal.

Deberá existir un adaptador:

```text
UnrealMaterialAdapter
```

responsable de traducir:

```text
MaterialDefinition
        ↓
UE Material
        ↓
UE Material Instance
```

---

# 73. UNREAL NAMING

El adapter deberá aplicar una política de nombres consistente.

Los nombres deberán derivarse de IDs semánticos y versiones.

---

# 74. UNREAL ASSET REFERENCES

Las referencias deberán utilizar IDs internos y paths configurables.

No deberán existir rutas absolutas codificadas.

---

# 75. MATERIAL PACKAGE

Cada material deberá poder producir:

```text
MaterialDefinition
Textures
Masks
MaterialInstanceDefinitions
Metadata
ValidationReport
```

---

# 76. SURFACE PACKAGE

Un asset deberá poder producir un paquete:

```text
SurfacePackage
├── Materials
├── Textures
├── Masks
├── UV metadata
├── Target metadata
├── Validation
└── Provenance
```

---

# 77. PROVENANCE

Cada texture deberá registrar:

```text
source
generator
generator_version
seed
input_hashes
parameters
tool_version
```

---

# 78. REBUILD

Si cambia:

```text
roughness parameter
```

el sistema deberá determinar si necesita reconstruir:

```text
material only
```

y no:

```text
geometry
UV
LOD
```

---

# 79. DIRTY GRAPH

El surface system deberá integrarse con el dependency graph global.

Ejemplo:

```text
Geometry changed
      ↓
Curvature
      ↓
Bake
      ↓
Masks
      ↓
Textures
      ↓
Material
```

---

# 80. CACHE

Podrán cachearse:

```text
bakes
masks
procedural textures
packed textures
materials
```

La cache key deberá incluir todos los inputs relevantes.

---

# 81. QUALITY PROFILES

Mínimo:

```text
PROTOTYPE
GAMEPLAY
PRODUCTION
HERO
CINEMATIC
```

Cada uno podrá definir:

```text
texture resolution
channel count
detail level
shader complexity
material layers
bake quality
```

---

# 82. TARGET PROFILES

Mínimo:

```text
UE5_PC
UE5_CONSOLE
UE5_HIGH_END
UE5_MOBILE
CINEMATIC_RENDER
```

---

# 83. CROSS-TARGET GENERATION

Una misma SurfaceDefinition deberá poder generar diferentes outputs.

Ejemplo:

```text
HeroMaterial
├── PC High
├── Console
└── Preview
```

---

# 84. FAILURE MODES

Errores mínimos:

```text
TEXTURE_GENERATION_ERROR
BAKE_ERROR
UV_DEPENDENCY_ERROR
MATERIAL_COMPILATION_ERROR
UNSUPPORTED_FEATURE
BUDGET_EXCEEDED
INVALID_CHANNEL
INVALID_COLOR_SPACE
MISSING_INPUT
```

---

# 85. FALLBACK

Un fallback podrá cambiar:

```text
procedural → baked
UDIM → atlas
high resolution → lower resolution
complex shader → simplified shader
```

siempre que las hard requirements continúen satisfechas.

---

# 86. QUALITY DEGRADATION

Toda degradación deberá registrarse:

```text
original_requirement
actual_result
reason
severity
```

---

# 87. SECURITY

Los generadores de superficies no deberán ejecutar procesos arbitrarios fuera de las capacidades y permisos declarados.

---

# 88. TESTING

Cada componente deberá disponer de:

```text
contract tests
generation tests
determinism tests
color-space tests
channel tests
budget tests
validation tests
target tests
```

---

# 89. INTEGRATION TEST — CHARACTER

Deberá construirse un personaje con:

```text
skin
eyes
hair
cloth
painted metal
bare metal
emissive element
```

y cada región deberá generar correctamente su SurfaceDefinition.

---

# 90. INTEGRATION TEST — WEAPON

Un arma deberá demostrar:

```text
metal
paint
rubber
emissive
damage
decals
```

utilizando material families e instancias reutilizables.

---

# 91. INTEGRATION TEST — MODULAR ENVIRONMENT

Un kit arquitectónico deberá demostrar:

```text
concrete
painted metal
glass
dirt
wear
trim sheet
material instances
```

sin crear duplicados innecesarios.

---

# 92. INTEGRATION TEST — TARGET

El mismo asset deberá producir al menos:

```text
PRODUCTION + UE5_PC
```

y:

```text
GAMEPLAY + UE5_CONSOLE
```

con diferencias de calidad declaradas.

---

# 93. ACCEPTANCE CRITERIA

UAF-81.4 estará completa cuando pueda:

```text
1. definir surfaces;
2. definir material families;
3. crear material layers;
4. crear procedural textures;
5. generar baked textures;
6. producir masks;
7. empaquetar canales;
8. validar color spaces;
9. soportar UDIM;
10. soportar trim sheets;
11. soportar texture atlases;
12. generar material instances;
13. controlar shader complexity;
14. controlar texture budgets;
15. generar variantes;
16. aplicar damage/weathering;
17. reutilizar materiales;
18. deduplicar texturas;
19. cachear resultados;
20. reconstruir parcialmente;
21. generar outputs para Unreal;
22. registrar provenance;
23. mantener determinismo;
24. validar visualmente;
25. soportar distintos quality profiles.
```

---

# 94. CRITICAL ARCHITECTURAL TEST

Debe demostrarse que:

```text
Character
```

puede cambiar:

```text
Armor Material
```

sin reconstruir:

```text
Body
Face
Hair
Skeleton
```

y que cambiar:

```text
Body Geometry
```

invalida únicamente los artifacts superficiales que realmente dependan de esa geometría.

---

# 95. FINAL ARCHITECTURAL MODEL

Después de UAF-81.4:

```text
                    ASSET
                      │
                COMPONENTS
                      │
              ┌───────┴────────┐
              │                │
          GEOMETRY          SURFACE
              │                │
       Primary/Secondary   Material
       Tertiary/Micro      Textures
              │             Masks
              │             Layers
              │                │
              └───────┬────────┘
                      ↓
                  VALIDATION
                      ↓
                  OPTIMIZATION
                      ↓
               UNREAL ADAPTER
                      ↓
               PRODUCTION PACKAGE
```

---

# 96. NEXT PHASE

# UAF-81.5 — CHARACTER RIGGING, SKINNING & DEFORMATION FABRIC

Esta fase deberá resolver uno de los principales límites actuales del sistema.

No bastará con crear una jerarquía de huesos.

Deberá establecer una fábrica completa para:

```text
Skeleton Definition
Bone Hierarchy
Joint Constraints
Bind Pose
Skin Weights
Weight Normalization
Deformation Zones
Corrective Shapes
Facial Rig
Facial Blendshapes
Animation Compatibility
IK
FK
Control Rig
Retargeting
Pose Validation
Deformation Validation
LOD Skinning
Unreal Skeleton
Physics Asset
```

El objetivo será que un personaje generado geométricamente no sea solamente un modelo estático, sino un **asset animable y utilizable realmente dentro de producción**.
