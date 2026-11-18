# UAF-81.57 — UNIVERSAL AI, NPC, CROWD, BEHAVIOR & SIMULATION SYSTEM

## UAF-81.57-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA UNIVERSAL DE IA, NPC, MULTITUDES, COMPORTAMIENTO Y SIMULACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.57 — Universal AI, NPC, Crowd, Behavior & Simulation System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.56  
**Next Phase:** UAF-81.58  

---

# 1. PURPOSE

UAF-81.57 define la capa universal de inteligencia artificial y simulación responsable de transformar entidades estáticas del mundo en agentes capaces de:

```text
PERCEIVE
THINK
DECIDE
MOVE
NAVIGATE
INTERACT
COMMUNICATE
FIGHT
COOPERATE
SCHEDULE
RESPOND
ADAPT
SLEEP
RESUME
```

---

# 2. PRIMARY OBJECTIVE

El resultado deberá ser:

```text
ProductionReadySimulation
```

reproducible mediante:

```text
simulation_definition
world_snapshot
agent_profiles
behavior_profiles
navigation_profile
seed
simulation_tick
simulation_version
```

---

# 3. AI ARCHITECTURE

La arquitectura deberá separar:

```text
PERCEPTION
        ↓
WORLD STATE
        ↓
MEMORY
        ↓
DECISION
        ↓
BEHAVIOR
        ↓
ACTION
        ↓
MOVEMENT
        ↓
WORLD EFFECT
```

Ninguna capa deberá asumir ownership de otra.

---

# 4. AI AGENT

Deberá existir:

```text
AIAgent
```

con:

```text
agent_id
profile_id
entity_reference
transform
state
needs
senses
memory
goals
behavior
navigation
combat
interaction
schedule
simulation
```

---

# 5. AGENT ID

El identificador deberá ser estable.

No deberá depender del orden accidental de spawn.

---

# 6. AGENT PROFILE

Deberá existir:

```text
AgentProfile
```

con:

```text
agent_type
movement
senses
intelligence
behavior
combat
interaction
needs
social
schedule
simulation_lod
```

---

# 7. AGENT TYPES

Mínimo:

```text
PLAYER_PROXY
NPC
ANIMAL
CREATURE
CROWD_AGENT
VEHICLE_AGENT
COMPANION
ENEMY
BOSS
CUSTOM
```

---

# 8. AGENT STATE

Deberá existir:

```text
AgentState
```

con:

```text
position
rotation
velocity
acceleration
health
stamina
current_action
current_goal
current_target
current_location
alert_level
simulation_level
```

---

# 9. AGENT LIFECYCLE

Estados mínimos:

```text
SPAWNING
ACTIVE
PAUSED
SUSPENDED
DESPAWNING
DEAD
PERSISTED
```

---

# 10. AGENT SPAWN

El spawn deberá validar:

```text
spawn_point
navigation
collision
world_bounds
profile
population_budget
```

---

# 11. SPAWN FAILURE

Si un agente no puede aparecer deberá producir:

```text
AI_SPAWN_FAILED
```

con diagnóstico.

Nunca deberá quedar un agente parcialmente creado.

---

# 12. DESPAWN

El despawn deberá ser reversible cuando la simulación requiera persistencia.

---

# 13. PERSISTENCE

Un agente persistente deberá poder guardar:

```text
transform
health
inventory_reference
state
schedule_state
memory
goal
relationships
```

---

# 14. AI WORLD STATE

Deberá existir:

```text
AIWorldState
```

que exponga información relevante del mundo sin copiar todo el World Scene Graph.

---

# 15. WORLD STATE SOURCES

Mínimo:

```text
TERRAIN
NAVIGATION
WEATHER
TIME
WATER
STRUCTURES
ACTORS
OBJECTS
QUEST_STATE
GAME_STATE
```

---

# 16. WORLD STATE SNAPSHOT

La IA deberá poder consumir un snapshot consistente por tick.

---

# 17. SIMULATION TICK

Deberá existir:

```text
SimulationTick
```

---

# 18. TICK STRUCTURE

Orden normativo:

```text
INPUT
↓
WORLD_UPDATE
↓
PERCEPTION
↓
MEMORY
↓
DECISION
↓
BEHAVIOR
↓
ACTION
↓
MOVEMENT
↓
INTERACTION
↓
COMBAT
↓
STATE_COMMIT
↓
EVENTS
```

---

# 19. TICK DETERMINISM

Cuando se solicite simulación determinista, el mismo:

```text
initial_state
seed
tick_sequence
inputs
simulation_version
```

deberá producir el mismo resultado lógico.

---

# 20. RANDOMNESS

La IA no deberá utilizar random global.

Deberá existir:

```text
AIRandomStream
```

por agente o subsistema.

---

# 21. RANDOM STREAM

La semilla deberá derivarse de:

```text
simulation_seed
agent_id
subsystem_id
tick
```

cuando corresponda.

---

# 22. PERCEPTION SYSTEM

Deberá existir:

```text
PerceptionSystem
```

---

# 23. SENSES

Mínimo:

```text
VISION
HEARING
SMELL
TOUCH
PROXIMITY
WORLD_QUERY
CUSTOM
```

---

# 24. VISION

Deberá soportar:

```text
range
field_of_view
vertical_fov
line_of_sight
occlusion
target_filters
```

---

# 25. VISION RESULT

Deberá producir:

```text
PerceptionEvent
```

con:

```text
source
target
sense
confidence
distance
direction
timestamp
```

---

# 26. LINE OF SIGHT

Deberá utilizar la capa de collision/world definida en UAF-81.56.

---

# 27. HEARING

Deberá existir:

```text
HearingProfile
```

con:

```text
range
attenuation
frequency
priority
occlusion
```

---

# 28. SOUND EVENT

Deberá existir:

```text
AISoundEvent
```

con:

```text
position
volume
category
source
timestamp
```

---

# 29. SMELL

Cuando el backend lo soporte deberá existir:

```text
ScentField
```

---

# 30. PROXIMITY

Deberá detectar agentes y objetos dentro de:

```text
radius
box
capsule
custom_volume
```

---

# 31. PERCEPTION FILTERS

Mínimo:

```text
ALLY
ENEMY
NEUTRAL
ANIMAL
PLAYER
OBJECT
ENVIRONMENT
CUSTOM
```

---

# 32. PERCEPTION CONFIDENCE

Deberá normalizarse:

```text
0..1
```

---

# 33. PERCEPTION MEMORY

Los eventos relevantes deberán poder persistir en memoria.

---

# 34. MEMORY SYSTEM

Deberá existir:

```text
AIMemory
```

---

# 35. MEMORY TYPES

Mínimo:

```text
SHORT_TERM
LONG_TERM
SPATIAL
SOCIAL
THREAT
TASK
EPISODIC
CUSTOM
```

---

# 36. MEMORY RECORD

Deberá contener:

```text
memory_id
type
subject
location
timestamp
confidence
importance
expiration
source
```

---

# 37. MEMORY DECAY

Deberá existir:

```text
decay_rate
minimum_confidence
expiration
```

---

# 38. MEMORY CAPACITY

Deberá existir límite configurable.

---

# 39. MEMORY PRIORITY

Cuando la memoria esté llena deberá conservar información de mayor prioridad.

---

# 40. MEMORY VALIDATION

Deberá detectar:

```text
duplicate_memory
invalid_timestamp
invalid_confidence
expired_memory
capacity_overflow
```

---

# 41. TARGETING SYSTEM

Deberá existir:

```text
TargetingSystem
```

---

# 42. TARGET SCORE

El score podrá considerar:

```text
distance
visibility
threat
health
priority
relationship
objective
```

---

# 43. TARGET LOCK

Deberá soportarse:

```text
LOCKED
SOFT_LOCK
NO_LOCK
```

---

# 44. TARGET INVALIDATION

Un target deberá invalidarse si:

```text
dead
despawned
out_of_range
invalid_relationship
not_visible
objective_completed
```

según profile.

---

# 45. DECISION SYSTEM

Deberá existir:

```text
DecisionSystem
```

---

# 46. DECISION MODELS

Mínimo:

```text
FINITE_STATE_MACHINE
BEHAVIOR_TREE
UTILITY_AI
GOAP
RULE_BASED
SCRIPTED
HYBRID
CUSTOM
```

---

# 47. FSM

Deberá existir:

```text
StateDefinition
StateTransition
```

---

# 48. FSM TRANSITION

Cada transición deberá poder declarar:

```text
condition
priority
cooldown
interruptibility
```

---

# 49. FSM VALIDATION

Deberá detectar:

```text
missing_initial_state
missing_target_state
cycle_without_exit
duplicate_transition
invalid_condition
```

---

# 50. BEHAVIOR TREE

Deberá existir:

```text
BehaviorTree
```

---

# 51. BEHAVIOR NODE TYPES

Mínimo:

```text
SEQUENCE
SELECTOR
PARALLEL
DECORATOR
CONDITION
ACTION
WAIT
REPEAT
RANDOM_SELECTOR
UTILITY_SELECTOR
```

---

# 52. BEHAVIOR STATUS

Mínimo:

```text
RUNNING
SUCCESS
FAILURE
ABORTED
```

---

# 53. BEHAVIOR TREE ABORT

Deberá soportar:

```text
SELF
LOWER_PRIORITY
BOTH
NONE
```

---

# 54. BEHAVIOR TREE VALIDATION

Deberá detectar:

```text
orphan_node
cycle
missing_child
invalid_decorator
invalid_root
```

---

# 55. UTILITY AI

Deberá existir:

```text
UtilityAction
```

con:

```text
considerations
curve
weight
cooldown
priority
```

---

# 56. UTILITY CONSIDERATIONS

Mínimo:

```text
DISTANCE
HEALTH
HUNGER
THIRST
FEAR
THREAT
TIME
WEATHER
RELATIONSHIP
OBJECTIVE
```

---

# 57. UTILITY CURVES

Mínimo:

```text
LINEAR
QUADRATIC
EXPONENTIAL
LOGISTIC
CUSTOM
```

---

# 58. GOAP

Deberá existir:

```text
Goal
WorldFact
Action
Precondition
Effect
Planner
```

---

# 59. GOAP ACTION

Cada action deberá declarar:

```text
preconditions
effects
cost
duration
interruptibility
```

---

# 60. GOAP PLANNER

Deberá poder producir:

```text
ActionPlan
```

---

# 61. GOAP FAILURE

Si no existe plan deberá devolver:

```text
NO_VALID_PLAN
```

y no ejecutar acciones parciales.

---

# 62. BEHAVIOR PRIORITY

Deberá existir una política explícita para resolver conflictos entre:

```text
combat
survival
mission
social
routine
idle
```

---

# 63. ACTION SYSTEM

Deberá existir:

```text
AIActionSystem
```

---

# 64. ACTION TYPES

Mínimo:

```text
MOVE
LOOK
WAIT
INTERACT
PICKUP
DROP
USE
TALK
ATTACK
DEFEND
FLEE
FOLLOW
GUARD
SEARCH
SLEEP
EAT
DRINK
WORK
CUSTOM
```

---

# 65. ACTION STATE

Mínimo:

```text
QUEUED
RUNNING
SUCCESS
FAILED
CANCELLED
INTERRUPTED
```

---

# 66. ACTION INTERRUPTS

Deberán soportarse:

```text
DAMAGE
THREAT
DEATH
PLAYER_COMMAND
HIGHER_PRIORITY
WORLD_CHANGE
```

---

# 67. ACTION FAILURE

Cada acción deberá declarar códigos de fallo posibles.

---

# 68. MOVEMENT SYSTEM

Deberá existir:

```text
AIMovementSystem
```

---

# 69. MOVEMENT MODES

Mínimo:

```text
WALK
RUN
SPRINT
CROUCH
CRAWL
CLIMB
SWIM
FLY
DRIVE
CUSTOM
```

---

# 70. MOVEMENT PROFILE

Deberá declarar:

```text
speed
acceleration
deceleration
turn_rate
radius
height
step_height
slope_limit
```

---

# 71. PATHFINDING

Deberá existir:

```text
PathfindingSystem
```

---

# 72. PATHFINDING ALGORITHMS

Mínimo:

```text
A_STAR
DIJKSTRA
FLOW_FIELD
NAVMESH_QUERY
GRID
CUSTOM
```

---

# 73. PATH RESULT

Deberá contener:

```text
status
waypoints
cost
distance
estimated_time
```

---

# 74. PATH STATUS

```text
SUCCESS
PARTIAL
FAILED
INVALID
```

---

# 75. PATH INVALIDATION

Un path deberá invalidarse cuando:

```text
navigation_changes
target_moves
obstacle_added
obstacle_removed
world_streaming_changes
```

según profile.

---

# 76. DYNAMIC OBSTACLES

Deberá existir:

```text
DynamicObstacle
```

---

# 77. AVOIDANCE

Deberá soportar:

```text
AGENT_AVOIDANCE
OBSTACLE_AVOIDANCE
LOCAL_REPATH
```

---

# 78. CROWD SYSTEM

Deberá existir:

```text
CrowdSimulation
```

---

# 79. CROWD AGENT

Mínimo:

```text
agent_id
position
velocity
radius
priority
desired_velocity
avoidance_group
```

---

# 80. CROWD GROUPS

Deberá soportar:

```text
PEDESTRIAN
CIVILIAN
MILITARY
ANIMAL
EMERGENCY
CUSTOM
```

---

# 81. CROWD DENSITY

Deberá poder medirse por cell.

---

# 82. CROWD FLOW

Deberá existir:

```text
CrowdFlowField
```

---

# 83. CROWD AVOIDANCE

Deberá evitar:

```text
agents
static_obstacles
dynamic_obstacles
restricted_regions
```

---

# 84. CROWD DEADLOCK

Deberá existir detección de:

```text
DEADLOCK
OSCILLATION
STAGNATION
```

---

# 85. FORMATION SYSTEM

Deberá existir:

```text
FormationDefinition
```

---

# 86. FORMATION TYPES

Mínimo:

```text
LINE
COLUMN
WEDGE
CIRCLE
SQUARE
CUSTOM
```

---

# 87. FORMATION MEMBERS

Cada miembro deberá tener:

```text
slot
priority
role
offset
```

---

# 88. FOLLOW SYSTEM

Deberá soportar:

```text
FOLLOW_AGENT
FOLLOW_TARGET
FOLLOW_PATH
FOLLOW_FORMATION
```

---

# 89. SOCIAL SYSTEM

Deberá existir:

```text
SocialSystem
```

---

# 90. RELATIONSHIP

Deberá existir:

```text
Relationship
```

con:

```text
source
target
affinity
trust
fear
respect
familiarity
faction
```

---

# 91. RELATIONSHIP RANGE

Los valores deberán normalizarse según el profile.

---

# 92. FACTION SYSTEM

Deberá existir:

```text
FactionDefinition
```

---

# 93. FACTION RELATIONS

Mínimo:

```text
ALLY
FRIENDLY
NEUTRAL
SUSPICIOUS
HOSTILE
```

---

# 94. SOCIAL MEMORY

Las interacciones importantes deberán alimentar memoria social.

---

# 95. COMMUNICATION SYSTEM

Deberá existir:

```text
AICommunicationSystem
```

---

# 96. COMMUNICATION TYPES

Mínimo:

```text
SPEECH
SIGNAL
RADIO
GESTURE
ALERT
CUSTOM
```

---

# 97. COMMUNICATION MESSAGE

Deberá contener:

```text
message_id
source
target
channel
payload
priority
timestamp
```

---

# 98. COMMUNICATION RANGE

Deberá depender del canal.

---

# 99. ALERT PROPAGATION

Deberá soportar propagación entre agentes.

---

# 100. GROUP BEHAVIOR

Deberá existir:

```text
GroupBehaviorSystem
```

---

# 101. GROUP ROLES

Mínimo:

```text
LEADER
FOLLOWER
SCOUT
SUPPORT
ATTACKER
DEFENDER
MEDIC
CIVILIAN
CUSTOM
```

---

# 102. GROUP STATE

Deberá contener:

```text
group_id
leader
members
objective
formation
threat_level
location
```

---

# 103. SQUAD SYSTEM

Deberá soportar:

```text
formation
orders
roles
shared_target
shared_memory
```

---

# 104. COMBAT SYSTEM

Deberá existir:

```text
AICombatSystem
```

---

# 105. COMBAT STATES

Mínimo:

```text
IDLE
ALERT
SEARCHING
ENGAGING
DEFENDING
RETREATING
DEAD
```

---

# 106. COMBAT TARGETING

Deberá integrarse con TargetingSystem.

---

# 107. COMBAT RANGE

Deberá distinguir:

```text
MELEE
SHORT
MEDIUM
LONG
```

---

# 108. ATTACK DECISION

Deberá considerar:

```text
distance
visibility
weapon
health
stamina
cover
allies
enemy_count
```

---

# 109. COVER SYSTEM

Deberá existir:

```text
CoverPoint
```

---

# 110. COVER DATA

Mínimo:

```text
position
normal
height
protection
visibility
```

---

# 111. COVER QUERY

Deberá poder consultar:

```text
best_cover
nearest_cover
safe_cover
cover_against_target
```

---

# 112. FLEE SYSTEM

Deberá calcular:

```text
threat_direction
safe_location
escape_path
```

---

# 113. COMBAT VALIDATION

Deberá detectar:

```text
invalid_target
invalid_weapon
no_path
impossible_attack
dead_agent_action
```

---

# 114. INTERACTION SYSTEM

Deberá existir:

```text
AIInteractionSystem
```

---

# 115. INTERACTABLE

Deberá existir:

```text
InteractableDefinition
```

---

# 116. INTERACTION TYPES

Mínimo:

```text
TALK
OPEN
CLOSE
USE
PICKUP
DROP
ACTIVATE
SIT
SLEEP
WORK
TRADE
CUSTOM
```

---

# 117. INTERACTION CONDITIONS

Deberá soportar:

```text
distance
line_of_sight
inventory
faction
quest
state
time
permission
```

---

# 118. INTERACTION RESERVATION

Los objetos interactuables podrán reservarse para evitar conflictos.

---

# 119. RESERVATION FAILURE

Deberá devolver:

```text
INTERACTION_BUSY
```

sin corromper estado.

---

# 120. NEEDS SYSTEM

Deberá existir:

```text
NeedsSystem
```

---

# 121. NEED TYPES

Mínimo:

```text
HUNGER
THIRST
ENERGY
SAFETY
SOCIAL
COMFORT
CURIOSITY
CUSTOM
```

---

# 122. NEED VALUES

Deberán ser normalizables:

```text
0..1
```

---

# 123. NEED DECAY

Cada necesidad deberá declarar:

```text
base_decay
environment_modifier
activity_modifier
```

---

# 124. NEED PRIORITY

Las necesidades podrán afectar Utility AI y GOAP.

---

# 125. SURVIVAL SYSTEM

Deberá existir:

```text
SurvivalSystem
```

para agentes que lo requieran.

---

# 126. SLEEP SYSTEM

Deberá soportar:

```text
sleep_start
sleep_duration
wake_condition
sleep_location
```

---

# 127. EATING SYSTEM

Deberá soportar:

```text
food_source
consumption_duration
nutrition
availability
```

---

# 128. WORK SYSTEM

Deberá existir:

```text
WorkDefinition
```

---

# 129. WORK PARAMETERS

Mínimo:

```text
location
duration
skill
schedule
reward
interruptibility
```

---

# 130. SCHEDULE SYSTEM

Deberá existir:

```text
ScheduleDefinition
```

---

# 131. SCHEDULE ENTRY

Cada entrada deberá contener:

```text
start_time
end_time
activity
location
priority
```

---

# 132. SCHEDULE TRANSITION

Deberá soportar:

```text
time
event
condition
interrupt
```

---

# 133. SCHEDULE CONFLICT

Deberá resolverse mediante prioridad explícita.

---

# 134. DAILY ROUTINE

Deberá poder construirse:

```text
WAKE
EAT
WORK
SOCIAL
REST
SLEEP
```

---

# 135. WORLD REACTION

Los agentes deberán poder reaccionar a:

```text
weather
time
danger
fire
explosion
death
crime
crowd
quest
world_change
```

---

# 136. EVENT SYSTEM

Deberá existir:

```text
AIEventBus
```

---

# 137. EVENT TYPES

Mínimo:

```text
SPAWN
DESPAWN
DAMAGE
DEATH
SOUND
VISUAL
INTERACTION
QUEST
WEATHER
TIME
WORLD_CHANGE
ALERT
CUSTOM
```

---

# 138. EVENT ORDER

Los eventos deberán ordenarse determinísticamente cuando se requiera.

---

# 139. EVENT PRIORITY

Mínimo:

```text
CRITICAL
HIGH
NORMAL
LOW
```

---

# 140. QUEST INTEGRATION

La IA deberá exponer hooks para:

```text
quest_started
quest_updated
quest_completed
quest_failed
objective_changed
```

---

# 141. SAVE/LOAD

Deberá existir:

```text
AISaveState
```

---

# 142. SAVE CONTENT

Mínimo:

```text
agent_id
transform
state
health
needs
memory
relationships
current_goal
schedule_state
group_state
```

---

# 143. SAVE VERSION

Cada save deberá declarar:

```text
simulation_version
schema_version
world_hash
```

---

# 144. SAVE MIGRATION

Deberán existir migraciones entre versiones compatibles.

---

# 145. REPLAY SYSTEM

Deberá existir:

```text
SimulationReplay
```

---

# 146. REPLAY CONTENT

Mínimo:

```text
initial_state_hash
seed
inputs
events
tick_count
simulation_version
```

---

# 147. REPLAY VALIDATION

El replay deberá comprobar hashes periódicos.

---

# 148. DIVERGENCE DETECTION

Deberá detectar:

```text
tick
agent_id
expected_hash
actual_hash
```

---

# 149. AI LOD

Deberá existir:

```text
AISimulationLOD
```

---

# 150. AI LOD LEVELS

Mínimo:

```text
LOD0_FULL
LOD1_REDUCED
LOD2_BACKGROUND
LOD3_ABSTRACT
LOD4_FROZEN
```

---

# 151. LOD0

Deberá ejecutar:

```text
perception
decision
behavior
movement
interaction
combat
```

---

# 152. LOD1

Podrá reducir frecuencia de percepción y decisiones.

---

# 153. LOD2

Deberá simular resultados agregados sin ejecutar cada comportamiento individual.

---

# 154. LOD3

Podrá representar:

```text
population
location
activity
threat
```

sin agente individual completo.

---

# 155. LOD4

Deberá conservar únicamente estado necesario para futura reactivación.

---

# 156. AI LOD TRANSITION

Cambiar de LOD no deberá destruir:

```text
goal
memory
schedule
health
relationships
```

cuando sean persistentes.

---

# 157. BACKGROUND SIMULATION

Deberá existir:

```text
BackgroundSimulation
```

---

# 158. ABSTRACT AGENT

Deberá existir:

```text
AbstractAgentState
```

con:

```text
location
activity
population_group
health_state
resource_state
threat_state
```

---

# 159. POPULATION SIMULATION

Deberá poder simular grandes poblaciones mediante agregación.

---

# 160. POPULATION GROUP

Mínimo:

```text
faction
region
profession
age_group
activity
```

según el juego.

---

# 161. CROWD LOD

El crowd deberá poder pasar de:

```text
INDIVIDUAL
GROUP
FLOW
STATISTICAL
```

---

# 162. AI PERFORMANCE BUDGET

Deberá existir:

```text
max_active_agents
max_full_agents
max_perception_cost
max_pathfinding_cost
max_behavior_cost
max_combat_cost
max_memory_cost
```

---

# 163. AI BUDGET SCHEDULER

Deberá priorizar agentes mediante:

```text
distance
visibility
importance
combat
player_relevance
quest_relevance
```

---

# 164. UPDATE FREQUENCY

Cada subsistema deberá permitir:

```text
tick_rate
tick_interval
priority
```

---

# 165. AI PROFILING

Deberá producir:

```text
AIPerformanceReport
```

---

# 166. PERFORMANCE METRICS

Mínimo:

```text
perception_time
decision_time
behavior_time
pathfinding_time
movement_time
combat_time
interaction_time
crowd_time
memory_time
save_time
```

---

# 167. AI DIAGNOSTICS

Deberá existir:

```text
AIDiagnosticReport
```

---

# 168. DIAGNOSTIC DATA

Mínimo:

```text
agent_count
active_count
lod_distribution
path_failures
decision_failures
deadlocks
memory_usage
budget_usage
```

---

# 169. DEBUG TRACE

Deberá existir:

```text
AIDebugTrace
```

---

# 170. DEBUG TRACE CONTENT

Podrá incluir:

```text
perception
decision
selected_action
target
path
state_transition
event
```

---

# 171. TRACE DETERMINISM

El trace deberá poder reproducir el orden de decisión.

---

# 172. AI QUERY SYSTEM

Deberá existir:

```text
AIQuerySystem
```

---

# 173. AI QUERY TYPES

Mínimo:

```text
NEAREST_AGENT
VISIBLE_TARGETS
THREATS
ALLIES
COVER
SAFE_LOCATION
PATH
INTERACTABLES
POPULATION
```

---

# 174. AI QUERY FILTERS

Mínimo:

```text
distance
faction
type
state
visibility
health
tag
```

---

# 175. QUERY PERFORMANCE

Las queries deberán utilizar índices espaciales cuando corresponda.

---

# 176. SPATIAL INDEX

Deberá existir:

```text
AISpatialIndex
```

---

# 177. SPATIAL INDEX TYPES

Mínimo:

```text
GRID
QUADTREE
OCTREE
BVH
ENGINE_NATIVE
CUSTOM
```

---

# 178. INDEX CONSISTENCY

Toda modificación de posición relevante deberá actualizar el índice.

---

# 179. AI RESOURCE SYSTEM

Deberá poder consultar:

```text
food
water
shelter
weapons
items
vehicles
workstations
```

sin asumir ownership del inventario global.

---

# 180. AI VEHICLE SYSTEM

Deberá existir hook para:

```text
enter_vehicle
exit_vehicle
drive
follow_road
avoid_obstacle
park
```

---

# 181. VEHICLE PATH

Deberá utilizar navegación específica para vehículos cuando exista.

---

# 182. ANIMAL BEHAVIOR

Los animales deberán poder utilizar:

```text
graze
flee
hunt
rest
wander
follow_group
territorial_behavior
```

---

# 183. TERRITORY SYSTEM

Deberá existir opcionalmente:

```text
TerritoryDefinition
```

con:

```text
center
radius
owner
resources
threat_level
```

---

# 184. TERRITORY CONFLICT

Deberá poder generar eventos sociales o de combate.

---

# 185. CUSTOM AI PLUGINS

La arquitectura deberá permitir:

```text
CustomPerception
CustomDecision
CustomAction
CustomSensor
CustomPlanner
CustomBehavior
```

---

# 186. PLUGIN ISOLATION

Un plugin AI defectuoso no deberá corromper el estado global.

---

# 187. FAILURE CONTAINMENT

Los errores de un agente deberán aislarse siempre que sea posible.

---

# 188. AGENT ERROR

Deberá producir:

```text
AI_AGENT_ERROR
```

con:

```text
agent_id
system
state
tick
error_code
```

---

# 189. RECOVERY POLICY

Cada subsistema deberá declarar:

```text
IGNORE
RETRY
RESET_ACTION
RESET_BEHAVIOR
SUSPEND_AGENT
FAIL_SIMULATION
```

---

# 190. GLOBAL SIMULATION FAILURE

Sólo errores críticos deberán detener toda la simulación.

---

# 191. VALIDATION PIPELINE

Deberá ejecutarse:

```text
SCHEMA VALIDATION
↓
PROFILE VALIDATION
↓
WORLD VALIDATION
↓
NAVIGATION VALIDATION
↓
AGENT VALIDATION
↓
BEHAVIOR VALIDATION
↓
SCHEDULE VALIDATION
↓
SIMULATION VALIDATION
↓
PERFORMANCE VALIDATION
↓
DETERMINISM VALIDATION
```

---

# 192. TEST DIRECTORY

Deberá existir:

```text
tests/ai/
tests/navigation/
tests/behavior/
tests/crowd/
tests/combat/
tests/simulation/
tests/replay/
```

---

# 193. AGENT TESTS

Mínimo:

```text
test_agent_definition
test_agent_id
test_agent_spawn
test_agent_lifecycle
test_agent_state
test_agent_despawn
test_agent_persistence
test_agent_failure
```

---

# 194. PERCEPTION TESTS

Mínimo:

```text
test_vision
test_fov
test_line_of_sight
test_occlusion
test_hearing
test_sound_event
test_smell
test_proximity
test_perception_filter
test_perception_confidence
test_perception_memory
```

---

# 195. MEMORY TESTS

Mínimo:

```text
test_memory_insert
test_memory_update
test_memory_decay
test_memory_expiration
test_memory_capacity
test_memory_priority
test_memory_determinism
```

---

# 196. TARGETING TESTS

Mínimo:

```text
test_target_selection
test_target_score
test_target_lock
test_target_filter
test_target_invalidation
test_target_determinism
```

---

# 197. FSM TESTS

Mínimo:

```text
test_fsm_definition
test_fsm_transition
test_fsm_priority
test_fsm_interrupt
test_fsm_invalid_graph
test_fsm_determinism
```

---

# 198. BEHAVIOR TREE TESTS

Mínimo:

```text
test_bt_sequence
test_bt_selector
test_bt_parallel
test_bt_decorator
test_bt_condition
test_bt_action
test_bt_abort
test_bt_validation
test_bt_determinism
```

---

# 199. UTILITY AI TESTS

Mínimo:

```text
test_utility_action
test_utility_consideration
test_utility_curve
test_utility_priority
test_utility_cooldown
test_utility_selection
test_utility_determinism
```

---

# 200. GOAP TESTS

Mínimo:

```text
test_goap_goal
test_goap_fact
test_goap_action
test_goap_precondition
test_goap_effect
test_goap_planner
test_goap_no_plan
test_goap_determinism
```

---

# 201. ACTION TESTS

Mínimo:

```text
test_action_queue
test_action_execution
test_action_success
test_action_failure
test_action_cancel
test_action_interrupt
test_action_priority
```

---

# 202. MOVEMENT TESTS

Mínimo:

```text
test_walk
test_run
test_sprint
test_crouch
test_climb
test_swim
test_movement_profile
test_movement_collision
test_movement_determinism
```

---

# 203. PATHFINDING TESTS

Mínimo:

```text
test_astar
test_dijkstra
test_navmesh_query
test_grid_path
test_path_success
test_partial_path
test_path_failure
test_path_invalidation
test_dynamic_obstacle
test_path_determinism
```

---

# 204. CROWD TESTS

Mínimo:

```text
test_crowd_agent
test_crowd_density
test_crowd_flow
test_agent_avoidance
test_obstacle_avoidance
test_deadlock_detection
test_crowd_lod
test_crowd_determinism
```

---

# 205. FORMATION TESTS

Mínimo:

```text
test_line_formation
test_column_formation
test_wedge_formation
test_circle_formation
test_formation_slots
test_formation_recovery
```

---

# 206. SOCIAL TESTS

Mínimo:

```text
test_relationship
test_affinity
test_trust
test_faction
test_social_memory
test_social_event
```

---

# 207. COMMUNICATION TESTS

Mínimo:

```text
test_speech
test_signal
test_radio
test_gesture
test_alert
test_message_priority
test_message_range
```

---

# 208. GROUP TESTS

Mínimo:

```text
test_group_creation
test_group_leader
test_group_members
test_group_roles
test_shared_target
test_shared_memory
test_group_determinism
```

---

# 209. COMBAT TESTS

Mínimo:

```text
test_combat_state
test_combat_target
test_attack_selection
test_melee_range
test_ranged_range
test_cover
test_flee
test_combat_failure
test_combat_determinism
```

---

# 210. INTERACTION TESTS

Mínimo:

```text
test_interactable
test_interaction_conditions
test_interaction_reservation
test_interaction_busy
test_interaction_success
test_interaction_failure
test_interaction_determinism
```

---

# 211. NEED TESTS

Mínimo:

```text
test_hunger
test_thirst
test_energy
test_safety
test_social_need
test_need_decay
test_need_priority
```

---

# 212. SCHEDULE TESTS

Mínimo:

```text
test_schedule_definition
test_schedule_entry
test_schedule_transition
test_schedule_conflict
test_daily_routine
test_schedule_interrupt
test_schedule_determinism
```

---

# 213. WORLD REACTION TESTS

Mínimo:

```text
test_weather_reaction
test_time_reaction
test_danger_reaction
test_fire_reaction
test_death_reaction
test_crowd_reaction
test_world_change_reaction
```

---

# 214. EVENT TESTS

Mínimo:

```text
test_event_bus
test_event_order
test_event_priority
test_event_filter
test_event_replay
test_event_determinism
```

---

# 215. SAVE/LOAD TESTS

Mínimo:

```text
test_ai_save
test_ai_load
test_save_hash
test_save_version
test_save_migration
test_save_roundtrip
test_save_determinism
```

---

# 216. REPLAY TESTS

Mínimo:

```text
test_replay_record
test_replay_playback
test_replay_hash
test_replay_divergence
test_replay_determinism
```

---

# 217. AI LOD TESTS

Mínimo:

```text
test_lod0
test_lod1
test_lod2
test_lod3
test_lod4
test_lod_transition
test_lod_state_preservation
```

---

# 218. BACKGROUND SIMULATION TESTS

Mínimo:

```text
test_background_agent
test_abstract_agent
test_population_simulation
test_population_transition
test_background_determinism
```

---

# 219. PERFORMANCE TESTS

Mínimo:

```text
test_agent_budget
test_perception_budget
test_pathfinding_budget
test_behavior_budget
test_combat_budget
test_crowd_budget
test_memory_budget
test_ai_lod_budget
```

---

# 220. SPATIAL INDEX TESTS

Mínimo:

```text
test_spatial_insert
test_spatial_remove
test_spatial_update
test_spatial_query
test_spatial_consistency
test_spatial_determinism
```

---

# 221. FAILURE TESTS

Mínimo:

```text
test_invalid_agent
test_spawn_failure
test_invalid_perception
test_invalid_memory
test_invalid_target
test_invalid_fsm
test_invalid_behavior_tree
test_invalid_utility
test_invalid_goap
test_invalid_action
test_path_failure
test_navigation_failure
test_crowd_deadlock
test_invalid_formation
test_invalid_relationship
test_invalid_message
test_invalid_group
test_combat_failure
test_interaction_failure
test_schedule_failure
test_save_failure
test_replay_failure
test_plugin_failure
```

---

# 222. DETERMINISM TESTS

Deberá comprobarse:

```text
agent_spawn
perception
memory
targeting
fsm
behavior_tree
utility_ai
goap
actions
movement
pathfinding
crowd
formation
social
communication
group_behavior
combat
interaction
needs
schedule
events
background_simulation
save_load
replay
lod_transition
world_reaction
```

---

# 223. GOLDEN AI SCENARIOS

Deberán existir como mínimo:

```text
GOLDEN_IDLE_NPC
GOLDEN_DAILY_ROUTINE
GOLDEN_PATROL
GOLDEN_FLEE
GOLDEN_COMBAT
GOLDEN_SQUAD
GOLDEN_CROWD
GOLDEN_ANIMAL
GOLDEN_CITY_POPULATION
GOLDEN_WORLD_REACTION
GOLDEN_BACKGROUND_SIMULATION
GOLDEN_SAVE_LOAD
GOLDEN_REPLAY
```

---

# 224. GOLDEN VALIDATION

Cada escenario deberá comprobar:

```text
INITIAL_STATE
EVENT_SEQUENCE
DECISIONS
ACTIONS
TRANSFORMS
FINAL_STATE
WORLD_HASH
SIMULATION_HASH
```

---

# 225. END-TO-END TEST

Deberá existir un escenario completo:

```text
WORLD
↓
NPC SPAWN
↓
NAVIGATION
↓
PERCEPTION
↓
MEMORY
↓
DAILY SCHEDULE
↓
WORLD EVENT
↓
DECISION
↓
MOVEMENT
↓
INTERACTION
↓
COMBAT
↓
GROUP RESPONSE
↓
CROWD RESPONSE
↓
LOD TRANSITION
↓
SAVE
↓
LOAD
↓
REPLAY
↓
FINAL HASH VALIDATION
```

---

# 226. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
8 AGENT
11 PERCEPTION
7 MEMORY
6 TARGETING
6 FSM
9 BEHAVIOR_TREE
7 UTILITY
8 GOAP
7 ACTION
9 MOVEMENT
10 PATHFINDING
8 CROWD
6 FORMATION
6 SOCIAL
7 COMMUNICATION
7 GROUP
9 COMBAT
7 INTERACTION
7 NEEDS
7 SCHEDULE
7 WORLD_REACTION
6 EVENTS
7 SAVE_LOAD
5 REPLAY
7 AI_LOD
5 BACKGROUND
8 PERFORMANCE
6 SPATIAL_INDEX
23 FAILURE
26 DETERMINISM
13 GOLDEN
1 END_TO_END
```

**Total mínimo: 264 tests.**

---

# 227. CROSS-PHASE INTEGRATION

Deberá integrarse con:

```text
UAF-81.50
UAF-81.51
UAF-81.52
UAF-81.53
UAF-81.54
UAF-81.55
UAF-81.56
```

---

# 228. WORLD INTEGRATION

La IA deberá consumir:

```text
WorldSnapshot
WorldQuery
NavigationDefinition
WorldCollisionProfile
WorldPartitionProfile
```

sin duplicar ownership.

---

# 229. CHARACTER INTEGRATION

Los agentes humanoides deberán poder utilizar:

```text
skeletal_definition
animation_graph
locomotion
IK
facial_hooks
```

provenientes de fases anteriores.

---

# 230. ANIMATION INTEGRATION

Las acciones deberán poder solicitar:

```text
idle
walk
run
attack
hit
flee
interact
talk
sit
sleep
work
```

sin contener directamente los assets de animación.

---

# 231. MATERIAL INTEGRATION

La IA no deberá asumir materiales concretos.

---

# 232. ASSET INTEGRATION

Weapons, props, vehicles y objetos interactuables deberán utilizar referencias de Asset Library.

---

# 233. DEPENDENCY GRAPH

La IA deberá registrar dependencias:

```text
AGENT
 ↓
PROFILE
 ↓
BEHAVIOR
 ↓
ASSETS
 ↓
WORLD
 ↓
NAVIGATION
```

---

# 234. INVALIDATION

Mínimo:

```text
CHANGE_AGENT_PROFILE
→ INVALIDATE AGENT BEHAVIOR

CHANGE_NAVIGATION
→ INVALIDATE PATHS

CHANGE_WORLD
→ INVALIDATE WORLD QUERIES

CHANGE_BEHAVIOR
→ INVALIDATE DECISION STATE

CHANGE_SCHEDULE
→ INVALIDATE ROUTINE

CHANGE_WEAPON
→ INVALIDATE COMBAT ACTIONS
```

---

# 235. NO HIDDEN AI STATE

Todo estado necesario para continuar una simulación deberá estar serializado o reconstruible.

---

# 236. SIMULATION SNAPSHOT

Deberá existir:

```text
SimulationSnapshot
```

con:

```text
simulation_hash
tick
world_hash
agent_states
group_states
event_queue
global_state
```

---

# 237. SIMULATION HASH

Deberá derivarse de estado relevante, no de timestamps accidentales ni orden de memoria.

---

# 238. MULTIPLAYER HOOK

La arquitectura deberá permitir separar:

```text
AUTHORITATIVE_SIMULATION
CLIENT_PRESENTATION
PREDICTION
RECONCILIATION
```

sin imponer un modelo de red concreto.

---

# 239. SERVER SIMULATION

El backend deberá poder ejecutar IA sin renderer.

---

# 240. CLIENT SIMULATION

El cliente podrá ejecutar únicamente los niveles necesarios de simulación.

---

# 241. NETWORK DETERMINISM

Cuando el proyecto lo requiera deberá existir soporte para comparar:

```text
server_hash
client_hash
tick
```

---

# 242. SECURITY BOUNDARY

La IA recibida desde datos externos deberá validarse antes de ejecución.

---

# 243. SCRIPT SANDBOX

Los scripts AI deberán poder ejecutarse dentro de un entorno controlado cuando el backend lo requiera.

---

# 244. SCRIPT TIMEOUT

Un comportamiento/script que exceda presupuesto deberá poder ser interrumpido.

---

# 245. SCRIPT FAILURE

No deberá provocar corrupción del estado global.

---

# 246. ACCEPTANCE CRITERIA

UAF-81.57 estará completa únicamente cuando:

```text
AI AGENT MODEL IMPLEMENTED
AGENT LIFECYCLE IMPLEMENTED
PERCEPTION IMPLEMENTED
VISION IMPLEMENTED
HEARING IMPLEMENTED
SMELL HOOK IMPLEMENTED
MEMORY IMPLEMENTED
TARGETING IMPLEMENTED
FSM IMPLEMENTED
BEHAVIOR TREE IMPLEMENTED
UTILITY AI IMPLEMENTED
GOAP IMPLEMENTED
ACTION SYSTEM IMPLEMENTED
MOVEMENT IMPLEMENTED
PATHFINDING IMPLEMENTED
DYNAMIC OBSTACLES IMPLEMENTED
AVOIDANCE IMPLEMENTED
CROWD SYSTEM IMPLEMENTED
FORMATION SYSTEM IMPLEMENTED
SOCIAL SYSTEM IMPLEMENTED
FACTION SYSTEM IMPLEMENTED
COMMUNICATION IMPLEMENTED
GROUP BEHAVIOR IMPLEMENTED
SQUAD SYSTEM IMPLEMENTED
COMBAT IMPLEMENTED
COVER SYSTEM IMPLEMENTED
FLEE SYSTEM IMPLEMENTED
INTERACTION IMPLEMENTED
NEEDS IMPLEMENTED
SURVIVAL IMPLEMENTED
SCHEDULE IMPLEMENTED
DAILY ROUTINE IMPLEMENTED
WORLD REACTION IMPLEMENTED
EVENT BUS IMPLEMENTED
QUEST HOOKS IMPLEMENTED
SAVE/LOAD IMPLEMENTED
SAVE MIGRATION IMPLEMENTED
REPLAY IMPLEMENTED
DIVERGENCE DETECTION IMPLEMENTED
AI LOD IMPLEMENTED
BACKGROUND SIMULATION IMPLEMENTED
POPULATION SIMULATION IMPLEMENTED
PERFORMANCE BUDGETS IMPLEMENTED
AI PROFILING IMPLEMENTED
AI DIAGNOSTICS IMPLEMENTED
DEBUG TRACE IMPLEMENTED
AI QUERY SYSTEM IMPLEMENTED
SPATIAL INDEX IMPLEMENTED
VEHICLE AI HOOK IMPLEMENTED
ANIMAL BEHAVIOR IMPLEMENTED
TERRITORY SYSTEM IMPLEMENTED
CUSTOM AI PLUGINS IMPLEMENTED
FAILURE CONTAINMENT IMPLEMENTED
VALIDATION PIPELINE IMPLEMENTED
MINIMUM 264 TESTS IMPLEMENTED
FAILURE TESTS IMPLEMENTED
DETERMINISM TESTS IMPLEMENTED
GOLDEN SCENARIOS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
MULTIPLAYER HOOKS IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 247. NEXT PHASE

```text
UAF-81.58 — UNIVERSAL GAMEPLAY, QUEST, MISSION, DIALOGUE, INVENTORY, ECONOMY & INTERACTION SYSTEM
```

La siguiente fase deberá cerrar la capa de gameplay que conecta:

```text
WORLD
+
CHARACTER
+
NPC
+
AI
+
ITEMS
+
INVENTORY
+
QUESTS
+
MISSIONS
+
DIALOGUE
+
FACTIONS
+
ECONOMY
+
REWARDS
+
PROGRESSION
+
SAVE/LOAD
+
EVENTS
```
