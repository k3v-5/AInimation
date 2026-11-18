# UAF-81.87 — UNIVERSAL DEEP UNREAL ENGINE 5 LIVELINK, BIDIRECTIONAL SYNCHRONIZATION, HOT RELOAD & INTEROPERABILITY BRIDGE

**Estado:** Fase Normativa Activa  
**Dependencias:** UAF-81.73 → UAF-81.86  
**Objetivo:** Integración profunda, determinista y bidireccional entre el Headless Core de UAF/AOE y Unreal Engine 5.

---

# 1. MISIÓN Y PRINCIPIOS CENTRALES

UAF-81.87 implementa el puente oficial de interoperabilidad y sincronización en tiempo real entre:
- **AOE / UAF Headless Runtime**: Scene Graph, ECS, Física, AI, Animación, VFX, Audio, Rendering, Asset Factory, Telemetría (81.86).
- **Unreal Engine 5**: UObject / Actor, Componentes, Niveles / World Partition, Materiales, Niagara, Control Rig, Sequencer, LiveLink.

### Principio de Autoridad Explícita
UAF es el sistema autoritativo para los datos generativos y de simulación procedural. UE5 no puede mutar silenciosamente entidades autoritativas de UAF.
Tres modelos de autoridad:
1. `UAF_AUTHORITATIVE`: Transformaciones procedurales, generación de mallas, lógica de gameplay central.
2. `UE_AUTHORITATIVE`: Manipulación manual de transformaciones en el Editor de UE5, instancias de materiales ajustadas a mano.
3. `SHARED`: Cámaras de preview, viewport sync, gizmos.

Toda modificación genera un `ChangeEvent` explícito con `object_id`, `property`, `old_value`, `new_value`, `source`, `revision`, `timestamp` y `frame`.

---

# 2. IDENTIDAD UNIVERSAL Y REGISTRO

- **Universal Object ID (`uaf_object_id`)**: Identificador inmutable y persistente a través de destrucción de actores, recargas de nivel, hot reloads y streaming.
- **`UE5ObjectRegistry`**: Mapeo bidireccional estable entre `uaf_object_id` ↔ UE5 Object Path ↔ Instancia de Actor / UObject.
- **Identidad de Assets**: `asset_id`, `asset_type`, `source_hash`, `content_hash`, `build_hash`, `revision`, `generation`.
- **Path Mapping Determinista**: `/Game/UAF/Assets/{AssetType}/{SemanticName}_{ShortHash}`.

---

# 3. PROTOCOLO Y TRANSPORTE DESACOPLADO

- **Capa de Transporte**:
  - Local IPC (Memoria compartida / pipes)
  - TCP (Sockets de alta fiabilidad)
  - WebSocket (Inspección y tooling remoto)
  - Embedded (In-process directo en tests o builds monolíticas)
- **Mensajería Tipada**:
  - Handshake: `HELLO`, `WELCOME`, `CAPABILITIES`, `READY`, `VERSION_MISMATCH`
  - Heartbeat & Control: `PING`, `PONG`, `ACK`, `NACK`, `ERROR`, `WARNING`
  - CRUD & Delta Sync: `CREATE`, `UPDATE`, `DELETE`, `PATCH`, `SNAPSHOT`
  - Assets: `ASSET_CREATE`, `ASSET_UPDATE`, `ASSET_DELETE`, `ASSET_RELOAD`
  - Escena y Actores: `SCENE_LOAD`, `SCENE_UNLOAD`, `ACTOR_SPAWN`, `ACTOR_UPDATE`, `ACTOR_DESTROY`
  - Subsistemas: `TRANSFORM_UPDATE`, `CAMERA_UPDATE`, `ANIMATION_UPDATE`, `VFX_UPDATE`, `LIGHT_UPDATE`, `AUDIO_UPDATE`
- **Tolerancia a Fallos y Reconexión**: Detección de pérdida de heartbeat, congelación de cambios salientes, delta replay tras reconexión, validación de hashes canónicos.

---

# 4. TRANSACCIONES, CONFLICTOS Y HOT RELOAD

- **Modelo Transaccional**: `begin_transaction()`, `commit()`, `rollback()` con atomicidad completa para cambios multi-actor/multi-asset.
- **Control de Concurrencia y Conflictos**: Vectores de revisión (`RevisionVector`), políticas de resolución (`UAF_WINS`, `UE_WINS`, `LATEST_TIMESTAMP`, `MERGE`).
- **Hot Reload sin Ruptura**:
  - Recarga en caliente de Mallas, Skeletal MMs, Texturas, Materiales, Niagara Systems y Animaciones preservando punteros, instancias y bindings en escena.
- **Sincronización de Parámetros Niagara**: Mapeo dinámico de emisores y user parameters en tiempo de ejecución.

---

# 5. SUBSYSTEM BRIDGES ESPECÍFICOS

1. **Mesh & Skeletal Mesh Bridge**: Mapeo de LODs, nanite flags, jerarquías de huesos y sockets.
2. **Animation, Control Rig & Sequencer Bridge**: Blends, poses de streaming, pistas cinematográficas.
3. **Niagara VFX Bridge**: Sincronización de sistemas de partículas, parámetros y eventos.
4. **Camera & Multi-Camera Bridge**: Posición, FOV, post-process de cámara, vista cine.
5. **Lighting & Atmosphere Bridge**: Directional, Point, Spot, Rect, SkyLight, parámetros Lumen y sombras.
6. **Material & Texture Bridge**: Master materials, material instances escalonadas, texturas virtuales.
7. **World & World Partition Bridge**: Celda activa, streaming priority, data layers, HLODs.
8. **Actor & Component Bridge**: Mapeo bidireccional de componentes ECS a UActorComponents.

---

# 6. OBSERVABILIDAD, CRASH RECOVERY Y CERTIFICACIÓN

- **Integración con UAF-81.86 Telemetry**:
  - Métricas de bridge: latencia, queue depth, mensajes/s, tamaño de payload, tiempo de serialización.
  - Alertas automáticas de desincronización, desbordamiento de cola y stalls.
- **Manejo de Errores y Cuarentena**:
  - Detección y poda de actores huérfanos (`OrphanPolicy`).
  - Aislamiento de assets corruptos en cuarentena sin derribar la sesión LiveLink.
- **Certification Gate**:
  - Pruebas automatizadas de escenas doradas (Golden Scenes), replicación bidireccional y paridad de hashes deterministas.
