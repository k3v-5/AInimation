# UAF-81.70 — UNIVERSAL ASSET IMPORT PIPELINE, SOURCE PROCESSORS, FORMAT DETECTION, IMPORT PROFILES, PROCESSING GRAPH, JOB QUEUE, WORKER POOL, CACHING, INCREMENTAL PROCESSING, ERROR RECOVERY, DEPENDENCY PROCESSING & IMPORT TESTING SYSTEM

## UAF-81.70-ARCH

### ARQUITECTURA NORMATIVA DEL PIPELINE UNIVERSAL DE IMPORTACIÓN DE ACTIVOS, PROCESADORES DE FUENTES, DETECCIÓN DE FORMATOS, PERFILES DE IMPORTACIÓN, GRAFO DE PROCESAMIENTO, COLA DE TRABAJOS, GRUPO DE TRABAJADORES, CACHÉ, PROCESAMIENTO INCREMENTAL, RECUPERACIÓN DE ERRORES, PROCESAMIENTO DE DEPENDENCIAS Y PRUEBAS DE IMPORTACIÓN

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.70 — Universal Asset Import Pipeline, Source Processors, Format Detection, Import Profiles, Processing Graph, Job Queue, Worker Pool, Caching, Incremental Processing, Error Recovery, Dependency Processing & Import Testing System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.69  
**Next Phase:** UAF-81.71  

---

# 1. PURPOSE

UAF-81.70 define el pipeline universal de importación y procesamiento de assets.

La fase deberá proporcionar:

```text
SOURCE DISCOVERY
SOURCE IDENTITY
FORMAT DETECTION
FORMAT REGISTRY
IMPORT PROFILE
PROFILE RESOLUTION
IMPORT SETTINGS
PROCESSOR REGISTRY
SOURCE PROCESSOR
PROCESSING GRAPH
PROCESSING NODE
PROCESSING EDGE
JOB
JOB QUEUE
JOB PRIORITY
JOB CANCELLATION
WORKER POOL
WORKER LIFECYCLE
RESOURCE LIMITS
DEPENDENCY PROCESSING
INCREMENTAL PROCESSING
PROCESS CACHE
CACHE INVALIDATION
IMPORT ARTIFACTS
IMPORT MANIFEST
IMPORT LOG
PROGRESS
ERROR HANDLING
RETRY
RECOVERY
RESUME
DETERMINISTIC PROCESSING
IMPORT COMMANDS
IMPORT UI
IMPORT TESTING
```

---

# 2. ARCHITECTURAL PIPELINE

```text
SOURCE
  ↓
DISCOVERY
  ↓
IDENTITY
  ↓
FORMAT DETECTION
  ↓
IMPORT PROFILE
  ↓
PROCESSOR RESOLUTION
  ↓
PROCESSING GRAPH
  ↓
DEPENDENCY GRAPH
  ↓
JOB QUEUE
  ↓
WORKER POOL
  ↓
PROCESSOR
  ↓
ARTIFACTS
  ↓
CACHE
  ↓
CATALOG UPDATE
  ↓
BROWSER / INSPECTOR
```

---

# 3. SOURCE IDENTITY

Toda fuente deberá tener identidad estable.

Mínimo:

```text
source_id
canonical_path
source_type
content_hash
source_version
```

---

# 4. SOURCE NORMALIZATION

Las fuentes deberán normalizarse antes de entrar al pipeline.

Deberá contemplarse:

```text
path separators
relative paths
case policy
unicode normalization
symlink policy
reserved paths
```

---

# 5. SOURCE VALIDATION

Antes de procesar una fuente deberá validarse:

```text
exists
readable
supported
within_allowed_scope
not_directory_when_file_expected
```

---

# 6. FORMAT DETECTION

Deberá existir:

```text
FormatDetector
```

capaz de identificar el formato de una fuente.

---

# 7. DETECTION SOURCES

La detección podrá utilizar:

```text
extension
magic bytes
container metadata
header
content signature
```

---

# 8. DETECTION PRIORITY

La prioridad deberá ser determinista.

Una política mínima:

```text
CONTENT_SIGNATURE
HEADER
CONTAINER_METADATA
EXTENSION
```

---

# 9. DETECTION CONFLICT

Cuando extensión y contenido difieran, el sistema deberá conservar el diagnóstico y aplicar una política explícita.

---

# 10. UNKNOWN FORMAT

Los formatos desconocidos deberán producir:

```text
UNSUPPORTED_FORMAT
```

sin corrupción del catálogo.

---

# 11. FORMAT REGISTRY

Deberá existir un registro extensible:

```text
FormatRegistry
```

---

# 12. FORMAT DESCRIPTOR

Mínimo:

```text
format_id
extensions
mime_types
detector
processor_ids
version
```

---

# 13. FORMAT REGISTRATION

Deberá rechazarse el registro duplicado de formatos incompatibles.

---

# 14. IMPORT PROFILE

Deberá existir:

```text
ImportProfile
```

que determine cómo procesar una fuente.

---

# 15. PROFILE CONTENT

Mínimo:

```text
profile_id
profile_version
format
processor
settings
output_policy
```

---

# 16. PROFILE RESOLUTION

La resolución podrá depender de:

```text
source
format
path
asset_type
project_settings
user_override
```

---

# 17. PROFILE PRIORITY

La prioridad deberá ser determinista.

---

# 18. DEFAULT PROFILE

Todo formato soportado deberá tener un profile por defecto o una política explícita de ausencia.

---

# 19. USER OVERRIDE

El usuario podrá sobrescribir settings cuando el editor lo permita.

---

# 20. PROFILE VALIDATION

Los settings deberán validarse antes de crear jobs.

---

# 21. PROFILE VERSIONING

Cambios de profile deberán poder provocar reimportación cuando corresponda.

---

# 22. IMPORT SETTINGS

Los settings deberán ser serializables.

---

# 23. SETTINGS DETERMINISM

Los mismos settings deberán producir el mismo fingerprint de procesamiento.

---

# 24. PROCESSOR REGISTRY

Deberá existir:

```text
ProcessorRegistry
```

---

# 25. PROCESSOR DESCRIPTOR

Mínimo:

```text
processor_id
version
supported_formats
input_types
output_types
capabilities
```

---

# 26. PROCESSOR CONTRACT

Cada processor deberá declarar:

```text
can_process
prepare
process
finalize
cancel
```

según corresponda.

---

# 27. PROCESSOR ISOLATION

Un processor no deberá modificar directamente el estado global del catálogo.

---

# 28. PROCESSING GRAPH

El procesamiento deberá representarse como grafo.

```text
ProcessingGraph
```

---

# 29. GRAPH NODE

Cada node deberá poseer:

```text
node_id
processor_id
settings
inputs
outputs
```

---

# 30. GRAPH EDGE

Cada edge deberá definir:

```text
source_node
output
target_node
input
```

---

# 31. GRAPH VALIDATION

Deberá rechazarse:

```text
cycle
missing node
missing input
missing output
type mismatch
duplicate node id
```

---

# 32. GRAPH DETERMINISM

El mismo graph deberá producir el mismo orden lógico de ejecución.

---

# 33. GRAPH TOPOLOGICAL ORDER

Cuando existan dependencias, el orden deberá ser topológico y determinista.

---

# 34. GRAPH PARALLELISM

Los nodes independientes podrán procesarse en paralelo.

---

# 35. GRAPH FAILURE

El fallo de un node deberá propagarse únicamente a sus dependientes afectados.

---

# 36. OPTIONAL NODES

Podrán existir nodes opcionales con comportamiento explícito.

---

# 37. JOB MODEL

Cada procesamiento deberá materializarse como job.

Mínimo:

```text
job_id
source_id
graph
priority
state
progress
timestamps
```

---

# 38. JOB STATES

```text
QUEUED
PREPARING
RUNNING
COMPLETED
FAILED
CANCELLED
RETRYING
BLOCKED
```

---

# 39. JOB PRIORITY

Mínimo:

```text
LOW
NORMAL
HIGH
CRITICAL
```

---

# 40. PRIORITY ORDER

A igual prioridad deberá existir tie-breaker determinista.

---

# 41. JOB QUEUE

Deberá existir:

```text
JobQueue
```

---

# 42. QUEUE OPERATIONS

Mínimo:

```text
enqueue
dequeue
cancel
reprioritize
inspect
```

---

# 43. QUEUE FAIRNESS

La prioridad no deberá provocar starvation indefinido bajo condiciones normales.

---

# 44. QUEUE CANCELLATION

Un job queued deberá poder cancelarse sin ejecutarse.

---

# 45. RUNNING CANCELLATION

Un job running deberá cooperar con cancelación.

---

# 46. WORKER POOL

Deberá existir:

```text
WorkerPool
```

---

# 47. WORKER STATES

```text
IDLE
STARTING
RUNNING
STOPPING
STOPPED
FAILED
```

---

# 48. WORKER COUNT

El número de workers deberá ser configurable.

---

# 49. WORKER LIMITS

No deberá excederse el límite global de recursos.

---

# 50. WORKER FAILURE

El fallo de un worker no deberá perder silenciosamente el job.

---

# 51. JOB REQUEUE

Los jobs afectados podrán volver a queue según política.

---

# 52. RESOURCE LIMITS

Deberán existir límites para:

```text
workers
memory
CPU
disk
IO
concurrent_processes
preview_generation
```

cuando aplique.

---

# 53. BACKPRESSURE

Cuando los recursos estén saturados, el sistema deberá aplicar backpressure.

---

# 54. PROGRESS

Cada job podrá reportar:

```text
0..1
```

---

# 55. PROGRESS DETERMINISM

El progreso deberá ser monotónico dentro de un node cuando sea posible.

---

# 56. PROGRESS AGGREGATION

El graph deberá agregar progreso de forma determinista.

---

# 57. LOGGING

Cada job deberá generar log estructurado.

Mínimo:

```text
job_id
node_id
severity
code
message
timestamp
```

---

# 58. ERROR MODEL

Errores mínimos:

```text
SOURCE_NOT_FOUND
SOURCE_UNREADABLE
UNSUPPORTED_FORMAT
INVALID_PROFILE
PROCESSOR_NOT_FOUND
INVALID_GRAPH
PROCESSING_FAILED
DEPENDENCY_FAILED
CACHE_FAILURE
OUTPUT_FAILURE
CANCELLED
RESOURCE_LIMIT
```

---

# 59. ERROR CLASSIFICATION

Cada error deberá clasificarse como:

```text
RECOVERABLE
RETRYABLE
FATAL
USER_ACTION_REQUIRED
```

---

# 60. RETRY POLICY

Los retries deberán ser controlados.

Mínimo:

```text
max_attempts
backoff
retryable_errors
```

---

# 61. RETRY DETERMINISM

El retry deberá usar la misma entrada lógica salvo que la política indique explícitamente lo contrario.

---

# 62. RECOVERY

El sistema deberá poder recuperar jobs interrumpidos.

---

# 63. RESUME

Cuando un processor sea reanudable, deberá poder continuar desde un checkpoint válido.

---

# 64. CHECKPOINT

Un checkpoint deberá identificar:

```text
job_id
graph_version
node_id
processor_version
input_fingerprint
state
```

---

# 65. CHECKPOINT VALIDATION

No deberá reutilizarse un checkpoint incompatible.

---

# 66. DEPENDENCY PROCESSING

Las dependencias deberán representarse explícitamente.

---

# 67. DEPENDENCY STATES

```text
AVAILABLE
MISSING
OUTDATED
PROCESSING
FAILED
```

---

# 68. DEPENDENCY ORDER

Las dependencias deberán procesarse antes que sus consumidores cuando sea necesario.

---

# 69. DEPENDENCY CYCLES

Los ciclos deberán detectarse antes de ejecutar el graph.

---

# 70. DEPENDENCY FAILURE

Un consumidor no deberá procesarse usando silenciosamente una dependencia inválida.

---

# 71. INCREMENTAL PROCESSING

El pipeline deberá evitar trabajo innecesario.

---

# 72. INPUT FINGERPRINT

El fingerprint deberá considerar:

```text
source_hash
processor_version
profile_version
settings
dependency_fingerprints
```

---

# 73. PROCESS CACHE

Deberá existir:

```text
ProcessCache
```

---

# 74. CACHE KEY

La key deberá derivarse del fingerprint de procesamiento.

---

# 75. CACHE HIT

Un cache hit deberá producir un resultado equivalente al procesamiento completo.

---

# 76. CACHE MISS

Un cache miss deberá ejecutar el processor correspondiente.

---

# 77. CACHE INVALIDATION

Deberá invalidarse cuando cambie:

```text
source
processor
profile
settings
dependency
```

---

# 78. CACHE CORRUPTION

Una entrada corrupta deberá tratarse como cache miss o error recuperable.

---

# 79. CACHE VERSIONING

El cache deberá incluir versión de formato.

---

# 80. ARTIFACT MODEL

Los resultados deberán representarse mediante artifacts.

Mínimo:

```text
artifact_id
source_id
type
path
hash
metadata
```

---

# 81. ARTIFACT OWNERSHIP

Los artifacts deberán tener ownership claro.

---

# 82. ARTIFACT ATOMICITY

La publicación de artifacts deberá ser atómica.

---

# 83. PARTIAL OUTPUT

No deberán publicarse outputs parciales como artifacts válidos.

---

# 84. OUTPUT MANIFEST

Cada job completado deberá poder producir manifest.

---

# 85. IMPORT MANIFEST

Mínimo:

```text
source
format
profile
processor_versions
inputs
outputs
dependencies
fingerprint
```

---

# 86. MANIFEST DETERMINISM

Equivalentemente procesado deberá producir manifest lógico equivalente.

---

# 87. CATALOG INTEGRATION

Al finalizar correctamente:

```text
processor
 ↓
artifacts
 ↓
manifest
 ↓
catalog
 ↓
browser
```

---

# 88. BROWSER STATUS

UAF-81.69 deberá reflejar:

```text
QUEUED
PROCESSING
READY
FAILED
```

---

# 89. INSPECTOR INTEGRATION

UAF-81.68 deberá poder mostrar:

```text
import status
processor
profile
errors
outputs
```

---

# 90. IMPORT COMMANDS

Mínimo:

```text
IMPORT
REIMPORT
CANCEL_IMPORT
RETRY_IMPORT
CLEAR_IMPORT_ERROR
REBUILD_ARTIFACTS
```

---

# 91. COMMAND VALIDATION

Las operaciones inválidas deberán rechazarse antes de crear efectos parciales.

---

# 92. IMPORT UI

La UI deberá poder mostrar:

```text
queue
progress
state
errors
processor
profile
```

---

# 93. BATCH IMPORT

Deberá soportarse importación de múltiples sources.

---

# 94. BATCH TRANSACTION

La importación batch deberá permitir políticas:

```text
FAIL_FAST
CONTINUE
ATOMIC
```

---

# 95. BATCH FAILURE

Los resultados individuales deberán conservarse cuando la política sea `CONTINUE`.

---

# 96. IMPORT PRIORITY

Los jobs derivados de acciones explícitas del usuario podrán tener prioridad superior a trabajos background.

---

# 97. BACKGROUND PROCESSING

El sistema deberá poder procesar cambios automáticamente.

---

# 98. FOREGROUND PROCESSING

Una operación explícita podrá solicitar prioridad foreground.

---

# 99. IMPORT QUEUE PERSISTENCE

Podrá persistirse la queue para recuperación después de reinicio.

---

# 100. PERSISTED JOB VALIDATION

Un job restaurado deberá validarse contra:

```text
source
processor
profile
graph
cache
dependencies
```

---

# 101. PROCESSOR PLUGINS

Los processors podrán ser extensibles.

---

# 102. PLUGIN ISOLATION

Un processor externo deberá respetar el contrato de seguridad y lifecycle.

---

# 103. PROCESSOR VERSIONING

Cambiar processor version deberá invalidar resultados incompatibles.

---

# 104. PROFILE MIGRATION

Los profiles deberán poder migrarse entre versiones cuando sea necesario.

---

# 105. MIGRATION FAILURE

Un profile no migrable deberá quedar en estado explícito de error.

---

# 106. FORMAT MIGRATION

Los formatos/versiones deberán poder indicar incompatibilidades.

---

# 107. LARGE ASSET PROCESSING

Deberá soportarse procesamiento incremental/chunked cuando el formato lo permita.

---

# 108. MEMORY CONTROL

Los processors no deberán cargar innecesariamente un asset completo cuando exista estrategia streaming.

---

# 109. STREAMING

Podrá soportarse:

```text
read stream
process chunks
write stream
```

---

# 110. TEMPORARY FILES

Los temporales deberán tener lifecycle controlado.

---

# 111. TEMPORARY CLEANUP

Un job completado, cancelado o fallido deberá limpiar temporales según política.

---

# 112. OUTPUT PATH POLICY

Los outputs deberán generarse dentro de scopes permitidos.

---

# 113. PATH SAFETY

No deberá permitirse:

```text
path traversal
absolute escape
unsafe symlink escape
```

---

# 114. IMPORT SECURITY

Deberá tratarse toda fuente como potencialmente no confiable.

---

# 115. RESOURCE EXHAUSTION

Deberán existir límites contra:

```text
oversized input
decompression bombs
path explosion
job explosion
dependency explosion
memory exhaustion
disk exhaustion
```

---

# 116. DETERMINISTIC PROCESSING

La misma combinación:

```text
source
processor
profile
dependencies
environment contract
```

deberá producir artifacts equivalentes.

---

# 117. ENVIRONMENT DEPENDENCY

Los processors deberán declarar dependencias externas que puedan afectar determinismo.

---

# 118. PROCESSING ENVIRONMENT

Cuando sea necesario deberá fijarse:

```text
locale
timezone
encoding
floating-point policy
tool version
```

---

# 119. IMPORT REPLAY

Un import deberá poder reproducirse desde un manifest/replay suficientemente completo.

---

# 120. REPLAY VALIDATION

El replay deberá comparar:

```text
inputs
settings
processor versions
outputs
fingerprints
```

---

# 121. TESTING SYSTEM

UAF-81.70 deberá incluir tests completos del pipeline.

---

# 122. SOURCE TESTS

Mínimo:

```text
test_source_identity
test_source_normalization
test_source_exists
test_source_readability
test_source_scope
test_source_hash
test_source_version
```

---

# 123. FORMAT DETECTION TESTS

Mínimo:

```text
test_extension_detection
test_magic_byte_detection
test_header_detection
test_container_detection
test_detection_priority
test_detection_conflict
test_unknown_format
test_format_registry
test_duplicate_format
test_detection_determinism
```

---

# 124. PROFILE TESTS

Mínimo:

```text
test_profile_registration
test_profile_resolution
test_default_profile
test_profile_override
test_profile_validation
test_profile_version
test_profile_migration
test_settings_serialization
test_settings_fingerprint
```

---

# 125. PROCESSOR TESTS

Mínimo:

```text
test_processor_registration
test_processor_resolution
test_processor_can_process
test_processor_prepare
test_processor_process
test_processor_finalize
test_processor_cancel
test_processor_version
test_processor_failure
test_processor_isolation
```

---

# 126. GRAPH TESTS

Mínimo:

```text
test_graph_creation
test_graph_node
test_graph_edge
test_graph_validation
test_graph_cycle_detection
test_graph_type_mismatch
test_graph_missing_node
test_graph_duplicate_node
test_graph_topological_order
test_graph_parallel_nodes
test_graph_failure_propagation
test_graph_determinism
```

---

# 127. JOB TESTS

Mínimo:

```text
test_job_creation
test_job_queue
test_job_priority
test_job_tie_breaker
test_job_cancel_queued
test_job_cancel_running
test_job_state_machine
test_job_progress
test_job_logging
test_job_retry
test_job_recovery
test_job_resume
```

---

# 128. WORKER TESTS

Mínimo:

```text
test_worker_start
test_worker_stop
test_worker_execute
test_worker_failure
test_worker_requeue
test_worker_limit
test_worker_pool
test_worker_cleanup
```

---

# 129. DEPENDENCY TESTS

Mínimo:

```text
test_dependency_order
test_dependency_available
test_dependency_missing
test_dependency_outdated
test_dependency_processing
test_dependency_failure
test_dependency_cycle
test_dependency_fingerprint
test_dependency_determinism
```

---

# 130. CACHE TESTS

Mínimo:

```text
test_cache_key
test_cache_hit
test_cache_miss
test_cache_invalidation
test_cache_version
test_cache_corruption
test_cache_equivalence
test_cache_cleanup
```

---

# 131. ARTIFACT TESTS

Mínimo:

```text
test_artifact_creation
test_artifact_identity
test_artifact_hash
test_artifact_atomic_publish
test_partial_output_rejection
test_manifest
test_manifest_determinism
test_artifact_cleanup
```

---

# 132. INCREMENTAL PROCESSING TESTS

Mínimo:

```text
test_incremental_no_change
test_incremental_source_change
test_incremental_settings_change
test_incremental_processor_change
test_incremental_dependency_change
test_incremental_profile_change
test_incremental_cache_hit
test_incremental_equivalence
```

---

# 133. ERROR/RECOVERY TESTS

Mínimo:

```text
test_source_failure
test_processor_failure
test_output_failure
test_retry
test_retry_limit
test_backoff
test_cancel
test_resume
test_checkpoint_validation
test_worker_failure_recovery
test_queue_recovery
test_cache_recovery
```

---

# 134. BATCH IMPORT TESTS

Mínimo:

```text
test_batch_import
test_batch_fail_fast
test_batch_continue
test_batch_atomic
test_batch_progress
test_batch_cancel
test_batch_retry
```

---

# 135. COMMAND TESTS

Mínimo:

```text
test_import_command
test_reimport_command
test_cancel_import_command
test_retry_import_command
test_clear_error_command
test_rebuild_artifacts_command
test_command_validation
test_command_undo_redo
```

---

# 136. UI TESTS

Mínimo:

```text
test_import_queue_ui
test_import_progress_ui
test_import_error_ui
test_import_retry_ui
test_import_cancel_ui
test_import_profile_ui
test_import_processor_ui
test_browser_status_update
test_inspector_status_update
```

---

# 137. SECURITY TESTS

Mínimo:

```text
test_path_traversal
test_symlink_escape
test_oversized_input
test_memory_exhaustion
test_disk_exhaustion
test_job_flood
test_dependency_explosion
test_malicious_metadata
test_malicious_archive
test_unsafe_output_path
test_processor_isolation
test_invalid_profile
test_invalid_graph
test_invalid_checkpoint
test_cache_poisoning
test_manifest_tampering
test_replay_tampering
```

---

# 138. PERFORMANCE TESTS

Mínimo:

```text
test_1k_jobs
test_10k_jobs
test_large_asset
test_large_dependency_graph
test_large_processing_graph
test_large_cache
test_large_batch_import
test_incremental_import
test_parallel_workers
test_queue_throughput
test_search_status_updates
test_manifest_generation
test_rebuild
test_recovery
```

---

# 139. STRESS TESTS

Mínimo:

```text
rapid_enqueue
rapid_cancel
rapid_retry
rapid_reprioritize
rapid_worker_restart
rapid_catalog_changes
rapid_dependency_changes
rapid_cache_invalidation
rapid_profile_changes
rapid_import_requests
rapid_ui_updates
rapid_recovery
```

---

# 140. PROPERTY-BASED TESTS

Deberán verificarse propiedades:

```text
rebuild(source) == incremental(source_without_change)
cache_hit(source) == process(source)
retry(process) preserves input fingerprint
cancel(job) does not publish partial artifact
topological_order(graph) respects dependencies
same_inputs → same_fingerprint
same_fingerprint → equivalent_outputs
```

---

# 141. GOLDEN TESTS

Mínimo:

```text
GOLDEN_IMPORT_IMAGE
GOLDEN_IMPORT_MODEL
GOLDEN_IMPORT_MATERIAL
GOLDEN_IMPORT_SCENE
GOLDEN_IMPORT_AUDIO
GOLDEN_IMPORT_DATA
GOLDEN_IMPORT_ERROR
GOLDEN_IMPORT_PROGRESS
GOLDEN_IMPORT_QUEUE
GOLDEN_IMPORT_DEPENDENCIES
GOLDEN_IMPORT_RETRY
GOLDEN_IMPORT_CANCELLED
GOLDEN_IMPORT_INSPECTOR
GOLDEN_IMPORT_BROWSER
GOLDEN_IMPORT_DARK_THEME
```

---

# 142. REPLAY TESTS

Mínimo:

```text
test_import_replay
test_replay_same_fingerprint
test_replay_same_manifest
test_replay_output_equivalence
```

---

# 143. INTEGRATION TESTS

Mínimo:

```text
test_browser_import_integration
test_inspector_import_integration
test_catalog_import_integration
test_search_index_import_integration
test_command_import_integration
test_viewport_import_integration
test_ui_import_integration
test_cache_catalog_integration
test_dependency_catalog_integration
test_import_replay_integration
```

---

# 144. CLEANUP TESTS

Mínimo:

```text
test_job_cleanup
test_worker_cleanup
test_processor_cleanup
test_temp_file_cleanup
test_cache_cleanup
test_checkpoint_cleanup
test_subscription_cleanup
test_import_ui_cleanup
test_failed_job_cleanup
```

---

# 145. OBSERVABILITY

Deberán exponerse:

```text
queued_jobs
running_jobs
completed_jobs
failed_jobs
cancelled_jobs
worker_count
worker_utilization
average_job_latency
processor_latency
cache_hit_rate
retry_count
failure_count
throughput
```

---

# 146. MEMORY TELEMETRY

Mínimo:

```text
queue_memory
worker_memory
cache_memory
processor_memory
artifact_memory
dependency_graph_memory
```

---

# 147. ACCEPTANCE CRITERIA

UAF-81.70 estará completa únicamente cuando:

```text
SOURCE IDENTITY IMPLEMENTED
SOURCE NORMALIZATION IMPLEMENTED
FORMAT DETECTION IMPLEMENTED
FORMAT REGISTRY IMPLEMENTED
IMPORT PROFILES IMPLEMENTED
PROFILE RESOLUTION IMPLEMENTED
PROFILE VERSIONING IMPLEMENTED
PROCESSOR REGISTRY IMPLEMENTED
PROCESSOR CONTRACT IMPLEMENTED
PROCESSING GRAPH IMPLEMENTED
GRAPH VALIDATION IMPLEMENTED
GRAPH TOPOLOGICAL ORDER IMPLEMENTED
JOB MODEL IMPLEMENTED
JOB QUEUE IMPLEMENTED
JOB PRIORITY IMPLEMENTED
JOB CANCELLATION IMPLEMENTED
WORKER POOL IMPLEMENTED
RESOURCE LIMITS IMPLEMENTED
BACKPRESSURE IMPLEMENTED
DEPENDENCY PROCESSING IMPLEMENTED
INCREMENTAL PROCESSING IMPLEMENTED
PROCESS CACHE IMPLEMENTED
CACHE INVALIDATION IMPLEMENTED
ARTIFACT MODEL IMPLEMENTED
ATOMIC OUTPUT PUBLISHING IMPLEMENTED
IMPORT MANIFEST IMPLEMENTED
PROGRESS IMPLEMENTED
ERROR MODEL IMPLEMENTED
RETRY IMPLEMENTED
RECOVERY IMPLEMENTED
CHECKPOINT/RESUME IMPLEMENTED
BATCH IMPORT IMPLEMENTED
IMPORT COMMANDS IMPLEMENTED
BROWSER INTEGRATION IMPLEMENTED
INSPECTOR INTEGRATION IMPLEMENTED
VIEWPORT INTEGRATION IMPLEMENTED
SECURITY BOUNDARIES IMPLEMENTED
DETERMINISTIC PROCESSING IMPLEMENTED
REPLAY IMPLEMENTED
GOLDEN TESTS IMPLEMENTED
UNIT TESTS IMPLEMENTED
PROPERTY TESTS IMPLEMENTED
INTEGRATION TESTS IMPLEMENTED
PERFORMANCE TESTS IMPLEMENTED
STRESS TESTS IMPLEMENTED
SECURITY TESTS IMPLEMENTED
CLEANUP TESTS IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 148. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
7 SOURCE
10 FORMAT
9 PROFILE
10 PROCESSOR
12 GRAPH
12 JOB
8 WORKER
9 DEPENDENCY
8 CACHE
8 ARTIFACT
8 INCREMENTAL
12 ERROR/RECOVERY
7 BATCH
8 COMMAND
9 UI
17 SECURITY
14 PERFORMANCE
12 STRESS
7 PROPERTY_BASED
15 GOLDEN
4 REPLAY
10 INTEGRATION
9 CLEANUP
```

**Total mínimo: 229 tests.**

---

# 149. CROSS-PHASE TEST REQUIREMENT

La suite acumulada deberá verificar:

```text
UAF-81.64
RUNTIME
      ↓
UAF-81.65
COMMANDS / INPUT
      ↓
UAF-81.66
UI
      ↓
UAF-81.67
VIEWPORT
      ↓
UAF-81.68
INSPECTOR
      ↓
UAF-81.69
BROWSER / CATALOG
      ↓
UAF-81.70
IMPORT PIPELINE
```

y deberá garantizar:

```text
catalog ↔ import
browser ↔ import status
inspector ↔ import status
commands ↔ import jobs
viewport ↔ imported assets
cache ↔ catalog
dependencies ↔ processing graph
replay ↔ deterministic processing
```

---

# 150. NON-NEGOTIABLE INVARIANTS

```text
NO DUPLICATE SOURCE IDENTITY
NO UNSUPPORTED FORMAT SILENT ACCEPTANCE
NO INVALID PROFILE EXECUTION
NO INVALID GRAPH EXECUTION
NO GRAPH CYCLES
NO NON-DETERMINISTIC JOB ORDER
NO LOST JOB AFTER WORKER FAILURE
NO PARTIAL ARTIFACT PUBLICATION
NO CACHE RESULT WITHOUT VALID FINGERPRINT
NO STALE CACHE AFTER DEPENDENCY CHANGE
NO DEPENDENCY CYCLE
NO UNSAFE OUTPUT PATH
NO PATH TRAVERSAL
NO RESOURCE LIMIT BYPASS
NO SILENT PROCESSOR FAILURE
NO UNCONTROLLED RETRY LOOP
NO CHECKPOINT REUSE AFTER INCOMPATIBLE CHANGE
NO REPLAY DIVERGENCE
NO TEMPORARY RESOURCE LEAK
NO CROSS-PHASE STATE BYPASS
```

---

# 151. NEXT PHASE

```text
UAF-81.71 — UNIVERSAL ASSET PROCESSING PRODUCTS, DERIVED RESOURCE GENERATION, TEXTURE/MESH/AUDIO PROCESSING, MATERIAL COMPILATION, SHADER PIPELINE, LOD GENERATION, COMPRESSION, OPTIMIZATION, PLATFORM VARIANTS, BUILD ARTIFACTS & PROCESSOR TESTING SYSTEM
```
