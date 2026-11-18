# UAF-81.69 — UNIVERSAL ASSET BROWSER, RESOURCE CATALOG, SEARCH INDEX, FILTERING, TAGGING, COLLECTIONS, FAVORITES, RECENT ITEMS, PREVIEW SYSTEM, THUMBNAILS, IMPORT STATUS, ASSET DISCOVERY & BROWSER TESTING SYSTEM

## UAF-81.69-ARCH

### ARQUITECTURA NORMATIVA DEL EXPLORADOR UNIVERSAL DE ACTIVOS, CATÁLOGO DE RECURSOS, ÍNDICE DE BÚSQUEDA, FILTRADO, ETIQUETAS, COLECCIONES, FAVORITOS, ELEMENTOS RECIENTES, SISTEMA DE PREVISUALIZACIÓN, MINIATURAS, ESTADO DE IMPORTACIÓN, DESCUBRIMIENTO DE ACTIVOS Y PRUEBAS DE EXPLORADOR

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.69 — Universal Asset Browser, Resource Catalog, Search Index, Filtering, Tagging, Collections, Favorites, Recent Items, Preview System, Thumbnails, Import Status, Asset Discovery & Browser Testing System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.68  
**Next Phase:** UAF-81.70  

---

# 1. PURPOSE

UAF-81.69 define el sistema universal de descubrimiento, catalogación y navegación de assets y recursos.

La fase deberá proporcionar:

```text
RESOURCE CATALOG
ASSET IDENTITY
ASSET METADATA
RESOURCE INDEX
SEARCH INDEX
FULL-TEXT SEARCH
STRUCTURED SEARCH
FILTER SYSTEM
SORT SYSTEM
TAG SYSTEM
COLLECTION SYSTEM
FAVORITES
RECENT ITEMS
HISTORY
ASSET BROWSER
TREE VIEW
GRID VIEW
LIST VIEW
VIRTUALIZATION
THUMBNAILS
PREVIEWS
PREVIEW CACHE
IMPORT STATUS
PROCESSING STATUS
ERROR STATUS
DEPENDENCY STATUS
ASSET HEALTH
ASSET DISCOVERY
ASSET REFRESH
ASSET INVALIDATION
ASSET WATCHING
BROWSER COMMANDS
BROWSER SELECTION
BROWSER DRAG/DROP
BROWSER CONTEXT ACTIONS
INSPECTOR INTEGRATION
VIEWPORT INTEGRATION
SEARCH TESTING
BROWSER TESTING
```

---

# 2. ARCHITECTURAL PIPELINE

```text
FILES / RESOURCES
      ↓
DISCOVERY
      ↓
IDENTITY
      ↓
CATALOG
      ↓
METADATA EXTRACTION
      ↓
INDEXING
      ↓
SEARCH
      ↓
FILTER
      ↓
SORT
      ↓
BROWSER MODEL
      ↓
VIRTUALIZED UI
      ↓
PREVIEW / THUMBNAIL
      ↓
INSPECTOR / VIEWPORT
```

---

# 3. RESOURCE CATALOG

Deberá existir un catálogo central de assets.

```text
ResourceCatalog
```

---

# 4. CATALOG RESPONSIBILITY

El catálogo deberá resolver:

```text
asset_id
resource_type
source
metadata
status
dependencies
preview_state
```

---

# 5. ASSET IDENTITY

Cada asset deberá poseer identidad estable.

Mínimo:

```text
asset_id
canonical_path
resource_type
identity_version
```

---

# 6. CANONICAL PATH

Las rutas deberán normalizarse antes de indexarse.

---

# 7. PATH NORMALIZATION

Deberá definirse comportamiento para:

```text
separator
case
relative segments
duplicate separators
unicode normalization
reserved names
```

---

# 8. DUPLICATE IDENTITY

El sistema deberá detectar identidades duplicadas.

---

# 9. CATALOG ENTRY

Mínimo:

```text
asset_id
path
type
size
timestamp
hash
metadata
tags
status
```

---

# 10. CATALOG STATES

Mínimo:

```text
DISCOVERED
INDEXING
READY
MODIFIED
PROCESSING
ERROR
MISSING
DELETED
```

---

# 11. CATALOG VERSIONING

Las entradas deberán poder detectar cambios.

---

# 12. CHANGE DETECTION

Deberá soportarse detección por:

```text
timestamp
size
content_hash
source_revision
```

cuando estén disponibles.

---

# 13. ASSET HASH

El hash deberá ser determinista.

---

# 14. CATALOG UPDATE

Los cambios deberán poder aplicarse incrementalmente.

---

# 15. CATALOG TRANSACTION

Una actualización múltiple del catálogo deberá poder ejecutarse de forma transaccional.

---

# 16. CATALOG CONSISTENCY

No deberán existir entradas parcialmente actualizadas.

---

# 17. RESOURCE TYPES

El catálogo deberá permitir tipos extensibles.

Ejemplos:

```text
MODEL
MATERIAL
TEXTURE
ANIMATION
AUDIO
SCENE
PREFAB
SCRIPT
FONT
SHADER
DATA
```

---

# 18. TYPE REGISTRY

Los tipos deberán registrarse mediante un registry estable.

---

# 19. TYPE FILTERING

El browser deberá poder filtrar por tipo.

---

# 20. METADATA

Los assets podrán exponer:

```text
name
author
description
dimensions
duration
vertex_count
memory_size
format
version
```

según tipo.

---

# 21. METADATA EXTRACTION

La extracción deberá ser desacoplada del browser.

---

# 22. METADATA FAILURE

Un fallo de metadata no deberá destruir la entrada principal del catálogo.

---

# 23. SEARCH INDEX

Deberá existir un índice dedicado a búsqueda.

---

# 24. INDEXED FIELDS

Mínimo:

```text
name
path
type
tags
description
metadata
```

---

# 25. FULL-TEXT SEARCH

Deberá soportarse búsqueda textual.

---

# 26. TOKENIZATION

La tokenización deberá ser determinista.

---

# 27. CASE NORMALIZATION

La búsqueda deberá definir sensibilidad a mayúsculas/minúsculas.

---

# 28. DIACRITICS

Deberá definirse normalización de diacríticos.

---

# 29. PREFIX SEARCH

Deberá soportarse búsqueda por prefijo.

---

# 30. FUZZY SEARCH

Podrá soportarse búsqueda aproximada, pero su algoritmo deberá ser determinista.

---

# 31. SEARCH RANKING

Cuando existan múltiples resultados, el ranking deberá ser determinista.

---

# 32. SEARCH PRIORITY

Una política posible:

```text
EXACT_NAME
PREFIX_NAME
NAME_TOKEN
PATH_TOKEN
TAG
DESCRIPTION
METADATA
```

---

# 33. SEARCH QUERY

La query deberá poder representar:

```text
text
type
tag
path
status
size
date
```

---

# 34. STRUCTURED QUERY

Ejemplo conceptual:

```text
type:model tag:environment status:ready
```

---

# 35. QUERY PARSER

El parser deberá rechazar sintaxis inválida de forma segura.

---

# 36. QUERY NORMALIZATION

Queries equivalentes deberán producir una representación normalizada.

---

# 37. SEARCH CANCELLATION

Las búsquedas deberán poder cancelarse.

---

# 38. SEARCH PAGINATION

Deberá soportarse paginación.

---

# 39. SEARCH CURSOR

Cuando se utilicen cursores, deberán ser estables durante una consulta determinada.

---

# 40. SEARCH LIMIT

El límite de resultados deberá estar controlado.

---

# 41. SEARCH RESULT

Mínimo:

```text
asset_id
score
matched_fields
```

---

# 42. FILTER SYSTEM

Deberá existir un sistema de filtros independiente.

---

# 43. FILTER TYPES

Mínimo:

```text
TYPE
TAG
PATH
STATUS
SIZE
DATE
FAVORITE
RECENT
```

---

# 44. FILTER COMPOSITION

Deberá soportarse:

```text
AND
OR
NOT
```

---

# 45. FILTER DETERMINISM

La misma entrada deberá producir los mismos resultados.

---

# 46. SORT SYSTEM

Deberá soportarse:

```text
NAME
PATH
TYPE
SIZE
DATE
STATUS
```

---

# 47. SORT DIRECTION

```text
ASCENDING
DESCENDING
```

---

# 48. SORT TIE BREAKER

Siempre deberá existir un tie-breaker determinista.

Ejemplo:

```text
primary_field
 ↓
canonical_path
 ↓
asset_id
```

---

# 49. TAG SYSTEM

Deberá existir tagging.

---

# 50. TAG IDENTITY

Cada tag deberá tener identificador estable.

---

# 51. TAG NAME

El nombre visual podrá diferir del identificador interno.

---

# 52. TAG ASSIGNMENT

Un asset podrá poseer múltiples tags.

---

# 53. TAG REMOVAL

Deberá poder retirarse un tag.

---

# 54. TAG VALIDATION

Deberán validarse:

```text
empty
duplicate
reserved
invalid characters
```

---

# 55. TAG GROUPS

Podrán existir grupos/categorías de tags.

---

# 56. TAG SEARCH

El browser deberá poder filtrar por tags.

---

# 57. COLLECTION SYSTEM

Deberán existir colecciones.

---

# 58. COLLECTION TYPES

Mínimo:

```text
STATIC
SMART
```

---

# 59. STATIC COLLECTION

Contendrá referencias explícitas a assets.

---

# 60. SMART COLLECTION

Contendrá una query/filtro persistente.

---

# 61. COLLECTION ID

Deberá ser estable.

---

# 62. COLLECTION ORDER

El orden de colecciones deberá ser determinista.

---

# 63. COLLECTION NESTING

Si se permite nesting, deberá evitarse:

```text
cycle
self-reference
duplicate ownership
```

---

# 64. FAVORITES

Deberá existir sistema de favoritos.

---

# 65. FAVORITE STATE

El favorito deberá asociarse a `asset_id`, no a una posición visual.

---

# 66. RECENT ITEMS

Deberá existir lista de recientes.

---

# 67. RECENT ORDER

El orden deberá ser:

```text
most_recent → oldest
```

con tie-breaker determinista.

---

# 68. RECENT LIMIT

Deberá existir límite configurable.

---

# 69. HISTORY

Podrá existir historial de navegación.

---

# 70. HISTORY STATES

Mínimo:

```text
BACK
FORWARD
```

---

# 71. BROWSER MODEL

El browser deberá poseer modelo independiente de la UI.

---

# 72. BROWSER VIEWS

Mínimo:

```text
TREE
LIST
GRID
```

---

# 73. TREE VIEW

Deberá mostrar jerarquía de carpetas/colecciones.

---

# 74. LIST VIEW

Deberá mostrar columnas configurables.

---

# 75. GRID VIEW

Deberá mostrar:

```text
thumbnail
name
status
```

cuando corresponda.

---

# 76. VIRTUALIZATION

La UI deberá virtualizar grandes cantidades de elementos.

---

# 77. VIRTUALIZATION TEST

Deberá garantizarse que:

```text
visible_items
```

no dependa de la cantidad total de assets de manera lineal en memoria visual.

---

# 78. BROWSER SELECTION

Deberá reutilizar las reglas de selección definidas anteriormente.

---

# 79. MULTI-SELECTION

Deberá soportarse selección múltiple.

---

# 80. RANGE SELECTION

Deberá soportarse selección por rango cuando el orden sea estable.

---

# 81. SEARCH SELECTION

Una búsqueda no deberá destruir la selección global salvo política explícita.

---

# 82. BROWSER DRAG/DROP

Deberá soportar operaciones como:

```text
asset → viewport
asset → inspector
asset → collection
asset → folder
```

cuando sean válidas.

---

# 83. DRAG VALIDATION

Antes de aceptar drop deberá validarse compatibilidad.

---

# 84. DRAG PREVIEW

Deberá existir representación visual del destino.

---

# 85. CONTEXT MENU

Las acciones deberán depender de:

```text
selection
asset_type
permissions
status
```

---

# 86. BROWSER COMMANDS

Mínimo:

```text
Open
Inspect
Rename
Delete
Duplicate
Favorite
Tag
AddToCollection
Refresh
Reveal
Import
Retry
```

según permisos/capacidades.

---

# 87. COMMAND VALIDATION

Las acciones inválidas deberán rechazarse antes de modificar estado.

---

# 88. RENAME

El rename deberá mantener identidad o actualizarla según política explícita.

---

# 89. DELETE

El delete deberá distinguir:

```text
remove_from_catalog
delete_source
```

---

# 90. DUPLICATE

Duplicar deberá producir nueva identidad.

---

# 91. IMPORT STATUS

El browser deberá mostrar estados de importación.

---

# 92. IMPORT STATES

Mínimo:

```text
QUEUED
IMPORTING
PROCESSING
READY
FAILED
CANCELLED
```

---

# 93. PROCESSING PROGRESS

Cuando sea posible deberá mostrarse progreso.

---

# 94. ERROR STATUS

Los errores deberán poder inspeccionarse.

---

# 95. RETRY

Los procesos fallidos deberán poder reintentarse cuando sean recuperables.

---

# 96. ASSET HEALTH

Deberá existir un estado de salud:

```text
HEALTHY
WARNING
ERROR
MISSING
OUTDATED
```

---

# 97. DEPENDENCY STATUS

El browser podrá indicar dependencias faltantes o inválidas.

---

# 98. THUMBNAIL SYSTEM

Deberá existir generación de thumbnails.

---

# 99. THUMBNAIL TYPES

Según recurso:

```text
IMAGE
MODEL
MATERIAL
SCENE
AUDIO
GENERIC
```

---

# 100. THUMBNAIL SIZE

Deberán existir tamaños configurables.

---

# 101. THUMBNAIL CACHE

Las thumbnails deberán cachearse.

---

# 102. CACHE KEY

La key deberá considerar como mínimo:

```text
asset_id
content_hash/version
thumbnail_size
render_settings
```

---

# 103. CACHE INVALIDATION

Un cambio relevante deberá invalidar la thumbnail.

---

# 104. CACHE FAILURE

Un fallo de thumbnail no deberá impedir navegar por el asset.

---

# 105. PLACEHOLDER

Deberá existir thumbnail placeholder.

---

# 106. PREVIEW SYSTEM

Deberá existir preview de assets.

---

# 107. PREVIEW MODES

Mínimo:

```text
STATIC
INTERACTIVE
METADATA
```

según tipo.

---

# 108. PREVIEW LIFECYCLE

```text
REQUESTED
LOADING
READY
FAILED
CANCELLED
```

---

# 109. PREVIEW CANCELLATION

Las previews fuera de pantalla deberán poder cancelarse.

---

# 110. PREVIEW CACHE

Deberá existir cache independiente de thumbnails.

---

# 111. PREVIEW RESOURCE LIMIT

Deberá existir límite de previews simultáneas.

---

# 112. PREVIEW SECURITY

Los previews deberán ejecutarse dentro de los límites de seguridad definidos por el runtime.

---

# 113. ASSET DISCOVERY

El sistema deberá descubrir assets nuevos.

---

# 114. WATCHERS

Cuando el entorno lo permita, deberá soportarse filesystem watching.

---

# 115. WATCHER EVENTS

Mínimo:

```text
CREATED
MODIFIED
DELETED
RENAMED
```

---

# 116. EVENT DEBOUNCE

Eventos repetidos podrán agruparse.

---

# 117. WATCHER FAILURE

Si el watcher falla, deberá existir fallback mediante rescan.

---

# 118. FULL RESCAN

Deberá existir operación de rescan completo.

---

# 119. INCREMENTAL RESCAN

Deberá existir rescan parcial por scope.

---

# 120. DISCOVERY DETERMINISM

El mismo conjunto de fuentes deberá producir el mismo catálogo lógico.

---

# 121. BROWSER REFRESH

Refresh deberá poder ejecutarse:

```text
current folder
current collection
current search
entire catalog
```

---

# 122. SEARCH INDEX REBUILD

Deberá existir reconstrucción completa del índice.

---

# 123. INDEX RECOVERY

Un índice corrupto deberá poder reconstruirse desde el catálogo.

---

# 124. INDEX VERSION

El índice deberá tener versión compatible.

---

# 125. INDEX MIGRATION

Cambios incompatibles deberán disparar migración o rebuild.

---

# 126. BROWSER PERSISTENCE

Podrá persistirse:

```text
current_location
view_mode
sort
filters
search
expanded_tree
favorites
collections
```

---

# 127. EPHEMERAL STATE

No deberá persistirse automáticamente:

```text
hover
active_drag
temporary_preview
pointer_capture
```

---

# 128. INSPECTOR INTEGRATION

Seleccionar un asset deberá poder actualizar el inspector.

---

# 129. VIEWPORT INTEGRATION

Los assets compatibles podrán abrirse/instanciarse en viewport mediante comandos.

---

# 130. ASSET OPEN

Abrir deberá delegar en el editor apropiado.

---

# 131. ASSET DOUBLE CLICK

La acción deberá ser configurable por tipo.

---

# 132. ASSET CONTEXT ACTIONS

El menú contextual deberá ser extensible.

---

# 133. BROWSER ACCESSIBILITY

Deberá soportarse:

```text
keyboard navigation
screen-reader labels
focus
selection announcement
status announcement
```

---

# 134. KEYBOARD NAVIGATION

Mínimo:

```text
ARROWS
ENTER
ESCAPE
HOME
END
PAGE_UP
PAGE_DOWN
```

según view.

---

# 135. SEARCH ACCESSIBILITY

La búsqueda deberá anunciar:

```text
result_count
no_results
search_error
```

---

# 136. STATUS ACCESSIBILITY

Estados de error/warning deberán ser accesibles sin depender únicamente del color.

---

# 137. BROWSER TESTING SYSTEM

La fase deberá incorporar una suite dedicada.

---

# 138. CATALOG TESTS

Mínimo:

```text
test_catalog_insert
test_catalog_update
test_catalog_remove
test_catalog_duplicate
test_catalog_transaction
test_catalog_consistency
test_catalog_hash
test_catalog_version
test_catalog_state
test_catalog_recovery
```

---

# 139. IDENTITY TESTS

Mínimo:

```text
test_asset_identity
test_canonical_path
test_path_normalization
test_duplicate_identity
test_unicode_path
test_case_policy
```

---

# 140. SEARCH TESTS

Mínimo:

```text
test_exact_search
test_prefix_search
test_token_search
test_path_search
test_tag_search
test_full_text
test_case_normalization
test_diacritic_normalization
test_fuzzy_search
test_search_ranking
test_structured_query
test_invalid_query
test_search_cancel
test_search_pagination
test_search_determinism
```

---

# 141. FILTER TESTS

Mínimo:

```text
test_type_filter
test_tag_filter
test_path_filter
test_status_filter
test_size_filter
test_date_filter
test_favorite_filter
test_recent_filter
test_and_filter
test_or_filter
test_not_filter
test_filter_determinism
```

---

# 142. SORT TESTS

Mínimo:

```text
test_sort_name
test_sort_path
test_sort_type
test_sort_size
test_sort_date
test_sort_status
test_sort_ascending
test_sort_descending
test_sort_tie_breaker
```

---

# 143. TAG TESTS

Mínimo:

```text
test_tag_create
test_tag_assign
test_tag_remove
test_duplicate_tag
test_invalid_tag
test_empty_tag
test_tag_search
test_tag_group
```

---

# 144. COLLECTION TESTS

Mínimo:

```text
test_static_collection
test_smart_collection
test_collection_id
test_collection_order
test_collection_membership
test_collection_query
test_collection_cycle_rejection
test_collection_persistence
```

---

# 145. FAVORITE/RECENT TESTS

Mínimo:

```text
test_favorite
test_unfavorite
test_favorite_filter
test_recent_add
test_recent_order
test_recent_limit
test_recent_duplicate
test_recent_persistence
```

---

# 146. BROWSER MODEL TESTS

Mínimo:

```text
test_tree_view
test_list_view
test_grid_view
test_view_switch
test_browser_selection
test_multi_selection
test_range_selection
test_search_selection
test_browser_state
test_browser_snapshot
```

---

# 147. VIRTUALIZATION TESTS

Mínimo:

```text
test_virtualized_list
test_virtualized_grid
test_large_catalog
test_scroll_virtualization
test_item_reuse
test_virtualization_selection
test_virtualization_focus
```

---

# 148. THUMBNAIL TESTS

Mínimo:

```text
test_thumbnail_request
test_thumbnail_generation
test_thumbnail_cache
test_thumbnail_cache_key
test_thumbnail_invalidation
test_thumbnail_placeholder
test_thumbnail_failure
test_thumbnail_cancel
```

---

# 149. PREVIEW TESTS

Mínimo:

```text
test_preview_request
test_preview_loading
test_preview_ready
test_preview_failure
test_preview_cancel
test_preview_cache
test_preview_limit
test_preview_invalidation
```

---

# 150. DISCOVERY TESTS

Mínimo:

```text
test_discovery_new_asset
test_discovery_modified_asset
test_discovery_deleted_asset
test_discovery_renamed_asset
test_watcher
test_watcher_debounce
test_watcher_failure
test_full_rescan
test_incremental_rescan
test_discovery_determinism
```

---

# 151. IMPORT STATUS TESTS

Mínimo:

```text
test_import_queued
test_importing
test_import_processing
test_import_ready
test_import_failed
test_import_cancelled
test_import_retry
test_import_progress
```

---

# 152. COMMAND TESTS

Mínimo:

```text
test_open_command
test_inspect_command
test_rename_command
test_delete_command
test_duplicate_command
test_favorite_command
test_tag_command
test_collection_command
test_refresh_command
test_retry_command
```

---

# 153. DRAG/DROP TESTS

Mínimo:

```text
test_asset_to_viewport
test_asset_to_inspector
test_asset_to_collection
test_asset_to_folder
test_invalid_drop
test_drag_preview
test_drag_cancel
```

---

# 154. ACCESSIBILITY TESTS

Mínimo:

```text
test_browser_focus
test_keyboard_navigation
test_screen_reader_name
test_selection_announcement
test_result_count
test_error_announcement
test_status_without_color
```

---

# 155. INTEGRATION TESTS

Mínimo:

```text
test_browser_inspector
test_browser_viewport
test_browser_commands
test_browser_undo_redo
test_browser_catalog
test_browser_search_index
test_browser_theme
test_browser_accessibility
test_browser_replay
test_browser_external_change
```

---

# 156. GOLDEN TESTS

Mínimo:

```text
GOLDEN_EMPTY_BROWSER
GOLDEN_TREE
GOLDEN_LIST
GOLDEN_GRID
GOLDEN_SEARCH
GOLDEN_FILTER
GOLDEN_MULTI_SELECTION
GOLDEN_FAVORITES
GOLDEN_COLLECTION
GOLDEN_THUMBNAILS
GOLDEN_PREVIEW
GOLDEN_IMPORT_PROGRESS
GOLDEN_ERROR
GOLDEN_MISSING_ASSET
GOLDEN_DARK_THEME
GOLDEN_HIGH_DPI
```

---

# 157. REPLAY TESTS

Deberá poder reproducirse:

```text
open_browser
search
filter
select
open_inspector
drag_asset
open_viewport
favorite
tag
collection
```

y producir el mismo estado final.

---

# 158. PROPERTY-BASED TESTS

Deberán verificarse propiedades:

```text
query(normalize(q)) == query(normalize(q))
sort_deterministic
filter_idempotent
favorite_idempotent
tag_assignment_idempotent
catalog_rebuild_equivalence
index_rebuild_equivalence
recent_order_deterministic
```

---

# 159. PERFORMANCE TESTS

Mínimo:

```text
test_10k_assets
test_100k_assets
test_1m_indexed_entries
test_large_search
test_large_filter
test_large_sort
test_large_tag_set
test_large_collection
test_virtualized_grid
test_thumbnail_cache
test_preview_queue
test_incremental_index
test_full_index_rebuild
test_catalog_rescan
```

---

# 160. STRESS TESTS

Mínimo:

```text
rapid_search
rapid_filter
rapid_selection
rapid_view_switch
rapid_scroll
rapid_thumbnail_requests
rapid_preview_requests
rapid_catalog_changes
rapid_import_updates
rapid_rename
rapid_delete
rapid_refresh
```

---

# 161. SECURITY TESTS

Mínimo:

```text
test_path_traversal
test_malformed_path
test_invalid_unicode
test_oversized_path
test_malicious_metadata
test_malicious_query
test_query_flood
test_search_flood
test_catalog_flood
test_thumbnail_resource_exhaustion
test_preview_resource_exhaustion
test_invalid_asset_type
test_duplicate_identity_injection
test_symlink_policy
test_permission_boundary
test_import_status_spoof
```

---

# 162. CLEANUP TESTS

Mínimo:

```text
test_catalog_cleanup
test_search_index_cleanup
test_search_subscription_cleanup
test_thumbnail_cache_cleanup
test_preview_cleanup
test_watcher_cleanup
test_browser_cleanup
test_selection_cleanup
test_collection_cleanup
```

---

# 163. FAILURE RECOVERY

Deberán probarse:

```text
index corruption
catalog interruption
watcher failure
thumbnail failure
preview failure
import failure
partial scan
```

---

# 164. RECOVERY INVARIANT

Después de recuperación:

```text
source_state
    ↓
rebuild
    ↓
catalog_state
    ↓
index_state
```

deberá ser equivalente al estado esperado.

---

# 165. DETERMINISM

La misma colección de fuentes deberá producir:

```text
same asset IDs
same catalog
same index
same search results
same ordering
same thumbnails keys
same browser state
```

---

# 166. RESOURCE LIMITS

Deberán existir límites configurables para:

```text
search results
preview concurrency
thumbnail concurrency
catalog batch size
index batch size
recent items
collection size
```

---

# 167. BACKPRESSURE

Los sistemas de preview, thumbnail, indexing e import deberán soportar backpressure.

---

# 168. CANCELLATION

Las operaciones largas deberán soportar cancelación donde sea seguro.

---

# 169. OBSERVABILITY

Deberán exponerse:

```text
catalog_size
index_size
search_latency
filter_latency
sort_latency
thumbnail_hit_rate
preview_hit_rate
import_queue_size
watcher_events
```

---

# 170. MEMORY TELEMETRY

Mínimo:

```text
catalog_memory
index_memory
thumbnail_cache_memory
preview_cache_memory
browser_model_memory
collection_memory
```

---

# 171. ACCEPTANCE CRITERIA

UAF-81.69 estará completa únicamente cuando:

```text
RESOURCE CATALOG IMPLEMENTED
ASSET IDENTITY IMPLEMENTED
PATH NORMALIZATION IMPLEMENTED
CATALOG VERSIONING IMPLEMENTED
CHANGE DETECTION IMPLEMENTED
RESOURCE TYPE REGISTRY IMPLEMENTED
METADATA EXTRACTION IMPLEMENTED
SEARCH INDEX IMPLEMENTED
FULL-TEXT SEARCH IMPLEMENTED
STRUCTURED SEARCH IMPLEMENTED
SEARCH RANKING IMPLEMENTED
SEARCH CANCELLATION IMPLEMENTED
SEARCH PAGINATION IMPLEMENTED
FILTER SYSTEM IMPLEMENTED
FILTER COMPOSITION IMPLEMENTED
SORT SYSTEM IMPLEMENTED
DETERMINISTIC TIE-BREAKING IMPLEMENTED
TAG SYSTEM IMPLEMENTED
COLLECTION SYSTEM IMPLEMENTED
SMART COLLECTIONS IMPLEMENTED
FAVORITES IMPLEMENTED
RECENT ITEMS IMPLEMENTED
HISTORY IMPLEMENTED
TREE VIEW IMPLEMENTED
LIST VIEW IMPLEMENTED
GRID VIEW IMPLEMENTED
VIRTUALIZATION IMPLEMENTED
BROWSER SELECTION IMPLEMENTED
DRAG/DROP IMPLEMENTED
CONTEXT ACTIONS IMPLEMENTED
IMPORT STATUS IMPLEMENTED
ASSET HEALTH IMPLEMENTED
THUMBNAIL SYSTEM IMPLEMENTED
THUMBNAIL CACHE IMPLEMENTED
PREVIEW SYSTEM IMPLEMENTED
PREVIEW CACHE IMPLEMENTED
ASSET DISCOVERY IMPLEMENTED
WATCHER IMPLEMENTED
FULL RESCAN IMPLEMENTED
INCREMENTAL RESCAN IMPLEMENTED
INDEX REBUILD IMPLEMENTED
INDEX RECOVERY IMPLEMENTED
INSPECTOR INTEGRATION IMPLEMENTED
VIEWPORT INTEGRATION IMPLEMENTED
ACCESSIBILITY IMPLEMENTED
GOLDEN TESTS IMPLEMENTED
REPLAY TESTS IMPLEMENTED
PROPERTY TESTS IMPLEMENTED
PERFORMANCE TESTS IMPLEMENTED
STRESS TESTS IMPLEMENTED
SECURITY TESTS IMPLEMENTED
CLEANUP TESTS IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 172. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
10 CATALOG
6 IDENTITY
15 SEARCH
12 FILTER
9 SORT
8 TAG
8 COLLECTION
8 FAVORITE/RECENT
10 BROWSER_MODEL
7 VIRTUALIZATION
8 THUMBNAIL
8 PREVIEW
10 DISCOVERY
8 IMPORT
10 COMMAND
7 DRAG/DROP
7 ACCESSIBILITY
10 INTEGRATION
16 GOLDEN
1 REPLAY
8 PROPERTY_BASED
14 PERFORMANCE
12 STRESS
16 SECURITY
9 CLEANUP
```

**Total mínimo: 256 tests.**

---

# 173. CROSS-PHASE TEST REQUIREMENT

La suite acumulada deberá verificar:

```text
UAF-81.64
RUNTIME
      ↓
UAF-81.65
INPUT / COMMANDS
      ↓
UAF-81.66
UI
      ↓
UAF-81.67
VIEWPORT / SCENE
      ↓
UAF-81.68
INSPECTOR / PROPERTIES
      ↓
UAF-81.69
BROWSER / CATALOG / SEARCH
```

con:

```text
determinism
transactionality
cancellation
recovery
undo/redo
replay
accessibility
resource limits
cleanup
```

---

# 174. NON-NEGOTIABLE INVARIANTS

```text
NO DUPLICATE ASSET IDENTITY
NO NON-CANONICAL CATALOG PATH
NO INDEX/CATALOG DIVERGENCE AFTER REBUILD
NO NON-DETERMINISTIC SEARCH ORDER
NO NON-DETERMINISTIC SORT
NO INVALID FILTER COMPOSITION
NO COLLECTION CYCLES
NO INVALID TAG STATE
NO STALE THUMBNAIL AFTER INVALIDATION
NO PREVIEW RESOURCE LEAK
NO WATCHER SUBSCRIPTION LEAK
NO PARTIAL CATALOG TRANSACTION
NO PATH TRAVERSAL
NO UNSAFE PREVIEW EXECUTION
NO BROWSER SELECTION CORRUPTION
NO CROSS-PHASE COMMAND BYPASS
NO REPLAY DIVERGENCE
```

---

# 175. NEXT PHASE

```text
UAF-81.70 — UNIVERSAL ASSET IMPORT PIPELINE, SOURCE PROCESSORS, FORMAT DETECTION, IMPORT PROFILES, PROCESSING GRAPH, JOB QUEUE, WORKER POOL, CACHING, INCREMENTAL PROCESSING, ERROR RECOVERY, DEPENDENCY PROCESSING & IMPORT TESTING SYSTEM
```

La siguiente fase deberá construir:

```text
UAF-81.64 RUNTIME
        ↓
UAF-81.65 COMMANDS / INPUT
        ↓
UAF-81.66 UI
        ↓
UAF-81.67 VIEWPORT
        ↓
UAF-81.68 INSPECTOR
        ↓
UAF-81.69 BROWSER / CATALOG
        ↓
SOURCE DISCOVERY
        ↓
FORMAT DETECTION
        ↓
IMPORT PROFILE
        ↓
PROCESSING GRAPH
        ↓
JOB QUEUE
        ↓
WORKER POOL
        ↓
CACHE
        ↓
DEPENDENCIES
        ↓
ERROR RECOVERY
        ↓
IMPORT TESTS
```
