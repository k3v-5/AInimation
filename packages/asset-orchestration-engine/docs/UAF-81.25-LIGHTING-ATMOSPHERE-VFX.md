# UAF-81.25 — PROCEDURAL LIGHTING, ATMOSPHERE, VFX & PRESENTATION FABRICATION SYSTEM

## UAF-81.25-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA DE FABRICACIÓN PROCEDURAL DE ILUMINACIÓN, ATMÓSFERA, VFX Y PRESENTACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.25 — Procedural Lighting, Atmosphere, VFX & Presentation Fabrication System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.24  
**Next Phase:** UAF-81.26  

---

# 1. PURPOSE

UAF-81.25 establece el sistema profesional para fabricar, configurar, validar y empaquetar:

```text
LIGHTING
SKY
ATMOSPHERE
FOG
VOLUMETRICS
POST PROCESS
VFX
NIAGARA
PARTICLES
WEATHER
FIRE
SMOKE
DUST
EXPLOSIONS
ENERGY EFFECTS
ENVIRONMENTAL EFFECTS
DECALS
LIGHT PROBES
REFLECTION SUPPORT
CINEMATIC PRESENTATION
```

El sistema deberá producir resultados compatibles con Unreal Engine y deberá integrarse con:

```text
UAF-81.22 Surface & Material Fabrication
UAF-81.24 Environment & World Fabrication
```

---

# 2. FUNDAMENTAL PRINCIPLE

La iluminación y los efectos no deberán considerarse elementos decorativos independientes.

Deberán formar parte de una representación semántica del mundo:

```text
WORLD
├── GEOMETRY
├── MATERIALS
├── LIGHTING
├── ATMOSPHERE
├── VFX
├── WEATHER
├── POST_PROCESS
└── PRESENTATION
```

---

# 3. PRESENTATION DEFINITION

Deberá existir:

```text
PresentationDefinition
```

Mínimo:

```text
presentation_id
version
lighting_profile
atmosphere_profile
vfx_profile
weather_profile
post_process_profile
cinematic_profile
performance_profile
seed
```

---

# 4. LIGHTING PROFILE

Deberá existir:

```text
LightingProfile
```

Mínimo:

```text
lighting_id
intensity_scale
color_temperature
exposure
contrast
shadow_policy
indirect_lighting_policy
accent_policy
```

---

# 5. LIGHT TYPES

Deberán soportarse:

```text
POINT
SPOT
RECT
DIRECTIONAL
AREA
EMISSIVE_SOURCE
CUSTOM
```

---

# 6. LIGHT DEFINITION

Cada luz deberá declarar:

```text
light_id
type
position
rotation
intensity
color
temperature
radius
attenuation
shadow_policy
mobility
channel
```

---

# 7. LIGHT MOBILITY

Deberá distinguirse:

```text
STATIC
STATIONARY
MOVABLE
```

según el modelo de iluminación utilizado por Unreal.

---

# 8. LIGHT PLACEMENT

Las luces podrán colocarse mediante:

```text
WORLD
ROOM
SURFACE
PROP
SOCKET
LANDMARK
GAMEPLAY_ZONE
```

---

# 9. LIGHT ANCHORING

Una luz asociada a un asset deberá poder declarar:

```text
anchor_asset
anchor_socket
local_position
local_rotation
```

---

# 10. LIGHT SEMANTICS

Las luces podrán tener roles:

```text
KEY
FILL
RIM
AMBIENT
PRACTICAL
ACCENT
WARNING
OBJECTIVE
COMBAT
CINEMATIC
```

---

# 11. KEY LIGHT

Cada zona podrá declarar una fuente principal.

---

# 12. FILL LIGHT

Deberá existir una política para evitar zonas completamente ilegibles.

---

# 13. RIM LIGHT

Podrá utilizarse para:

```text
character_separation
landmark_separation
environment_separation
```

---

# 14. PRACTICAL LIGHT

Deberá existir soporte para luces derivadas de objetos:

```text
lamps
screens
machines
fires
neon
emissive_panels
```

---

# 15. LIGHT GROUPS

Deberá existir:

```text
LightGroup
```

con:

```text
group_id
members
priority
intensity_multiplier
color_multiplier
enabled
```

---

# 16. LIGHT PRIORITY

Cuando existan conflictos de presupuesto, deberán aplicarse prioridades explícitas.

---

# 17. LIGHT BUDGET

Cada mundo deberá poder declarar:

```text
max_dynamic_lights
max_shadow_casting_lights
max_visible_lights_per_zone
```

---

# 18. SHADOW POLICY

Cada luz deberá poder declarar:

```text
shadow_enabled
shadow_resolution
shadow_distance
contact_shadow
```

según las capacidades del target.

---

# 19. SHADOW OPTIMIZATION

Las sombras deberán optimizarse según:

```text
distance
importance
gameplay
visual_priority
performance_budget
```

---

# 20. LIGHT CHANNELS

Deberá existir soporte para separar grupos de iluminación cuando el proyecto lo requiera.

---

# 21. EXPOSURE

La exposición deberá formar parte del perfil visual.

No deberá depender de valores arbitrarios introducidos manualmente durante la generación.

---

# 22. EXPOSURE VALIDATION

Deberá analizarse:

```text
minimum_luminance
maximum_luminance
average_luminance
dynamic_range
```

---

# 23. OVEREXPOSURE DETECTION

Deberán detectarse zonas con:

```text
white_clip
emissive_bloom_overload
highlight_loss
```

---

# 24. UNDEREXPOSURE DETECTION

Deberán detectarse zonas con:

```text
black_crush
unreadable_geometry
unreadable_gameplay
```

---

# 25. COLOR TEMPERATURE

El sistema deberá soportar temperatura de color:

```text
KELVIN
RGB
HSV
HEX
```

---

# 26. COLOR CONSISTENCY

Los perfiles deberán evitar combinaciones cromáticas incompatibles con el `WorldStyleProfile`.

---

# 27. SKY SYSTEM

Deberá existir:

```text
SkyGenerator
```

---

# 28. SKY TYPES

Mínimo:

```text
CLEAR
OVERCAST
STORM
NIGHT
SUNSET
SUNRISE
ALIEN
SCI_FI
CUSTOM
```

---

# 29. SKY PARAMETERS

Mínimo:

```text
sun_direction
sun_intensity
sky_color
horizon_color
cloud_density
cloud_speed
star_density
moon_parameters
```

---

# 30. SUN SYSTEM

Deberá existir:

```text
SunDefinition
```

---

# 31. SUN VALIDATION

El sistema deberá validar:

```text
direction
intensity
color
shadow_direction
```

contra el perfil ambiental.

---

# 32. MOON SYSTEM

Deberá poder configurarse:

```text
moon_direction
moon_intensity
moon_color
phase
```

---

# 33. CLOUD SYSTEM

Deberá soportar:

```text
density
coverage
altitude
speed
direction
variation
```

---

# 34. ATMOSPHERE SYSTEM

Deberá existir:

```text
AtmosphereGenerator
```

---

# 35. ATMOSPHERIC PARAMETERS

Mínimo:

```text
density
height_falloff
scattering
absorption
sun_scattering
```

---

# 36. FOG SYSTEM

Deberá soportar:

```text
FOG
HEIGHT_FOG
VOLUMETRIC_FOG
LOCAL_FOG
CUSTOM
```

---

# 37. FOG VOLUME

Cada volumen deberá declarar:

```text
volume_id
bounds
density
color
height
falloff
priority
```

---

# 38. FOG ZONES

La niebla podrá variar según:

```text
biome
room
time
weather
gameplay_zone
```

---

# 39. VOLUMETRIC BUDGET

El sistema deberá controlar:

```text
volume_count
density
quality
distance
```

para evitar costes excesivos.

---

# 40. WEATHER SYSTEM

Deberá existir:

```text
WeatherGenerator
```

---

# 41. WEATHER TYPES

Mínimo:

```text
CLEAR
RAIN
HEAVY_RAIN
STORM
SNOW
ASH
DUST
FOG
ACID_RAIN
CUSTOM
```

---

# 42. WEATHER PARAMETERS

Mínimo:

```text
intensity
direction
speed
density
duration
coverage
visibility
```

---

# 43. WEATHER DETERMINISM

El clima procedural deberá depender del seed y del profile.

---

# 44. WEATHER TRANSITIONS

Las transiciones deberán poder definirse:

```text
CLEAR
→
RAIN
→
STORM
→
RAIN
→
CLEAR
```

---

# 45. WEATHER VFX

Los efectos meteorológicos deberán utilizar el sistema VFX común.

---

# 46. VFX SYSTEM

Deberá existir:

```text
VFXGenerator
```

---

# 47. VFX DEFINITION

Mínimo:

```text
vfx_id
type
location
rotation
scale
duration
intensity
material
particle_profile
audio_profile
gameplay_tags
```

---

# 48. VFX TYPES

Mínimo:

```text
FIRE
SMOKE
DUST
SPARK
ELECTRIC
ENERGY
EXPLOSION
IMPACT
DEBRIS
FOG
STEAM
RAIN
SNOW
CUSTOM
```

---

# 49. NIAGARA REPRESENTATION

Los efectos destinados a Unreal deberán poder representarse mediante perfiles compatibles con Niagara.

---

# 50. PARTICLE EMITTER

Cada sistema de partículas deberá declarar:

```text
emitter_id
spawn_rate
burst_count
lifetime
velocity
size
color
material
collision_policy
```

---

# 51. PARTICLE LIFETIME

Deberá poder utilizarse:

```text
constant
random_range
curve
```

---

# 52. PARTICLE VELOCITY

Deberá soportarse:

```text
direction
radial
surface_normal
gravity
wind
custom_force
```

---

# 53. PARTICLE COLLISION

Deberá poder declararse:

```text
NONE
WORLD
SURFACE
CHARACTER
CUSTOM
```

---

# 54. VFX ATTACHMENT

Los efectos deberán poder asociarse a:

```text
asset
socket
bone
surface
gameplay_event
world_position
```

---

# 55. CHARACTER VFX

Los personajes podrán tener:

```text
footstep_effect
weapon_effect
damage_effect
shield_effect
death_effect
ability_effect
```

---

# 56. WEAPON VFX

Las armas podrán declarar:

```text
muzzle_flash
impact
tracer
heat
energy
reload
overheat
```

---

# 57. ENVIRONMENT VFX

El entorno podrá declarar:

```text
steam
sparks
leaking_pipe
electrical_failure
dust
debris
fire
smoke
```

---

# 58. DAMAGE VFX

Deberá existir integración con estados de daño:

```text
INTACT
DAMAGED
HEAVILY_DAMAGED
DESTROYED
```

---

# 59. DESTRUCTION VFX

Los elementos destruibles deberán poder declarar:

```text
debris
dust
particles
lights
emissive
smoke
```

---

# 60. EMISSIVE INTEGRATION

Los materiales emisivos podrán actuar como fuentes visuales de iluminación.

El sistema deberá distinguir:

```text
VISUAL_EMISSION
ACTUAL_LIGHT
```

No deberá asumir que todo emissive ilumina físicamente la escena.

---

# 61. POST PROCESS SYSTEM

Deberá existir:

```text
PostProcessProfile
```

---

# 62. POST PROCESS PARAMETERS

Mínimo:

```text
exposure
contrast
saturation
temperature
bloom
vignette
chromatic_aberration
film_grain
color_grading
```

---

# 63. POST PROCESS VOLUME

Los volúmenes deberán tener:

```text
bounds
priority
blend_radius
profile
```

---

# 64. POST PROCESS ZONING

Los perfiles podrán asociarse a:

```text
world
biome
room
gameplay_zone
cinematic_zone
```

---

# 65. CINEMATIC PROFILE

Deberá existir:

```text
CinematicPresentationProfile
```

---

# 66. CINEMATIC CAMERA

Deberá poder definirse:

```text
position
rotation
fov
near_clip
far_clip
```

---

# 67. CAMERA VALIDATION

Las cámaras deberán comprobar:

```text
collision
visibility
framing
clipping
exposure
```

---

# 68. HERO SHOTS

El sistema deberá poder producir cámaras de referencia para:

```text
character
environment
landmark
boss
weapon
POI
```

---

# 69. FOUR-VIEW VALIDATION

Los assets relevantes deberán poder evaluarse mediante:

```text
FRONT
BACK
SIDE
ACTION
```

o el perfil de vistas correspondiente.

---

# 70. LIGHTING GOLDEN VIEWS

Deberán existir vistas estándar:

```text
DAY
NIGHT
INTERIOR
COMBAT
CINEMATIC
```

---

# 71. VISUAL QA

Cada generación deberá poder producir evidencia visual.

---

# 72. VISUAL QA DATA

Mínimo:

```text
camera
exposure
lighting_profile
weather_profile
vfx_profile
render_configuration
```

---

# 73. VFX BUDGET

Cada VFX deberá declarar:

```text
particle_budget
overdraw_budget
material_budget
texture_budget
simulation_budget
```

---

# 74. OVERDRAW ANALYSIS

Los efectos deberán poder clasificarse por coste de overdraw.

---

# 75. PARTICLE COUNT

Deberá existir límite:

```text
max_particles
max_spawn_rate
max_simultaneous_particles
```

---

# 76. VFX LOD

Los efectos deberán soportar:

```text
LOD0
LOD1
LOD2
DISABLED
```

---

# 77. DISTANCE SCALING

La calidad podrá reducirse según distancia:

```text
distance
importance
screen_size
```

---

# 78. EFFECT PRIORITY

Cada VFX deberá tener:

```text
LOW
NORMAL
HIGH
CRITICAL
```

---

# 79. PERFORMANCE FALLBACK

Cuando un presupuesto sea excedido, el sistema deberá aplicar la política configurada:

```text
REDUCE_RATE
REDUCE_QUALITY
DISABLE_SECONDARY_EFFECT
REPLACE_EFFECT
REJECT
```

---

# 80. NO SILENT DEGRADATION

Toda degradación automática deberá registrarse.

---

# 81. LIGHTING CONSISTENCY

Deberá comprobarse que:

```text
materials
lights
post_process
atmosphere
```

utilicen una exposición coherente.

---

# 82. EMISSIVE VALIDATION

Deberán detectarse materiales emisivos que provoquen:

```text
clipping
bloom_explosion
unreadable_highlights
```

---

# 83. SHADOW CONSISTENCY

Deberán detectarse:

```text
missing_shadow
unexpected_shadow
shadow_conflict
shadow_budget_overflow
```

---

# 84. VFX DEPENDENCY GRAPH

Deberá existir:

```text
VFXDependencyGraph
```

para representar:

```text
EVENT
→
VFX
→
MATERIAL
→
TEXTURE
→
LIGHT
→
AUDIO
```

---

# 85. EVENT-DRIVEN VFX

Los efectos deberán poder declararse mediante eventos:

```text
SPAWN
IMPACT
DAMAGE
DEATH
DESTRUCTION
INTERACTION
OBJECTIVE
WEAPON_FIRE
WEATHER_CHANGE
CUSTOM
```

---

# 86. VFX EVENT CONTRACT

Cada evento deberá declarar:

```text
event_id
event_type
source
target
location
parameters
```

---

# 87. VFX REPRODUCIBILITY

Los efectos procedurales deberán ser reproducibles mediante:

```text
seed
generator_version
profile_version
```

---

# 88. RANDOMNESS

La aleatoriedad visual deberá estar limitada a:

```text
particle_variation
rotation
scale
timing
color_variation
spawn_offset
```

cuando el profile lo permita.

---

# 89. LIGHTING SEED

Los sistemas procedurales de iluminación deberán poder reproducirse con el seed del mundo.

---

# 90. WORLD PRESENTATION GRAPH

Deberá existir:

```text
PresentationGraph
```

que conecte:

```text
BIOME
→
WEATHER
→
ATMOSPHERE
→
LIGHTING
→
VFX
→
POST_PROCESS
```

---

# 91. BIOME PRESENTATION

Cada biome podrá definir:

```text
lighting_profile
weather_profile
atmosphere_profile
vfx_profile
```

---

# 92. ROOM PRESENTATION

Cada room podrá sobrescribir determinados parámetros.

---

# 93. OVERRIDE HIERARCHY

La prioridad será:

```text
GLOBAL
↓
WORLD
↓
BIOME
↓
ZONE
↓
ROOM
↓
ASSET
↓
EVENT
```

---

# 94. OVERRIDE RULE

Un nivel inferior podrá modificar únicamente propiedades permitidas.

No podrá romper contratos globales.

---

# 95. LIGHTING VALIDATION PIPELINE

```text
PLAN
↓
GENERATE
↓
ANALYZE
↓
OPTIMIZE
↓
VALIDATE
↓
COMMIT
```

---

# 96. VFX VALIDATION PIPELINE

```text
SPECIFICATION
↓
GENERATION
↓
SIMULATION
↓
PERFORMANCE ANALYSIS
↓
VISUAL VALIDATION
↓
EXPORT
```

---

# 97. TEST ARCHITECTURE

UAF-81.25 deberá implementar obligatoriamente:

```text
UNIT TESTS
INTEGRATION TESTS
CONTRACT TESTS
DETERMINISM TESTS
REGRESSION TESTS
GOLDEN TESTS
FAILURE TESTS
PERFORMANCE TESTS
EXPORT TESTS
```

---

# 98. UNIT TESTS — LIGHTS

Deberán probar:

```text
light_creation
light_defaults
light_validation
light_transform
light_color
light_temperature
light_shadow_policy
light_budget
```

---

# 99. UNIT TESTS — ATMOSPHERE

Deberán probar:

```text
sky_creation
fog_creation
density_validation
height_falloff
atmosphere_parameters
```

---

# 100. UNIT TESTS — VFX

Deberán probar:

```text
vfx_creation
particle_parameters
lifetime
velocity
spawn_rate
attachment
priority
LOD
```

---

# 101. UNIT TESTS — WEATHER

Deberán probar:

```text
weather_creation
weather_parameters
transition_rules
intensity_limits
seed_reproducibility
```

---

# 102. UNIT TESTS — POST PROCESS

Deberán probar:

```text
profile_creation
parameter_ranges
volume_assignment
priority
blend_radius
```

---

# 103. CONTRACT TESTS

Deberán verificarse contratos entre:

```text
WORLD
LIGHTING
MATERIALS
VFX
WEATHER
POST_PROCESS
UNREAL_EXPORT
```

---

# 104. MATERIAL/LIGHT CONTRACT

Deberá comprobarse que los materiales emisivos utilizados por lighting respeten:

```text
emissive_limits
color_space
exposure_policy
```

---

# 105. WORLD/LIGHT CONTRACT

Toda luz deberá encontrarse dentro de:

```text
world_bounds
```

salvo excepciones explícitas.

---

# 106. WORLD/VFX CONTRACT

Todo VFX deberá tener:

```text
valid_location
valid_attachment
valid_budget
```

---

# 107. DETERMINISM TEST

Dado:

```text
same_world
same_seed
same_generator_version
same_profile
```

el resultado deberá ser equivalente.

---

# 108. DETERMINISM ASSERTION

Deberán compararse:

```text
light_count
light_transforms
light_parameters
vfx_count
vfx_transforms
particle_configuration
weather_state
post_process_configuration
```

---

# 109. SEED DIFFERENTIATION TEST

Seeds diferentes deberán poder producir variación cuando el profile lo permita.

---

# 110. FALSE RANDOMNESS TEST

No deberán existir variaciones no explicadas por:

```text
seed
time
explicit_runtime_state
```

---

# 111. GOLDEN LIGHTING TESTS

Deberán existir escenas de referencia:

```text
GOLDEN_INTERIOR
GOLDEN_EXTERIOR
GOLDEN_NIGHT
GOLDEN_STORM
GOLDEN_SCI_FI
```

---

# 112. GOLDEN VFX TESTS

Deberán existir:

```text
GOLDEN_FIRE
GOLDEN_SMOKE
GOLDEN_EXPLOSION
GOLDEN_ELECTRIC
GOLDEN_DUST
GOLDEN_RAIN
```

---

# 113. GOLDEN PRESENTATION TEST

Una escena completa deberá combinar:

```text
geometry
materials
lighting
atmosphere
vfx
post_process
```

---

# 114. VISUAL REGRESSION

Las escenas golden deberán producir evidencia comparable entre versiones.

---

# 115. REGRESSION POLICY

Una diferencia visual significativa deberá generar:

```text
REGRESSION
```

hasta que sea aceptada explícitamente.

---

# 116. FAILURE TEST — INVALID LIGHT

Debe rechazarse una luz con:

```text
NaN
infinite_intensity
invalid_color
invalid_position
```

---

# 117. FAILURE TEST — INVALID VFX

Debe rechazarse un VFX con:

```text
negative_lifetime
negative_spawn_rate
invalid_material
invalid_attachment
```

---

# 118. FAILURE TEST — BUDGET

Debe rechazarse o degradarse un sistema que exceda el presupuesto según policy.

---

# 119. FAILURE TEST — WORLD BOUNDS

Debe rechazarse contenido fuera del mundo cuando no exista autorización explícita.

---

# 120. FAILURE TEST — MISSING DEPENDENCY

Un VFX que requiera un material inexistente deberá producir:

```text
DEPENDENCY_MISSING
```

y no una referencia inválida silenciosa.

---

# 121. FAILURE TEST — INVALID PROFILE

Un profile incompatible deberá fallar antes de comenzar la generación destructiva.

---

# 122. PERFORMANCE TEST — LIGHTING

Deberá medirse:

```text
light_count
shadow_light_count
estimated_shadow_cost
estimated_gpu_cost
```

---

# 123. PERFORMANCE TEST — VFX

Deberá medirse:

```text
particle_count
spawn_rate
material_count
overdraw_estimate
simulation_cost
```

---

# 124. PERFORMANCE TEST — WEATHER

Deberá medirse:

```text
active_emitters
particle_count
volume_count
update_cost
```

---

# 125. PERFORMANCE TEST — COMPLETE SCENE

Deberá medirse:

```text
lighting_cost
vfx_cost
material_cost
texture_cost
estimated_memory
estimated_draw_calls
```

---

# 126. PERFORMANCE REGRESSION

Ninguna modificación podrá incrementar costes por encima de los límites configurados sin producir diagnóstico explícito.

---

# 127. EXPORT TESTS

Deberá verificarse que el paquete final contenga:

```text
LIGHTING_DATA
VFX_DATA
WEATHER_DATA
ATMOSPHERE_DATA
POST_PROCESS_DATA
MATERIAL_REFERENCES
TEXTURE_REFERENCES
METADATA
VALIDATION_REPORT
```

---

# 128. UNREAL CONTRACT TEST

Los nombres, tipos, referencias y parámetros destinados a Unreal deberán cumplir el contrato definido por el exporter.

---

# 129. BROKEN REFERENCE TEST

No deberán existir referencias hacia:

```text
missing_asset
missing_material
missing_texture
missing_vfx
missing_profile
```

---

# 130. SERIALIZATION TEST

Todos los profiles deberán poder:

```text
serialize
deserialize
validate
```

sin pérdida semántica.

---

# 131. ROUND-TRIP TEST

Deberá cumplirse:

```text
OBJECT
→
SERIALIZE
→
DESERIALIZE
→
OBJECT
```

manteniendo equivalencia.

---

# 132. SNAPSHOT TEST

La ejecución deberá generar:

```text
PresentationSnapshot
```

con:

```text
generator_version
seed
profiles
placements
overrides
diagnostics
```

---

# 133. ROLLBACK TEST

Una generación fallida deberá poder revertirse sin dejar:

```text
orphan_assets
orphan_lights
orphan_vfx
invalid_references
temporary_state
```

---

# 134. INCREMENTAL TEST

Deberá poder regenerarse:

```text
LIGHTING_ONLY
WEATHER_ONLY
VFX_ONLY
POST_PROCESS_ONLY
SINGLE_ZONE
SINGLE_ROOM
FULL_PRESENTATION
```

---

# 135. DEPENDENCY INVALIDATION TEST

Modificar un perfil deberá invalidar únicamente sus dependencias.

---

# 136. ISOLATION TEST

Modificar:

```text
ROOM_A
```

no deberá alterar silenciosamente:

```text
ROOM_B
```

---

# 137. CROSS-WORLD ISOLATION TEST

Dos mundos diferentes deberán mantener separados:

```text
assets
profiles
seeds
snapshots
diagnostics
exports
```

---

# 138. CONCURRENCY TEST

El sistema deberá poder detectar o impedir conflictos entre generaciones concurrentes que intenten modificar el mismo destino.

---

# 139. PATH PORTABILITY TEST

No deberán existir rutas absolutas obligatorias como:

```text
E:\
D:\
C:\
```

dentro de los contratos del sistema.

---

# 140. ENVIRONMENT PORTABILITY TEST

La fase deberá funcionar independientemente de la letra de unidad del sistema.

---

# 141. MODULE IMPORT TEST

Todos los módulos de UAF-81.25 deberán poder importarse sin:

```text
NameError
ImportError
ModuleNotFoundError
```

por dependencias internas ausentes.

---

# 142. TYPE VALIDATION TEST

Todas las estructuras públicas deberán poder validarse con los tipos definidos por el contrato.

---

# 143. TEST DISCOVERY REQUIREMENT

Los tests deberán ser descubiertos automáticamente mediante:

```text
python -m unittest discover
```

y/o:

```text
python -m pytest
```

según la infraestructura existente.

---

# 144. TEST NAMING

Los tests deberán seguir:

```text
test_uaf8125_<subsystem>_<behavior>
```

Ejemplo:

```text
test_uaf8125_lighting_budget_rejects_overflow
test_uaf8125_vfx_deterministic_generation
test_uaf8125_weather_transition_validation
```

---

# 145. TEST DATA

Los datos golden deberán permanecer versionados.

No deberán depender de archivos temporales.

---

# 146. TEST ISOLATION

Cada test deberá limpiar:

```text
temporary_assets
temporary_profiles
temporary_exports
temporary_world_state
```

---

# 147. TEST FAILURE REPORT

Cada fallo deberá incluir:

```text
test_id
phase
subsystem
expected
actual
seed
profile
world_id
asset_id
location
diagnostic_code
```

cuando corresponda.

---

# 148. ACCEPTANCE TEST — EMPTY WORLD

Debe poder generarse un mundo sin VFX y sin iluminación avanzada.

Resultado:

```text
VALID
```

si el profile lo permite.

---

# 149. ACCEPTANCE TEST — FULL SCI-FI SCENE

Debe poder generarse:

```text
terrain
architecture
materials
lighting
fog
VFX
weather
post_process
```

como una única composición.

---

# 150. ACCEPTANCE TEST — NIGHT SCENE

Debe validarse:

```text
visibility
exposure
navigation
landmarks
combat readability
```

---

# 151. ACCEPTANCE TEST — STORM

Debe validarse:

```text
rain
fog
wind
lightning
visibility
particle_budget
lighting_budget
```

---

# 152. ACCEPTANCE TEST — COMBAT

La iluminación y VFX no deberán destruir:

```text
enemy readability
cover readability
navigation readability
weapon readability
objective readability
```

---

# 153. ACCEPTANCE TEST — CINEMATIC

Debe poder producirse una composición visual controlada para:

```text
character
boss
landmark
environment
```

---

# 154. ACCEPTANCE TEST — REGENERATION

La regeneración con el mismo seed deberá producir un resultado equivalente.

---

# 155. ACCEPTANCE TEST — FAILURE RECOVERY

Una generación deliberadamente fallida deberá:

```text
FAIL
REPORT
ROLLBACK
```

sin corrupción del estado anterior.

---

# 156. ACCEPTANCE TEST — PORTABILITY

La fase deberá ejecutarse sin depender de una unidad de disco específica.

---

# 157. ACCEPTANCE TEST — COMPLETE PIPELINE

Deberá existir una prueba:

```text
INTENT
→
WORLD
→
MATERIALS
→
LIGHTING
→
VFX
→
VALIDATION
→
UNREAL_PACKAGE
```

---

# 158. REQUIRED TEST MINIMUM

UAF-81.25 no podrá considerarse completa si no existen como mínimo:

```text
30 UNIT TESTS
15 INTEGRATION TESTS
10 CONTRACT TESTS
10 FAILURE TESTS
10 DETERMINISM TESTS
10 PERFORMANCE TESTS
10 EXPORT TESTS
10 GOLDEN/REGRESSION TESTS
```

Total mínimo:

```text
105 TESTS
```

La cantidad podrá aumentar; nunca reducirse por debajo de este mínimo.

---

# 159. QUALITY GATE

La fase podrá avanzar únicamente cuando:

```text
ALL_REQUIRED_TESTS_DISCOVERED
AND
ALL_UNIT_TESTS_PASS
AND
ALL_INTEGRATION_TESTS_PASS
AND
ALL_CONTRACT_TESTS_PASS
AND
ALL_FAILURE_TESTS_PASS
AND
ALL_DETERMINISM_TESTS_PASS
AND
ALL_EXPORT_TESTS_PASS
AND
NO_CRITICAL_DIAGNOSTICS
```

---

# 160. PERFORMANCE GATE

Además:

```text
LIGHTING_BUDGET_VALID
AND
VFX_BUDGET_VALID
AND
TEXTURE_BUDGET_VALID
AND
MEMORY_BUDGET_VALID
```

---

# 161. REGRESSION GATE

No deberá existir una regresión golden sin:

```text
documented_reason
approved_change
updated_baseline
```

---

# 162. EXPORT GATE

No deberá producirse un paquete final si existen:

```text
BROKEN_REFERENCES
INVALID_PROFILES
MISSING_DEPENDENCIES
CRITICAL_PERFORMANCE_FAILURE
CRITICAL_VISUAL_FAILURE
```

---

# 163. DEFINITION OF DONE

UAF-81.25 estará terminada únicamente cuando:

```text
ARCHITECTURE_IMPLEMENTED
SCHEMAS_IMPLEMENTED
LIGHTING_IMPLEMENTED
ATMOSPHERE_IMPLEMENTED
WEATHER_IMPLEMENTED
VFX_IMPLEMENTED
POST_PROCESS_IMPLEMENTED
PRESENTATION_GRAPH_IMPLEMENTED
VALIDATION_IMPLEMENTED
OPTIMIZATION_IMPLEMENTED
SERIALIZATION_IMPLEMENTED
SNAPSHOT_IMPLEMENTED
ROLLBACK_IMPLEMENTED
UNREAL_EXPORT_IMPLEMENTED
UNIT_TESTS_IMPLEMENTED
INTEGRATION_TESTS_IMPLEMENTED
CONTRACT_TESTS_IMPLEMENTED
FAILURE_TESTS_IMPLEMENTED
DETERMINISM_TESTS_IMPLEMENTED
PERFORMANCE_TESTS_IMPLEMENTED
EXPORT_TESTS_IMPLEMENTED
GOLDEN_TESTS_IMPLEMENTED
REGRESSION_TESTS_IMPLEMENTED
DOCUMENTATION_COMPLETE
```

---

# 164. FINAL ACCEPTANCE CONDITION

La fase será aceptada cuando el sistema pueda recibir:

```text
WORLD
+
WORLD_STYLE
+
LIGHTING_PROFILE
+
ATMOSPHERE_PROFILE
+
WEATHER_PROFILE
+
VFX_PROFILE
+
POST_PROCESS_PROFILE
+
SEED
```

y producir de forma determinista:

```text
COMPLETE_PRESENTATION
+
VALIDATION_REPORT
+
PERFORMANCE_REPORT
+
UNREAL_EXPORT_PACKAGE
+
REPRODUCTION_SNAPSHOT
```

sin intervención manual obligatoria.

---

# 165. FINAL OBJECTIVE

UAF-81.25 deberá transformar:

```text
GENERATED WORLD
```

en:

```text
PRESENTABLE GAME WORLD
```

manteniendo simultáneamente:

```text
VISUAL QUALITY
GAMEPLAY READABILITY
PERFORMANCE
DETERMINISM
TRACEABILITY
REPRODUCIBILITY
UNREAL COMPATIBILITY
```

---

# 166. NEXT PHASE

```text
UAF-81.26 — CHARACTER FABRICATION, ADVANCED ANATOMY, CLOTHING, HAIR, SKINNING & RIGGING SYSTEM
```

La siguiente fase deberá resolver específicamente la principal limitación actual del generador de personajes:

```text
COMPLEX ORGANIC CHARACTERS
+
CLOTHING
+
ACCESSORIES
+
HAIR
+
FACE
+
ANATOMY
+
MODULAR BODY PARTS
+
SKINNING
+
SKELETON
+
RIGGING
+
WEIGHT TRANSFER
+
DEFORMATION
+
LOD
+
UNREAL CHARACTER EXPORT
```

y deberá incorporar desde su definición inicial **tests unitarios, integración, golden, deformación, skinning, rigging, determinismo, regresión, performance y exportación**.
