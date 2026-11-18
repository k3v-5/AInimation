# UAF-81.13 — PROCEDURAL TERRAIN, BIOME & WORLD SURFACE FABRICATION

## UAF-81.13-ARCH

### ARQUITECTURA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE TERRENO, BIOMAS Y SUPERFICIES MUNDIALES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.13 — Procedural Terrain, Biome & World Surface Fabrication  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.12  
**Next Phase:** UAF-81.14  

---

# 1. PURPOSE

UAF-81.13 define el sistema encargado de convertir una especificación territorial en un mundo exterior coherente, navegable, visualmente consistente y preparado para Unreal Engine.

El sistema deberá controlar conjuntamente:

```text
TERRAIN
BIOMES
CLIMATE
EROSION
WATER
ROADS
VEGETATION
ROCKS
GROUND MATERIALS
NATURAL LANDMARKS
SURFACE DISTRIBUTION
NAVIGATION
GAMEPLAY
STREAMING
PERFORMANCE
```

---

# 2. PRIMARY OBJECTIVE

El objetivo no es producir ruido procedural.

El objetivo es producir:

```text
WORLD SURFACE
+
ENVIRONMENTAL LOGIC
+
GAMEPLAY LOGIC
+
ART DIRECTION
```

---

# 3. CORE PRINCIPLE

Ningún sistema de distribución deberá operar de forma completamente independiente.

La generación deberá seguir:

```text
WORLD INTENT
↓
TERRITORY
↓
TERRAIN
↓
CLIMATE
↓
BIOMES
↓
SURFACE TYPES
↓
WATER
↓
VEGETATION
↓
ROCKS / PROPS
↓
ROADS / PATHS
↓
NAVIGATION
↓
GAMEPLAY
↓
OPTIMIZATION
```

---

# 4. TERRITORY MODEL

Deberá existir:

```text
TerritoryModel
```

que represente la superficie global antes de fabricar los detalles.

---

# 5. TERRITORY PARAMETERS

Mínimo:

```text
world_width
world_length
maximum_height
minimum_height
seed
coordinate_system
world_scale
```

---

# 6. TERRAIN REPRESENTATION

El sistema deberá soportar:

```text
HEIGHTFIELD
PROCEDURAL_MESH
HYBRID_TERRAIN
```

---

# 7. HEIGHTFIELD

El heightfield será apropiado para:

```text
mountains
hills
valleys
plains
plateaus
```

---

# 8. PROCEDURAL MESH

El procedural mesh podrá utilizarse para:

```text
cliffs
overhangs
caves
rock formations
special terrain
```

---

# 9. HYBRID TERRAIN

El modo híbrido deberá permitir:

```text
heightfield
+
local mesh modifications
```

---

# 10. TERRAIN SEED

Todo terreno deberá ser reproducible mediante seed.

---

# 11. SEED STABILITY

Cambiar un parámetro no relacionado no deberá modificar áreas no afectadas.

---

# 12. TERRAIN GENERATION LAYERS

La generación deberá separarse en:

```text
BASE SHAPE
MACRO FEATURES
MESO FEATURES
MICRO FEATURES
```

---

# 13. BASE SHAPE

Define:

```text
continental form
large elevation
major slopes
major valleys
```

---

# 14. MACRO FEATURES

Define:

```text
mountains
canyons
large valleys
plateaus
coastlines
large rivers
```

---

# 15. MESO FEATURES

Define:

```text
hills
small valleys
rock fields
terraces
ravines
```

---

# 16. MICRO FEATURES

Define:

```text
surface noise
small erosion
minor depressions
surface breakup
```

---

# 17. FREQUENCY CONTROL

Cada escala deberá poder controlarse independientemente.

---

# 18. AMPLITUDE CONTROL

Cada escala deberá permitir:

```text
amplitude
frequency
octaves
falloff
```

---

# 19. TERRAIN MASK SYSTEM

Deberá existir:

```text
TerrainMaskSystem
```

---

# 20. TERRAIN MASK TYPES

Mínimo:

```text
HEIGHT
SLOPE
CURVATURE
ASPECT
DISTANCE_TO_WATER
DISTANCE_TO_ROAD
DISTANCE_TO_STRUCTURE
MOISTURE
TEMPERATURE
```

---

# 21. MASK COMPOSITION

Las máscaras deberán poder combinarse mediante:

```text
ADD
SUBTRACT
MULTIPLY
MIN
MAX
BLEND
THRESHOLD
REMAP
```

---

# 22. MASK NORMALIZATION

Toda máscara deberá poder normalizarse al rango:

```text
0.0 — 1.0
```

---

# 23. SLOPE

La pendiente deberá calcularse de forma determinista.

---

# 24. SLOPE CLASSIFICATION

Mínimo:

```text
FLAT
LOW
MEDIUM
STEEP
CLIFF
```

---

# 25. ASPECT

El sistema deberá calcular orientación de superficie.

Esto permitirá reglas como:

```text
sun_exposure
vegetation
snow
moisture
material
```

---

# 26. CURVATURE

La curvatura permitirá identificar:

```text
ridge
valley
flat_region
concavity
convexity
```

---

# 27. EROSION SYSTEM

Deberá existir:

```text
ErosionSystem
```

---

# 28. EROSION TYPES

Mínimo:

```text
HYDRAULIC
THERMAL
WIND
MANUAL_MASK
```

---

# 29. EROSION PARAMETERS

Deberán poder configurarse:

```text
iterations
strength
sediment
flow
evaporation
deposition
thermal_rate
```

---

# 30. EROSION LIMIT

La erosión deberá respetar límites para evitar destruir la navegabilidad o intención territorial.

---

# 31. EROSION DETERMINISM

La erosión deberá producir resultados reproducibles.

---

# 32. LANDMARK SYSTEM

Deberá existir:

```text
LandmarkSystem
```

---

# 33. LANDMARK TYPES

Mínimo:

```text
MOUNTAIN
CLIFF
MONOLITH
RUIN
TREE_GROUP
CRATER
LAKE
STRUCTURE
STATUE
NATURAL_FORMATION
```

---

# 34. LANDMARK PLACEMENT

Los landmarks deberán considerar:

```text
visibility
distance
terrain suitability
gameplay
composition
```

---

# 35. VISUAL COMPOSITION

El sistema deberá evitar concentrar todos los landmarks en una única zona salvo configuración explícita.

---

# 36. SILHOUETTE CONTROL

Los landmarks importantes deberán ser evaluables desde rutas principales.

---

# 37. BIOME SYSTEM

Deberá existir:

```text
BiomeSystem
```

---

# 38. BIOME PROFILE

Cada biome deberá declarar:

```text
biome_id
climate_profile
terrain_profile
material_profile
vegetation_profile
rock_profile
water_profile
atmosphere_profile
gameplay_profile
```

---

# 39. BIOME PARAMETERS

Mínimo:

```text
temperature
moisture
elevation
vegetation_density
rock_density
surface_types
```

---

# 40. BIOME MAP

El mundo deberá poder representar una distribución espacial de biomas.

---

# 41. BIOME TRANSITIONS

Las transiciones deberán poder ser:

```text
HARD
SOFT
GRADIENT
CUSTOM
```

---

# 42. TRANSITION WIDTH

Toda transición gradual deberá tener una anchura configurable.

---

# 43. BIOME PRIORITY

Cuando múltiples biomas sean posibles deberá existir una prioridad determinista.

---

# 44. BIOME CONSTRAINTS

Un biome podrá prohibir determinadas condiciones.

Ejemplo:

```text
temperature < threshold
slope > threshold
```

---

# 45. CLIMATE SYSTEM

Deberá existir:

```text
ClimateProfile
```

---

# 46. CLIMATE VARIABLES

Mínimo:

```text
temperature
humidity
precipitation
wind
sun_exposure
```

---

# 47. CLIMATE DISTRIBUTION

Las variables climáticas deberán poder variar espacialmente.

---

# 48. CLIMATE CONSISTENCY

La distribución deberá evitar combinaciones físicamente absurdas salvo que el ArtDirectionProfile las permita.

---

# 49. VEGETATION SYSTEM

Deberá existir:

```text
VegetationSystem
```

---

# 50. VEGETATION PROFILE

Cada especie o grupo deberá declarar:

```text
species_id
height_range
density
slope_range
height_range
moisture_range
temperature_range
biome_compatibility
```

---

# 51. VEGETATION DISTRIBUTION

La distribución deberá depender de máscaras ambientales.

---

# 52. VEGETATION CLUSTERS

El sistema deberá soportar agrupaciones naturales.

---

# 53. VEGETATION AVOIDANCE

La vegetación deberá poder evitar:

```text
roads
buildings
gameplay zones
navigation corridors
water
spawn areas
```

---

# 54. VEGETATION CLEARING

Deberá poder definirse una distancia mínima respecto a estructuras y rutas.

---

# 55. VEGETATION VARIATION

La variación podrá afectar:

```text
scale
rotation
species
age
health
density
material
```

---

# 56. VEGETATION INSTANCE STRATEGY

El sistema deberá decidir entre:

```text
STATIC_MESH
INSTANCED_MESH
HISM
FOLIAGE
PCG
```

según el perfil de producción.

---

# 57. VEGETATION LOD

Cada grupo vegetal deberá tener estrategia LOD.

---

# 58. VEGETATION WIND

Podrá declarar:

```text
wind_response
wind_strength
wind_profile
```

---

# 59. ROCK SYSTEM

Deberá existir:

```text
RockPlacementSystem
```

---

# 60. ROCK TYPES

Mínimo:

```text
BOULDER
CLIFF_ROCK
RUBBLE
ROCK_CLUSTER
PEBBLE
SPECIAL_FORMATION
```

---

# 61. ROCK PLACEMENT

Deberá depender de:

```text
slope
height
curvature
biome
distance
```

---

# 62. ROCK CLUSTERING

Las rocas deberán poder agruparse mediante reglas naturales.

---

# 63. ROCK ORIENTATION

La orientación podrá depender de la normal del terreno y de una variación controlada.

---

# 64. SURFACE MATERIAL SYSTEM

Deberá existir:

```text
SurfaceMaterialSystem
```

---

# 65. SURFACE TYPES

Mínimo:

```text
rock
sand
mud
soil
grass
snow
ash
metal
concrete
industrial
```

---

# 66. MATERIAL DISTRIBUTION

La distribución dependerá de:

```text
biome
height
slope
moisture
curvature
distance
manual masks
```

---

# 67. MATERIAL BLENDING

Deberá soportarse transición entre superficies.

---

# 68. MATERIAL LAYERING

Las superficies podrán tener:

```text
base
secondary
detail
decals
wetness
damage
```

---

# 69. WETNESS

La humedad podrá modificar visualmente:

```text
roughness
color
specular
surface response
```

---

# 70. SNOW SYSTEM

Cuando exista snow:

```text
height
slope
temperature
exposure
```

deberán controlar su distribución.

---

# 71. WATER SYSTEM

Deberá existir:

```text
WaterSystem
```

---

# 72. WATER TYPES

Mínimo:

```text
RIVER
LAKE
OCEAN
POOL
WATERFALL
INDUSTRIAL_WATER
```

---

# 73. RIVER GENERATION

Los ríos deberán seguir un sistema basado en:

```text
elevation
flow
basin
slope
```

y no únicamente curvas aleatorias.

---

# 74. RIVER VALIDATION

Un río deberá mantener coherencia direccional desde origen hacia destino.

---

# 75. WATER BODY

Los lagos y cuerpos de agua deberán poseer:

```text
boundary
depth
shore
material
navigation_profile
```

---

# 76. SHORE SYSTEM

Deberá existir generación de zonas costeras.

---

# 77. WATER INTERACTION

El sistema deberá poder producir metadata para:

```text
swimming
water_damage
water_audio
water_vfx
```

---

# 78. ROAD SYSTEM

Deberá existir:

```text
RoadSystem
```

---

# 79. ROAD GRAPH

Las carreteras deberán representarse mediante:

```text
RoadGraph
```

---

# 80. ROAD NODE

Cada nodo deberá contener:

```text
position
width
type
connections
slope
```

---

# 81. ROAD TYPES

Mínimo:

```text
HIGHWAY
ROAD
STREET
PATH
TRAIL
SERVICE
MILITARY
INDUSTRIAL
```

---

# 82. ROAD GENERATION

Las carreteras deberán respetar:

```text
maximum_slope
minimum_radius
terrain
structures
gameplay
```

---

# 83. ROAD WIDTH

Cada tipo de carretera deberá declarar su anchura.

---

# 84. ROAD CURVATURE

Las curvas deberán respetar un radio mínimo configurable.

---

# 85. ROAD INTERSECTIONS

Deberán soportarse:

```text
T
CROSS
ROUNDABOUT
Y
```

según profile.

---

# 86. PATH SYSTEM

Los caminos peatonales deberán utilizar reglas diferentes de las carreteras vehiculares.

---

# 87. PATH CONNECTIVITY

Los caminos deberán integrarse con:

```text
navigation
buildings
gameplay
landmarks
```

---

# 88. TERRAIN CONSTRUCTION ZONES

Deberá existir:

```text
BuildableZone
```

---

# 89. BUILDABLE CONDITIONS

Una zona podrá requerir:

```text
maximum_slope
minimum_area
minimum_clearance
terrain_type
road_access
```

---

# 90. STRUCTURE-TERRAIN INTEGRATION

Las estructuras de UAF-81.12 deberán poder consultar el terreno antes de colocarse.

---

# 91. FOUNDATION SYSTEM

Deberá existir un sistema de adaptación de estructuras al terreno.

---

# 92. FOUNDATION TYPES

Mínimo:

```text
FLAT
PIER
PLATFORM
TERRACED
CUT_AND_FILL
```

---

# 93. TERRAIN CUT

Cuando una estructura requiera modificar el terreno deberá generarse una operación explícita.

---

# 94. TERRAIN FILL

Las operaciones de relleno deberán quedar registradas.

---

# 95. NO SILENT TERRAIN DEFORMATION

No se permitirá modificar el terreno sin registrar la operación.

---

# 96. CLIFF SYSTEM

Deberá existir:

```text
CliffSystem
```

---

# 97. CLIFF VALIDATION

Los acantilados deberán comprobar:

```text
height
slope
collision
navigation
visual continuity
```

---

# 98. CAVE SYSTEM

Si el profile lo permite deberá existir soporte para:

```text
caves
tunnels
overhangs
```

---

# 99. CAVE OWNERSHIP

Las cuevas no deberán depender exclusivamente de heightfields.

Deberán poder utilizar geometría especializada.

---

# 100. NATURAL STRUCTURE SYSTEM

Deberá existir soporte para:

```text
arches
pillars
formations
bridges
ravines
```

---

# 101. ENVIRONMENTAL STORYTELLING

El sistema deberá permitir colocar elementos que comuniquen:

```text
history
damage
occupation
abandonment
conflict
industry
civilization
```

---

# 102. STORYTELLING PROFILE

Deberá existir:

```text
EnvironmentalStoryProfile
```

---

# 103. STORY ELEMENTS

Mínimo:

```text
debris
wreckage
destroyed_structures
signage
containers
burn_marks
bloodless_damage
abandoned_equipment
```

---

# 104. STORY CONSISTENCY

Los elementos deberán ser compatibles con:

```text
biome
faction
time_period
technology_level
art_direction
```

---

# 105. FACTION TERRITORY

Podrá existir:

```text
FactionTerritoryProfile
```

---

# 106. FACTION DISTRIBUTION

Una facción podrá influir sobre:

```text
structures
roads
props
lighting
materials
defenses
vegetation_control
```

---

# 107. TERRITORIAL BOUNDARIES

Las fronteras podrán ser:

```text
natural
architectural
visual
gameplay
```

---

# 108. WEATHER PROFILE

Deberá existir integración con:

```text
WeatherProfile
```

---

# 109. WEATHER VARIABLES

Mínimo:

```text
rain
fog
wind
snow
dust
storm
```

---

# 110. WEATHER IMPACT

El clima podrá modificar:

```text
surface_material
visibility
vegetation
water
lighting
VFX
audio
```

---

# 111. WEATHER DETERMINISM

Para builds reproducibles deberá existir seed o estado climático explícito.

---

# 112. GAMEPLAY TERRAIN

El terreno deberá poder declarar:

```text
combat_area
safe_area
restricted_area
hazard
objective_zone
spawn_zone
```

---

# 113. HAZARD SYSTEM

Deberá existir:

```text
TerrainHazard
```

---

# 114. HAZARD TYPES

Mínimo:

```text
cliff
fire
water
poison
radiation
electric
unstable_ground
```

---

# 115. HAZARD NAVIGATION

Los hazards deberán integrarse con navegación y gameplay.

---

# 116. PLAYER ROUTING

Deberá existir:

```text
TerrainTraversalProfile
```

---

# 117. TRAVERSAL TYPES

Mínimo:

```text
WALK
RUN
JUMP
CLIMB
SWIM
VEHICLE
```

---

# 118. TRAVERSAL VALIDATION

El sistema deberá comprobar si una superficie permite el tipo de movimiento declarado.

---

# 119. NAVIGATION TERRAIN

El terreno deberá generar metadata suficiente para navegación.

---

# 120. NAVIGATION SURFACE CLASSES

Mínimo:

```text
WALKABLE
SLOW
UNWALKABLE
CLIMBABLE
SWIMMABLE
VEHICLE
HAZARD
```

---

# 121. NAVIGATION COST

Cada superficie podrá declarar un coste de navegación.

---

# 122. AI TERRAIN

La IA podrá tener restricciones distintas a las del jugador.

---

# 123. AI TERRAIN PROFILE

Deberá soportar:

```text
infantry
large_creature
robot
vehicle
flying
```

---

# 124. TERRAIN COVER

El sistema podrá identificar:

```text
natural_cover
partial_cover
full_cover
high_ground
```

---

# 125. HIGH GROUND

Deberán identificarse posiciones tácticamente relevantes.

---

# 126. LINE OF SIGHT TERRAIN

Deberá poder analizarse la visibilidad entre puntos estratégicos.

---

# 127. OBSERVATION POINTS

El sistema podrá generar:

```text
sniper_positions
lookout_points
enemy_observation
landmark_views
```

---

# 128. COMPOSITION SYSTEM

Deberá existir:

```text
WorldCompositionSystem
```

---

# 129. COMPOSITION VARIABLES

Mínimo:

```text
focal_points
negative_space
visual_rhythm
density
silhouette
color_distribution
```

---

# 130. FOCAL POINTS

Los puntos focales deberán ser configurables.

---

# 131. NEGATIVE SPACE

El sistema deberá evitar llenar indiscriminadamente toda la superficie.

---

# 132. DENSITY MAP

Deberá existir una distribución de densidad.

---

# 133. DENSITY ZONES

Mínimo:

```text
EMPTY
LOW
MEDIUM
HIGH
HERO
```

---

# 134. ART DIRECTION

Todo biome deberá consumir el ArtDirectionProfile global.

---

# 135. COLOR DISTRIBUTION

El sistema deberá controlar familias cromáticas por región.

---

# 136. VISUAL REPETITION

Deberá detectarse repetición excesiva de:

```text
trees
rocks
props
materials
formations
```

---

# 137. REPETITION BREAKING

Las estrategias podrán incluir:

```text
rotation
scale
variant
cluster
material variation
spacing
```

---

# 138. ASSET SELECTION

Los assets deberán seleccionarse semánticamente desde AssetLibrary.

---

# 139. ASSET FALLBACK

Si falta un asset:

```text
FAIL
FALLBACK
GENERATE
```

deberá ser una decisión explícita del profile.

---

# 140. ASSET PROVENANCE

Cada instancia deberá registrar:

```text
source_asset
asset_version
generation_method
seed
```

---

# 141. WORLD INSTANCE

Deberá existir:

```text
WorldInstance
```

---

# 142. INSTANCE DATA

Mínimo:

```text
instance_id
asset_id
transform
region
biome
semantic_tags
seed
```

---

# 143. SPATIAL INDEX

Deberá existir un índice espacial para consultar instancias eficientemente.

---

# 144. SPATIAL PARTITION

El índice podrá utilizar:

```text
grid
quadtree
octree
engine_partition
```

---

# 145. WORLD CELLS

El mundo deberá dividirse en células cuando el tamaño lo requiera.

---

# 146. CELL GENERATION

Cada célula deberá poder regenerarse independientemente cuando sus dependencias lo permitan.

---

# 147. CELL DEPENDENCIES

Una célula deberá declarar dependencias con células vecinas cuando existan:

```text
roads
rivers
biome transitions
gameplay paths
large structures
```

---

# 148. BORDER VALIDATION

Las fronteras entre células deberán comprobar continuidad.

---

# 149. TERRAIN CONTINUITY

No deberán aparecer discontinuidades artificiales en:

```text
height
materials
vegetation
roads
water
```

---

# 150. STREAMING

El sistema deberá producir información para streaming.

---

# 151. STREAMING PRIORITY

Las células podrán tener:

```text
critical
high
medium
low
```

prioridad.

---

# 152. MEMORY BUDGET

Cada célula deberá declarar su presupuesto de memoria.

---

# 153. TRIANGLE BUDGET

Cada célula deberá declarar su presupuesto geométrico.

---

# 154. MATERIAL BUDGET

Cada célula deberá declarar:

```text
unique_materials
material_instances
```

---

# 155. TEXTURE BUDGET

Cada célula deberá declarar:

```text
texture_count
texture_memory
resolution_classes
```

---

# 156. INSTANCING BUDGET

Se deberá controlar el número de instancias.

---

# 157. NANITE POLICY

Los assets compatibles deberán poder utilizar Nanite según el target profile.

---

# 158. FOLIAGE POLICY

La vegetación deberá utilizar la estrategia más eficiente permitida por el target.

---

# 159. HLOD POLICY

Las regiones grandes deberán poder agruparse en HLOD.

---

# 160. WORLD PARTITION POLICY

El sistema deberá poder generar metadatos de particionado espacial.

---

# 161. PCG EXPORT

Cuando se utilice PCG, el sistema deberá distinguir:

```text
SOURCE_GRAPH
GENERATED_RESULT
```

para evitar duplicación.

---

# 162. PCG SEED

El seed de PCG deberá formar parte del EnvironmentManifest.

---

# 163. PROCEDURAL GRAPH VERSION

Toda gramática procedural deberá tener:

```text
grammar_id
version
```

---

# 164. PROFILE VERSION

Todo profile deberá versionarse.

---

# 165. GENERATION VERSION

El manifest deberá registrar la versión del generador.

---

# 166. REPRODUCTION CONTRACT

La reproducción requerirá:

```text
generator_version
profile_version
grammar_version
seed
asset_versions
```

---

# 167. CHANGE ISOLATION

Las modificaciones deberán identificar qué regiones se ven afectadas.

---

# 168. INVALIDATION GRAPH

Deberá existir:

```text
WorldInvalidationGraph
```

---

# 169. INVALIDATION EXAMPLE

Modificar:

```text
vegetation_density
```

no deberá invalidar:

```text
building_geometry
room_graph
road_graph
```

si no existen dependencias.

---

# 170. TERRAIN INVALIDATION

Modificar la altura del terreno deberá invalidar al menos:

```text
structures
roads
navigation
surface_distribution
vegetation
water
```

según dependencia.

---

# 171. BIOME INVALIDATION

Modificar un biome deberá invalidar:

```text
surface
vegetation
rocks
atmosphere
environmental_story
```

cuando corresponda.

---

# 172. VALIDATION SYSTEM

Deberá existir:

```text
WorldSurfaceValidator
```

---

# 173. TERRAIN VALIDATION

Comprobará:

```text
height_range
slope
continuity
erosion
```

---

# 174. BIOME VALIDATION

Comprobará:

```text
coverage
transitions
compatibility
distribution
```

---

# 175. VEGETATION VALIDATION

Comprobará:

```text
density
overlap
clearance
biome compatibility
navigation interference
```

---

# 176. WATER VALIDATION

Comprobará:

```text
flow
boundaries
terrain intersection
navigation
```

---

# 177. ROAD VALIDATION

Comprobará:

```text
connectivity
slope
curvature
terrain intersection
navigation
```

---

# 178. GAMEPLAY VALIDATION

Comprobará:

```text
spawn
objective
critical path
combat areas
visibility
```

---

# 179. PERFORMANCE VALIDATION

Comprobará:

```text
triangles
instances
materials
textures
memory
streaming
```

---

# 180. VISUAL VALIDATION

Comprobará:

```text
repetition
density
composition
biome coherence
art direction
```

---

# 181. WORLD GOLDEN TESTS

Deberán existir como mínimo:

```text
DESERT
FOREST
ARCTIC
VOLCANIC
URBAN_OUTSKIRTS
INDUSTRIAL_WASTELAND
ALIEN_BIOME
```

---

# 182. GOLDEN TEST DATA

Cada golden world deberá definir:

```text
seed
profile
expected_regions
expected_biomes
expected_landmarks
expected_budgets
```

---

# 183. REGRESSION TEST

Una modificación del generador no deberá cambiar resultados sin que el cambio sea explícitamente aceptado.

---

# 184. VISUAL REGRESSION

Deberán poder generarse snapshots desde:

```text
top
north
south
east
west
gameplay_views
```

---

# 185. TERRAIN DEBUG

Deberán existir overlays para:

```text
height
slope
curvature
biome
moisture
temperature
water
navigation
density
```

---

# 186. BIOME DEBUG

Deberá poder visualizarse el biome asignado a cada región.

---

# 187. VEGETATION DEBUG

Deberán poder visualizarse las reglas responsables de cada instancia.

---

# 188. ROAD DEBUG

Deberá visualizar:

```text
road graph
width
slope
connections
```

---

# 189. GAMEPLAY DEBUG

Deberá visualizar:

```text
spawn
cover
objective
critical path
hazards
```

---

# 190. MANIFEST

Cada mundo deberá generar:

```text
WorldSurfaceManifest
```

---

# 191. MANIFEST CONTENT

Mínimo:

```text
world_id
seed
terrain_profile
biome_profile
climate_profile
water_profile
vegetation_profile
road_profile
landmarks
cells
assets
materials
navigation
gameplay
budgets
validation
generator_version
```

---

# 192. CHECKPOINTS

Mínimo:

```text
terrain_checkpoint
biome_checkpoint
water_checkpoint
surface_checkpoint
vegetation_checkpoint
road_checkpoint
gameplay_checkpoint
optimization_checkpoint
```

---

# 193. RECOVERY

Un fallo durante vegetación no deberá requerir regenerar el terreno.

---

# 194. PARTIAL REGENERATION

Cada subsistema deberá poder regenerarse de forma independiente cuando el grafo de dependencias lo permita.

---

# 195. EXPORT

El sistema deberá poder exportar:

```text
terrain
landscape data
meshes
materials
foliage
instances
roads
water
metadata
navigation metadata
gameplay metadata
```

---

# 196. UNREAL TARGET

La arquitectura deberá permanecer independiente de Unreal internamente, pero deberá disponer de un adapter específico para el target Unreal.

---

# 197. ENGINE ADAPTER

Deberá existir conceptualmente:

```text
UnrealWorldAdapter
```

---

# 198. ADAPTER RESPONSIBILITIES

El adapter deberá traducir:

```text
AOE Terrain
→ Unreal Landscape / Mesh

AOE Materials
→ Unreal Material / Material Instance

AOE Foliage
→ Unreal Foliage / PCG

AOE Navigation
→ Unreal Navigation metadata

AOE World Cells
→ Unreal World Partition-compatible structures
```

---

# 199. NO ENGINE LEAKAGE

Las reglas fundamentales de generación no deberán depender directamente de APIs específicas de Unreal.

---

# 200. FINAL PIPELINE

El pipeline normativo será:

```text
WORLD INTENT
↓
TERRITORY PROFILE
↓
SEED INITIALIZATION
↓
BASE TERRAIN
↓
MACRO TERRAIN
↓
EROSION
↓
TERRAIN MASKS
↓
CLIMATE
↓
BIOME MAP
↓
BIOME TRANSITIONS
↓
SURFACE MATERIALS
↓
WATER
↓
ROADS / PATHS
↓
LANDMARKS
↓
VEGETATION
↓
ROCKS
↓
STRUCTURE INTEGRATION
↓
GAMEPLAY TERRAIN
↓
NAVIGATION
↓
WORLD COMPOSITION
↓
STREAMING
↓
OPTIMIZATION
↓
VALIDATION
↓
MANIFEST
↓
UNREAL EXPORT
```

---

# 201. FINAL ACCEPTANCE CRITERIA

UAF-81.13 será considerada implementada cuando pueda producir de forma reproducible:

```text
1 desert world
1 forest world
1 industrial wasteland
1 alien biome
1 hybrid multi-biome world
```

Cada resultado deberá incluir:

```text
terrain
biomes
surface materials
water where applicable
vegetation where applicable
rocks
landmarks
navigation
gameplay metadata
streaming metadata
performance report
manifest
```

---

# 202. NON-NEGOTIABLE

No se permitirá:

```text
random terrain without seed
random biome assignment
unvalidated vegetation
unvalidated water
unvalidated roads
untracked terrain deformation
```

---

# 203. NON-NEGOTIABLE

El terreno deberá ser considerado una dependencia de:

```text
structures
roads
navigation
vegetation
water
gameplay
```

cuando exista dependencia geométrica o semántica.

---

# 204. NON-NEGOTIABLE

La vegetación nunca deberá bloquear silenciosamente:

```text
player_spawn
critical_path
objective
navigation
combat_area
```

---

# 205. NON-NEGOTIABLE

El sistema deberá distinguir entre:

```text
GENERATED
AUTHORED
IMPORTED
HYBRID
```

para cada componente territorial.

---

# 206. NON-NEGOTIABLE

El resultado deberá ser reproducible mediante:

```text
WORLD PROFILE
+
SEED
+
GENERATOR VERSION
+
ASSET VERSIONS
```

---

# 207. NON-NEGOTIABLE

Una optimización deberá preservar:

```text
WORLD TOPOLOGY
NAVIGATION
GAMEPLAY
SEMANTICS
```

---

# 208. NON-NEGOTIABLE

Ningún subsistema podrá asumir que el mundo es plano.

---

# 209. NON-NEGOTIABLE

Ningún subsistema podrá asumir que existe un único biome.

---

# 210. NON-NEGOTIABLE

Ningún subsistema podrá asumir que todos los assets son estáticos.

---

# 211. NON-NEGOTIABLE

El sistema deberá poder representar tanto:

```text
REALISTIC WORLD
```

como:

```text
STYLIZED WORLD
```

sin cambiar la arquitectura.

---

# 212. RESULTADO ESPERADO

Al completar UAF-81.13, AOE deberá haber evolucionado desde:

```text
MODULAR ENVIRONMENT FACTORY
```

hacia:

```text
WORLD SURFACE FACTORY
```

capaz de producir un territorio completo donde:

```text
terrain
determines
biomes

biomes
determine
surface ecology

terrain + ecology
determine
distribution

distribution
supports
navigation

navigation
supports
gameplay

gameplay
constrains
composition

composition
conforms to
art direction

everything
conforms to
performance budgets
```
