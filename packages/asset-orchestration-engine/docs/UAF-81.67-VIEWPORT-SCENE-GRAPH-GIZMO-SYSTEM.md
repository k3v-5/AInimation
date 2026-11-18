# UAF-81.67 — UNIVERSAL ASSET VIEWPORT, SCENE GRAPH, CAMERA SYSTEM, TRANSFORM HIERARCHY, SPATIAL INDEXING, SELECTION, GIZMOS, EDITOR INTERACTION, VIEWPORT INPUT & VIEWPORT TESTING SYSTEM

## UAF-81.67-ARCH

### ARQUITECTURA NORMATIVA DEL VIEWPORT UNIVERSAL DE ACTIVOS, GRAFO DE ESCENA, SISTEMA DE CÁMARAS, JERARQUÍA DE TRANSFORMACIONES, INDEXACIÓN ESPACIAL, SELECCIÓN, GIZMOS, INTERACCIÓN DE EDITOR, ENTRADA DE VIEWPORT Y PRUEBAS DE VIEWPORT

**Project:** Asset Orchestration Engine  
**Program:** Universal Asset Factory  
**Phase:** UAF-81.67 — Universal Asset Viewport, Scene Graph, Camera System, Transform Hierarchy, Spatial Indexing, Selection, Gizmos, Editor Interaction, Viewport Input & Viewport Testing System  
**Status:** NORMATIVE  
**Version:** 1.0.0  
**Previous Phase:** UAF-81.66  
**Next Phase:** UAF-81.68  

---

# 1. PURPOSE

UAF-81.67 define el sistema completo de viewport/editor espacial.

La fase deberá proporcionar:

```text
VIEWPORT ROOT
SCENE GRAPH
SCENE NODE
ENTITY REPRESENTATION
TRANSFORM HIERARCHY
LOCAL/WORLD SPACE
CAMERA
PROJECTION
FRUSTUM
VIEWPORT RESIZE
PICKING
RAYCAST
SELECTION
MULTI-SELECTION
HIERARCHICAL SELECTION
MARQUEE SELECTION
GIZMOS
TRANSLATE
ROTATE
SCALE
PIVOT
SNAPPING
GRID
AXIS CONSTRAINTS
TRANSFORM MANIPULATION
SPATIAL INDEX
VISIBILITY
EDITOR OVERLAYS
VIEWPORT INPUT
VIEWPORT COMMANDS
UNDO/REDO INTEGRATION
VIEWPORT RENDERING
DETERMINISTIC REPLAY
VIEWPORT TESTING
```

---

# 2. ARCHITECTURAL PIPELINE

```text
INPUT
 ↓
VIEWPORT EVENT
 ↓
CAMERA / PICK / GIZMO / SELECTION
 ↓
EDITOR COMMAND
 ↓
COMMAND BUS
 ↓
APPLICATION STATE
 ↓
SCENE GRAPH
 ↓
TRANSFORM UPDATE
 ↓
SPATIAL INDEX
 ↓
VIEWPORT INVALIDATION
 ↓
RENDER
```

---

# 3. VIEWPORT ROOT

Cada viewport deberá poseer:

```text
viewport_id
scene_reference
camera_reference
selection_reference
tool_state
overlay_state
viewport_bounds
```

---

# 4. VIEWPORT LIFECYCLE

Estados mínimos:

```text
CREATED
ATTACHED
ACTIVE
SUSPENDED
DETACHED
DESTROYED
```

---

# 5. VIEWPORT OWNERSHIP

Un viewport deberá tener ownership claro sobre:

```text
camera_state
selection_state
tool_state
overlay_state
input_context
```

Los assets y entidades de dominio no deberán ser propiedad del viewport.

---

# 6. MULTIPLE VIEWPORTS

Deberán soportarse múltiples viewports simultáneos.

Ejemplos:

```text
PERSPECTIVE
TOP
FRONT
SIDE
UV
PREVIEW
```

---

# 7. VIEWPORT ISOLATION

Cada viewport deberá poder poseer cámara, selección y herramientas independientes.

---

# 8. SCENE GRAPH

Deberá existir un árbol jerárquico de nodos espaciales.

```text
Scene
 ├── Node
 │    ├── Node
 │    └── Node
 └── Node
```

---

# 9. SCENE NODE

Cada nodo deberá soportar:

```text
node_id
parent_id
children
local_transform
world_transform
visibility
enabled
metadata
```

---

# 10. NODE INVARIANTS

Deberá garantizarse:

```text
NO_SELF_PARENT
NO_CYCLES
ONE_PARENT
UNIQUE_NODE_ID
VALID_ROOT
DETERMINISTIC_CHILD_ORDER
```

---

# 11. NODE MUTATION

Mínimo:

```text
add_node
remove_node
insert_node
move_node
reparent_node
clear_children
```

---

# 12. REPARENTING

Al cambiar el parent deberá existir una política explícita:

```text
KEEP_LOCAL
KEEP_WORLD
```

---

# 13. KEEP WORLD TRANSFORM

Cuando se solicite `KEEP_WORLD`, el sistema deberá calcular el nuevo local transform necesario para preservar la transformación mundial.

---

# 14. TRANSFORM

Cada nodo deberá poseer:

```text
position
rotation
scale
```

---

# 15. TRANSFORM REPRESENTATION

La representación interna deberá evitar ambigüedad de orden de operaciones.

---

# 16. TRANSFORM ORDER

Deberá definirse explícitamente:

```text
LOCAL = TRANSLATION × ROTATION × SCALE
```

o la convención equivalente elegida por el engine.

---

# 17. LOCAL SPACE

El local transform deberá ser relativo al parent.

---

# 18. WORLD SPACE

El world transform deberá derivarse de la cadena de ancestors.

---

# 19. TRANSFORM PROPAGATION

Un cambio de transform de un nodo deberá actualizar los descendientes afectados.

---

# 20. DIRTY TRANSFORM

Mínimo:

```text
LOCAL_DIRTY
WORLD_DIRTY
BOUNDS_DIRTY
SPATIAL_DIRTY
```

---

# 21. TRANSFORM CACHE

Los world transforms deberán poder cachearse.

---

# 22. CACHE INVALIDATION

La invalidación deberá propagarse únicamente a descendientes afectados.

---

# 23. NUMERICAL STABILITY

El sistema deberá definir tolerancias para:

```text
position
rotation
scale
matrix comparison
```

---

# 24. NON-FINITE TRANSFORMS

No deberán aceptarse silenciosamente:

```text
NaN
+INF
-INF
```

---

# 25. ZERO SCALE

El comportamiento de escala cero deberá estar definido.

---

# 26. NEGATIVE SCALE

La escala negativa deberá soportarse o rechazarse explícitamente.

---

# 27. PIVOT

Los objetos deberán poder tener pivot configurable.

---

# 28. PIVOT SPACE

Deberán distinguirse:

```text
LOCAL_PIVOT
WORLD_PIVOT
MEDIAN_PIVOT
CUSTOM_PIVOT
```

---

# 29. CAMERA

Deberá existir un sistema de cámara independiente.

---

# 30. CAMERA STATE

Mínimo:

```text
position
rotation
projection
near_clip
far_clip
viewport_size
```

---

# 31. CAMERA MODES

Mínimo:

```text
PERSPECTIVE
ORTHOGRAPHIC
```

---

# 32. PERSPECTIVE CAMERA

Deberá soportar:

```text
field_of_view
aspect_ratio
near_clip
far_clip
```

---

# 33. ORTHOGRAPHIC CAMERA

Deberá soportar:

```text
orthographic_width
orthographic_height
near_clip
far_clip
```

---

# 34. VIEW MATRIX

Deberá existir cálculo determinista de view matrix.

---

# 35. PROJECTION MATRIX

Deberá existir cálculo determinista de projection matrix.

---

# 36. VIEW-PROJECTION

Deberá existir:

```text
view_projection = projection × view
```

según la convención matemática adoptada.

---

# 37. SCREEN TO WORLD

Deberá existir conversión:

```text
screen_position
 ↓
world_ray
```

---

# 38. WORLD TO SCREEN

Deberá existir conversión:

```text
world_position
 ↓
screen_position
```

---

# 39. DEPTH

La conversión screen/world deberá definir claramente el tratamiento de profundidad.

---

# 40. CAMERA ORBIT

Las cámaras editoriales deberán soportar orbit alrededor de un target.

---

# 41. CAMERA PAN

Deberá soportarse pan.

---

# 42. CAMERA DOLLY

Deberá soportarse dolly/zoom.

---

# 43. CAMERA FLY

Cuando exista modo navegación libre deberá soportarse movimiento relativo a la cámara.

---

# 44. CAMERA FOCUS

Deberá existir una operación para enfocar una selección o bounds.

---

# 45. CAMERA CLAMP

Los límites de cámara configurables deberán aplicarse de forma determinista.

---

# 46. CAMERA INPUT

La navegación de cámara deberá integrarse con UAF-81.65.

---

# 47. FRUSTUM

La cámara deberá poder producir un frustum.

---

# 48. FRUSTUM PLANES

Mínimo:

```text
LEFT
RIGHT
TOP
BOTTOM
NEAR
FAR
```

---

# 49. FRUSTUM CULLING

El renderer deberá poder descartar objetos fuera del frustum.

---

# 50. VISIBILITY

La visibilidad deberá evaluarse mediante:

```text
NODE_VISIBILITY
ANCESTOR_VISIBILITY
LAYER_VISIBILITY
FRUSTUM_VISIBILITY
EDITOR_VISIBILITY
```

---

# 51. LAYERS

Deberán existir capas o categorías de visibilidad.

---

# 52. SPATIAL INDEX

Deberá existir un índice espacial para acelerar:

```text
picking
frustum queries
selection
visibility
```

---

# 53. SPATIAL INDEX OPTIONS

Podrán utilizarse:

```text
AABB_TREE
BVH
OCTREE
GRID
```

La implementación concreta deberá quedar encapsulada.

---

# 54. SPATIAL ENTRY

Cada entrada deberá asociarse a:

```text
node_id
world_bounds
visibility
```

---

# 55. SPATIAL UPDATE

Un cambio de bounds deberá actualizar el índice.

---

# 56. SPATIAL REMOVE

La eliminación de un nodo deberá eliminar su entrada espacial.

---

# 57. SPATIAL QUERY

Deberá soportarse:

```text
query_aabb
query_frustum
query_ray
```

---

# 58. WORLD BOUNDS

Cada nodo renderizable deberá poder proporcionar bounds mundiales.

---

# 59. BOUNDS TYPES

Mínimo:

```text
AABB
SPHERE
OBB
```

cuando el renderer lo requiera.

---

# 60. PICKING

Deberá existir picking determinista.

---

# 61. PICK RAY

El picking deberá comenzar con:

```text
screen_position
 ↓
camera
 ↓
world_ray
```

---

# 62. PICK FILTER

Deberán poder filtrarse:

```text
layers
visibility
editor_only
locked
selectable
```

---

# 63. PICK RESULT

Mínimo:

```text
node_id
distance
world_position
normal
primitive_id
```

cuando estén disponibles.

---

# 64. PICK PRIORITY

La prioridad deberá ser determinista cuando múltiples objetos intersecten el mismo ray.

---

# 65. GIZMO

Deberá existir un sistema de gizmos editoriales.

Tipos mínimos:

```text
TRANSLATE
ROTATE
SCALE
UNIVERSAL
```

---

# 66. GIZMO AXES

Mínimo:

```text
X
Y
Z
XY
XZ
YZ
SCREEN
```

---

# 67. GIZMO STATES

```text
IDLE
HOVERED
ACTIVE
DISABLED
```

---

# 68. GIZMO HIT TEST

Los handles deberán poder seleccionarse mediante hit testing independiente del objeto.

---

# 69. GIZMO PRIORITY

Cuando un gizmo está activo deberá tener prioridad sobre picking de objetos.

---

# 70. TRANSLATE GIZMO

Deberá soportar:

```text
axis constraint
plane constraint
screen-space movement
```

---

# 71. ROTATE GIZMO

Deberá soportar:

```text
axis rotation
view rotation
angle calculation
```

---

# 72. SCALE GIZMO

Deberá soportar:

```text
axis scale
plane scale
uniform scale
```

---

# 73. UNIVERSAL GIZMO

Deberá poder combinar translate, rotate y scale.

---

# 74. GIZMO ORIENTATION

Deberá existir:

```text
LOCAL
WORLD
```

---

# 75. GIZMO PIVOT MODE

Deberá soportarse:

```text
ACTIVE_OBJECT
MEDIAN
INDIVIDUAL
CUSTOM
```

---

# 76. TRANSFORM CONSTRAINTS

Deberán existir restricciones:

```text
AXIS
PLANE
ANGLE
DISTANCE
SCALE
```

---

# 77. GRID

Deberá existir grid configurable.

---

# 78. GRID STATE

Mínimo:

```text
enabled
spacing
subdivisions
orientation
origin
```

---

# 79. SNAP

Deberá existir snapping.

Tipos:

```text
GRID
VERTEX
EDGE
FACE
ANGLE
INCREMENT
```

---

# 80. SNAP SETTINGS

Deberán poder configurarse:

```text
enabled
increment
threshold
mode
```

---

# 81. SNAP DETERMINISM

El resultado del snapping deberá ser determinista para los mismos inputs y estado.

---

# 82. SELECTION

Deberá existir SelectionManager.

---

# 83. SELECTION MODES

Mínimo:

```text
SINGLE
MULTIPLE
TOGGLE
EXTEND
SUBTRACT
```

---

# 84. ACTIVE SELECTION

Deberá existir un elemento activo dentro de una selección múltiple.

---

# 85. SELECTION ORDER

El orden de selección deberá ser determinista.

---

# 86. HIERARCHICAL SELECTION

Deberá poder seleccionarse:

```text
NODE
PARENT
CHILD
INSTANCE
```

según configuración del editor.

---

# 87. MARQUEE SELECTION

Deberá soportarse selección rectangular en viewport.

---

# 88. MARQUEE MODES

Mínimo:

```text
TOUCH
CONTAIN
```

---

# 89. SELECTION FILTER

Deberá poder filtrarse:

```text
selectable
visible
locked
layer
type
```

---

# 90. LOCKED OBJECTS

Un objeto bloqueado deberá permanecer visible pero no seleccionable/modificable según configuración.

---

# 91. SELECTION HIGHLIGHT

Los objetos seleccionados deberán poder recibir overlay visual.

---

# 92. HOVER HIGHLIGHT

El objeto bajo el cursor podrá recibir highlight independiente de selection.

---

# 93. EDITOR OVERLAYS

Deberán existir overlays:

```text
grid
axes
gizmos
selection
hover
bounds
guides
measurements
warnings
```

---

# 94. OVERLAY ORDER

El orden deberá ser:

```text
SCENE
SELECTION
GUIDES
GIZMOS
CURSOR/HOVER
DEBUG
```

o una política equivalente explícitamente definida.

---

# 95. VIEWPORT INPUT

Deberán distinguirse:

```text
CAMERA_INPUT
SELECTION_INPUT
GIZMO_INPUT
NAVIGATION_INPUT
OVERLAY_INPUT
```

---

# 96. INPUT CAPTURE

Un gizmo activo podrá capturar el pointer hasta completar/cancelar la operación.

---

# 97. DRAG OPERATION

Toda operación de transformación interactiva deberá tener:

```text
BEGIN
UPDATE*
COMMIT | CANCEL
```

---

# 98. TRANSFORM TRANSACTION

Una transformación interactiva deberá tratarse como una única operación lógica para undo/redo.

---

# 99. CANCEL TRANSFORM

Cancelar deberá restaurar exactamente el estado previo.

---

# 100. COMMIT TRANSFORM

Confirmar deberá producir un comando de edición persistible/reproducible.

---

# 101. UNDO/REDO

Las operaciones del viewport deberán integrarse con el sistema de comandos.

---

# 102. UNDO TEST

Una transformación deberá poder:

```text
apply
undo
redo
```

sin divergencia.

---

# 103. MULTI-OBJECT TRANSFORM

Deberá soportarse transformación simultánea de múltiples objetos.

---

# 104. MULTI-OBJECT PIVOT

El cálculo deberá respetar el pivot mode configurado.

---

# 105. PARENT/CHILD TRANSFORM

Las transformaciones jerárquicas deberán mantener coherencia entre local y world space.

---

# 106. VIEWPORT RENDERING

El viewport deberá producir una secuencia determinista de:

```text
scene geometry
materials
selection overlays
gizmos
grid
debug overlays
```

---

# 107. RENDER PASSES

Como mínimo deberá existir separación lógica entre:

```text
SCENE_PASS
OVERLAY_PASS
GIZMO_PASS
DEBUG_PASS
```

---

# 108. DEPTH

Los overlays deberán definir explícitamente si utilizan depth testing.

---

# 109. WIREFRAME

Deberá existir soporte de representación wireframe cuando el backend lo permita.

---

# 110. BOUNDS DISPLAY

Deberá poder visualizarse bounds de selección.

---

# 111. NORMAL DISPLAY

Deberá poder visualizarse información de normales para debugging.

---

# 112. CAMERA DEBUG

Deberá poder visualizarse frustum/cámara para debugging.

---

# 113. VIEWPORT RESIZE

El resize deberá actualizar:

```text
viewport_bounds
camera_aspect
projection
render_target
```

---

# 114. VIEWPORT DPI

La escala DPI deberá afectar correctamente la relación:

```text
logical_coordinates
 ↔
physical_pixels
```

---

# 115. VIEWPORT INVALIDATION

Cambios en:

```text
camera
scene
selection
gizmo
overlay
```

deberán invalidar el viewport apropiadamente.

---

# 116. PARTIAL VIEWPORT UPDATE

Cuando sea posible, el sistema deberá evitar recomputaciones innecesarias.

---

# 117. FRAME LOOP

El viewport deberá integrarse con el frame loop:

```text
INPUT
UPDATE
TRANSFORM
CULL
RENDER
PRESENT
```

---

# 118. DETERMINISTIC FRAME

El mismo estado e inputs deberán producir el mismo estado lógico de viewport.

---

# 119. REPLAY

Deberán poder reproducirse:

```text
camera movement
selection
gizmo interaction
snapping
viewport commands
```

---

# 120. VIEWPORT STATE SNAPSHOT

Mínimo:

```text
camera
selection
active_tool
pivot_mode
orientation
snap_settings
grid_settings
visibility
```

---

# 121. TESTING ARCHITECTURE

Deberán existir:

```text
UNIT TESTS
PROPERTY TESTS
INTEGRATION TESTS
GOLDEN TESTS
REPLAY TESTS
PERFORMANCE TESTS
STRESS TESTS
SECURITY TESTS
```

---

# 122. SCENE GRAPH TESTS

Mínimo:

```text
test_add_node
test_remove_node
test_insert_node
test_move_node
test_reparent
test_keep_local
test_keep_world
test_cycle_rejection
test_self_parent_rejection
test_unique_ids
test_child_order
test_root_integrity
```

---

# 123. TRANSFORM TESTS

Mínimo:

```text
test_local_transform
test_world_transform
test_nested_transform
test_transform_propagation
test_transform_cache
test_transform_invalidation
test_rotation
test_scale
test_negative_scale
test_zero_scale
test_non_finite_rejection
test_keep_world_reparent
```

---

# 124. CAMERA TESTS

Mínimo:

```text
test_perspective_projection
test_orthographic_projection
test_view_matrix
test_projection_matrix
test_view_projection
test_screen_to_world
test_world_to_screen
test_camera_orbit
test_camera_pan
test_camera_dolly
test_camera_focus
test_camera_resize
test_camera_clamp
```

---

# 125. FRUSTUM TESTS

Mínimo:

```text
test_frustum_generation
test_frustum_planes
test_inside_frustum
test_outside_frustum
test_boundary_frustum
test_frustum_culling
```

---

# 126. SPATIAL INDEX TESTS

Mínimo:

```text
test_insert
test_remove
test_update
test_aabb_query
test_frustum_query
test_ray_query
test_visibility_filter
test_spatial_consistency
```

---

# 127. PICKING TESTS

Mínimo:

```text
test_pick_single
test_pick_multiple
test_nearest_hit
test_layer_filter
test_locked_filter
test_hidden_filter
test_non_selectable_filter
test_pick_determinism
test_pick_after_transform
```

---

# 128. SELECTION TESTS

Mínimo:

```text
test_single_selection
test_multi_selection
test_toggle_selection
test_extend_selection
test_subtract_selection
test_active_selection
test_selection_order
test_hierarchical_selection
test_marquee_touch
test_marquee_contain
test_selection_filter
test_locked_selection
```

---

# 129. GIZMO TESTS

Mínimo:

```text
test_translate_gizmo
test_rotate_gizmo
test_scale_gizmo
test_universal_gizmo
test_axis_handle
test_plane_handle
test_screen_handle
test_gizmo_hit_test
test_gizmo_priority
test_gizmo_orientation
test_gizmo_pivot
```

---

# 130. SNAPPING TESTS

Mínimo:

```text
test_grid_snap
test_vertex_snap
test_edge_snap
test_face_snap
test_angle_snap
test_increment_snap
test_snap_threshold
test_snap_disable
test_snap_determinism
```

---

# 131. TRANSFORM INTERACTION TESTS

Mínimo:

```text
test_transform_begin
test_transform_update
test_transform_commit
test_transform_cancel
test_transform_capture
test_transform_multi_selection
test_transform_constraint
test_transform_undo
test_transform_redo
test_transform_replay
```

---

# 132. OVERLAY TESTS

Mínimo:

```text
test_grid_overlay
test_axis_overlay
test_selection_overlay
test_hover_overlay
test_gizmo_overlay
test_bounds_overlay
test_debug_overlay
test_overlay_order
test_overlay_depth
```

---

# 133. VIEWPORT INPUT TESTS

Mínimo:

```text
test_camera_input
test_selection_input
test_gizmo_input
test_pointer_capture
test_pointer_release
test_navigation
test_keyboard_navigation
test_modifier_mapping
test_input_priority
test_input_cancel
```

---

# 134. RENDER TESTS

Mínimo:

```text
test_scene_pass
test_overlay_pass
test_gizmo_pass
test_debug_pass
test_depth
test_wireframe
test_selection_render
test_hover_render
test_deterministic_render_order
test_viewport_resize
```

---

# 135. SNAPSHOT TESTS

Mínimo:

```text
test_viewport_snapshot
test_camera_snapshot
test_selection_snapshot
test_tool_snapshot
test_grid_snapshot
test_snap_snapshot
test_visibility_snapshot
test_replay_snapshot
```

---

# 136. GOLDEN TESTS

Mínimo:

```text
GOLDEN_EMPTY_VIEWPORT
GOLDEN_SINGLE_OBJECT
GOLDEN_MULTI_SELECTION
GOLDEN_TRANSLATE_GIZMO
GOLDEN_ROTATE_GIZMO
GOLDEN_SCALE_GIZMO
GOLDEN_GRID
GOLDEN_ORTHOGRAPHIC
GOLDEN_PERSPECTIVE
GOLDEN_WIREFRAME
GOLDEN_SELECTION
GOLDEN_HOVER
GOLDEN_BOUNDS
GOLDEN_DARK_THEME
GOLDEN_HIGH_DPI
```

---

# 137. INTEGRATION TESTS

Mínimo:

```text
test_viewport_ui_integration
test_viewport_input_integration
test_viewport_command_integration
test_viewport_selection_integration
test_viewport_scene_integration
test_viewport_camera_integration
test_viewport_undo_redo
test_viewport_replay
test_viewport_accessibility_controls
test_viewport_multiple_instances
```

---

# 138. END-TO-END TEST

Escenario obligatorio:

```text
USER INPUT
 ↓
VIEWPORT
 ↓
PICK
 ↓
SELECTION
 ↓
GIZMO
 ↓
TRANSFORM
 ↓
COMMAND
 ↓
STATE
 ↓
SCENE GRAPH
 ↓
SPATIAL INDEX
 ↓
RENDER
 ↓
SNAPSHOT
```

---

# 139. REPLAY TEST

Una interacción completa deberá poder grabarse y reproducirse:

```text
camera
selection
tool activation
pointer movement
keyboard modifiers
snap
transform
commit
```

El resultado deberá coincidir en:

```text
scene state
selection
camera state
transform
command sequence
viewport snapshot
```

---

# 140. PROPERTY TESTS

Deberán probarse propiedades como:

```text
world_transform_consistency
inverse_transform_consistency
projection_roundtrip
selection_idempotence
undo_redo_identity
reparent_keep_world_identity
snap_determinism
spatial_index_consistency
```

---

# 141. PERFORMANCE TESTS

Mínimo:

```text
test_10k_nodes
test_100k_nodes
test_deep_hierarchy
test_large_selection
test_large_spatial_query
test_many_gizmos
test_large_marquee
test_many_viewports
test_camera_update
test_transform_propagation
test_frustum_culling
test_picking
test_render_submission
```

---

# 142. STRESS TESTS

Deberán cubrir:

```text
rapid_selection
rapid_reparent
rapid_transform
rapid_camera_motion
continuous_resize
massive_scene_updates
rapid_tool_switch
rapid_undo_redo
```

---

# 143. SECURITY TESTS

Mínimo:

```text
test_cycle_injection
test_invalid_node_id
test_invalid_transform
test_nan_transform
test_inf_transform
test_extreme_coordinates
test_extreme_scale
test_deep_hierarchy
test_spatial_index_corruption
test_malicious_pick_input
test_event_flood
test_gizmo_input_flood
```

---

# 144. DETERMINISM TESTS

Deberá comprobarse que:

```text
same_scene
+
same_camera
+
same_input
+
same_settings
=
same_selection
+
same_transforms
+
same_commands
+
same_snapshot
```

---

# 145. RESOURCE CLEANUP

Al destruir un viewport deberán liberarse:

```text
camera resources
render targets
spatial index entries
selection subscriptions
input subscriptions
gizmo resources
overlay resources
```

---

# 146. LEAK TESTS

Mínimo:

```text
test_viewport_leak
test_camera_leak
test_spatial_entry_leak
test_selection_subscription_leak
test_gizmo_leak
test_render_target_leak
```

---

# 147. MULTI-VIEWPORT TESTS

Deberá verificarse que:

```text
viewport A camera
viewport A selection
viewport A tools
```

no modifiquen accidentalmente:

```text
viewport B camera
viewport B selection
viewport B tools
```

---

# 148. ACCESSIBILITY

Las funciones esenciales del viewport deberán poder utilizarse sin depender exclusivamente de pointer input.

Mínimo:

```text
select
focus
activate tool
navigate
transform where feasible
cancel
commit
```

---

# 149. KEYBOARD SHORTCUTS

Los shortcuts deberán integrarse con el sistema de comandos y ser configurables.

---

# 150. CONTEXTUAL SHORTCUTS

Los shortcuts deberán respetar:

```text
focused widget
active viewport
active tool
modal state
```

---

# 151. CONFLICT RESOLUTION

Si UI y viewport reciben el mismo input, deberá existir prioridad determinista.

---

# 152. ACTIVE VIEWPORT

Deberá existir un único viewport activo por contexto de interacción.

---

# 153. VIEWPORT FOCUS

El viewport podrá adquirir y perder focus.

---

# 154. VIEWPORT COMMANDS

Mínimo:

```text
Select
Deselect
FocusSelection
FrameSelection
Translate
Rotate
Scale
Delete
Duplicate
Reparent
SetCamera
SetTool
ToggleGrid
ToggleSnap
```

---

# 155. COMMAND VALIDATION

Los comandos deberán validarse antes de modificar el scene graph.

---

# 156. TRANSACTION SAFETY

Una operación fallida deberá dejar el scene graph exactamente en el estado previo.

---

# 157. EDITOR STATE

El estado editorial deberá mantenerse separado del estado de dominio cuando corresponda.

---

# 158. PERSISTENCE

Deberá definirse qué estado de viewport es persistible:

```text
camera
grid
snap
tool
selection
layout
```

según configuración del producto.

---

# 159. NON-PERSISTENT STATE

El estado efímero deberá incluir:

```text
hover
active_drag
pointer_capture
temporary_gizmo_state
```

---

# 160. DIAGNOSTICS

El viewport deberá poder reportar:

```text
viewport_id
camera
visible_nodes
selected_nodes
active_tool
spatial_index_stats
frame_stats
dirty_state
```

---

# 161. VIEWPORT INSPECTOR

Deberá existir una capacidad de inspección/debug.

---

# 162. PERFORMANCE TELEMETRY

Mínimo:

```text
frame_time
update_time
transform_time
culling_time
picking_time
selection_time
render_time
visible_nodes
culled_nodes
draw_calls
```

---

# 163. MEMORY TELEMETRY

Mínimo:

```text
scene_node_memory
spatial_index_memory
selection_memory
gizmo_memory
render_command_memory
```

---

# 164. ACCEPTANCE CRITERIA

UAF-81.67 estará completa únicamente cuando:

```text
VIEWPORT ROOT IMPLEMENTED
MULTI-VIEWPORT IMPLEMENTED
SCENE GRAPH IMPLEMENTED
SCENE NODE IMPLEMENTED
TREE INVARIANTS IMPLEMENTED
LOCAL/WORLD TRANSFORMS IMPLEMENTED
TRANSFORM PROPAGATION IMPLEMENTED
TRANSFORM CACHE IMPLEMENTED
PIVOT SYSTEM IMPLEMENTED
CAMERA IMPLEMENTED
PERSPECTIVE IMPLEMENTED
ORTHOGRAPHIC IMPLEMENTED
SCREEN/WORLD CONVERSION IMPLEMENTED
CAMERA NAVIGATION IMPLEMENTED
FRUSTUM IMPLEMENTED
CULLING IMPLEMENTED
SPATIAL INDEX IMPLEMENTED
PICKING IMPLEMENTED
SELECTION IMPLEMENTED
MULTI-SELECTION IMPLEMENTED
MARQUEE SELECTION IMPLEMENTED
GIZMOS IMPLEMENTED
TRANSLATE IMPLEMENTED
ROTATE IMPLEMENTED
SCALE IMPLEMENTED
PIVOT MODES IMPLEMENTED
AXIS CONSTRAINTS IMPLEMENTED
GRID IMPLEMENTED
SNAPPING IMPLEMENTED
EDITOR OVERLAYS IMPLEMENTED
VIEWPORT INPUT IMPLEMENTED
POINTER CAPTURE IMPLEMENTED
TRANSFORM TRANSACTIONS IMPLEMENTED
UNDO/REDO INTEGRATION IMPLEMENTED
VIEWPORT RENDERING IMPLEMENTED
VIEWPORT INVALIDATION IMPLEMENTED
VIEWPORT SNAPSHOT IMPLEMENTED
REPLAY IMPLEMENTED
ACCESSIBILITY CONTROLS IMPLEMENTED
PERFORMANCE TELEMETRY IMPLEMENTED
SECURITY TESTS IMPLEMENTED
UNIT TESTS IMPLEMENTED
PROPERTY TESTS IMPLEMENTED
INTEGRATION TESTS IMPLEMENTED
GOLDEN TESTS IMPLEMENTED
PERFORMANCE TESTS IMPLEMENTED
STRESS TESTS IMPLEMENTED
LEAK TESTS IMPLEMENTED
DOCUMENTATION COMPLETE
```

---

# 165. MINIMUM TEST COUNT

La fase deberá contener como mínimo:

```text
12 SCENE_GRAPH
12 TRANSFORM
13 CAMERA
6 FRUSTUM
8 SPATIAL_INDEX
9 PICKING
12 SELECTION
11 GIZMO
9 SNAPPING
9 TRANSFORM_INTERACTION
9 OVERLAY
10 VIEWPORT_INPUT
10 RENDER
8 SNAPSHOT
15 GOLDEN
10 INTEGRATION
1 END_TO_END
1 REPLAY
8 PROPERTY
13 PERFORMANCE
8 STRESS
11 SECURITY
6 LEAK
```

**Total mínimo: 217 tests.**

---

# 166. CROSS-PHASE TEST REQUIREMENT

La suite acumulada deberá comprobar:

```text
UAF-81.64
RUNTIME
   ↓
UAF-81.65
INPUT / EVENTS / COMMANDS
   ↓
UAF-81.66
UI
   ↓
UAF-81.67
VIEWPORT / SCENE / CAMERA / EDITOR
```

y garantizar:

```text
determinism
ownership
lifecycle
cleanup
undo/redo
replay
```

---

# 167. NON-NEGOTIABLE INVARIANTS

```text
NO SCENE GRAPH CYCLES
NO INVALID PARENT
NO STALE WORLD TRANSFORM
NO STALE SPATIAL ENTRY
NO NON-DETERMINISTIC PICK
NO NON-DETERMINISTIC SELECTION
NO GIZMO INPUT LEAK
NO UNCOMMITTED TRANSFORM LOSS
NO BROKEN UNDO/REDO
NO CAMERA STATE LEAK BETWEEN VIEWPORTS
NO CROSS-VIEWPORT SELECTION CORRUPTION
NO NON-FINITE TRANSFORMS
NO RESOURCE LEAKS
NO REPLAY DIVERGENCE
```

---

# 168. NEXT PHASE

```text
UAF-81.68 — UNIVERSAL ASSET INSPECTOR, PROPERTY SYSTEM, SCHEMA-DRIVEN EDITORS, PROPERTY GRIDS, COMPONENT INSPECTION, MULTI-EDIT, VALIDATION, ENUMERATION, RESOURCE REFERENCES, EDITOR FORMS & INSPECTOR TESTING SYSTEM
```

La siguiente fase deberá construir el sistema de inspección sobre:

```text
UAF-81.64 RUNTIME
        ↓
UAF-81.65 COMMANDS / INPUT
        ↓
UAF-81.66 UI
        ↓
UAF-81.67 VIEWPORT / SCENE
        ↓
PROPERTY MODEL
        ↓
SCHEMA
        ↓
INSPECTOR
        ↓
PROPERTY EDITORS
        ↓
VALIDATION
        ↓
MULTI-EDIT
        ↓
UNDO/REDO
        ↓
INSPECTOR TESTS
```
