# UAF-81.56 — UNIVERSAL WORLD, ENVIRONMENT, TERRAIN, VEGETATION & PROCEDURAL SCENE SYSTEM

## UAF-81.56-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA UNIVERSAL DE MUNDO, ENTORNO, TERRENO, VEGETACIÓN Y ESCENAS PROCEDURALES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.56 — Universal World, Environment, Terrain, Vegetation & Procedural Scene System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.55  
**Next Phase:** UAF-81.57  

---

# 1. PURPOSE

UAF-81.56 define el sistema universal para generar, organizar, validar, optimizar y exportar mundos y escenas procedurales.

El sistema deberá transformar:

```text
CHARACTER
ASSET
MATERIAL
ANIMATION
```

en una estructura coherente de:

```text
WORLD
REGIONS
BIOMES
TERRAIN
VEGETATION
ROCKS
WATER
ROADS
BUILDINGS
PROPS
LIGHTING HOOKS
NAVIGATION
COLLISION
STREAMING
HLOD
```

---

# 2. PRIMARY OBJECTIVE

El resultado deberá ser un:

```text
ProductionReadyWorld
```

reproducible mediante:

```text
world_definition
seed
generator_version
environment_profile
biome_profile
terrain_profile
scatter_profile
streaming_profile
lod_profile
```

---

# 3. WORLD DATA MODEL

Deberá existir:

```text
WorldDefinition
```

con:

```text
world_id
name
seed
dimensions
coordinate_system
regions
biomes
terrain
water
roads
structures
vegetation
props
navigation
streaming
lighting
environment
metadata
```

---

# 4. WORLD IDENTIFIER

El world_id deberá ser estable.

Cambiar el nombre visible del mundo no deberá cambiar el identificador lógico salvo que se solicite explícitamente.

---

# 5. WORLD SEED

Toda generación procedural deberá aceptar:

```text
seed
```

como parámetro obligatorio.

No deberá dependerse de random global.

---

# 6. WORLD DIMENSIONS

Deberá soportar:

```text
FINITE
INFINITE
TILED
STREAMED
```

---

# 7. WORLD BOUNDS

Un mundo finito deberá tener:

```text
min_x
max_x
min_y
max_y
min_z
max_z
```

---

# 8. WORLD COORDINATE SYSTEM

Deberá declarar:

```text
up_axis
forward_axis
handedness
unit_scale
origin
```

---

# 9. WORLD REGION

Deberá existir:

```text
WorldRegion
```

con:

```text
region_id
bounds
biomes
terrain
assets
streaming_policy
navigation_policy
```

---

# 10. REGION HIERARCHY

Deberá soportarse:

```text
WORLD
 └── CONTINENT
      └── REGION
           └── SUBREGION
                └── CELL
```

---

# 11. WORLD CELL

Deberá existir:

```text
WorldCell
```

Cada cell deberá tener:

```text
cell_id
bounds
origin
lod
assets
terrain_reference
streaming_state
```

---

# 12. CELL SIZE

El tamaño deberá ser configurable por profile.

No graphical estar hardcoded.

---

# 13. CELL COORDINATES

Deberán ser enteros:

```text
cell_x
cell_y
cell_z
```

para garantizar estabilidad.

---

# 14. WORLD HASH

Deberá existir:

```text
WorldHash
```

derivado de los inputs relevantes.

---

# 15. WORLD HASH INPUTS

Mínimo:

```text
world_definition
seed
terrain_profile
biome_profile
scatter_profile
asset_library_hash
generator_version
```

---

# 16. SCENE GRAPH

Deberá existir:

```text
WorldSceneGraph
```

---

# 17. SCENE NODE

Cada nodo deberá contener:

```text
node_id
parent_id
transform
bounds
asset_reference
children
visibility
streaming
metadata
```

---

# 18. SCENE NODE TYPES

Mínimo:

```text
WORLD
REGION
CELL
TERRAIN
WATER
VEGETATION
STRUCTURE
ROAD
PROP
LIGHT
VOLUME
NAVIGATION
CUSTOM
```

---

# 19. TRANSFORM REPRESENTATION

Deberá utilizar:

```text
translation
rotation
scale
```

con representación determinista.

---

# 20. HIERARCHY VALIDATION

Deberá detectar:

```text
missing_parent
cyclic_parent
duplicate_node_id
invalid_transform
orphan_node
```

---

# 21. BIOME SYSTEM

Deberá existir:

```text
BiomeDefinition
```

---

# 22. BIOME DATA

Mínimo:

```text
biome_id
name
temperature_range
humidity_range
altitude_range
slope_range
terrain_profile
vegetation_profile
rock_profile
structure_profile
color_profile
```

---

# 23. BIOME TYPES

Mínimo:

```text
DESERT
SAVANNA
GRASSLAND
FOREST
RAINFOREST
TUNDRA
SNOW
MOUNTAIN
SWAMP
COAST
URBAN
CUSTOM
```

---

# 24. BIOME DISTRIBUTION

Deberá soportar:

```text
height
slope
temperature
humidity
moisture
distance_to_water
distance_to_road
noise
manual_mask
```

---

# 25. BIOME WEIGHT

Cada biome deberá producir:

```text
weight
```

normalizado.

---

# 26. BIOME BLENDING

Deberán existir transiciones suaves entre biomas.

---

# 27. BIOME PRIORITY

Cuando existan reglas contradictorias deberá existir prioridad determinista.

---

# 28. BIOME MASK

Deberá existir:

```text
BiomeMask
```

---

# 29. BIOME MASK CHANNELS

Mínimo:

```text
PRIMARY
SECONDARY
TERTIARY
TRANSITION
EXCLUSION
```

---

# 30. BIOME VALIDATION

Deberá detectar:

```text
invalid_range
overlapping_exclusion
empty_world_coverage
unreachable_biome
invalid_priority
```

---

# 31. TERRAIN SYSTEM

Deberá existir:

```text
TerrainDefinition
```

---

# 32. TERRAIN REPRESENTATION

Deberá soportar:

```text
HEIGHTFIELD
VOXEL
MESH
HYBRID
```

---

# 33. HEIGHTFIELD

Deberá contener:

```text
resolution_x
resolution_y
height_scale
samples
```

---

# 34. HEIGHTFIELD NORMALIZATION

Los valores deberán poder normalizarse a:

```text
0..1
```

antes de aplicar escala física.

---

# 35. TERRAIN GENERATORS

Mínimo:

```text
FLAT
HILLS
MOUNTAIN
VALLEY
RIDGED
FRACTAL
NOISE
CUSTOM
```

---

# 36. NOISE SYSTEM

Deberá existir:

```text
NoiseDefinition
```

---

# 37. NOISE PARAMETERS

Mínimo:

```text
seed
frequency
amplitude
octaves
lacunarity
gain
domain_scale
```

---

# 38. NOISE TYPES

Mínimo:

```text
VALUE
PERLIN
SIMPLEX
WORLEY
RIDGED
FRACTAL
CUSTOM
```

---

# 39. NOISE DETERMINISM

El mismo:

```text
seed
coordinates
parameters
generator_version
```

deberá producir exactamente el mismo resultado lógico.

---

# 40. TERRAIN LAYERS

Deberán existir:

```text
base_height
detail_height
erosion
depression
ridge
flatten
```

---

# 41. TERRAIN OPERATORS

Mínimo:

```text
ADD
SUBTRACT
MULTIPLY
MIN
MAX
LERP
CLAMP
SMOOTH
```

---

# 42. TERRAIN MODIFIERS

Deberán soportarse:

```text
TERRACE
EROSION
SMOOTH
STAMP
CRATER
RIDGE
VALLEY
FLATTEN
CUSTOM
```

---

# 43. TERRAIN STAMP

Deberá existir:

```text
TerrainStamp
```

con:

```text
shape
position
rotation
scale
strength
falloff
```

---

# 44. TERRAIN SPLATMAP

Deberá existir:

```text
TerrainSplatDefinition
```

---

# 45. SPLAT CHANNELS

Mínimo:

```text
grass
dirt
rock
sand
snow
mud
custom
```

---

# 46. MATERIAL TERRAIN MAPPING

Cada terreno deberá poder asociar:

```text
terrain_layer
material_reference
uv_profile
macro_variation
detail_profile
```

---

# 47. TERRAIN MATERIAL BLENDING

Deberá existir blending por:

```text
height
slope
biome
noise
manual_mask
```

---

# 48. SLOPE CALCULATION

Deberá existir:

```text
SlopeField
```

---

# 49. SLOPE RANGE

El slope deberá poder expresarse en:

```text
degrees
normalized
```

---

# 50. TERRAIN NORMALS

Deberán calcularse de forma estable.

---

# 51. TERRAIN TANGENTS

Cuando el backend lo requiera deberán generarse de forma consistente.

---

# 52. TERRAIN COLLISION

Deberá existir:

```text
TerrainCollisionProfile
```

---

# 53. COLLISION MODES

Mínimo:

```text
HEIGHTFIELD
COMPLEX_MESH
SIMPLIFIED
CUSTOM
```

---

# 54. TERRAIN NAVIGATION

Deberá poder derivarse:

```text
walkable
non_walkable
water
cliff
blocked
```

---

# 55. TERRAIN VALIDATION

Deberá detectar:

```text
holes
invalid_normals
height_outlier
collision_mismatch
navigation_mismatch
uv_failure
```

---

# 56. EROSION

Deberá existir:

```text
ErosionProfile
```

---

# 57. EROSION TYPES

Mínimo:

```text
HYDRAULIC
THERMAL
WIND
CUSTOM
```

---

# 58. EROSION DETERMINISM

La erosión procedural deberá aceptar seed explícito.

---

# 59. WATER SYSTEM

Deberá existir:

```text
WaterDefinition
```

---

# 60. WATER TYPES

Mínimo:

```text
OCEAN
SEA
LAKE
RIVER
STREAM
POND
WATERFALL
CUSTOM
```

---

# 61. WATER BODY

Deberá contener:

```text
water_id
type
bounds
surface_level
depth
material_reference
flow_profile
shore_profile
```

---

# 62. LAKE GENERATION

Deberá soportar:

```text
basin
shoreline
surface
depth
```

---

# 63. RIVER GENERATION

Deberá existir:

```text
RiverDefinition
```

---

# 64. RIVER DATA

Mínimo:

```text
source
destination
control_points
width
depth
flow
slope
```

---

# 65. RIVER VALIDATION

Deberá detectar:

```text
uphill_flow
self_intersection
invalid_source
invalid_destination
negative_width
```

---

# 66. WATER FLOW

Deberá existir:

```text
FlowField
```

---

# 67. WATERFALL

Deberá generarse cuando:

```text
slope > waterfall_threshold
```

según profile.

---

# 68. SHORELINE

Deberá existir:

```text
ShorelineDefinition
```

---

# 69. SHORE MATERIAL

Podrá depender de:

```text
depth
slope
water_type
biome
wave_exposure
```

---

# 70. WATER VALIDATION

Mínimo:

```text
surface_continuity
terrain_intersection
shoreline_validity
flow_direction
collision
```

---

# 71. VEGETATION SYSTEM

Deberá existir:

```text
VegetationDefinition
```

---

# 72. VEGETATION CATEGORIES

Mínimo:

```text
TREE
SHRUB
GRASS
FLOWER
FERN
MUSHROOM
CACTUS
CROP
CUSTOM
```

---

# 73. VEGETATION SPECIES

Deberá existir:

```text
VegetationSpecies
```

con:

```text
species_id
asset_variants
scale_range
rotation_range
density
biome_rules
slope_rules
height_rules
water_rules
```

---

# 74. VEGETATION SCATTER

Deberá existir:

```text
VegetationScatterProfile
```

---

# 75. SCATTER PARAMETERS

Mínimo:

```text
density
seed
min_distance
scale_min
scale_max
rotation_mode
slope_min
slope_max
height_min
height_max
```

---

# 76. POISSON DISTRIBUTION

Deberá soportarse:

```text
POISSON
```

para distribución con distancia mínima.

---

# 77. GRID DISTRIBUTION

Deberá soportarse:

```text
GRID
```

---

# 78. RANDOM DISTRIBUTION

Deberá soportarse:

```text
JITTERED_RANDOM
```

---

# 79. CLUSTER DISTRIBUTION

Deberá soportarse:

```text
CLUSTER
```

---

# 80. VEGETATION MASKS

Deberá soportar:

```text
BIOME
HEIGHT
SLOPE
MOISTURE
DISTANCE_WATER
DISTANCE_ROAD
CUSTOM
```

---

# 81. VEGETATION COLLISION

Deberá permitir:

```text
NONE
SIMPLE
COMPLEX
PROXY
```

---

# 82. TREE VARIATION

Deberá variar determinísticamente:

```text
scale
rotation
variant
lean
color
```

---

# 83. FOLIAGE SYSTEM

Deberá existir:

```text
FoliageDefinition
```

---

# 84. FOLIAGE LAYERS

Mínimo:

```text
GROUND_COVER
LOW
MEDIUM
CANOPY
UNDERSTORY
```

---

# 85. FOLIAGE DENSITY

Deberá poder depender de:

```text
biome
slope
height
moisture
noise
```

---

# 86. FOLIAGE LOD

Deberá soportar:

```text
INSTANCE
BILLBOARD
IMPOSTOR
DISABLED
```

según distancia y profile.

---

# 87. ROCK SYSTEM

Deberá existir:

```text
RockDefinition
```

---

# 88. ROCK TYPES

Mínimo:

```text
BOULDER
CLIFF
PEBBLE
OUTCROP
COLUMN
CUSTOM
```

---

# 89. ROCK SCATTER

Deberá reutilizar el sistema general de scatter.

---

# 90. ROCK ORIENTATION

Deberá soportar:

```text
RANDOM
SURFACE_ALIGNED
GRAVITY_ALIGNED
CUSTOM
```

---

# 91. CLIFF GENERATION

Deberá poder derivarse de:

```text
slope
height
noise
biome
```

---

# 92. PROP SYSTEM

Deberá existir:

```text
PropDefinition
```

---

# 93. PROP CATEGORIES

Mínimo:

```text
FENCE
SIGN
LAMP
BENCH
CONTAINER
DECORATION
DEBRIS
VEHICLE_PROXY
CUSTOM
```

---

# 94. PROP PLACEMENT

Deberá soportar:

```text
SURFACE
ROAD
BUILDING
WATER
CUSTOM
```

---

# 95. PROP EXCLUSION

Deberá existir:

```text
ExclusionVolume
```

para impedir colocaciones.

---

# 96. EXCLUSION TYPES

Mínimo:

```text
CIRCLE
BOX
CAPSULE
POLYGON
HEIGHTFIELD
CUSTOM
```

---

# 97. ASSET SCATTER SYSTEM

Deberá existir:

```text
UniversalScatterSystem
```

---

# 98. SCATTER INPUT

Mínimo:

```text
surface
mask
density
seed
asset_set
constraints
```

---

# 99. SCATTER CONSTRAINTS

Mínimo:

```text
MIN_DISTANCE
MAX_DISTANCE
SLOPE
HEIGHT
BIOME
WATER_DISTANCE
ROAD_DISTANCE
EXCLUSION
CUSTOM
```

---

# 100. SCATTER OUTPUT

Cada instancia deberá contener:

```text
instance_id
asset_id
position
rotation
scale
variant
cell_id
seed_path
```

---

# 101. INSTANCE ID

Deberá ser estable respecto a:

```text
world
cell
generator
seed
local_index
```

---

# 102. STABLE REGENERATION

Regenerar una cell sin modificar sus inputs deberá producir los mismos:

```text
instance_id
asset_id
transform
variant
```

---

# 103. BUILDING SYSTEM

Deberá existir:

```text
BuildingDefinition
```

---

# 104. BUILDING TYPES

Mínimo:

```text
HOUSE
APARTMENT
OFFICE
WAREHOUSE
SHOP
INDUSTRIAL
RUIN
CUSTOM
```

---

# 105. BUILDING PARAMETERS

Mínimo:

```text
footprint
floors
height
roof_type
wall_material
roof_material
window_profile
door_profile
variation
```

---

# 106. PROCEDURAL BUILDING

Deberá poder generar:

```text
walls
floors
windows
doors
roof
stairs
facade_details
```

---

# 107. BUILDING VARIATION

Deberá utilizar seed determinista.

---

# 108. BUILDING VALIDATION

Deberá detectar:

```text
invalid_footprint
zero_floor
invalid_height
missing_roof
interior_collision
self_intersection
```

---

# 109. ROAD SYSTEM

Deberá existir:

```text
RoadDefinition
```

---

# 110. ROAD TYPES

Mínimo:

```text
HIGHWAY
ROAD
STREET
LANE
PATH
TRAIL
BRIDGE
CUSTOM
```

---

# 111. ROAD PATH

Deberá contener:

```text
control_points
width
banking
slope_limit
surface_profile
```

---

# 112. ROAD GENERATION

Deberá generar:

```text
road_surface
shoulders
markings
curbs
barriers
```

según profile.

---

# 113. ROAD-TERRAIN INTEGRATION

Las carreteras deberán poder modificar localmente el terreno.

---

# 114. ROAD CUT/FILL

Deberá soportar:

```text
CUT
FILL
BLEND
```

---

# 115. ROAD VALIDATION

Deberá detectar:

```text
excessive_slope
self_intersection
terrain_gap
terrain_penetration
invalid_width
```

---

# 116. BRIDGE SYSTEM

Deberá existir soporte para puentes.

Un bridge deberá declarar:

```text
start
end
span
height
width
support_profile
```

---

# 117. BRIDGE VALIDATION

Deberá comprobar:

```text
terrain_clearance
water_clearance
support_alignment
collision
```

---

# 118. WORLD PATH SYSTEM

Deberá existir:

```text
PathNetwork
```

---

# 119. PATH NODE

Mínimo:

```text
node_id
position
type
connections
```

---

# 120. PATH TYPES

```text
ROAD
FOOTPATH
TRAIL
SERVICE
NAVIGATION
CUSTOM
```

---

# 121. PATH GRAPH VALIDATION

Deberá detectar:

```text
orphan_node
invalid_edge
self_edge
disconnected_graph
```

---

# 122. NAVIGATION SYSTEM

Deberá existir:

```text
NavigationDefinition
```

---

# 123. NAVIGATION SOURCES

Mínimo:

```text
TERRAIN
ROAD
BUILDING
WATER
PROP
CUSTOM
```

---

# 124. NAVIGATION FLAGS

Mínimo:

```text
WALKABLE
BLOCKED
WATER
CLIMBABLE
JUMPABLE
DANGEROUS
CUSTOM
```

---

# 125. NAVIGATION REGION

Deberá soportar regiones separadas.

---

# 126. NAVIGATION CONNECTIVITY

Deberá comprobarse conectividad entre regiones cuando sea requerida.

---

# 127. NAVIGATION VALIDATION

Deberá detectar:

```text
unreachable_region
invalid_surface
missing_connection
invalid_height
```

---

# 128. WORLD COLLISION

Deberá existir:

```text
WorldCollisionProfile
```

---

# 129. COLLISION LAYERS

Mínimo:

```text
WORLD
TERRAIN
VEGETATION
STRUCTURE
ROAD
WATER
PROP
NAVIGATION
CUSTOM
```

---

# 130. COLLISION COMPLEXITY

Deberá soportar:

```text
SIMPLE
COMPLEX
HYBRID
```

---

# 131. WORLD PARTITION

Deberá existir:

```text
WorldPartitionProfile
```

---

# 132. PARTITION CELL

Cada cell deberá tener:

```text
bounds
load_distance
unload_distance
priority
runtime_state
```

---

# 133. STREAMING STATES

Mínimo:

```text
UNLOADED
LOADING
LOADED
VISIBLE
HIDDEN
UNLOADING
```

---

# 134. STREAMING DETERMINISM

La asignación de assets a cells deberá ser determinista.

---

# 135. LEVEL STREAMING

Deberá soportar:

```text
ON_DEMAND
DISTANCE
PRIORITY
MANUAL
```

---

# 136. HLOD

Deberá existir:

```text
WorldHLODProfile
```

---

# 137. HLOD LEVELS

Mínimo:

```text
HLOD0
HLOD1
HLOD2
HLOD3
```

---

# 138. HLOD GROUPING

Podrá agrupar por:

```text
cell
material
asset_type
distance
region
```

---

# 139. HLOD VALIDATION

Deberá comprobar:

```text
bounds
visibility
material_compatibility
transition
triangle_budget
```

---

# 140. IMPOSTOR SYSTEM

Deberá existir:

```text
ImpostorDefinition
```

para assets de larga distancia.

---

# 141. IMPOSTOR VALIDATION

Deberá verificar:

```text
coverage
orientation
alpha
silhouette
distance
```

---

# 142. WORLD LIGHTING HOOKS

UAF no deberá asumir un único renderer.

Deberá exponer:

```text
LightingProfile
```

con hooks para:

```text
SUN
MOON
SKY
AMBIENT
FOG
VOLUMETRICS
LOCAL_LIGHTS
```

---

# 143. TIME OF DAY HOOK

Deberá existir:

```text
TimeOfDayProfile
```

---

# 144. TIME PARAMETERS

Mínimo:

```text
time
sun_direction
sun_intensity
sky_color
ambient_intensity
```

---

# 145. WEATHER HOOK

Deberá existir:

```text
WeatherProfile
```

---

# 146. WEATHER TYPES

Mínimo:

```text
CLEAR
CLOUDY
RAIN
STORM
SNOW
FOG
DUST
CUSTOM
```

---

# 147. WEATHER DOES NOT OWN WORLD GEOMETRY

El sistema meteorológico deberá modificar parámetros ambientales y no duplicar assets de mundo.

---

# 148. ENVIRONMENT PROFILE

Deberá existir:

```text
EnvironmentProfile
```

con:

```text
sky
fog
weather
time_of_day
ambient
water
terrain
```

---

# 149. WORLD AUDIO HOOKS

Deberá existir:

```text
WorldAudioProfile
```

para:

```text
ambient_zones
water
wind
forest
urban
custom
```

---

# 150. AUDIO ZONES

Deberá soportar:

```text
BOX
SPHERE
CAPSULE
POLYGON
CUSTOM
```

---

# 151. WORLD VFX HOOKS

Deberá existir:

```text
WorldVFXProfile
```

para:

```text
dust
leaves
rain
snow
mist
water
fire
custom
```

---

# 152. WORLD DECAL SYSTEM

Deberá existir soporte para:

```text
DECAL
ROAD_MARKING
TERRAIN_MARKING
DAMAGE
CUSTOM
```

---

# 153. WORLD ANCHORS

Deberá existir:

```text
WorldAnchor
```

para:

```text
spawn
landmark
quest
camera
navigation
streaming
custom
```

---

# 154. SPAWN SYSTEM

Deberá existir:

```text
SpawnProfile
```

---

# 155. SPAWN RULES

Mínimo:

```text
biome
height
slope
distance
navigation
exclusion
seed
```

---

# 156. LANDMARK SYSTEM

Deberá existir:

```text
LandmarkDefinition
```

---

# 157. LANDMARK TYPES

Mínimo:

```text
MOUNTAIN
TOWER
BUILDING
MONUMENT
TREE
WATER_BODY
ROAD_JUNCTION
CUSTOM
```

---

# 158. LANDMARK VALIDATION

Deberá comprobar:

```text
visibility
collision
navigation
streaming
uniqueness
```

---

# 159. WORLD QUERY SYSTEM

Deberá existir:

```text
WorldQuery
```

---

# 160. QUERY TYPES

Mínimo:

```text
HEIGHT_AT
SLOPE_AT
BIOME_AT
WATER_AT
ASSET_AT
NAVIGATION_AT
CELL_AT
NEAREST_ASSET
NEAREST_ROAD
```

---

# 161. WORLD QUERY DETERMINISM

La misma consulta sobre el mismo snapshot deberá producir el mismo resultado.

---

# 162. WORLD SNAPSHOT

Deberá existir:

```text
WorldSnapshot
```

que contenga:

```text
world_hash
cells
scene_graph
terrain_hash
vegetation_hash
water_hash
structure_hash
navigation_hash
```

---

# 163. WORLD DIFF

Deberá existir:

```text
WorldDiff
```

---

# 164. WORLD DIFF CATEGORIES

Mínimo:

```text
ADDED
REMOVED
MODIFIED
MOVED
REPLACED
LOD_CHANGED
STREAMING_CHANGED
```

---

# 165. PARTIAL REGENERATION

Deberá ser posible regenerar únicamente:

```text
CELL
REGION
BIOME
TERRAIN_LAYER
VEGETATION_LAYER
ROAD
BUILDING
```

sin reconstruir todo el mundo.

---

# 166. REGENERATION DEPENDENCIES

Ejemplo:

```text
CHANGE_TERRAIN
→ REBUILD TERRAIN
→ UPDATE SLOPE
→ UPDATE BIOME MASKS
→ UPDATE VEGETATION
→ UPDATE NAVIGATION
→ UPDATE COLLISION
```

---

# 167. MATERIAL CHANGE

Cambiar únicamente el material de terreno no deberá regenerar geometría salvo que el material profile lo requiera.

---

# 168. ASSET VARIANT CHANGE

Cambiar una variante de árbol deberá invalidar únicamente las instancias dependientes.

---

# 169. WORLD CACHE

Deberá existir:

```text
WorldCache
```

---

# 170. WORLD CACHE KEY

Mínimo:

```text
world_hash
cell_id
generator_version
profile_hash
asset_library_hash
```

---

# 171. CACHE INVALIDATION

Deberá existir invalidación por dependencia.

---

# 172. MEMORY BUDGET

El world profile deberá permitir:

```text
max_instances
max_cells
max_memory
max_texture_memory
max_collision_memory
max_navigation_memory
```

---

# 173. INSTANCE BUDGET

Deberá calcularse por:

```text
vegetation
rocks
props
buildings
roads
water
custom
```

---

# 174. TRIANGLE BUDGET

Deberá existir presupuesto por:

```text
terrain
structures
vegetation
rocks
props
water
HLOD
```

---

# 175. STREAMING BUDGET

Deberá estimarse:

```text
load_cost
unload_cost
visible_memory
resident_memory
```

---

# 176. WORLD PERFORMANCE REPORT

Deberá producir:

```text
WorldPerformanceReport
```

---

# 177. PERFORMANCE METRICS

Mínimo:

```text
generation_time
terrain_time
scatter_time
structure_time
water_time
navigation_time
hlod_time
export_time
validation_time
```

---

# 178. WORLD DIAGNOSTICS

Deberá producir:

```text
WorldDiagnosticReport
```

con:

```text
errors
warnings
statistics
budgets
connectivity
streaming
lod
navigation
collision
```

---

# 179. WORLD EXPORT

Deberá existir:

```text
WorldExporter
```

---

# 180. EXPORT TARGETS

Mínimo:

```text
ENGINE_RUNTIME
EDITOR
OFFLINE
DATASET
CUSTOM
```

---

# 181. UNREAL WORLD EXPORT

Cuando el backend sea Unreal, deberá producir metadata suficiente para:

```text
World
World Partition
Landscape
Foliage
Static Mesh Actors
Instanced Meshes
Water
Navigation
HLOD
Data Layers
```

según las capacidades del exporter.

---

# 182. WORLD READBACK

Después de exportar deberá verificarse:

```text
cell_count
actor_count
terrain_count
foliage_count
water_count
road_count
building_count
navigation_count
hlod_count
```

---

# 183. WORLD READBACK HASH

El export readback deberá producir hashes comparables con el snapshot.

---

# 184. TEST DIRECTORY

Deberá existir:

```text
tests/world/
```

---

# 185. WORLD MODEL TESTS

Mínimo:

```text
test_world_definition
test_world_region
test_world_cell
test_world_hash
test_world_snapshot
test_scene_graph
test_scene_hierarchy
test_scene_transform
```

---

# 186. BIOME TESTS

Mínimo:

```text
test_biome_definition
test_biome_weight
test_biome_blending
test_biome_mask
test_biome_priority
test_biome_validation
test_biome_determinism
```

---

# 187. TERRAIN TESTS

Mínimo:

```text
test_heightfield
test_terrain_generator
test_noise
test_noise_determinism
test_terrain_layer
test_terrain_operator
test_terrain_stamp
test_slope
test_normals
test_tangents
test_terrain_collision
test_terrain_navigation
test_terrain_validation
```

---

# 188. EROSION TESTS

Mínimo:

```text
test_hydraulic_erosion
test_thermal_erosion
test_wind_erosion
test_erosion_determinism
test_erosion_validation
```

---

# 189. WATER TESTS

Mínimo:

```text
test_water_definition
test_ocean
test_lake
test_river
test_stream
test_waterfall
test_flow_field
test_shoreline
test_water_validation
```

---

# 190. VEGETATION TESTS

Mínimo:

```text
test_vegetation_definition
test_species
test_scatter
test_poisson_scatter
test_grid_scatter
test_cluster_scatter
test_vegetation_mask
test_tree_variation
test_foliage
test_foliage_lod
test_vegetation_determinism
```

---

# 191. ROCK TESTS

Mínimo:

```text
test_rock_definition
test_rock_scatter
test_rock_orientation
test_cliff_generation
test_rock_determinism
```

---

# 192. PROP TESTS

Mínimo:

```text
test_prop_definition
test_prop_placement
test_exclusion_volume
test_prop_constraints
test_prop_determinism
```

---

# 193. BUILDING TESTS

Mínimo:

```text
test_building_definition
test_building_footprint
test_building_generation
test_building_variation
test_building_validation
test_building_determinism
```

---

# 194. ROAD TESTS

Mínimo:

```text
test_road_definition
test_road_path
test_road_generation
test_road_cut
test_road_fill
test_bridge
test_road_validation
test_road_determinism
```

---

# 195. NAVIGATION TESTS

Mínimo:

```text
test_navigation_definition
test_navigation_source
test_navigation_region
test_navigation_connectivity
test_navigation_query
test_navigation_validation
```

---

# 196. COLLISION TESTS

Mínimo:

```text
test_world_collision
test_terrain_collision
test_structure_collision
test_water_collision
test_collision_layers
test_collision_validation
```

---

# 197. STREAMING TESTS

Mínimo:

```text
test_world_partition
test_cell_assignment
test_streaming_distance
test_streaming_priority
test_streaming_state
test_streaming_determinism
```

---

# 198. HLOD TESTS

Mínimo:

```text
test_hlod_profile
test_hlod_grouping
test_hlod_generation
test_hlod_bounds
test_hlod_materials
test_hlod_transition
test_hlod_budget
```

---

# 199. IMPOSTOR TESTS

Mínimo:

```text
test_impostor_definition
test_impostor_generation
test_impostor_orientation
test_impostor_alpha
test_impostor_validation
```

---

# 200. ENVIRONMENT TESTS

Mínimo:

```text
test_environment_profile
test_lighting_hook
test_time_of_day
test_weather_hook
test_audio_zone
test_vfx_hook
```

---

# 201. SPAWN TESTS

Mínimo:

```text
test_spawn_profile
test_spawn_rules
test_spawn_exclusion
test_spawn_determinism
```

---

# 202. LANDMARK TESTS

Mínimo:

```text
test_landmark_definition
test_landmark_visibility
test_landmark_collision
test_landmark_navigation
test_landmark_validation
```

---

# 203. WORLD QUERY TESTS

Mínimo:

```text
test_height_query
test_slope_query
test_biome_query
test_water_query
test_asset_query
test_navigation_query
test_cell_query
test_nearest_asset
test_nearest_road
```

---

# 204. PARTIAL REGENERATION TESTS

Mínimo:

```text
test_regenerate_cell
test_regenerate_region
test_regenerate_biome
test_regenerate_terrain_layer
test_regenerate_vegetation
test_regenerate_road
test_regenerate_building
test_dependency_invalidation
```

---

# 205. CACHE TESTS

Mínimo:

```text
test_world_cache
test_cell_cache
test_profile_cache
test_asset_cache_dependency
test_cache_invalidation
test_cache_reuse
```

---

# 206. PERFORMANCE TESTS

Mínimo:

```text
test_generation_budget
test_instance_budget
test_triangle_budget
test_memory_budget
test_streaming_budget
test_navigation_budget
test_hlod_budget
```

---

# 207. FAILURE TESTS

Mínimo:

```text
test_invalid_world
test_invalid_region
test_invalid_cell
test_invalid_biome
test_invalid_terrain
test_invalid_noise
test_invalid_water
test_invalid_river
test_invalid_scatter
test_invalid_asset
test_invalid_building
test_invalid_road
test_invalid_navigation
test_invalid_collision
test_invalid_streaming
test_invalid_hlod
test_invalid_environment
test_invalid_spawn
test_invalid_landmark
```

---

# 208. DETERMINISM TESTS

Deberá comprobarse determinismo de:

```text
world_generation
region_generation
cell_generation
biome_assignment
noise
terrain
erosion
water
vegetation_scatter
rock_scatter
prop_scatter
building_generation
road_generation
navigation
hlod
impostors
spawn
landmarks
world_queries
partial_regeneration
cache_keys
export_metadata
```

---

# 209. GOLDEN WORLD SET

Deberán existir como mínimo:

```text
GOLDEN_FLAT_WORLD
GOLDEN_DESERT
GOLDEN_GRASSLAND
GOLDEN_FOREST
GOLDEN_MOUNTAIN
GOLDEN_SNOW
GOLDEN_COAST
GOLDEN_RIVER_VALLEY
GOLDEN_URBAN
GOLDEN_HYBRID_WORLD
```

---

# 210. GOLDEN WORLD VALIDATION

Cada golden deberá validar:

```text
WORLD_HASH
CELL_LAYOUT
TERRAIN
BIOMES
WATER
VEGETATION
ROADS
STRUCTURES
NAVIGATION
COLLISION
HLOD
STREAMING
EXPORT
```

---

# 211. END-TO-END WORLD TEST

Deberá existir un test que ejecute:

```text
WORLD DEFINITION
↓
SEED
↓
REGIONS
↓
CELLS
↓
BIOME ASSIGNMENT
↓
TERRAIN
↓
EROSION
↓
WATER
↓
VEGETATION
↓
ROCKS
↓
PROPS
↓
BUILDINGS
↓
ROADS
↓
NAVIGATION
↓
COLLISION
↓
WORLD PARTITION
↓
HLOD
↓
IMPOSTORS
↓
ENVIRONMENT HOOKS
↓
VALIDATION
↓
CACHE
↓
EXPORT
↓
READBACK
↓
FINAL VALIDATION
```

---

# 212. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
8 WORLD_MODEL
7 BIOME
13 TERRAIN
5 EROSION
9 WATER
11 VEGETATION
5 ROCK
5 PROP
6 BUILDING
8 ROAD
6 NAVIGATION
6 COLLISION
6 STREAMING
7 HLOD
5 IMPOSTOR
6 ENVIRONMENT
4 SPAWN
5 LANDMARK
9 WORLD_QUERY
8 PARTIAL_REGENERATION
6 CACHE
7 PERFORMANCE
19 FAILURE
26 DETERMINISM
10 GOLDEN
1 END_TO_END
```

**Total mínimo: 213 tests.**

---

# 213. CROSS-PHASE INTEGRATION

Deberá integrarse con:

```text
UAF-81.50
UAF-81.51
UAF-81.52
UAF-81.53
UAF-81.54
UAF-81.55
```

---

# 214. CHARACTER INTEGRATION

Los personajes de UAF-81.55 deberán poder:

```text
spawn
navigate
move
interact
stream
```

dentro del mundo generado.

---

# 215. ANIMATION INTEGRATION

La locomoción deberá utilizar:

```text
terrain_height
slope
navigation_state
movement_direction
```

para seleccionar la animación correspondiente.

---

# 216. FOOT IK INTEGRATION

El sistema deberá exponer el terreno necesario para:

```text
foot_placement
ground_normal
ground_height
```

---

# 217. MATERIAL INTEGRATION

El terrain system deberá consumir materiales generados previamente sin duplicar su ownership.

---

# 218. ASSET LIBRARY INTEGRATION

Vegetación, rocas, props y estructuras deberán utilizar referencias al Asset Library.

No deberán generarse copias lógicas innecesarias.

---

# 219. DEPENDENCY GRAPH

El mundo deberá integrarse al dependency graph global.

Ejemplo:

```text
ASSET
 ↓
MATERIAL
 ↓
WORLD CELL
 ↓
VEGETATION INSTANCE
 ↓
HLOD
 ↓
EXPORT
```

---

# 220. INVALIDATION RULES

Mínimo:

```text
CHANGE_WORLD_SEED
→ REGENERATE WORLD

CHANGE_TERRAIN_PROFILE
→ INVALIDATE TERRAIN + DEPENDENT SYSTEMS

CHANGE_BIOME_PROFILE
→ INVALIDATE BIOME MASKS + DEPENDENT SCATTER

CHANGE_TREE_ASSET
→ INVALIDATE TREE INSTANCES + HLOD

CHANGE_MATERIAL
→ INVALIDATE MATERIAL REFERENCES ONLY

CHANGE_ROAD_PROFILE
→ INVALIDATE ROAD + DEPENDENT NAVIGATION

CHANGE_NAVIGATION_PROFILE
→ INVALIDATE NAVIGATION ONLY

CHANGE_STREAMING_PROFILE
→ INVALIDATE STREAMING/HLOD METADATA

CHANGE_HLOD_PROFILE
→ INVALIDATE HLOD ONLY
```

---

# 221. NO HIDDEN STATE

Toda información necesaria para regenerar una world cell deberá estar serializada.

---

# 222. REPRODUCIBILITY

Dado:

```text
world_definition
seed
profiles
asset_library
generator_version
```

deberá ser posible reproducir el mundo.

---

# 223. PARTIAL REPRODUCIBILITY

Una cell regenerada aisladamente deberá coincidir con esa misma cell generada dentro del world completo, salvo dependencias explícitamente globales.

---

# 224. ERROR REPORTING

Cada error deberá contener cuando corresponda:

```text
error_code
severity
world_id
region_id
cell_id
asset_id
coordinate
parameter
expected
actual
suggested_fix
```

---

# 225. WORLD EXPORT VALIDATION

El exporter no podrá marcar éxito si:

```text
missing_cell
missing_asset
missing_reference
invalid_transform
invalid_collision
invalid_navigation
invalid_hlod
```

permanece sin resolver.

---

# 226. DOCUMENTATION

Deberá documentarse:

```text
world_schema
terrain_schema
biome_schema
water_schema
scatter_schema
building_schema
road_schema
navigation_schema
streaming_schema
hlod_schema
export_schema
```

---

# 227. ACCEPTANCE CRITERIA

La fase estará completa únicamente cuando:

```text
WORLD DATA MODEL IMPLEMENTED
REGION SYSTEM IMPLEMENTED
CELL SYSTEM IMPLEMENTED
SCENE GRAPH IMPLEMENTED
BIOME SYSTEM IMPLEMENTED
BIOME MASKS IMPLEMENTED
TERRAIN SYSTEM IMPLEMENTED
NOISE SYSTEM IMPLEMENTED
TERRAIN OPERATORS IMPLEMENTED
TERRAIN MODIFIERS IMPLEMENTED
EROSION IMPLEMENTED
SPLATMAP SYSTEM IMPLEMENTED
WATER SYSTEM IMPLEMENTED
RIVER SYSTEM IMPLEMENTED
SHORELINE SYSTEM IMPLEMENTED
VEGETATION SYSTEM IMPLEMENTED
FOLIAGE SYSTEM IMPLEMENTED
ROCK SYSTEM IMPLEMENTED
PROP SYSTEM IMPLEMENTED
UNIVERSAL SCATTER IMPLEMENTED
BUILDING SYSTEM IMPLEMENTED
ROAD SYSTEM IMPLEMENTED
BRIDGE SYSTEM IMPLEMENTED
PATH NETWORK IMPLEMENTED
NAVIGATION SYSTEM IMPLEMENTED
WORLD COLLISION IMPLEMENTED
WORLD PARTITION IMPLEMENTED
LEVEL STREAMING IMPLEMENTED
HLOD IMPLEMENTED
IMPOSTOR SYSTEM IMPLEMENTED
LIGHTING HOOKS IMPLEMENTED
TIME OF DAY HOOKS IMPLEMENTED
WEATHER HOOKS IMPLEMENTED
AUDIO HOOKS IMPLEMENTED
VFX HOOKS IMPLEMENTED
DECAL SYSTEM IMPLEMENTED
WORLD ANCHORS IMPLEMENTED
SPAWN SYSTEM IMPLEMENTED
LANDMARK SYSTEM IMPLEMENTED
WORLD QUERY SYSTEM IMPLEMENTED
WORLD SNAPSHOT IMPLEMENTED
WORLD DIFF IMPLEMENTED
PARTIAL REGENERATION IMPLEMENTED
CACHE IMPLEMENTED
MEMORY BUDGETS IMPLEMENTED
PERFORMANCE REPORT IMPLEMENTED
DIAGNOSTICS IMPLEMENTED
WORLD EXPORT IMPLEMENTED
WORLD READBACK IMPLEMENTED
MINIMUM 213 TESTS IMPLEMENTED
FAILURE TESTS IMPLEMENTED
DETERMINISM TESTS IMPLEMENTED
GOLDEN WORLDS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 228. NEXT PHASE

```text
UAF-81.57 — UNIVERSAL AI, NAVIGATION, NPC, CROWD, BEHAVIOR & SIMULATION SYSTEM
```

La siguiente fase deberá cerrar la capa de comportamiento sobre el mundo:

```text
AI FOUNDATION
NAVIGATION RUNTIME
NAVMESH
PATHFINDING
NPC DEFINITION
AGENT DEFINITION
SENSES
PERCEPTION
TARGETING
DECISION MAKING
BEHAVIOR TREES
STATE MACHINES
UTILITY AI
GOAP
GROUP BEHAVIOR
SQUADS
CROWD SIMULATION
AVOIDANCE
FORMATION
COMBAT
INTERACTION
QUEST HOOKS
SPAWN LOGIC
SCHEDULES
WORLD SIMULATION
AI LOD
SIMULATION LOD
SERVER/CLIENT HOOKS
DETERMINISTIC SIMULATION
REPLAY
SAVE/LOAD
AI VALIDATION
AI GOLDENS
AI FAILURE TESTS
AI DETERMINISM TESTS
END-TO-END SIMULATION TESTS
```
