# UAF-81.51 — WORLD TERRAIN, BIOME, VEGETATION & NATURAL ECOSYSTEM SYSTEM

## UAF-81.51-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE TERRENO, BIOMAS, VEGETACIÓN Y ECOSISTEMAS NATURALES

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.51 — World Terrain, Biome, Vegetation & Natural Ecosystem System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.50  
**Next Phase:** UAF-81.52  

---

# 1. PURPOSE

UAF-81.51 define e implementa el sistema profesional para generar, ensamblar, validar, optimizar y empaquetar entornos naturales y sistemas híbridos de mundo.

El sistema deberá soportar:

```text
TERRAIN
BIOMES
VEGETATION
FOLIAGE
TREES
SHRUBS
GRASS
FLOWERS
ROCKS
BOULDERS
CLIFFS
CAVES
WATER
RIVERS
LAKES
OCEANS
WETLANDS
SNOW
SAND
MUD
NATURAL_DECALS
NATURAL_POI
WEATHER_METADATA
ATMOSPHERIC_METADATA
```

El resultado deberá ser compatible con la arquitectura existente de AOE y con los requisitos de producción de Unreal Engine.

---

# 2. PRIMARY OBJECTIVE

El sistema deberá producir un:

```text
ProductionReadyNaturalEnvironment
```

que contenga como mínimo:

```text
WORLD_DEFINITION
TERRAIN_DEFINITION
BIOME_DEFINITION
TERRAIN_DATA
BIOME_MASKS
MATERIAL_ASSIGNMENTS
VEGETATION_DEFINITIONS
FOLIAGE_INSTANCES
ROCK_DEFINITIONS
WATER_DEFINITIONS
NATURAL_POI
NAVIGATION_METADATA
COLLISION_METADATA
LOD_METADATA
HLOD_METADATA
STREAMING_METADATA
PERFORMANCE_METADATA
GAMEPLAY_METADATA
VALIDATION_RESULTS
UNREAL_EXPORT_METADATA
```

---

# 3. DESIGN PRINCIPLE

El sistema deberá separar:

```text
TERRAIN SHAPE
TERRAIN MATERIAL
BIOME
VEGETATION
NATURAL STRUCTURE
WATER
GAMEPLAY
```

No se permitirá que una única operación monolítica controle todos estos sistemas.

---

# 4. PIPELINE

El pipeline deberá ser:

```text
WORLD INTENT
        ↓
NATURAL ENVIRONMENT SPECIFICATION
        ↓
TERRAIN PROFILE
        ↓
HEIGHTFIELD / TERRAIN GENERATION
        ↓
EROSION
        ↓
TERRAIN ANALYSIS
        ↓
BIOME CLASSIFICATION
        ↓
BIOME MASK GENERATION
        ↓
MATERIAL ASSIGNMENT
        ↓
NATURAL ASSET SELECTION
        ↓
VEGETATION DISTRIBUTION
        ↓
ROCK / CLIFF DISTRIBUTION
        ↓
WATER SYSTEM
        ↓
NATURAL POI
        ↓
NAVIGATION
        ↓
COLLISION
        ↓
LOD / HLOD
        ↓
STREAMING
        ↓
PERFORMANCE
        ↓
UNREAL VALIDATION
        ↓
PACKAGE
```

---

# 5. TERRAIN DEFINITION

Deberá existir:

```text
TerrainDefinition
```

con:

```text
terrain_id
terrain_type
width
depth
height_scale
resolution
seed
profile_id
erosion_profile
slope_profile
surface_profile
water_profile
biome_profile
```

---

# 6. TERRAIN TYPES

Mínimo:

```text
FLAT
ROLLING
HILLY
MOUNTAINOUS
ALPINE
CANYON
CLIFF
VALLEY
PLATEAU
DESERT
COASTAL
VOLCANIC
TUNDRA
SWAMP
CUSTOM
```

---

# 7. TERRAIN RESOLUTION

La resolución deberá declararse explícitamente.

No se permitirá una resolución incompatible con:

```text
world_size
gameplay_scale
streaming_cell_size
terrain_target
```

---

# 8. TERRAIN SEED

Toda generación deberá utilizar un seed explícito.

La ausencia de seed deberá considerarse inválida salvo que el caller solicite explícitamente un seed generado.

---

# 9. TERRAIN DETERMINISM

Mismo:

```text
terrain_definition
seed
generator_version
profile_version
```

deberá producir el mismo resultado lógico.

---

# 10. HEIGHTFIELD

Deberá existir una representación:

```text
TerrainHeightField
```

capaz de almacenar:

```text
height
normal
slope
curvature
```

---

# 11. TERRAIN NORMALIZATION

El sistema deberá normalizar internamente:

```text
height
slope
curvature
```

para permitir que otros sistemas utilicen valores consistentes.

---

# 12. TERRAIN FEATURES

Deberá detectar o generar:

```text
PEAK
RIDGE
VALLEY
BASIN
PLATEAU
CLIFF
SLOPE
DEPRESSION
PLAIN
```

---

# 13. SLOPE ANALYSIS

El sistema deberá calcular:

```text
slope_angle
slope_class
walkability
vegetation_suitability
building_suitability
```

---

# 14. SLOPE CLASSES

Mínimo:

```text
FLAT
GENTLE
MODERATE
STEEP
VERY_STEEP
CLIFF
```

Los rangos deberán ser configurables por profile.

---

# 15. CURVATURE ANALYSIS

Deberá calcular:

```text
CONVEX
CONCAVE
FLAT
```

y permitir su uso para:

```text
erosion
vegetation
rock_distribution
water_flow
material_assignment
```

---

# 16. EROSION SYSTEM

Deberá existir:

```text
TerrainErosionSystem
```

---

# 17. EROSION TYPES

Mínimo:

```text
HYDRAULIC
THERMAL
WIND
SEDIMENT
CUSTOM
```

---

# 18. EROSION PARAMETERS

Mínimo:

```text
iterations
strength
rainfall
evaporation
sediment_capacity
talus_rate
wind_strength
seed
```

---

# 19. EROSION LIMITS

El sistema deberá imponer límites para evitar:

```text
unusable_terrain
extreme_noise
invalid_slopes
gameplay_blocking_features
```

---

# 20. TERRAIN MASK SYSTEM

Deberá existir:

```text
TerrainMask
TerrainMaskSet
```

---

# 21. REQUIRED MASKS

Mínimo:

```text
HEIGHT
SLOPE
CURVATURE
MOISTURE
ALTITUDE
TEMPERATURE
EROSION
FLOW
WATER_DISTANCE
ROAD_DISTANCE
BUILDING_DISTANCE
```

---

# 22. MASK NORMALIZATION

Todas las máscaras deberán utilizar un rango normalizado:

```text
0.0 - 1.0
```

salvo que el tipo de dato requiera otra unidad explícita.

---

# 23. BIOME SYSTEM

Deberá existir:

```text
BiomeDefinition
BiomeProfile
BiomeClassifier
BiomeValidator
```

---

# 24. BIOME TYPES

Mínimo:

```text
FOREST
JUNGLE
GRASSLAND
DESERT
SAVANNA
TUNDRA
TAIGA
SWAMP
WETLAND
MOUNTAIN
ALPINE
COASTAL
VOLCANIC
URBAN_NATURE
ALIEN
CUSTOM
```

---

# 25. BIOME PARAMETERS

Cada biome deberá declarar:

```text
temperature_range
moisture_range
altitude_range
slope_range
vegetation_profile
rock_profile
ground_material_profile
water_profile
```

---

# 26. BIOME CLASSIFICATION

La clasificación deberá utilizar las máscaras disponibles.

Ejemplo:

```text
temperature
+
moisture
+
altitude
+
slope
=
biome
```

---

# 27. BIOME PRIORITY

Los biomas deberán tener prioridad configurable cuando existan condiciones superpuestas.

---

# 28. BIOME TRANSITIONS

No se permitirán transiciones abruptas salvo que el profile las declare.

Deberán soportarse:

```text
hard_transition
soft_transition
gradient_transition
```

---

# 29. BIOME BLENDING

El sistema deberá generar pesos de transición.

---

# 30. BIOME VALIDATION

Deberá detectar:

```text
invalid_biome
undefined_region
conflicting_biomes
invalid_transition
unsupported_biome
```

---

# 31. GROUND MATERIAL SYSTEM

Cada biome deberá poder definir:

```text
PRIMARY_GROUND
SECONDARY_GROUND
ACCENT_GROUND
DEPOSIT
```

---

# 32. GROUND MATERIAL TYPES

Mínimo:

```text
SOIL
GRASS
MUD
SAND
ROCK
GRAVEL
SNOW
ICE
ASH
CONCRETE
ASPHALT
ALIEN_SURFACE
```

---

# 33. MATERIAL DISTRIBUTION

La distribución deberá considerar:

```text
height
slope
moisture
curvature
biome
erosion
water_distance
```

---

# 34. MATERIAL VARIATION

Deberá soportar variaciones controladas de:

```text
color
roughness
normal_strength
wear
wetness
coverage
```

---

# 35. VEGETATION SYSTEM

Deberá existir:

```text
VegetationDefinition
VegetationProfile
VegetationGenerator
VegetationValidator
```

---

# 36. VEGETATION CATEGORIES

Mínimo:

```text
TREE
SHRUB
GRASS
FLOWER
FERN
MOSS
VINE
CACTUS
REED
CROP
ALIEN_PLANT
CUSTOM
```

---

# 37. VEGETATION PARAMETERS

Cada asset vegetal deberá declarar:

```text
species_id
height_range
width_range
density
slope_limit
altitude_range
moisture_range
biome_tags
ground_tags
```

---

# 38. VEGETATION DISTRIBUTION

La distribución deberá estar basada en máscaras y reglas.

No se permitirá distribución puramente uniforme.

---

# 39. DISTRIBUTION MODES

Mínimo:

```text
UNIFORM
CLUSTERED
POISSON
GRID_JITTERED
PAINTED
MASK_DRIVEN
CUSTOM
```

---

# 40. NATURAL CLUSTERING

El sistema deberá permitir:

```text
forest_cluster
shrub_cluster
grass_cluster
flower_cluster
rock_cluster
```

---

# 41. DENSITY FIELD

Deberá existir:

```text
VegetationDensityField
```

que permita controlar densidad espacialmente.

---

# 42. DENSITY FACTORS

Mínimo:

```text
biome
moisture
slope
altitude
distance_to_water
distance_to_road
distance_to_building
gameplay_area
```

---

# 43. VEGETATION EXCLUSION

Deberá existir un sistema de exclusión.

Podrá excluir vegetación por:

```text
roads
buildings
navigation
gameplay
water
spawn
objectives
```

---

# 44. CLEARANCE

Cada especie deberá declarar clearance mínimo.

---

# 45. VEGETATION COLLISION

Deberá distinguir entre:

```text
NONE
SIMPLE
INTERACTION
BLOCKING
```

---

# 46. FOLIAGE INSTANCE SYSTEM

Deberá existir metadata para:

```text
ISM
HISM
FOLIAGE_INSTANCE
```

cuando sea aplicable.

---

# 47. INSTANCE REUSE

Vegetación idéntica deberá reutilizar referencias siempre que sea posible.

---

# 48. VEGETATION VARIANTS

Un mismo asset podrá variar mediante:

```text
scale
rotation
lean
color_variation
material_variation
health
growth
```

dentro de límites definidos.

---

# 49. NO_OBVIOUS_REPETITION

Deberá detectarse repetición visual excesiva.

---

# 50. TREE SYSTEM

Deberá existir:

```text
TreeDefinition
TreeVariant
TreePlacementRule
```

---

# 51. TREE PARAMETERS

Mínimo:

```text
height
trunk_radius
canopy_radius
branch_density
leaf_density
age
species
```

---

# 52. TREE AGE

Deberán existir perfiles:

```text
YOUNG
MATURE
OLD
DEAD
```

---

# 53. DEAD VEGETATION

Deberá soportar:

```text
dead_tree
fallen_tree
broken_branch
stump
dry_vegetation
```

---

# 54. FOREST STRUCTURE

Los bosques deberán soportar niveles:

```text
CANOPY
UNDERSTORY
GROUND_COVER
```

---

# 55. FOREST DENSITY

Deberá existir:

```text
sparse
medium
dense
very_dense
```

---

# 56. UNDERSTORY VALIDATION

La vegetación secundaria no deberá bloquear completamente navegación cuando el biome profile no lo permita.

---

# 57. ROCK SYSTEM

Deberá existir:

```text
RockDefinition
RockGenerator
RockPlacementRule
```

---

# 58. ROCK TYPES

Mínimo:

```text
PEBBLE
ROCK
BOULDER
CLIFF
OUTCROP
COLUMN
SLAB
CUSTOM
```

---

# 59. ROCK PARAMETERS

```text
scale_range
rotation_range
slope_range
density
cluster_size
```

---

# 60. ROCK CLUSTERING

Los grupos deberán soportar:

```text
small
medium
large
```

y perfiles específicos.

---

# 61. CLIFF SYSTEM

Deberá existir:

```text
CliffDefinition
CliffGenerator
```

---

# 62. CLIFF GENERATION

Los cliffs deberán respetar:

```text
terrain_boundary
slope
rock_profile
collision
navigation
```

---

# 63. CAVE SYSTEM

Deberá existir soporte para:

```text
CAVE_ENTRANCE
CAVE_NETWORK
CAVE_ROOM
CAVE_CORRIDOR
```

---

# 64. CAVE CONNECTIVITY

Las cuevas deberán integrarse con el mismo sistema de connectivity graph de UAF-81.50.

---

# 65. CAVE VALIDATION

Deberá comprobar:

```text
entrance
clearance
connectivity
collision
navigation
streaming
```

---

# 66. WATER SYSTEM

Deberá existir:

```text
WaterDefinition
WaterBody
WaterGenerator
WaterValidator
```

---

# 67. WATER TYPES

Mínimo:

```text
RIVER
STREAM
LAKE
POND
OCEAN
POOL
FLOOD
CUSTOM
```

---

# 68. WATER PARAMETERS

Mínimo:

```text
surface_height
depth
width
flow_direction
flow_speed
shore_profile
material_profile
```

---

# 69. RIVER GENERATION

Los ríos deberán poder derivarse de:

```text
terrain_height
flow_map
slope
basins
```

---

# 70. RIVER CONNECTIVITY

Los ríos deberán conservar continuidad hidráulica lógica cuando formen parte de una misma red.

---

# 71. WATER-TERRAIN INTERACTION

El sistema deberá generar metadata para:

```text
shoreline
wetness
sediment
erosion
water_distance
```

---

# 72. SHORELINE SYSTEM

Deberá existir:

```text
ShorelineDefinition
```

---

# 73. WATER EXCLUSION

La vegetación y los props deberán respetar:

```text
water_depth
shore_clearance
water_type
```

---

# 74. WEATHER PROFILE

Deberá existir:

```text
WeatherProfile
```

con:

```text
rain
snow
wind
fog
dust
storm
cloudiness
```

---

# 75. WEATHER NOISE

Los parámetros meteorológicos deberán ser deterministas cuando formen parte de la generación.

---

# 76. ATMOSPHERE METADATA

Deberá soportarse:

```text
sky_profile
fog_profile
cloud_profile
atmospheric_density
visibility
```

---

# 77. NATURAL POI SYSTEM

Deberá existir:

```text
NaturalPOIDefinition
NaturalPOIGenerator
```

---

# 78. NATURAL POI TYPES

Mínimo:

```text
WATERFALL
CAVE
CLIFF
ANCIENT_TREE
ROCK_FORMATION
LAKE
RUIN
GROVE
CRATER
VOLCANIC_VENT
CUSTOM
```

---

# 79. POI SEMANTICS

Cada POI deberá declarar:

```text
poi_id
poi_type
location
bounds
importance
gameplay_relevance
navigation_relevance
```

---

# 80. GAMEPLAY LANDMARKS

El sistema deberá poder marcar:

```text
LANDMARK
NAVIGATION_LANDMARK
MISSION_LANDMARK
VISUAL_LANDMARK
```

---

# 81. NATURAL COVER

Deberá identificar o generar:

```text
ROCK_COVER
TREE_COVER
TERRAIN_COVER
VEGETATION_COVER
```

---

# 82. COVER VALIDATION

Deberá integrarse con el cover system de UAF-81.50.

---

# 83. NAVIGATION

El terrain system deberá producir:

```text
walkability_map
slope_map
blocked_map
water_map
vegetation_obstacle_map
```

---

# 84. NAVIGATION RULES

Deberán configurarse perfiles para:

```text
PLAYER
NPC
VEHICLE
LARGE_CREATURE
```

---

# 85. VEHICLE NAVIGATION

Cuando el environment lo requiera deberá existir:

```text
vehicle_clearance
vehicle_slope_limit
vehicle_turn_radius
```

---

# 86. SPAWN VALIDATION

Los spawn points no podrán colocarse:

```text
inside_water
inside_rock
inside_tree
on_invalid_slope
outside_navigation
inside_blocked_area
```

salvo excepción explícita.

---

# 87. TERRAIN COLLISION

Deberá existir metadata para:

```text
terrain_collision
rock_collision
vegetation_collision
water_collision
cave_collision
```

---

# 88. LOD SYSTEM

Deberá existir LOD específico para:

```text
terrain
trees
rocks
vegetation
water
```

---

# 89. VEGETATION LOD

Deberá soportar:

```text
FULL_GEOMETRY
REDUCED_GEOMETRY
BILLBOARD
IMPOSTOR
CULLED
```

---

# 90. TERRAIN HLOD

Las regiones lejanas deberán poder agruparse en HLOD clusters.

---

# 91. STREAMING

El sistema deberá producir:

```text
terrain_cells
vegetation_cells
rock_cells
water_cells
poi_cells
```

---

# 92. STREAMING BOUNDARIES

Los elementos naturales no deberán cruzar celdas de streaming de forma que provoquen referencias inconsistentes.

Cuando sea inevitable deberá existir metadata de dependencia.

---

# 93. PERFORMANCE BUDGET

Cada environment deberá definir:

```text
max_terrain_triangles
max_foliage_instances
max_unique_foliage_assets
max_visible_instances
max_water_bodies
max_collision_objects
max_material_variants
```

---

# 94. INSTANCE BUDGET

La generación deberá detectar exceso de instancias.

---

# 95. VISIBILITY BUDGET

Deberá existir:

```text
near_distance
mid_distance
far_distance
cull_distance
```

por categoría.

---

# 96. MATERIAL BUDGET

La vegetación y terrain deberán minimizar:

```text
unique_materials
unique_textures
material_instances
```

sin degradar el resultado por debajo del quality threshold.

---

# 97. NATURAL VARIATION

La variación deberá producir diferencias en:

```text
scale
rotation
position
age
density
color
material
health
```

pero permanecer dentro del profile.

---

# 98. ART-DIRECTED RANDOMNESS

La aleatoriedad nunca deberá reemplazar reglas de composición.

---

# 99. COMPOSITION RULES

Deberá soportar:

```text
foreground
midground
background
focal_area
negative_space
landmark_area
```

---

# 100. VIEWPORT COMPOSITION

El sistema deberá poder evaluar desde cámaras definidas:

```text
PLAYER
GAMEPLAY
CINEMATIC
OVERVIEW
```

---

# 101. VISUAL REGRESSION

Deberán producirse snapshots:

```text
TOP
NORTH
SOUTH
EAST
WEST
PLAYER_VIEW
GAMEPLAY_VIEW
DISTANT_VIEW
```

---

# 102. TERRAIN DEBUG VIEWS

Mínimo:

```text
HEIGHT
SLOPE
CURVATURE
MOISTURE
BIOME
MATERIAL
VEGETATION_DENSITY
WATER
NAVIGATION
COLLISION
LOD
STREAMING
```

---

# 103. BIOME DEBUG VIEW

Deberá visualizar claramente las regiones y transiciones entre biomas.

---

# 104. VEGETATION DEBUG VIEW

Deberá mostrar:

```text
species
density
exclusion
collision
lod
```

---

# 105. WATER DEBUG VIEW

Deberá mostrar:

```text
surface
depth
flow
shoreline
collision
```

---

# 106. DETERMINISTIC SNAPSHOT

Deberá existir:

```text
NaturalEnvironmentSnapshot
```

conteniendo hashes de:

```text
terrain
erosion
masks
biomes
materials
vegetation
rocks
water
poi
navigation
collision
lod
streaming
```

---

# 107. HASH VALIDATION

El sistema deberá comprobar que el mismo input produce el mismo hash lógico.

---

# 108. INCREMENTAL REBUILD

Cambiar:

```text
vegetation_density
```

no deberá reconstruir:

```text
terrain
erosion
water
architecture
```

salvo dependencia explícita.

---

# 109. DEPENDENCY GRAPH

Mínimo:

```text
TERRAIN
 ├── EROSION
 ├── MASKS
 ├── BIOMES
 │    ├── MATERIALS
 │    └── VEGETATION
 ├── ROCKS
 └── WATER

BIOMES
 └── VEGETATION

TERRAIN
 └── NAVIGATION

ALL NATURAL SYSTEMS
 └── STREAMING
```

---

# 110. ARTIST OVERRIDES

Deberán poder modificarse manualmente:

```text
biome_boundary
vegetation_exclusion
vegetation_density
rock_placement
water_path
poi_location
material_assignment
landmark
navigation
```

---

# 111. OVERRIDE PERSISTENCE

Las regeneraciones deberán conservar overrides compatibles.

---

# 112. VERSIONING

Deberá registrar:

```text
terrain_version
biome_version
vegetation_version
water_version
generator_version
schema_version
```

---

# 113. TEST DIRECTORY

Deberá existir:

```text
tests/world/
```

o una estructura equivalente claramente separada de los tests generales.

---

# 114. TERRAIN TESTS

Mínimo:

```text
test_terrain_generation
test_terrain_resolution
test_terrain_scale
test_heightfield
test_slope_analysis
test_curvature_analysis
test_terrain_determinism
```

---

# 115. EROSION TESTS

Mínimo:

```text
test_hydraulic_erosion
test_thermal_erosion
test_erosion_limits
test_erosion_determinism
```

---

# 116. MASK TESTS

Mínimo:

```text
test_height_mask
test_slope_mask
test_curvature_mask
test_moisture_mask
test_altitude_mask
test_water_distance_mask
test_mask_normalization
```

---

# 117. BIOME TESTS

Mínimo:

```text
test_biome_classification
test_biome_priority
test_biome_transition
test_biome_blending
test_invalid_biome
test_biome_determinism
```

---

# 118. MATERIAL TESTS

Mínimo:

```text
test_ground_material_assignment
test_material_mask
test_material_variation
test_material_determinism
```

---

# 119. VEGETATION TESTS

Mínimo:

```text
test_vegetation_generation
test_vegetation_density
test_vegetation_distribution
test_vegetation_exclusion
test_vegetation_clearance
test_vegetation_determinism
```

---

# 120. TREE TESTS

Mínimo:

```text
test_tree_generation
test_tree_age_variants
test_tree_clearance
test_tree_distribution
```

---

# 121. ROCK TESTS

Mínimo:

```text
test_rock_generation
test_rock_distribution
test_rock_clustering
test_rock_clearance
test_rock_determinism
```

---

# 122. CLIFF TESTS

Mínimo:

```text
test_cliff_generation
test_cliff_collision
test_cliff_navigation
test_cliff_determinism
```

---

# 123. CAVE TESTS

Mínimo:

```text
test_cave_generation
test_cave_connectivity
test_cave_clearance
test_cave_navigation
test_cave_collision
```

---

# 124. WATER TESTS

Mínimo:

```text
test_water_generation
test_river_generation
test_water_connectivity
test_shoreline_generation
test_water_exclusion
test_water_determinism
```

---

# 125. WEATHER TESTS

Mínimo:

```text
test_weather_profile
test_weather_determinism
test_weather_validation
```

---

# 126. POI TESTS

Mínimo:

```text
test_poi_generation
test_poi_location
test_poi_bounds
test_poi_semantics
test_poi_determinism
```

---

# 127. NAVIGATION TESTS

Mínimo:

```text
test_terrain_walkability
test_slope_navigation
test_water_blocking
test_vegetation_blocking
test_spawn_validation
test_vehicle_navigation
```

---

# 128. COLLISION TESTS

Mínimo:

```text
test_terrain_collision
test_rock_collision
test_tree_collision
test_water_collision
test_cave_collision
```

---

# 129. LOD TESTS

Mínimo:

```text
test_terrain_lod
test_tree_lod
test_rock_lod
test_foliage_lod
test_water_lod
test_hlod
```

---

# 130. STREAMING TESTS

Mínimo:

```text
test_terrain_cells
test_vegetation_cells
test_rock_cells
test_water_cells
test_cross_cell_dependencies
test_streaming_determinism
```

---

# 131. PERFORMANCE TESTS

Mínimo:

```text
test_foliage_instance_budget
test_visible_instance_budget
test_triangle_budget
test_collision_budget
test_material_budget
test_streaming_budget
```

---

# 132. VISUAL TESTS

Mínimo:

```text
test_top_view
test_player_view
test_gameplay_view
test_biome_view
test_vegetation_view
test_water_view
```

---

# 133. DETERMINISM TESTS

Deberán comprobar:

```text
terrain
erosion
masks
biomes
materials
vegetation
trees
rocks
water
poi
navigation
collision
lod
streaming
```

---

# 134. FAILURE TESTS

Mínimo:

```text
test_invalid_terrain
test_invalid_resolution
test_invalid_seed
test_invalid_biome
test_conflicting_biomes
test_invalid_material
test_invalid_vegetation
test_invalid_clearance
test_invalid_rock
test_invalid_water
test_invalid_river
test_invalid_poi
test_invalid_navigation
test_invalid_collision
test_budget_overflow
test_streaming_overflow
```

---

# 135. GOLDEN ENVIRONMENTS

Deberán existir como mínimo:

```text
GOLDEN_FOREST
GOLDEN_DESERT
GOLDEN_MOUNTAIN
GOLDEN_SWAMP
GOLDEN_COASTAL
GOLDEN_HYBRID
```

---

# 136. GOLDEN VALIDATION

Cada golden environment deberá validar:

```text
terrain
biomes
materials
vegetation
rocks
water
navigation
collision
lod
streaming
performance
determinism
unreal_compatibility
```

---

# 137. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
7 TERRAIN
4 EROSION
7 MASK
6 BIOME
4 MATERIAL
6 VEGETATION
4 TREE
5 ROCK
4 CLIFF
5 CAVE
6 WATER
3 WEATHER
5 POI
6 NAVIGATION
5 COLLISION
6 LOD
6 STREAMING
6 PERFORMANCE
6 VISUAL
14 DETERMINISM
16 FAILURE
6 GOLDEN
1 END_TO_END
```

Total mínimo:

```text
127 TESTS
```

---

# 138. END-TO-END TEST

Deberá ejecutarse:

```text
WORLD INTENT
↓
TERRAIN
↓
EROSION
↓
MASKS
↓
BIOMES
↓
MATERIALS
↓
VEGETATION
↓
ROCKS
↓
WATER
↓
NATURAL POI
↓
NAVIGATION
↓
COLLISION
↓
LOD
↓
STREAMING
↓
PERFORMANCE
↓
UNREAL EXPORT
↓
VALIDATION
```

---

# 139. UNREAL EXPORT CONTRACT

Deberá existir:

```text
NaturalEnvironmentExportContract
```

---

# 140. EXPORT TARGETS

Mínimo:

```text
TERRAIN
LANDSCAPE_METADATA
MATERIAL_ASSIGNMENT
FOLIAGE_METADATA
STATIC_MESH
WATER_METADATA
COLLISION
NAVIGATION_METADATA
HLOD_METADATA
WORLD_PARTITION_METADATA
STREAMING_METADATA
```

---

# 141. ROUND TRIP

Deberá validarse:

```text
AOE
↓
EXPORT
↓
UNREAL
↓
READBACK
↓
VALIDATION
```

---

# 142. PACKAGE

El paquete final deberá contener:

```text
terrain_definition
terrain_data
heightfield
terrain_masks
biome_definitions
biome_masks
material_assignments
vegetation_definitions
vegetation_instances
rock_definitions
rock_instances
water_definitions
water_metadata
natural_poi
navigation
collision
lod
hlod
streaming
performance
validation
unreal_metadata
```

---

# 143. CRITICAL REQUIREMENT

El sistema NO deberá producir únicamente un paisaje visual.

Deberá producir:

```text
GEOMETRY
TERRAIN DATA
BIOME DATA
MATERIAL DATA
VEGETATION DATA
WATER DATA
SEMANTICS
NAVIGATION
COLLISION
GAMEPLAY DATA
STREAMING
PERFORMANCE
UNREAL METADATA
```

---

# 144. NO ORPHAN DATA

Ningún elemento deberá existir sin relación con el environment graph.

---

# 145. NO INVALID PLACEMENT

No deberán existir elementos naturales colocados:

```text
inside_invalid_geometry
inside_water_when_forbidden
inside_navigation
inside_building
inside_spawn
inside_objective
outside_world_bounds
```

salvo reglas explícitas.

---

# 146. NO UNCONTROLLED DENSITY

Ninguna categoría de vegetación podrá superar su presupuesto sin producir:

```text
WARNING
```

o:

```text
ERROR
```

según la severidad configurada.

---

# 147. NO HIDDEN PERFORMANCE COST

Cada sistema deberá registrar su contribución estimada a:

```text
triangles
instances
draw_calls
memory
collision
streaming
```

---

# 148. FINAL ACCEPTANCE CRITERIA

UAF-81.51 estará completa únicamente cuando:

```text
TERRAIN SCHEMA IMPLEMENTED
HEIGHTFIELD IMPLEMENTED
SLOPE ANALYSIS IMPLEMENTED
CURVATURE ANALYSIS IMPLEMENTED
EROSION IMPLEMENTED
TERRAIN MASK SYSTEM IMPLEMENTED
BIOME SYSTEM IMPLEMENTED
BIOME CLASSIFICATION IMPLEMENTED
BIOME TRANSITIONS IMPLEMENTED
GROUND MATERIAL SYSTEM IMPLEMENTED
VEGETATION SYSTEM IMPLEMENTED
DENSITY FIELD IMPLEMENTED
VEGETATION DISTRIBUTION IMPLEMENTED
VEGETATION EXCLUSION IMPLEMENTED
TREE SYSTEM IMPLEMENTED
TREE VARIANTS IMPLEMENTED
DEAD VEGETATION IMPLEMENTED
FOREST STRUCTURE IMPLEMENTED
ROCK SYSTEM IMPLEMENTED
ROCK CLUSTERING IMPLEMENTED
CLIFF SYSTEM IMPLEMENTED
CAVE SYSTEM IMPLEMENTED
WATER SYSTEM IMPLEMENTED
RIVER SYSTEM IMPLEMENTED
SHORELINE SYSTEM IMPLEMENTED
WEATHER PROFILE IMPLEMENTED
ATMOSPHERIC METADATA IMPLEMENTED
NATURAL POI IMPLEMENTED
NATURAL COVER IMPLEMENTED
NAVIGATION IMPLEMENTED
COLLISION IMPLEMENTED
LOD IMPLEMENTED
HLOD IMPLEMENTED
STREAMING IMPLEMENTED
PERFORMANCE BUDGET IMPLEMENTED
INSTANCE REUSE IMPLEMENTED
VISUAL REGRESSION IMPLEMENTED
DEBUG VISUALIZATIONS IMPLEMENTED
SNAPSHOT IMPLEMENTED
HASHING IMPLEMENTED
INCREMENTAL BUILD IMPLEMENTED
DEPENDENCY GRAPH IMPLEMENTED
ARTIST OVERRIDES IMPLEMENTED
VERSIONING IMPLEMENTED
GOLDEN ENVIRONMENTS IMPLEMENTED
MINIMUM 127 TESTS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
UNREAL ROUND_TRIP VALIDATION IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 149. INTEGRATION CONTRACT

UAF-81.51 deberá integrarse obligatoriamente con:

```text
UAF-81.48 — WORLD SYSTEM
UAF-81.50 — ENVIRONMENT, ARCHITECTURE & MODULAR WORLD ASSEMBLY
UAF-81.46 — MATERIAL & TEXTURE SYSTEM
```

No deberá duplicar funcionalidad ya existente.

Cuando exista una capacidad equivalente en una fase anterior, deberá utilizarse el contrato existente.

---

# 150. NEXT PHASE

```text
UAF-81.52 — UNIVERSAL MATERIAL, TEXTURE & SURFACE AUTHORING SYSTEM
```

Esta fase deberá convertirse en la fábrica transversal de:

```text
MATERIALS
TEXTURES
PBR
NORMAL MAPS
ROUGHNESS
METALLIC
AO
HEIGHT
DISPLACEMENT
MASKS
DECALS
TRIMS
TILEABLE SURFACES
UNIQUE SURFACES
SURFACE VARIANTS
MATERIAL INSTANCES
VIRTUAL TEXTURES
TEXTURE ATLASES
UDIMS
```

y deberá servir tanto a:

```text
CHARACTERS
CREATURES
WEAPONS
PROPS
ARCHITECTURE
ENVIRONMENTS
VEGETATION
TERRAIN
VFX
```

sin convertirse en un subsistema exclusivo de ninguna categoría.
