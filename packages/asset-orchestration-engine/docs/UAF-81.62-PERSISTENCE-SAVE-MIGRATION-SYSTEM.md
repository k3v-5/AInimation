# UAF-81.62 — UNIVERSAL SAVE, LOAD, CHECKPOINT, PROFILE, SETTINGS, CONFIGURATION, VERSIONING, MIGRATION & DATA PERSISTENCE SYSTEM

## UAF-81.62-ARCH

### ARQUITECTURA NORMATIVA DEL SISTEMA UNIVERSAL DE GUARDADO, CARGA, PUNTOS DE CONTROL, PERFILES, AJUSTES, CONFIGURACIÓN, VERSIONADO, MIGRACIÓN Y PERSISTENCIA DE DATOS

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.62 — Universal Save, Load, Checkpoint, Profile, Settings, Configuration, Versioning, Migration & Data Persistence System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.61  
**Next Phase:** UAF-81.63  

---

# 1. PURPOSE

UAF-81.62 define el sistema universal de persistencia de datos del producto.

La fase deberá cubrir:

```text
SAVE
LOAD
AUTOSAVE
CHECKPOINT
SAVE SLOTS
PLAYER PROFILE
USER PROFILE
SETTINGS
CONFIGURATION
INPUT PROFILE
ACCESSIBILITY PROFILE
GRAPHICS PROFILE
AUDIO PROFILE
LANGUAGE PROFILE
LOCAL SAVE
REMOTE SAVE
CLOUD SAVE
BACKUP
RESTORE
INTEGRITY
CHECKSUM
CORRUPTION DETECTION
SCHEMA
VERSIONING
MIGRATION
ROLLBACK
TRANSACTION
ATOMIC WRITE
CRASH RECOVERY
PARTIAL SAVE RECOVERY
CONFLICT RESOLUTION
DATA VALIDATION
SECURITY
ENCRYPTION INTERFACE
COMPRESSION INTERFACE
MULTIPLAYER PERSISTENCE
TESTING
```

---

# 2. PRIMARY OBJECTIVE

Toda persistencia deberá seguir:

```text
RUNTIME STATE
 ↓
SNAPSHOT
 ↓
VALIDATION
 ↓
SERIALIZATION
 ↓
TRANSFORMATION
 ↓
INTEGRITY
 ↓
ATOMIC STORAGE
 ↓
COMMIT
 ↓
INDEX UPDATE
 ↓
VERIFICATION
```

La carga deberá seguir:

```text
STORAGE
 ↓
DISCOVERY
 ↓
READ
 ↓
INTEGRITY CHECK
 ↓
VERSION CHECK
 ↓
MIGRATION
 ↓
VALIDATION
 ↓
DESERIALIZATION
 ↓
DEPENDENCY RESOLUTION
 ↓
RUNTIME RESTORE
 ↓
POST-LOAD VALIDATION
```

---

# 3. CORE PRINCIPLES

El sistema deberá ser:

```text
ATOMIC
CONSISTENT
VALIDATED
VERSIONED
MIGRATABLE
RECOVERABLE
DETERMINISTIC
CRASH SAFE
FAILURE AWARE
TESTABLE
```

---

# 4. DATA OWNERSHIP

Todo dato persistible deberá tener:

```text
owner
schema
version
lifetime
scope
permissions
```

---

# 5. PERSISTENCE SCOPES

Mínimo:

```text
GLOBAL
USER
PROFILE
SESSION
SAVE_SLOT
CHECKPOINT
WORLD
PLAYER
ACCOUNT
NETWORK
```

---

# 6. DATA CLASSES

Deberán diferenciarse:

```text
EPHEMERAL
PERSISTENT
DERIVED
CACHE
AUTHORITATIVE
USER_CONFIG
SYSTEM_CONFIG
```

Los datos derivados no deberán almacenarse como fuente primaria salvo justificación explícita.

---

# 7. SAVE SYSTEM

Deberá existir:

```text
SaveService
```

con:

```text
create_save
write_save
commit_save
load_save
delete_save
validate_save
list_saves
```

---

# 8. SAVE REQUEST

Cada operación de guardado deberá generar:

```text
SaveRequest
```

con:

```text
request_id
scope
slot_id
source
priority
timestamp
schema_version
requested_by
```

---

# 9. SAVE STATES

Mínimo:

```text
IDLE
QUEUED
SNAPSHOTTING
SERIALIZING
VALIDATING
WRITING
COMMITTING
VERIFYING
COMPLETED
FAILED
CANCELLED
RECOVERING
```

---

# 10. SAVE SLOT

Deberá existir:

```text
SaveSlot
```

con:

```text
slot_id
profile_id
save_id
created_at
updated_at
playtime
location
version
schema_version
status
integrity_status
thumbnail
metadata
```

---

# 11. SLOT STATES

Mínimo:

```text
EMPTY
VALID
INVALID
CORRUPTED
INCOMPATIBLE
MIGRATION_REQUIRED
LOCKED
BUSY
```

---

# 12. SLOT ID

Los identificadores de slot deberán ser estables y no depender del nombre mostrado al usuario.

---

# 13. SAVE METADATA

Deberá existir metadata suficiente para mostrar un save sin cargar completamente el estado:

```text
display_name
timestamp
playtime
progress
location
version
thumbnail
validity
```

---

# 14. SAVE THUMBNAIL

La miniatura deberá ser opcional y deberá existir fallback cuando no pueda generarse.

---

# 15. AUTOSAVE

Deberá existir:

```text
AutosaveService
```

---

# 16. AUTOSAVE TRIGGERS

Podrá dispararse por:

```text
TIME
LEVEL_CHANGE
AREA_CHANGE
QUEST_MILESTONE
CHECKPOINT
MISSION_COMPLETE
PLAYER_DEATH
MANUAL_EVENT
SYSTEM_EVENT
```

---

# 17. AUTOSAVE POLICY

Deberá ser configurable:

```text
enabled
interval
minimum_interval
allowed_states
blocked_states
slot_policy
```

---

# 18. AUTOSAVE THROTTLING

Nunca deberá producirse una cascada de saves por eventos simultáneos.

---

# 19. AUTOSAVE COALESCING

Múltiples solicitudes próximas deberán poder combinarse en una sola operación cuando sea seguro.

---

# 20. AUTOSAVE FAILURE

Un autosave fallido no deberá destruir el último save válido.

---

# 21. CHECKPOINT SYSTEM

Deberá existir:

```text
CheckpointService
```

---

# 22. CHECKPOINT

Un checkpoint deberá representar un estado recuperable del runtime.

---

# 23. CHECKPOINT TYPES

Mínimo:

```text
WORLD
MISSION
QUEST
COMBAT
AREA
SCRIPT
MANUAL
```

---

# 24. CHECKPOINT LIFETIME

Deberá poder configurarse:

```text
SESSION_ONLY
UNTIL_NEXT_CHECKPOINT
UNTIL_SAVE
PERSISTENT
```

---

# 25. CHECKPOINT INVALIDATION

Un checkpoint podrá invalidarse por:

```text
VERSION
WORLD_CHANGE
PROFILE_CHANGE
SCHEMA_CHANGE
EXPLICIT_INVALIDATION
```

---

# 26. PLAYER PROFILE

Deberá existir:

```text
PlayerProfile
```

---

# 27. PLAYER PROFILE DATA

Podrá contener:

```text
progression
unlocks
inventory
statistics
achievements
preferences
cosmetics
control_profile
accessibility_profile
```

---

# 28. USER PROFILE

Deberá diferenciarse del estado de una partida.

```text
UserProfile
```

podrá contener:

```text
language
input_bindings
accessibility
audio_preferences
graphics_preferences
UI_preferences
```

---

# 29. PROFILE OWNERSHIP

Un save no deberá asumir que existe un único perfil global.

---

# 30. PROFILE SWITCH

El cambio de perfil deberá:

```text
flush_pending_data
validate_current_profile
commit_required_changes
load_target_profile
reinitialize_user_preferences
```

---

# 31. PROFILE SWITCH FAILURE

Si falla el cambio:

```text
restore_previous_profile
```

deberá ser posible.

---

# 32. SETTINGS

Deberá existir:

```text
SettingsStore
```

---

# 33. SETTINGS CATEGORIES

Mínimo:

```text
GAMEPLAY
GRAPHICS
AUDIO
CONTROLS
ACCESSIBILITY
LANGUAGE
DISPLAY
NETWORK
UI
PRIVACY
```

---

# 34. SETTINGS TYPES

Deberán soportarse:

```text
BOOL
INT
FLOAT
STRING
ENUM
COLOR
KEY_BINDING
VECTOR
STRUCT
```

---

# 35. SETTING VALIDATION

Cada setting deberá declarar:

```text
type
default
minimum
maximum
allowed_values
validator
```

cuando corresponda.

---

# 36. SETTING TRANSACTION

Los cambios deberán poder mantenerse en estado:

```text
PENDING
APPLIED
CONFIRMED
REVERTED
```

---

# 37. SAFE SETTINGS

Un cambio peligroso deberá contar con:

```text
preview
timeout
automatic_revert
confirmation
```

cuando corresponda.

---

# 38. GRAPHICS SETTINGS

Deberán poder persistirse:

```text
resolution
refresh_rate
display_mode
quality
upscaling
v_sync
hdr
brightness
```

---

# 39. AUDIO SETTINGS

Mínimo:

```text
master
music
sfx
dialogue
voice
UI
dynamic_range
output_device
```

---

# 40. LANGUAGE SETTINGS

Deberán soportarse:

```text
interface_language
subtitle_language
audio_language
```

cuando el producto lo permita.

---

# 41. ACCESSIBILITY PROFILE

Deberá persistirse:

```text
text_scale
high_contrast
colorblind_mode
reduced_motion
screen_reader
input_assistance
subtitle_preferences
```

---

# 42. INPUT PROFILE

Deberá persistirse:

```text
device_type
bindings
sensitivity
dead_zones
invert_axes
vibration
presets
```

---

# 43. DEAD ZONE

Los valores deberán validarse contra límites seguros.

---

# 44. CONFIGURATION SYSTEM

Deberá existir separación entre:

```text
DEFAULT_CONFIG
PLATFORM_CONFIG
USER_CONFIG
PROFILE_CONFIG
SESSION_CONFIG
```

---

# 45. CONFIGURATION PRECEDENCE

Orden mínimo:

```text
DEFAULT
 ↓
PLATFORM
 ↓
USER
 ↓
PROFILE
 ↓
SESSION
```

La prioridad deberá estar definida explícitamente.

---

# 46. CONFIGURATION IMMUTABILITY

Las configuraciones de sistema que no puedan ser modificadas por el usuario deberán marcarse como read-only.

---

# 47. SERIALIZATION

Deberá existir una abstracción:

```text
Serializer
```

---

# 48. SERIALIZATION REQUIREMENTS

Deberá soportar:

```text
primitive
enum
array
map
struct
optional
reference
versioned_object
```

---

# 49. NULL HANDLING

Deberá existir comportamiento explícito para:

```text
null
missing
default
invalid
```

---

# 50. REFERENCE HANDLING

Las referencias persistentes deberán utilizar identificadores estables.

No deberán depender de punteros de memoria.

---

# 51. REFERENCE RESOLUTION

Durante carga:

```text
ID
 ↓
REGISTRY
 ↓
OBJECT
```

---

# 52. MISSING REFERENCES

Deberán poder resolverse mediante:

```text
NULL
FALLBACK
PLACEHOLDER
ERROR
```

según contrato.

---

# 53. SERIALIZATION FAILURE

Un objeto que no pueda serializarse deberá generar un error estructurado y no un archivo parcialmente válido marcado como completo.

---

# 54. DESERIALIZATION FAILURE

Un dato corrupto deberá poder aislarse al máximo nivel posible.

---

# 55. SCHEMA

Todo formato persistente deberá tener:

```text
schema_id
schema_version
```

---

# 56. VERSIONING

Deberá diferenciarse:

```text
PRODUCT_VERSION
SAVE_FORMAT_VERSION
SCHEMA_VERSION
CONTENT_VERSION
```

---

# 57. COMPATIBILITY

Cada versión deberá declarar:

```text
compatible
requires_migration
unsupported
```

---

# 58. MIGRATION

Deberá existir:

```text
MigrationService
```

---

# 59. MIGRATION PATH

Las migraciones deberán definir:

```text
from_version
to_version
migration_id
preconditions
transform
validation
rollback_policy
```

---

# 60. MIGRATION CHAIN

Podrá ejecutarse:

```text
V1
 ↓
V2
 ↓
V3
 ↓
V4
```

---

# 61. DIRECT MIGRATION

Cuando sea necesario podrá existir:

```text
V1 -> V4
```

pero deberá ser explícitamente validada.

---

# 62. MIGRATION ATOMICITY

Una migración fallida no deberá destruir el original.

---

# 63. MIGRATION BACKUP

Antes de una migración destructiva deberá poder conservarse una copia recuperable.

---

# 64. MIGRATION IDEMPOTENCY

Una migración ya aplicada no deberá aplicarse dos veces accidentalmente.

---

# 65. MIGRATION LOG

Deberá registrarse:

```text
migration_id
source_version
target_version
timestamp
result
error
```

---

# 66. ROLLBACK

Deberá existir:

```text
RollbackService
```

o mecanismo equivalente.

---

# 67. ROLLBACK CONDITIONS

Mínimo:

```text
migration_failure
validation_failure
commit_failure
post_load_failure
integrity_failure
```

---

# 68. TRANSACTION

Toda operación crítica deberá poder agrupar:

```text
prepare
validate
write
commit
```

---

# 69. ATOMIC SAVE

El save final no deberá exponerse como válido hasta que la escritura haya completado y pasado verificación.

---

# 70. TEMPORARY FILE

Deberá utilizarse almacenamiento temporal o mecanismo equivalente:

```text
SAVE.tmp
```

seguido de commit.

---

# 71. COMMIT

El commit deberá ser atómico según las capacidades de la plataforma.

---

# 72. JOURNAL

Cuando la plataforma o criticidad lo requiera deberá existir:

```text
SaveJournal
```

---

# 73. JOURNAL STATES

Mínimo:

```text
PREPARED
WRITING
COMMITTED
ROLLED_BACK
ABANDONED
```

---

# 74. CRASH RECOVERY

Después de un crash el sistema deberá detectar operaciones incompletas.

---

# 75. CRASH RECOVERY POLICY

Mínimo:

```text
COMPLETE_COMMIT
ROLLBACK
USE_LAST_VALID
QUARANTINE_CORRUPT
```

---

# 76. LAST VALID SAVE

Siempre que sea posible deberá conservarse al menos una copia válida anterior.

---

# 77. SAVE ROTATION

Deberá poder existir:

```text
CURRENT
PREVIOUS
BACKUP
```

---

# 78. BACKUP

Deberá existir:

```text
BackupService
```

---

# 79. BACKUP POLICY

Deberá configurar:

```text
max_backups
retention
rotation
compression
verification
```

---

# 80. RESTORE

Deberá poder restaurarse desde:

```text
CURRENT
PREVIOUS
BACKUP
CLOUD
RECOVERY
```

---

# 81. RESTORE VALIDATION

Nunca deberá reemplazarse el estado activo con un backup no validado.

---

# 82. CORRUPTION DETECTION

Deberá existir:

```text
IntegrityService
```

---

# 83. INTEGRITY

Deberá verificarse:

```text
size
structure
checksum
schema
required_fields
references
```

---

# 84. CHECKSUM

El formato deberá permitir checksum o mecanismo equivalente.

---

# 85. CHECKSUM SCOPE

Deberá definirse claramente qué cubre:

```text
payload
metadata
header
complete_file
```

---

# 86. CORRUPTION STATES

Mínimo:

```text
VALID
SUSPECT
CORRUPTED
UNREADABLE
UNKNOWN
```

---

# 87. CORRUPTION QUARANTINE

Un archivo corrupto no deberá sobrescribirse automáticamente.

---

# 88. CORRUPTION REPORT

Deberá conservarse información suficiente para diagnóstico:

```text
save_id
slot_id
version
checksum_expected
checksum_actual
failure_stage
error_code
```

---

# 89. COMPRESSION

Deberá existir una interfaz:

```text
CompressionProvider
```

sin acoplar el sistema a un algoritmo específico.

---

# 90. ENCRYPTION

Deberá existir una interfaz:

```text
EncryptionProvider
```

cuando el producto requiera protección de datos.

---

# 91. KEY MANAGEMENT

Las claves no deberán almacenarse como datos ordinarios dentro del save.

---

# 92. SECURITY VALIDATION

Nunca deberá confiarse en:

```text
user-controlled metadata
slot names
timestamps
progress values
IDs
```

sin validación.

---

# 93. PATH SAFETY

Los nombres externos no deberán permitir traversal ni acceso arbitrario al filesystem.

---

# 94. FILE SIZE LIMIT

Deberá existir un límite configurable para evitar archivos de tamaño inesperado.

---

# 95. OBJECT COUNT LIMIT

Deberá existir protección contra datos que intenten crear cantidades excesivas de objetos al cargar.

---

# 96. RECURSION LIMIT

La deserialización deberá tener límites contra estructuras recursivas malformadas.

---

# 97. COLLECTION LIMITS

Arrays, maps y listas persistentes deberán validar sus tamaños.

---

# 98. UNKNOWN FIELDS

El sistema deberá definir si los campos desconocidos:

```text
IGNORE
PRESERVE
REJECT
```

---

# 99. MISSING FIELDS

Los campos faltantes deberán resolverse mediante:

```text
DEFAULT
MIGRATION
NULL
REJECT
```

---

# 100. DEFAULT VALUES

Los defaults deberán estar versionados cuando formen parte del contrato persistente.

---

# 101. DATA VALIDATION

Deberá existir:

```text
DataValidator
```

---

# 102. VALIDATION LEVELS

Mínimo:

```text
STRUCTURAL
SEMANTIC
REFERENCE
RANGE
SECURITY
CROSS_SYSTEM
```

---

# 103. VALIDATION RESULT

Deberá devolver:

```text
valid
warnings
errors
fatal_errors
```

---

# 104. CROSS-SYSTEM VALIDATION

Un save deberá poder verificar dependencias entre:

```text
player
world
quests
inventory
dialogue
settings
assets
progression
network
```

---

# 105. ORPHAN DATA

Deberán detectarse objetos persistidos sin owner válido.

---

# 106. DUPLICATE ID

Deberán rechazarse IDs persistentes duplicados cuando sean únicos por contrato.

---

# 107. INVALID ENUM

Valores enum desconocidos deberán seguir política explícita:

```text
DEFAULT
MIGRATE
REJECT
```

---

# 108. RANGE VALIDATION

Valores fuera de rango deberán:

```text
CLAMP
DEFAULT
REJECT
```

según el campo.

---

# 109. WORLD STATE

Deberá poder persistirse:

```text
world_id
world_version
seed
persistent_objects
destroyed_objects
spawn_state
world_flags
```

---

# 110. PLAYER STATE

Mínimo:

```text
position
rotation
health
resources
inventory
equipment
progression
status
```

---

# 111. QUEST STATE

Deberá persistirse:

```text
quest_id
state
objectives
progress
timestamps
rewards
```

---

# 112. DIALOGUE STATE

Cuando corresponda:

```text
dialogue_graph
node
choice_state
flags
history
```

---

# 113. INVENTORY STATE

Deberá incluir identificadores estables y cantidades validadas.

---

# 114. UNIQUE ITEMS

Los objetos únicos deberán poder conservar su identidad.

---

# 115. STACKED ITEMS

Las cantidades deberán estar limitadas y validadas.

---

# 116. EQUIPMENT

Las referencias de equipamiento deberán validarse contra el inventario y las reglas del producto.

---

# 117. PROGRESSION

No deberá permitirse cargar progreso incompatible con las reglas actuales sin migración o validación explícita.

---

# 118. ACHIEVEMENTS

El estado persistente de achievements deberá tener ownership definido y protección contra duplicación.

---

# 119. STATISTICS

Las estadísticas persistentes deberán diferenciarse de métricas temporales.

---

# 120. MULTIPLAYER

Deberá distinguirse:

```text
LOCAL_AUTHORITATIVE
SERVER_AUTHORITATIVE
CLIENT_CACHE
SHARED_PROFILE
```

---

# 121. MULTIPLAYER SAVE

El cliente no deberá sobrescribir datos autoritativos del servidor.

---

# 122. NETWORK INTERRUPTION

Una interrupción durante persistencia remota deberá dejar el estado local coherente.

---

# 123. CLOUD SAVE

Deberá existir una abstracción:

```text
CloudSaveProvider
```

---

# 124. CLOUD STATES

Mínimo:

```text
UNAVAILABLE
CONNECTING
AVAILABLE
UPLOADING
DOWNLOADING
CONFLICT
FAILED
```

---

# 125. CLOUD SYNC

Deberá existir:

```text
LOCAL_ONLY
REMOTE_ONLY
MATCH
LOCAL_NEWER
REMOTE_NEWER
CONFLICT
```

---

# 126. CONFLICT RESOLUTION

Nunca deberá sobrescribirse automáticamente un save conflictivo sin una política explícita.

---

# 127. CONFLICT POLICY

Podrá utilizar:

```text
LOCAL_WINS
REMOTE_WINS
NEWEST
MANUAL
MERGE
```

---

# 128. MERGE

Sólo deberá permitirse cuando el esquema defina reglas seguras para combinar campos.

---

# 129. CONFLICT UI

UAF-81.61 deberá poder representar:

```text
local_save
remote_save
timestamps
progress
version
actions
```

---

# 130. SAVE LOCK

Deberá existir protección contra dos operaciones incompatibles simultáneas sobre el mismo slot.

---

# 131. LOCK STATES

Mínimo:

```text
UNLOCKED
LOCKED
EXPIRED
STALE
```

---

# 132. STALE LOCK

Un lock abandonado deberá poder recuperarse de forma segura.

---

# 133. CONCURRENT SAVE

Dos saves sobre el mismo slot deberán resolverse mediante:

```text
QUEUE
REJECT
MERGE
REPLACE
```

según política.

---

# 134. DELETE SAVE

Eliminar un save deberá ser operación explícita.

---

# 135. DELETE PROTECTION

El sistema deberá poder requerir confirmación y/o preservar backup antes de eliminación.

---

# 136. SLOT REUSE

Un slot eliminado deberá poder reutilizarse sin conservar referencias inválidas.

---

# 137. SAVE INDEX

Deberá existir:

```text
SaveIndex
```

para descubrir saves disponibles sin abrir todos los archivos.

---

# 138. INDEX RECOVERY

Si el índice se corrompe deberá poder reconstruirse a partir de los datos existentes.

---

# 139. INDEX CONSISTENCY

El índice no deberá declarar válido un save inexistente.

---

# 140. THUMBNAIL FAILURE

Un fallo de thumbnail no deberá invalidar el save.

---

# 141. METADATA FAILURE

Un fallo de metadata no crítica deberá poder recuperarse si el payload sigue siendo válido.

---

# 142. SAVE SIZE OPTIMIZATION

Deberá existir soporte para evitar almacenar datos derivados innecesarios.

---

# 143. DELTA SAVE

Podrá existir:

```text
FULL_SAVE
DELTA_SAVE
```

siempre que exista mecanismo de reconstrucción y validación.

---

# 144. DELTA CHAIN

Una cadena de deltas deberá tener límites y mecanismo de compactación.

---

# 145. SAVE COMPACTION

Deberá poder transformarse:

```text
FULL + DELTA + DELTA + ...
```

en un nuevo full save.

---

# 146. SAVE GC

Los datos temporales, backups expirados y deltas obsoletos deberán poder limpiarse sin eliminar datos válidos.

---

# 147. STORAGE FULL

Ante falta de espacio:

```text
save
 ↓
FAIL
 ↓
PRESERVE_PREVIOUS
 ↓
REPORT_NO_SPACE
```

Nunca:

```text
overwrite_previous
```

antes de confirmar capacidad suficiente.

---

# 148. PERMISSION FAILURE

Deberá diferenciarse de:

```text
NO_SPACE
CORRUPTION
IO_ERROR
LOCK
```

---

# 149. IO FAILURE

Un fallo de I/O durante commit deberá activar recuperación.

---

# 150. POWER LOSS

Deberá contemplarse pérdida de energía durante:

```text
snapshot
serialization
write
commit
index update
```

---

# 151. CRASH TEST MATRIX

Deberán probarse crashes en cada fase:

```text
BEFORE_WRITE
MID_WRITE
AFTER_WRITE_BEFORE_COMMIT
MID_COMMIT
AFTER_COMMIT_BEFORE_INDEX
AFTER_INDEX
```

---

# 152. SAVE RETRY

Los retries deberán tener:

```text
max_attempts
backoff
retryable_errors
non_retryable_errors
```

---

# 153. IDEMPOTENT RETRY

Repetir un commit no deberá generar duplicados ni corrupción.

---

# 154. LOAD SYSTEM

Deberá existir:

```text
LoadService
```

---

# 155. LOAD STATES

Mínimo:

```text
DISCOVERING
READING
VERIFYING
MIGRATING
DESERIALIZING
RESOLVING
VALIDATING
RESTORING
POST_VALIDATING
COMPLETED
FAILED
```

---

# 156. LOAD PREVIEW

Deberá poder inspeccionarse metadata sin restaurar el mundo.

---

# 157. LOAD VALIDATION BEFORE RUNTIME

Los datos deberán validarse antes de mutar el estado activo siempre que sea posible.

---

# 158. STAGED LOAD

Deberá existir un estado intermedio:

```text
PARSED_STATE
```

antes de:

```text
ACTIVE_RUNTIME
```

---

# 159. LOAD FAILURE ISOLATION

Un save inválido no deberá destruir la sesión actualmente cargada si el usuario no ha confirmado el cambio.

---

# 160. LOAD ROLLBACK

Si la restauración falla después de mutar parcialmente el runtime:

```text
rollback
```

o mecanismo equivalente deberá restaurar un estado seguro.

---

# 161. SAFE LOAD

Deberá existir una estrategia:

```text
LOAD_TO_STAGING
VALIDATE
COMMIT_TO_RUNTIME
```

---

# 162. POST-LOAD VALIDATION

Después de cargar deberá comprobarse:

```text
player
world
quests
inventory
references
progression
settings
```

---

# 163. LOAD COMPLETION

Un load sólo podrá marcarse `COMPLETED` cuando todas las validaciones críticas hayan terminado.

---

# 164. SAVE/LOAD TELEMETRY

Deberán medirse:

```text
duration
size
compression_ratio
serialization_time
write_time
read_time
migration_time
validation_time
failure_stage
```

---

# 165. PRIVACY

Los datos sensibles deberán tener clasificación:

```text
PUBLIC
USER
PRIVATE
SECURE
```

---

# 166. LOGGING

Los logs no deberán registrar secretos ni datos sensibles innecesarios.

---

# 167. REDACTION

Deberá existir capacidad para ocultar:

```text
tokens
credentials
keys
private identifiers
```

cuando aparezcan accidentalmente en diagnostics.

---

# 168. BACKUP RETENTION

La política de retención deberá impedir crecimiento ilimitado.

---

# 169. RECOVERY PRIORITY

Ante corrupción:

```text
CURRENT VALID
 ↓
PREVIOUS VALID
 ↓
BACKUP VALID
 ↓
CLOUD VALID
 ↓
SAFE DEFAULT
```

según política.

---

# 170. SAFE DEFAULT

Si ningún save puede recuperarse, el producto deberá disponer de una ruta segura de inicialización.

---

# 171. NEW USER INITIALIZATION

Deberá poder crearse un perfil limpio con:

```text
defaults
default_settings
default_input
default_accessibility
default_language
```

---

# 172. FIRST BOOT

El primer arranque deberá funcionar sin saves existentes.

---

# 173. MIGRATION OF USER SETTINGS

Las preferencias deberán migrarse independientemente del progreso del juego cuando sea necesario.

---

# 174. PARTIAL MIGRATION

Un campo incompatible no deberá invalidar automáticamente todo el save si puede recuperarse de forma segura.

---

# 175. MIGRATION WARNING

Las migraciones con pérdida de información deberán producir warning explícito.

---

# 176. DATA LOSS POLICY

Toda pérdida de datos durante migración deberá ser:

```text
intentional
documented
validated
recoverable
```

cuando sea técnicamente posible.

---

# 177. SCHEMA REGISTRY

Deberá existir:

```text
SchemaRegistry
```

que conozca:

```text
schema_id
version
validator
serializer
migration
```

---

# 178. MIGRATION REGISTRY

Deberá existir:

```text
MigrationRegistry
```

---

# 179. MIGRATION DISCOVERY

El sistema deberá poder determinar automáticamente la ruta de migración válida.

---

# 180. MIGRATION CYCLE

No deberá permitirse:

```text
V1 -> V2 -> V1 -> V2
```

como consecuencia accidental de migraciones.

---

# 181. SCHEMA CYCLE

Las dependencias entre schemas deberán evitar ciclos no soportados.

---

# 182. DEPENDENCY ORDER

Los datos deberán cargarse en orden topológico cuando existan dependencias.

---

# 183. DEPENDENCY FAILURE

Si una dependencia obligatoria falla:

```text
LOAD FAILED
```

con error estructurado.

---

# 184. OPTIONAL DEPENDENCY

Una dependencia opcional podrá utilizar fallback.

---

# 185. UNKNOWN CONTENT

Contenido desconocido deberá manejarse mediante:

```text
IGNORE
PRESERVE
MIGRATE
REJECT
```

según contrato.

---

# 186. CONTENT VERSION

Los assets o contenidos referenciados por un save deberán tener versionado suficiente para detectar incompatibilidad.

---

# 187. MISSING CONTENT

Un save que referencia contenido eliminado deberá poder:

```text
fallback
placeholder
migration
safe failure
```

---

# 188. MODDED DATA

Si el producto soporta mods, el save deberá registrar dependencias necesarias.

---

# 189. MOD VERSION

Deberá poder detectarse:

```text
missing_mod
different_version
changed_schema
```

---

# 190. MOD SAVE SAFETY

No deberá cargar silenciosamente datos incompatibles que puedan corromper el estado.

---

# 191. TEST DIRECTORY

Deberá existir como mínimo:

```text
tests/persistence/
tests/persistence/save/
tests/persistence/load/
tests/persistence/autosave/
tests/persistence/checkpoint/
tests/persistence/profile/
tests/persistence/settings/
tests/persistence/configuration/
tests/persistence/serialization/
tests/persistence/schema/
tests/persistence/migration/
tests/persistence/rollback/
tests/persistence/transaction/
tests/persistence/integrity/
tests/persistence/corruption/
tests/persistence/backup/
tests/persistence/recovery/
tests/persistence/cloud/
tests/persistence/conflict/
tests/persistence/security/
tests/persistence/performance/
tests/persistence/determinism/
tests/persistence/crash/
tests/persistence/golden/
tests/persistence/integration/
tests/persistence/end_to_end/
```

---

# 192. CORE TESTS

Mínimo:

```text
test_save_service
test_save_request
test_save_state_machine
test_save_slot
test_slot_states
test_save_metadata
test_save_index
test_save_list
test_save_delete
test_save_lock
test_save_unlock
test_save_queue
```

---

# 193. SAVE TESTS

Mínimo:

```text
test_create_save
test_write_save
test_commit_save
test_validate_save
test_save_completion
test_save_failure
test_save_cancel
test_save_retry
test_save_idempotency
test_save_atomicity
test_save_previous_preserved
test_save_size_limit
test_save_object_limit
```

---

# 194. AUTOSAVE TESTS

Mínimo:

```text
test_autosave_timer
test_autosave_event
test_autosave_throttle
test_autosave_coalescing
test_autosave_blocked_state
test_autosave_failure
test_autosave_preserves_previous
test_autosave_retry
test_autosave_determinism
```

---

# 195. CHECKPOINT TESTS

Mínimo:

```text
test_checkpoint_create
test_checkpoint_load
test_checkpoint_replace
test_checkpoint_invalidate
test_checkpoint_session_lifetime
test_checkpoint_persistent
test_checkpoint_world_change
test_checkpoint_version_change
```

---

# 196. PROFILE TESTS

Mínimo:

```text
test_player_profile
test_user_profile
test_profile_switch
test_profile_switch_flush
test_profile_switch_failure
test_profile_restore
test_profile_isolation
test_profile_default
test_profile_version
```

---

# 197. SETTINGS TESTS

Mínimo:

```text
test_settings_store
test_setting_bool
test_setting_int
test_setting_float
test_setting_string
test_setting_enum
test_setting_range
test_setting_default
test_setting_pending
test_setting_apply
test_setting_confirm
test_setting_revert
test_setting_reset
test_unsafe_setting
test_setting_persistence
```

---

# 198. CONFIGURATION TESTS

Mínimo:

```text
test_default_config
test_platform_config
test_user_config
test_profile_config
test_session_config
test_config_precedence
test_config_read_only
test_config_validation
```

---

# 199. SERIALIZATION TESTS

Mínimo:

```text
test_serialize_primitive
test_serialize_enum
test_serialize_array
test_serialize_map
test_serialize_struct
test_serialize_optional
test_serialize_reference
test_serialize_versioned_object
test_null
test_missing_field
test_unknown_field
test_serialization_failure
test_deserialization_failure
test_reference_resolution
test_missing_reference
```

---

# 200. SCHEMA TESTS

Mínimo:

```text
test_schema_registry
test_schema_version
test_schema_lookup
test_schema_validator
test_schema_compatibility
test_schema_unknown_version
test_schema_missing_field
test_schema_unknown_field
test_schema_dependency
test_schema_cycle_rejection
```

---

# 201. MIGRATION TESTS

Mínimo:

```text
test_migration_registry
test_migration_discovery
test_migration_v1_v2
test_migration_v2_v3
test_migration_chain
test_direct_migration
test_migration_idempotency
test_migration_precondition
test_migration_validation
test_migration_failure
test_migration_backup
test_migration_rollback
test_migration_log
test_migration_loss_warning
test_migration_cycle_rejection
```

---

# 202. ROLLBACK TESTS

Mínimo:

```text
test_rollback_after_write
test_rollback_after_commit_failure
test_rollback_after_validation
test_rollback_after_migration
test_rollback_after_post_load
test_runtime_rollback
test_previous_save_restore
```

---

# 203. TRANSACTION TESTS

Mínimo:

```text
test_transaction_prepare
test_transaction_write
test_transaction_commit
test_transaction_abort
test_transaction_atomicity
test_transaction_recovery
test_transaction_idempotency
```

---

# 204. INTEGRITY TESTS

Mínimo:

```text
test_checksum
test_checksum_mismatch
test_size_validation
test_structure_validation
test_required_field_validation
test_integrity_valid
test_integrity_suspect
test_integrity_corrupted
test_integrity_unreadable
```

---

# 205. CORRUPTION TESTS

Mínimo:

```text
test_corrupt_header
test_corrupt_metadata
test_corrupt_payload
test_corrupt_checksum
test_truncated_file
test_invalid_encoding
test_invalid_reference
test_invalid_enum
test_invalid_range
test_excessive_collection
test_recursion_attack
test_corrupt_index
test_quarantine
test_recovery_from_previous
test_recovery_from_backup
```

---

# 206. BACKUP TESTS

Mínimo:

```text
test_backup_create
test_backup_rotation
test_backup_retention
test_backup_verification
test_backup_restore
test_backup_corruption
test_backup_cleanup
```

---

# 207. RECOVERY TESTS

Mínimo:

```text
test_crash_before_write
test_crash_during_write
test_crash_after_write
test_crash_before_commit
test_crash_during_commit
test_crash_after_commit
test_crash_before_index
test_crash_after_index
test_power_loss_simulation
test_journal_recovery
test_abandoned_temp_file
test_stale_lock_recovery
```

---

# 208. STORAGE FAILURE TESTS

Mínimo:

```text
test_no_space
test_permission_denied
test_read_error
test_write_error
test_delete_error
test_rename_error
test_lock_error
test_storage_unavailable
```

---

# 209. CLOUD TESTS

Mínimo:

```text
test_cloud_unavailable
test_cloud_connect
test_cloud_upload
test_cloud_download
test_cloud_match
test_cloud_local_newer
test_cloud_remote_newer
test_cloud_conflict
test_cloud_retry
test_cloud_failure
```

---

# 210. CONFLICT TESTS

Mínimo:

```text
test_local_wins
test_remote_wins
test_newest
test_manual_resolution
test_merge
test_merge_conflict
test_conflict_no_overwrite
```

---

# 211. MULTIPLAYER TESTS

Mínimo:

```text
test_server_authority
test_client_cache
test_shared_profile
test_authoritative_save
test_client_write_rejection
test_disconnect_during_save
test_reconnect_after_save
```

---

# 212. SECURITY TESTS

Mínimo:

```text
test_path_traversal_rejection
test_invalid_slot_id
test_invalid_profile_id
test_oversized_save
test_object_count_limit
test_recursion_limit
test_secret_redaction
test_untrusted_metadata
test_invalid_reference
test_invalid_schema
```

---

# 213. MOD DATA TESTS

Si se soportan mods:

```text
test_mod_dependency
test_missing_mod
test_mod_version_mismatch
test_mod_schema_mismatch
test_mod_save_fallback
```

---

# 214. DETERMINISM TESTS

Mínimo:

```text
test_save_determinism
test_serialization_determinism
test_checksum_determinism
test_migration_determinism
test_load_determinism
test_reference_resolution_determinism
test_index_determinism
test_conflict_determinism
test_recovery_determinism
test_snapshot_determinism
```

---

# 215. PERFORMANCE TESTS

Mínimo:

```text
test_large_save
test_large_inventory
test_large_world_state
test_large_quest_state
test_large_profile
test_serialization_budget
test_deserialization_budget
test_migration_budget
test_validation_budget
test_save_throughput
test_load_throughput
test_compression_ratio
```

---

# 216. GOLDEN TESTS

Mínimo:

```text
GOLDEN_NEW_PROFILE
GOLDEN_DEFAULT_SETTINGS
GOLDEN_BASIC_SAVE
GOLDEN_FULL_SAVE
GOLDEN_AUTOSAVE
GOLDEN_CHECKPOINT
GOLDEN_MIGRATED_SAVE
GOLDEN_BACKUP
GOLDEN_RECOVERY
GOLDEN_CORRUPTED_SAVE
GOLDEN_CLOUD_CONFLICT
GOLDEN_SETTINGS
GOLDEN_INPUT_PROFILE
GOLDEN_ACCESSIBILITY_PROFILE
GOLDEN_WORLD_STATE
GOLDEN_PLAYER_STATE
GOLDEN_QUEST_STATE
GOLDEN_INVENTORY_STATE
GOLDEN_COMPLETE_RUNTIME
```

---

# 217. END-TO-END TEST

Deberá existir como mínimo:

```text
FIRST_BOOT
 ↓
CREATE_PROFILE
 ↓
SET_LANGUAGE
 ↓
SET_ACCESSIBILITY
 ↓
SET_CONTROLS
 ↓
START_GAME
 ↓
PROGRESS
 ↓
CREATE_CHECKPOINT
 ↓
AUTOSAVE
 ↓
MANUAL_SAVE
 ↓
CLOSE
 ↓
RESTART
 ↓
DISCOVER_SAVE
 ↓
VERIFY_INTEGRITY
 ↓
LOAD
 ↓
POST_LOAD_VALIDATE
 ↓
CONTINUE
 ↓
CHANGE_SETTINGS
 ↓
SAVE
 ↓
SIMULATE_CRASH
 ↓
RECOVER
 ↓
LOAD_PREVIOUS_VALID
 ↓
MIGRATE_SCHEMA
 ↓
VALIDATE_MIGRATION
 ↓
BACKUP
 ↓
RESTORE
 ↓
CLOUD_SYNC
 ↓
CONFLICT
 ↓
RESOLVE
 ↓
FINAL_SAVE
```

---

# 218. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
12 CORE
13 SAVE
9 AUTOSAVE
8 CHECKPOINT
9 PROFILE
15 SETTINGS
8 CONFIGURATION
15 SERIALIZATION
10 SCHEMA
15 MIGRATION
7 ROLLBACK
7 TRANSACTION
9 INTEGRITY
15 CORRUPTION
7 BACKUP
12 RECOVERY
8 STORAGE_FAILURE
10 CLOUD
7 CONFLICT
7 MULTIPLAYER
10 SECURITY
5 MOD_DATA
10 DETERMINISM
12 PERFORMANCE
19 GOLDEN
1 END_TO_END
```

**Total mínimo: 269 tests.**

Los tests de integración y E2E no sustituyen los tests unitarios específicos.

---

# 219. FAILURE MATRIX

La implementación deberá demostrar comportamiento para:

| Failure              | Required behavior                   |
| -------------------- | ----------------------------------- |
| No space             | Preserve previous valid save        |
| Permission denied    | Fail without corruption             |
| Write failure        | Abort transaction                   |
| Commit failure       | Recover previous state              |
| Corrupt checksum     | Reject/quarantine                   |
| Truncated file       | Reject/recover                      |
| Unknown schema       | Migration or incompatibility        |
| Migration failure    | Rollback                            |
| Missing reference    | Contract-defined fallback/error     |
| Cloud unavailable    | Continue local operation            |
| Cloud conflict       | Do not overwrite silently           |
| Crash during save    | Recover atomically                  |
| Crash during load    | Preserve active safe state          |
| Corrupt index        | Rebuild                             |
| Stale lock           | Recover safely                      |
| Invalid metadata     | Ignore/reject according to contract |
| Oversized collection | Reject                              |
| Invalid enum         | Default/migrate/reject              |
| Invalid range        | Clamp/default/reject                |
| Missing content      | Fallback/migration/error            |

---

# 220. NO DATA LOSS GUARANTEE

El sistema deberá garantizar como principio:

```text
NEW SAVE FAILURE
≠
LOSS OF LAST VALID SAVE
```

y:

```text
MIGRATION FAILURE
≠
LOSS OF ORIGINAL SAVE
```

y:

```text
LOAD FAILURE
≠
CORRUPTION OF ACTIVE SESSION
```

---

# 221. NO PARTIAL COMMIT

Nunca deberá declararse un save como válido mientras:

```text
payload incomplete
checksum invalid
commit incomplete
required metadata missing
```

---

# 222. NO ORPHAN TEMP FILE

Los archivos temporales deberán:

```text
recover
complete
rollback
cleanup
```

según estado.

---

# 223. NO ORPHAN INDEX

Toda entrada de índice deberá apuntar a un save existente o poder ser reconstruida/eliminada.

---

# 224. NO STALE PROFILE

Un cambio de perfil deberá impedir que preferencias del perfil anterior se filtren al nuevo.

---

# 225. NO CROSS-SLOT CONTAMINATION

Una operación sobre `slot_A` no deberá modificar accidentalmente:

```text
slot_B
slot_C
backup_A
cloud_A
```

---

# 226. NO CROSS-USER CONTAMINATION

Los datos de un perfil no deberán aparecer en otro perfil.

---

# 227. NO SILENT DATA LOSS

Toda pérdida, truncamiento o eliminación de datos deberá generar diagnóstico cuando sea detectable.

---

# 228. RECOVERY REPORT

Después de una recuperación deberá poder conocerse:

```text
recovery_reason
source
target
timestamp
result
data_loss
warnings
```

---

# 229. USER-FACING RECOVERY

La información técnica deberá separarse del mensaje presentado al usuario.

---

# 230. USER-FACING SAVE STATES

El UI deberá poder mostrar:

```text
SAVING
SAVED
SAVE_FAILED
LOADING
LOAD_FAILED
RECOVERING
RECOVERED
MIGRATION_REQUIRED
INCOMPATIBLE
CORRUPTED
```

---

# 231. INTEGRATION WITH UAF-81.61

La UI deberá consumir únicamente estados oficiales del sistema de persistencia.

No deberá inferir:

```text
save complete
load complete
migration complete
```

a partir de timers o animaciones.

---

# 232. INTEGRATION WITH UAF-81.60

Dialogue, cinematic y world state deberán poder definir checkpoints y datos persistibles sin duplicar ownership.

---

# 233. INTEGRATION WITH EARLIER PHASES

Los sistemas anteriores deberán registrar explícitamente sus datos persistibles.

Ningún sistema deberá depender de serialización accidental.

---

# 234. PERSISTENCE CONTRACT

Cada subsistema persistible deberá declarar:

```text
schema_id
version
owner
serialize
deserialize
validate
migrate
default
reset
```

---

# 235. FINAL ACCEPTANCE CRITERIA

UAF-81.62 estará completa únicamente cuando:

```text
SAVE SYSTEM IMPLEMENTED
LOAD SYSTEM IMPLEMENTED
SAVE SLOTS IMPLEMENTED
AUTOSAVE IMPLEMENTED
CHECKPOINTS IMPLEMENTED
PLAYER PROFILE IMPLEMENTED
USER PROFILE IMPLEMENTED
SETTINGS IMPLEMENTED
CONFIGURATION PRECEDENCE IMPLEMENTED
SERIALIZATION IMPLEMENTED
DESERIALIZATION IMPLEMENTED
REFERENCE RESOLUTION IMPLEMENTED
SCHEMA REGISTRY IMPLEMENTED
VERSIONING IMPLEMENTED
MIGRATION IMPLEMENTED
MIGRATION ROLLBACK IMPLEMENTED
TRANSACTION SYSTEM IMPLEMENTED
ATOMIC SAVE IMPLEMENTED
SAVE JOURNAL IMPLEMENTED WHEN REQUIRED
CRASH RECOVERY IMPLEMENTED
BACKUP IMPLEMENTED
RESTORE IMPLEMENTED
CORRUPTION DETECTION IMPLEMENTED
CHECKSUM/INTEGRITY IMPLEMENTED
INDEX IMPLEMENTED
INDEX RECOVERY IMPLEMENTED
STORAGE FAILURE HANDLING IMPLEMENTED
CLOUD ABSTRACTION IMPLEMENTED
CONFLICT RESOLUTION IMPLEMENTED
MULTIPLAYER PERSISTENCE CONTRACT IMPLEMENTED
SECURITY VALIDATION IMPLEMENTED
PATH SAFETY IMPLEMENTED
SIZE LIMITS IMPLEMENTED
REFERENCE LIMITS IMPLEMENTED
RECURSION LIMITS IMPLEMENTED
PROFILE ISOLATION IMPLEMENTED
SETTINGS VALIDATION IMPLEMENTED
SAFE SETTINGS IMPLEMENTED
DATA LOSS PROTECTION IMPLEMENTED
RECOVERY REPORT IMPLEMENTED
UI INTEGRATION IMPLEMENTED
MINIMUM 269 TESTS IMPLEMENTED
FAILURE MATRIX COVERED
CRASH TESTS IMPLEMENTED
MIGRATION TESTS IMPLEMENTED
ROLLBACK TESTS IMPLEMENTED
DETERMINISM TESTS IMPLEMENTED
GOLDEN TESTS IMPLEMENTED
END_TO_END TEST IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 236. NEXT PHASE

```text
UAF-81.63 — UNIVERSAL BUILD, PACKAGING, DEPENDENCY, CONTENT ADDRESSING, ASSET REGISTRY, INSTALLATION, PATCHING, UPDATE, DLC, MODULAR CONTENT & RUNTIME DEPLOYMENT SYSTEM
```

La siguiente fase deberá cerrar el ciclo entre contenido producido y producto ejecutable:

```text
ASSET REGISTRY
CONTENT REGISTRY
DEPENDENCY GRAPH
CONTENT ADDRESSING
BUILD GRAPH
BUILD CACHE
ARTIFACTS
PACKAGING
BUNDLES
INSTALLATION
UNINSTALLATION
PATCHING
DELTA PATCHES
UPDATE
ROLLBACK UPDATE
DLC
OPTIONAL CONTENT
LANGUAGE PACKS
MODULAR CONTENT
MOD SUPPORT
CONTENT VERSIONING
COMPATIBILITY
MANIFESTS
SIGNING
INTEGRITY
HASHING
DEDUPLICATION
STORAGE
DOWNLOAD
INSTALL
VERIFY
REPAIR
RECOVERY
TESTS
FAILURE TESTS
CRASH TESTS
DETERMINISM TESTS
GOLDEN TESTS
END-TO-END TESTS
```
