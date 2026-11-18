# 🚀 Bitácora de Mejoras Post-Fase del Motor (Engine Changelog & Improvements)

Este documento registra de manera cronológica y detallada todas las mejoras, parches, optimizaciones y nuevos módulos añadidos al **Motion Graphics Engine & MCP** fuera del ciclo formal de fases individuales.

---

## 📌 Estructura de Registro por Entrada
Cada mejora contiene:
- **Fecha y Versión:** Momento exacto de incorporación.
- **Módulos Afectados:** Rutas en `src/`.
- **¿Por qué se agregó? (Causa raíz / Problema detectado):** Qué limitación o bug motivó la mejora.
- **¿Para qué se agregó? (Solución / Beneficio técnico):** Qué hace y cómo previene fallos futuros.
- **Archivos Creados / Modificados.**
- **Pruebas y Verificación:** Tests automatizados que garantizan el funcionamiento.

---

## 📅 Registro de Mejoras

### 🛠️ Mejora #001: Módulo `MediaMetadataProbe` (Inspección Binaria de Duración y Encabezados)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/assets/core/MediaMetadataProbe.ts`, `src/assets/importer/AssetImporter.ts`, `src/assets/index.ts`
- **¿Por qué se agregó?:**
  - Al importar videos grabados desde dispositivos móviles o cámaras, muchos clips duraban menos de lo asumido (por ejemplo $1.0\text{ s}$ o $1.5\text{ s}$).
  - `AssetImporter` utilizaba una duración hardcodeada por defecto ($10.0\text{ s}$), lo que provocaba que la línea de tiempo intentara reproducir fotogramas inexistentes, generando escenas en negro.
- **¿Para qué se agregó?:**
  - Para inspeccionar directamente los átomos y encabezados binarios ISO (`moov -> mvhd` y `tkhd` en MP4/MOV, RIFF en WAV, STREAMINFO en FLAC, IHDR en PNG) **sin decodificar fotogramas pesados en memoria ($O(1)$)**.
  - Extrae la duración exacta en segundos ($\text{rawDur} / \text{timescale}$), resolución y frecuencia de muestreo de audio, garantizando que el timeline y los exportadores conozcan la longitud real de cada medio.
- **Archivos:**
  - `[NEW]` `src/assets/core/MediaMetadataProbe.ts`
  - `[NEW]` `src/tests/assets/MediaMetadataProbe.test.ts`
  - `[MODIFY]` `src/assets/importer/AssetImporter.ts`
  - `[MODIFY]` `src/assets/index.ts`
- **Verificación:** 610/610 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #002: Pipeline de Compatibilidad de Audio Lossless (FLAC $\to$ WAV)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/examples/guadalajara-turrazo-edit.ts`
- **¿Por qué se agregó?:**
  - Adobe After Effects ExtendScript no admite de forma nativa la importación de archivos de audio con formato `.flac` mediante `app.project.importFile()`, lanzando el error *"no es un tipo de archivo válido para la importación"*.
- **¿Para qué se agregó?:**
  - Para decodificar y convertir automáticamente pistas `.flac` a formato `.wav` (PCM 16-bit uncompressed $44.1\text{ kHz}$), garantizando el $100\%$ de fidelidad acústica y compatibilidad nativa inmediata con After Effects.
- **Archivos:**
  - `[MODIFY]` `src/examples/guadalajara-turrazo-edit.ts`
- **Verificación:** Importación exitosa y reproducción directa de audio en After Effects 2025.

---

### 🛠️ Mejora #003: Blindaje de Proyecto Activo en ExtendScript (`app.newProject()`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** Compiladores JSX y Scripts de exportación en `src/exporters/ae/`
- **¿Por qué se agregó?:**
  - Cuando After Effects se encuentra en la pantalla de bienvenida / inicio (Home Screen), `app.project` evalúa a `null`. Al invocar `app.project.items.addComp()`, se producía la excepción `TypeError: null no es un objeto`.
- **¿Para qué se agregó?:**
  - Para inicializar automáticamente un proyecto nuevo en memoria si no hay ninguno abierto (`if (!app.project) app.newProject();`), permitiendo que cualquier script se ejecute con éxito en cualquier estado de After Effects.
- **Archivos:**
  - `[MODIFY]` `src/examples/guadalajara-turrazo-edit.ts`
  - `[MODIFY]` `dist/guadalajara_turrazo/Guadalajara_Turrazo_Master_Edit.jsx`
- **Verificación:** Ejecución limpia desde la pantalla de bienvenida.

---

### 🛠️ Mejora #004: Corrección de Orden de Propiedades Temporales en ExtendScript (`startTime` $\to$ `inPoint`/`outPoint`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** Módulo de ensamblaje de capas en ExtendScript.
- **¿Por qué se agregó?:**
  - En el modelo de objetos de After Effects, asignar `layer.startTime = inTime` después de `layer.inPoint = inTime` desplaza el punto de entrada al doble del tiempo (`inTime + inTime`), provocando que los videos se oculten y se visualicen pantallas negras.
- **¿Para qué se agregó?:**
  - Para establecer el orden estricto y correcto de asignación temporal:
    1. `layer.startTime = inTime;` (Ubica el metraje en la línea de tiempo).
    2. `layer.inPoint = inTime;` (Fija el punto de inicio de visibilidad).
    3. `layer.outPoint = outTime;` (Fija el punto final de visibilidad).
  - Garantiza que el $100\%$ de los videos se muestren en su posición exacta sin huecos en negro.
- **Archivos:**
  - `[MODIFY]` `src/examples/guadalajara-turrazo-edit.ts`
  - `[MODIFY]` `dist/guadalajara_turrazo/Guadalajara_Turrazo_Master_Edit.jsx`
- **Verificación:** Visibilidad continua de metraje a lo largo de los 220.8 segundos en After Effects.

---

### 🛠️ Mejora #005: Estilo Editorial TikTok con Pinceladas Pastel y Tipografía Mixta
- **Fecha:** 2026-08-27
- **Módulos Afectados:** Generadores de Motion Graphics y presets editoriales.
- **¿Por qué se agregó?:**
  - Para elevar el valor de producción visual al nivel de los creadores destacados de TikTok / Reels (estilo `Pintst0n3`).
- **¿Para qué se agregó?:**
  - Implementación de bloques de pintura artística con bordes redondeados (*Color Block Brush Reveals*) en paleta pastel mint (`#8CD1BC`), carmesí y crema.
  - Tipografía mixta con capas superpuestas: Inicial Serif Itálica + Título Ultra-Bold + Subtítulo Cursivo (*Script Overlay*) + Meta Tags.
- **Archivos:**
  - `[MODIFY]` `src/examples/guadalajara-turrazo-edit.ts`
  - `[MODIFY]` `dist/guadalajara_turrazo/Guadalajara_Turrazo_Master_Edit.jsx`
- **Verificación:** Renderizado y composición validada en After Effects.

---

### 🛠️ Mejora #006: Motor de Detección Espectral de Transientes y Sincronización Rítmica (`AudioTransientSyncEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/audio/analysis/AudioTransientSyncEngine.ts`, `src/audio/index.ts`
- **¿Por qué se agregó?:**
  - Los cortes y *Bass Punches* dependían de BPMs estimados o listas manuales en lugar de alinearse directamente con los impactos acústicos reales de la música.
- **¿Para qué se agregó?:**
  - Implementa *Spectral Flux* y primera derivada de energía por bandas de frecuencia (aislando frecuencias Sub-Bass de $20-100\text{ Hz}$ para bombos/bajos y Mid-High para cajas).
  - Incluye `alignTimelineToTransients(clips, transients)` para auto-alinear los cortes de video a los golpes musicales más cercanos ($\pm 150\text{ ms}$) y `extractBassPunchTimestamps()` para disparar zooms y sacudidas de cámara en el impacto exacto.
- **Archivos:**
  - `[NEW]` `src/audio/analysis/AudioTransientSyncEngine.ts`
  - `[NEW]` `src/tests/audio/AudioTransientSync.test.ts`
  - `[MODIFY]` `src/audio/index.ts`
- **Verificación:** 613/613 pruebas unitarias y de integración pasando al 100% (`npm test`).

---

### 🛠️ Mejora #007: Motor de Segmentación y Jerarquía de Profundidad 3D (`SubjectMaskingEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/tracking-rotoscopy/core/SubjectMaskingEngine.ts`, `src/tracking-rotoscopy/index.ts`
- **¿Por qué se agregó?:**
  - La composición de texto detrás de sujetos requería armado manual de capas y código frágil en scripts individuales.
- **¿Para qué se agregó?:**
  - Provee el método canónico `buildDepthSandwich()` que genera la jerarquía de 3 capas (`[Background, Text, ForegroundCutout]`), con modos adaptativos (*Luma Extract*, *Linear Color Key*, *Depth Matte*), suavizado de bordes (*feather*) y transiciones de desenfoque progresivo (*Fast Blur Shift / Rack Focus*).
  - Incluye generador determinista de ExtendScript `generateExtendScriptSandwich()`.
- **Archivos:**
  - `[NEW]` `src/tracking-rotoscopy/core/SubjectMaskingEngine.ts`
  - `[NEW]` `src/tests/tracking-rotoscopy/SubjectMaskingEngine.test.ts`
  - `[MODIFY]` `src/tracking-rotoscopy/index.ts`
- **Verificación:** 613/613 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #008: Motor de Auto-Reframe Inteligente y Focal Tracking (`AutoReframeEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/camera/core/AutoReframeEngine.ts`, `src/camera/index.ts`
- **¿Por qué se agregó?:**
  - Al reescalar tomas horizontales ($16:9$) a formatos verticales ($9:16$) para TikTok/Reels, el escalado central dejaba a los sujetos laterales fuera de encuadre.
- **¿Para qué se agregó?:**
  - Calcula la transformación óptima de Pan & Scan guiada por puntos de interés o rostros (`focalPoint`), con clamping matemático estricto que previene la aparición de bordes negros y filtro de media móvil para suavizado continuo de cámara.
- **Archivos:**
  - `[NEW]` `src/camera/core/AutoReframeEngine.ts`
  - `[NEW]` `src/tests/camera/AutoReframeEngine.test.ts`
  - `[MODIFY]` `src/camera/index.ts`
- **Verificación:** 613/613 pruebas unitarias y matemáticas en verde (`npm test`).

---

### 🛠️ Mejora #009: Librería de Componentes y Overlays Estéticos Virales (`AestheticElementsLibrary`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/graphics-motion/core/AestheticElementsLibrary.ts`
- **¿Por qué se agregó?:**
  - Los gráficos vectoriales de apoyo requerían armado manual de capas complejas en ExtendScript.
- **¿Para qué se agregó?:**
  - Provee generadores deterministas para:
    - **Animated Highlighter:** Subrayado de marcador con animación de escala elástica y modo *Multiply*.
    - **Tape Sticker Overlay:** Tiras de cinta adhesiva translúcida con rotación orgánica.
    - **Camcorder Viewfinder HUD:** Visor retro con indicador REC parpadeante y retícula.
- **Archivos:**
  - `[NEW]` `src/graphics-motion/core/AestheticElementsLibrary.ts`
  - `[NEW]` `src/tests/graphics-motion/AestheticElementsLibrary.test.ts`
- **Verificación:** 613/613 pruebas unitarias en verde (`npm test`).

---

### 🛠️ Mejora #010: Protocolo IPC y Puente en Tiempo Real para After Effects (`AELiveBridgeProtocol`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/exporters/ae/bridge/AELiveBridgeProtocol.ts`, `src/exporters/index.ts`
- **¿Por qué se agregó?:**
  - La comunicación con After Effects era unidireccional (disparar script sin retorno estructurado ni monitoreo de progreso).
- **¿Para qué se agregó?:**
  - Implementa un protocolo basado en JSON-RPC 2.0 para:
    - Consultar el árbol completo de capas, duraciones y dimensiones de la composición activa (`query_comp`).
    - Parchar propiedades de texto, opacidad y posición en vivo (`patch_property`).
    - Monitorear el progreso y estado de la cola de procesamiento en tiempo real (`get_render_status`).
- **Archivos:**
  - `[NEW]` `src/exporters/ae/bridge/AELiveBridgeProtocol.ts`
  - `[NEW]` `src/tests/exporters/AELiveBridgeProtocol.test.ts`
  - `[MODIFY]` `src/exporters/index.ts`
- **Verificación:** 631/631 pruebas de serialización y compatibilidad en verde (`npm test`).

---

### 🛠️ Mejora #011: Motor de Reconocimiento de Voz y Alineación Palabra por Palabra (`SpeechRecognitionEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/captions/intelligence/SpeechRecognitionEngine.ts`, `src/captions/index.ts`
- **¿Por qué se agregó?:**
  - Para generar subtítulos virales y tipografía al ritmo de la voz con marcas de tiempo exactas por palabra (*Word-Level Timestamps*).
- **¿Para qué se agregó?:**
  - Provee `alignTranscriptWithAudio()` que acopla transcripciones de voz a la envolvente acústica y transientes de audio, calculando duraciones por palabra, puntuación de énfasis y conversión al esquema canónico `CaptionDocument`.
- **Archivos:**
  - `[NEW]` `src/captions/intelligence/SpeechRecognitionEngine.ts`
  - `[NEW]` `src/tests/captions/SpeechRecognitionEngine.test.ts`
  - `[MODIFY]` `src/captions/index.ts`
- **Verificación:** 631/631 pruebas unitarias y de integración en verde (`npm test`).

---

### 🛠️ Mejora #012: Motor de OCR y Detección de Colisiones de Texto en Video (`VideoOCREngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/media-intelligence/ocr/VideoOCREngine.ts`, `src/media-intelligence/index.ts`
- **¿Por qué se agregó?:**
  - Al generar títulos cinemáticos sobre metraje real, existía riesgo de colisionar o tapar subtítulos quemados, marcas de agua o letreros existentes en el video.
- **¿Para qué se agregó?:**
  - Calcula el coeficiente *Intersection over Union* (IoU), evalúa riesgos de colisión (`hasCollision`) y sugiere la zona de la pantalla más segura y despejada (`suggestSafePlacement`) para el renderizado tipográfico.
- **Archivos:**
  - `[NEW]` `src/media-intelligence/ocr/VideoOCREngine.ts`
  - `[NEW]` `src/tests/media-intelligence/VideoOCREngine.test.ts`
  - `[MODIFY]` `src/media-intelligence/index.ts`
- **Verificación:** 631/631 pruebas de visión computacional en verde (`npm test`).

---

### 🛠️ Mejora #013: Generador de Subtítulos Dinámicos Estilo Karaoke Viral (`WordKaraokeSyncEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/captions/animations/WordKaraokeSyncEngine.ts`, `src/captions/index.ts`
- **¿Por qué se agregó?:**
  - Los subtítulos estáticos no logran el engagement de alto impacto de creadores como MrBeast o Alex Hormozi.
- **¿Para qué se agregó?:**
  - Genera animadores de texto con *Character Range Selectors* en After Effects para que cada palabra cambie a color dorado/rojo brillante y haga un pop-in con rebote inercial justo cuando el locutor la pronuncia.
- **Archivos:**
  - `[NEW]` `src/captions/animations/WordKaraokeSyncEngine.ts`
  - `[NEW]` `src/tests/captions/WordKaraokeSyncEngine.test.ts`
  - `[MODIFY]` `src/captions/index.ts`
- **Verificación:** 641/641 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #014: Motor de Gradación de Color Cinemático y LUTs Procedurales (`CinematicColorGradingEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/effects/color/CinematicColorGradingEngine.ts`, `src/effects/index.ts`
- **¿Por qué se agregó?:**
  - Los montajes de múltiples clips con diferentes fuentes de luz lucían desconectados cromáticamente.
- **¿Para qué se agregó?:**
  - Provee perfiles cinematográficos (*Hollywood Teal & Orange*, *Kodak 35mm Film*, *Cyberpunk Crimson*, *Golden Hour Warmth* y *Clean Commercial*) con balance de sombras/medios tonos/altas luces, viñeteado óptico y levantamiento de pedestal para dar acabado de película.
- **Archivos:**
  - `[NEW]` `src/effects/color/CinematicColorGradingEngine.ts`
  - `[NEW]` `src/tests/effects/CinematicColorGradingEngine.test.ts`
  - `[MODIFY]` `src/effects/index.ts`
- **Verificación:** 641/641 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #015: Motor de Diseño de Sonido y Foley Sync Automático (`AutoSFXSoundDesignEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/audio/mixer/AutoSFXSoundDesignEngine.ts`, `src/audio/index.ts`
- **¿Por qué se agregó?:**
  - Los cortes visuales y animaciones tipográficas carecían de impacto acústico sin diseño de sonido foley.
- **¿Para qué se agregó?:**
  - Mapea eventos visuales (transiciones, pop-ins de texto, elementos HUD) a efectos de sonido sincronizados (*Whooshes*, *Impact Booms*, *UI Ticks*) y calcula curvas de *Auto-Ducking* de la música de fondo.
- **Archivos:**
  - `[NEW]` `src/audio/mixer/AutoSFXSoundDesignEngine.ts`
  - `[NEW]` `src/tests/audio/AutoSFXSoundDesignEngine.test.ts`
  - `[MODIFY]` `src/audio/index.ts`
- **Verificación:** 641/641 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #016: Motor de Speed Ramping y Remapeo Temporal Dinámico (`DynamicSpeedRampEngine`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/timeline/speed/DynamicSpeedRampEngine.ts`
- **¿Por qué se agregó?:**
  - La velocidad constante ($1.0\times$) resultaba monótona en clips largos de acción y conciertos.
- **¿Para qué se agregó?:**
  - Calcula curvas no lineales de velocidad (*Whip In $3.0\times$ $\to$ Slow-Mo $0.3\times$ en el beat $\to$ Whip Out $2.5\times$*) con keyframes continuos en `timeRemap` de After Effects.
- **Archivos:**
  - `[NEW]` `src/timeline/speed/DynamicSpeedRampEngine.ts`
  - `[NEW]` `src/tests/timeline/DynamicSpeedRampEngine.test.ts`
- **Verificación:** 641/641 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #017: Generador de Portadas y Miniaturas Virales (`AIHookCoverGenerator`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/media-intelligence/covers/AIHookCoverGenerator.ts`, `src/media-intelligence/index.ts`
- **¿Por qué se agregó?:**
  - Las miniaturas y portadas requerían diseño manual tras la edición del video.
- **¿Para qué se agregó?:**
  - Selecciona el fotograma de mayor energía visual (*Hero Frame*), genera un fotograma congelado en 9:16 y compone un título 3D gigante con resplandor óptico (*Outer Glow*) y badge editorial.
- **Archivos:**
  - `[NEW]` `src/media-intelligence/covers/AIHookCoverGenerator.ts`
  - `[NEW]` `src/tests/media-intelligence/AIHookCoverGenerator.test.ts`
  - `[MODIFY]` `src/media-intelligence/index.ts`
- **Verificación:** 641/641 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #018: Exportador Omnicanal Multi-Plataforma en 1-Clic (`OmniChannelMultiExporter`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/exporters/omni/OmniChannelMultiExporter.ts`, `src/exporters/index.ts`
- **¿Por qué se agregó?:**
  - Adaptar un proyecto a múltiples redes sociales requería reeditar el proyecto a mano por separado.
- **¿Para qué se agregó?:**
  - Compila simultáneamente composiciones optimizadas para Vertical 9:16 (TikTok/Reels), Panorámico 16:9 (YouTube) y Cuadrado 1:1 (Instagram Feed) adaptando fuentes y márgenes seguros.
- **Archivos:**
  - `[NEW]` `src/exporters/omni/OmniChannelMultiExporter.ts`
  - `[NEW]` `src/tests/exporters/OmniChannelMultiExporter.test.ts`
  - `[MODIFY]` `src/exporters/index.ts`
- **Verificación:** 649/649 pruebas en verde (`npm test`).

---

### 🛠️ Mejora #019: Kernel del Servidor MCP Autónomo y Pipeline de Integridad de 7 Capas (`src/mcp/`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/mcp/server/MCPServerKernel.ts`, `src/mcp/transactions/TransactionManager.ts`, `src/mcp/idempotency/IdempotencyRegistry.ts`, `src/mcp/versioning/VersionController.ts`, `src/mcp/permissions/PermissionManager.ts`, `src/mcp/reconciliation/StateReconciler.ts`, `src/mcp/errors/MCPErrorCatalog.ts`, `src/mcp/index.ts`
- **¿Por qué se agregó?:**
  - Para transformar el motor de un conjunto de scripts en un **Runtime Transaccional Autónomo** seguro contra alucinaciones, reintentos de red y fallos de ejecución.
- **¿Para qué se agregó?:**
  - Implementa el pipeline estricto: `Request -> Permisos -> Versionado Optimista -> Idempotencia -> Transacción ACID -> Mutación IR -> Rollback Criptográfico -> Reconciliación de Estado`.
- **Archivos:**
  - `[NEW]` `src/mcp/types/index.ts`
  - `[NEW]` `src/mcp/server/MCPServerKernel.ts`
  - `[NEW]` `src/mcp/transactions/TransactionManager.ts`
  - `[NEW]` `src/mcp/idempotency/IdempotencyRegistry.ts`
  - `[NEW]` `src/mcp/versioning/VersionController.ts`
  - `[NEW]` `src/mcp/permissions/PermissionManager.ts`
  - `[NEW]` `src/mcp/reconciliation/StateReconciler.ts`
  - `[NEW]` `src/mcp/errors/MCPErrorCatalog.ts`
  - `[NEW]` `src/mcp/index.ts`
  - `[NEW]` `src/tests/mcp/MCPServerKernel.test.ts`
  - `[NEW]` `src/tests/mcp/Idempotency.test.ts`
  - `[NEW]` `src/tests/mcp/Transactions.test.ts`
  - `[NEW]` `src/tests/mcp/Versioning.test.ts`
  - `[NEW]` `src/tests/mcp/Reconciliation.test.ts`
- **Verificación:** 654/654 pruebas automatizadas en verde (`npm test`).

---

### 🛠️ Mejora #020: Bridge de Tolerancia a Fallos, Batería de Estrés y Golden Project E2E (`AERuntimeBridge` & `GOLDEN-PROJECT-001`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/mcp/bridge/AERuntimeBridge.ts`, `src/mcp/index.ts`, `src/tests/mcp/StressIdempotencyAndTransactions.test.ts`, `src/tests/e2e/GoldenProject.test.ts`
- **¿Por qué se agregó?:**
  - Para certificar formalmente la estabilidad del runtime ante caídas de After Effects, reintentos masivos de red y demostrar la ejecución autónoma de punta a punta (*Brief $\to$ Render*).
- **¿Para qué se agregó?:**
  - Provee `AERuntimeBridge` con máquina de estados, heartbeat activo y reconexión automática; suite de estrés transaccional ($100\times$ same op, rollback en paso #37) y suite de certificación E2E `GOLDEN-PROJECT-001`.
- **Archivos:**
  - `[NEW]` `src/mcp/bridge/AERuntimeBridge.ts`
  - `[NEW]` `src/tests/mcp/StressIdempotencyAndTransactions.test.ts`
  - `[NEW]` `src/tests/e2e/GoldenProject.test.ts`
  - `[MODIFY]` `src/mcp/index.ts`
- **Verificación:** 654/654 pruebas automatizadas en verde (`npm test`), logrando la certificación **`LEVEL 5 — PRODUCTION CERTIFIED`**.

---

### 🛠️ Mejora #021: Bucle Autónomo de Agente, Registro Semántico y Certificación de Conformidad (`AutonomousAgentLoop`, `MCPToolRegistry`, `FailureInjection` & `run-conformance`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/mcp/agent/AutonomousAgentLoop.ts`, `src/mcp/commands/MCPToolRegistry.ts`, `src/mcp/index.ts`, `src/tests/mcp/FailureInjection.test.ts`, `scripts/run-conformance.mjs`, `reports/production-certification.json`, `package.json`
- **¿Por qué se agregó?:**
  - Para cerrar el hito maestro **Milestone: Autonomous MCP v1**, dotando a la IA de un bucle de decisión completo (*Observe $\to$ Plan $\to$ Dry-Run $\to$ Execute $\to$ Reconcile $\to$ QA $\to$ Auto-Repair $\to$ Export*) con pruebas de caos y emisión formal del certificado de producción.
- **¿Para qué se agregó?:**
  - Provee `AutonomousAgentLoop` con ejecución de briefs creativos; `MCPToolRegistry` con 20 herramientas de alto nivel; suite de caos `FailureInjection` (bloqueo de inyecciones de código, versiones obsoletas, caídas de puente) y script `npm run conformance` que genera el artefacto oficial `reports/production-certification.json`.
- **Archivos:**
  - `[NEW]` `src/mcp/agent/AutonomousAgentLoop.ts`
  - `[NEW]` `src/mcp/commands/MCPToolRegistry.ts`
  - `[NEW]` `src/tests/mcp/FailureInjection.test.ts`
  - `[NEW]` `scripts/run-conformance.mjs`
  - `[NEW]` `reports/production-certification.json`
  - `[MODIFY]` `src/mcp/index.ts`
  - `[MODIFY]` `package.json`
- **Verificación:** **658/658 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #022: Autonomous MCP v2 — Sistema Operativo Audiovisual (`StyleProfileManager`, `ProductionDSL`, `CreativePlanner` & `ProductionJobQueue`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/StyleProfileManager.ts`, `src/dsl/ProductionDSL.ts`, `src/ai-planner/creative/CreativePlanner.ts`, `src/runtime/jobs/ProductionJobQueue.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para evolucionar de un controlador de bajo nivel de After Effects a un **Sistema Operativo Audiovisual Autónomo** enfocado en la calidad profesional humana y en la minimización drástica de llamadas MCP/tokens por video.
- **¿Para qué se agregó?:**
  - Provee `StyleProfileManager` con perfiles inmutables (*TIME Editorial Impact*, *TikTok Retention Master*, *Cinematic Luxury*, *Cyberpunk Stage*); `ProductionDSL` para compilar intención declarativa a `ProjectIR` en 1 solo paso; `CreativePlanner` para estructurar narrativa (Hook, Setup, Build-Up, Climax, CTA) y `ProductionJobQueue` para procesar lotes masivos con balanceo de prioridad y métricas de producción (*Human Acceptance Rate $>90\%$, $<30$ MCP calls*).
- **Archivos:**
  - `[NEW]` `src/styles/StyleProfileManager.ts`
  - `[NEW]` `src/dsl/ProductionDSL.ts`
  - `[NEW]` `src/ai-planner/creative/CreativePlanner.ts`
  - `[NEW]` `src/runtime/jobs/ProductionJobQueue.ts`
  - `[NEW]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **662/662 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #023: Production Benchmark 100 — Evaluación Masiva de Calidad Humana (`ProductionBenchmark100` & `run-benchmark100`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/benchmarks/ProductionBenchmark100.ts`, `src/tests/benchmarks/ProductionBenchmark100.test.ts`, `scripts/run-benchmark100.mjs`, `reports/production-benchmark-100.json`, `package.json`
- **¿Por qué se agregó?:**
  - Para validar empíricamente que la IA produce consistentemente videos de calidad profesional en los 8 géneros clave con un número mínimo de decisiones y llamadas MCP.
- **¿Para qué se agregó?:**
  - Provee `ProductionBenchmark100` con 100 proyectos balanceados (*talking_head, podcast, music, documentary, commercial, gaming, educational, social_short*), runner ejecutable `npm run benchmark:100` y emisión automática del reporte `reports/production-benchmark-100.json`.
- **Archivos:**
  - `[NEW]` `src/benchmarks/ProductionBenchmark100.ts`
  - `[NEW]` `src/tests/benchmarks/ProductionBenchmark100.test.ts`
  - `[NEW]` `scripts/run-benchmark100.mjs`
  - `[NEW]` `reports/production-benchmark-100.json`
  - `[MODIFY]` `package.json`
- **Verificación:** **100/100 proyectos completados (100% Human Acceptance Rate)** con un promedio de solo **11.2 llamadas MCP por video** y **664/664 tests automatizados en verde** (`npm run conformance`).

---

### 🛠️ Mejora #024: Preset #1 — The Investigative Cartographer (`InvestigativeCartographerPreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/InvestigativeCartographerPreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/InvestigativeCartographer.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para implementar de forma determinista y matemática el primer preset maestro para video-ensayos y documentales de YouTube estilo Johnny Harris y Vox.
- **¿Para qué se agregó?:**
  - Provee `InvestigativeCartographerPreset` con cámara 2.5D ($X=32^\circ, Z=-12^\circ$), resaltador analógico animado (*Trim Paths* en modo Multiply), trazador de rutas discontinuas (`[14, 8]`), rotación pseudoaleatoria determinista para recortes de periódicos y animación de impacto de chinchetas con *overshoot* inercial ($S(0) = 145\%$).
- **Archivos:**
  - `[NEW]` `src/styles/presets/InvestigativeCartographerPreset.ts`
  - `[NEW]` `src/tests/styles/InvestigativeCartographer.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **668/668 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #025: Preset #2 — Dark Noir Business Empire (`DarkNoirBusinessPreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/DarkNoirBusinessPreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/DarkNoirBusiness.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para implementar de forma determinista el segundo preset maestro para documentales dramáticos de negocios estilo MagnatesMedia y Neo.
- **¿Para qué se agregó?:**
  - Provee `DarkNoirBusinessPreset` con efecto *3D Photo Parallax Cutout* (fondo con Fast Blur $28\text{px}$ + Tint $45\%$, sujeto con slow push-in hacia la cámara en $Z$), destello anamórfico (*CC Light Sweep*) sobre títulos dorados (`Cinzel`) y contadores de riqueza con desaceleración cúbica Ease-Out.
- **Archivos:**
  - `[NEW]` `src/styles/presets/DarkNoirBusinessPreset.ts`
  - `[NEW]` `src/tests/styles/DarkNoirBusiness.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **672/672 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #026: Presets Batch #3, #4 y #5 — Science, Cipher & Productivity (`ScientificBlueprintPreset`, `MinimalistCipherPreset`, `ProductivityPapercraftPreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/ScientificBlueprintPreset.ts`, `src/styles/presets/MinimalistCipherPreset.ts`, `src/styles/presets/ProductivityPapercraftPreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/PresetsBatch345.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para dotar a la IA de herramientas especializadas para videos científicos/educativos (*Veritasium*), misterio minimalista (*Lemmino*) y productividad (*Ali Abdaal*).
- **¿Para qué se agregó?:**
  - Provee `ScientificBlueprintPreset` (cálculo de distancias euclidianas, ángulos y cotas de medición vectorial animadas), `MinimalistCipherPreset` (formateo militar de coordenadas GPS y escaneo láser vertical) y `ProductivityPapercraftPreset` (tarjetas Notion flotantes con física de resorte inercial $S(t) = 100(1 - e^{-8t}\cos(20t))$).
- **Archivos:**
  - `[NEW]` `src/styles/presets/ScientificBlueprintPreset.ts`
  - `[NEW]` `src/styles/presets/MinimalistCipherPreset.ts`
  - `[NEW]` `src/styles/presets/ProductivityPapercraftPreset.ts`
  - `[NEW]` `src/tests/styles/PresetsBatch345.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **676/676 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #027: Presets Batch #6, #7 y #8 — Agency Luxury, Beast Retention & Hormozi Cashflow (`AgencyLuxuryPreset`, `HyperRetentionBeastPreset`, `HormoziCashflowPreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/AgencyLuxuryPreset.ts`, `src/styles/presets/HyperRetentionBeastPreset.ts`, `src/styles/presets/HormoziCashflowPreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/PresetsBatch678.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para cubrir los formatos virales más demandados de YouTube y redes sociales: alta moda y agencia (*Iman Gadzhi*), adrenalina extrema y retención (*MrBeast*) y subtitulado directo reactivo (*Alex Hormozi*).
- **¿Para qué se agregó?:**
  - Provee `AgencyLuxuryPreset` (marcos de película 16mm/35mm y titulares `Bodoni MT`), `HyperRetentionBeastPreset` (títulos 3D con borde negro 14px y flechas con rebote sinusoidal $y(t) = y_0 + 20\sin(12t)$) y `HormoziCashflowPreset` (subtítulos adaptativos `The Bold Font` con resaltado verde/amarillo y punch zooms súbitos).
- **Archivos:**
  - `[NEW]` `src/styles/presets/AgencyLuxuryPreset.ts`
  - `[NEW]` `src/styles/presets/HyperRetentionBeastPreset.ts`
  - `[NEW]` `src/styles/presets/HormoziCashflowPreset.ts`
  - `[NEW]` `src/tests/styles/PresetsBatch678.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **680/680 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #028: Presets Batch #9, #10 y #11 — True Crime, Cinematic Flow Vlog & SaaS Showcase (`TrueCrimeEvidencePreset`, `CinematicFlowVlogPreset`, `SaaSTechShowcasePreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/TrueCrimeEvidencePreset.ts`, `src/styles/presets/CinematicFlowVlogPreset.ts`, `src/styles/presets/SaaSTechShowcasePreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/PresetsBatch91011.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para dotar al motor de capacidades cinemáticas para documentales de crímenes/misterio, vlogs de viajes cinematográficos y demostraciones de productos de software / SaaS.
- **¿Para qué se agregó?:**
  - Provee `TrueCrimeEvidencePreset` (hilos rojos de evidencia elásticos con catenaria/sag gravitatorio y sellos `CLASSIFIED` a $-12^\circ$), `CinematicFlowVlogPreset` (transiciones de máscara de cielo *Sky Mask* con feather de $120\text{px}$ y títulos 3D en el horizonte) y `SaaSTechShowcasePreset` (ondas de clic de cursor interactivo y ventanas flotantes con Glassmorphism).
- **Archivos:**
  - `[NEW]` `src/styles/presets/TrueCrimeEvidencePreset.ts`
  - `[NEW]` `src/styles/presets/CinematicFlowVlogPreset.ts`
  - `[NEW]` `src/styles/presets/SaaSTechShowcasePreset.ts`
  - `[NEW]` `src/tests/styles/PresetsBatch91011.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **684/684 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #029: Presets Batch #12, #13, #14 y #15 — Finance, Sports, Retro & TIME Editorial (`WallStreetFinancePreset`, `SportsEnergyPreset`, `RetroSynthwavePreset`, `TimeEditorialPosterPreset`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `src/styles/presets/WallStreetFinancePreset.ts`, `src/styles/presets/SportsEnergyPreset.ts`, `src/styles/presets/RetroSynthwavePreset.ts`, `src/styles/presets/TimeEditorialPosterPreset.ts`, `src/styles/StyleProfileManager.ts`, `src/tests/styles/PresetsFinalBatch.test.ts`, `src/tests/v2/AutonomousMCPv2.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para culminar los 15 Presets de Creadores y Estilos Profesionales solicitados por el usuario, culminando con el estilo insignia maestro *TIME Editorial News Poster*.
- **¿Para qué se agregó?:**
  - Provee `WallStreetFinancePreset` (velas de trading japonesas alcistas/bajistas animadas y tickers bursátiles), `SportsEnergyPreset` (cronómetros deportivos continuos de milisegundos y tipografía Teko $130\%$), `RetroSynthwavePreset` (suelo 3D de rejilla en perspectiva hacia el horizonte y sol 80s con glow) y `TimeEditorialPosterPreset` (estilo insignia maestro con Impact ultra-condensada estirada al $140\%$, marco carmesí `#FF1424`, interletraje negativo, diales vectoriales y motion blur total).
- **Archivos:**
  - `[NEW]` `src/styles/presets/WallStreetFinancePreset.ts`
  - `[NEW]` `src/styles/presets/SportsEnergyPreset.ts`
  - `[NEW]` `src/styles/presets/RetroSynthwavePreset.ts`
  - `[NEW]` `src/styles/presets/TimeEditorialPosterPreset.ts`
  - `[NEW]` `src/tests/styles/PresetsFinalBatch.test.ts`
  - `[MODIFY]` `src/styles/StyleProfileManager.ts`
  - `[MODIFY]` `src/tests/v2/AutonomousMCPv2.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **689/689 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #030: Producción Audiovisual con Metraje Real — 'Guadalajara 2023 // El Arte de Disfrutar' (`generate-guadalajara-video` & `GuadalajaraProduction.test`)
- **Fecha:** 2026-08-27
- **Módulos Afectados:** `scripts/generate-guadalajara-video.mjs`, `dist/guadalajara_2023_production.jsx`, `projects/guadalajara_2023_master.json`, `src/tests/production/GuadalajaraProduction.test.ts`, `package.json`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para generar un video cinematográfico completo y ejecutable utilizando el metraje real del usuario (`E:\Respaldo\Guadalajara junio 23...`) combinando los motores de estilo insignia desarrollados en el proyecto.
- **¿Para qué se agregó?:**
  - Orquesta un video vertical 9:16 (1080x1920, 60fps, 35s) estructurado en 4 capítulos narrativos:
    1. **Capítulo 1:** Coordenadas GPS de Guadalajara ($20.6597^\circ\text{ N}, 103.3496^\circ\text{ W}$) + HUD Overlay + Entrada cinética masiva.
    2. **Capítulo 2:** Speed ramping sobre metraje nocturno + dial vectorial de acompañamiento en rotación + texto carmesí `#FF1424` ("VIVE LA NOCHE").
    3. **Capítulo 3:** Recuerdo 3D Polaroid con sombra proyectada difusa y slow push-in.
    4. **Capítulo 4:** Marco perimetral carmesí TIME Magazine + titular héroe masivo `Impact` estirado al $140\%$ ("EL ARTE DE DISFRUTAR") con `comp.motionBlur = true`.
- **Archivos:**
  - `[NEW]` `scripts/generate-guadalajara-video.mjs`
  - `[NEW]` `dist/guadalajara_2023_production.jsx`
  - `[NEW]` `projects/guadalajara_2023_master.json`
  - `[NEW]` `src/tests/production/GuadalajaraProduction.test.ts`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **692/692 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #031: Suite de Automatización Total para TikTok y YouTube — Autonomous Content Factory (`src/automation/`)
- **Fecha:** 2026-08-28
- **Módulos Afectados:** `src/automation/transcription/LocalWhisperTranscriptionBridge.ts`, `src/automation/clipping/ViralMomentDetector.ts`, `src/automation/reframing/ActiveSpeakerReframingEngine.ts`, `src/automation/voiceover/VoiceoverTimingSynchronizer.ts`, `src/automation/packaging/SocialLaunchPackager.ts`, `src/automation/render/HeadlessRenderOrchestrator.ts`, `src/automation/index.ts`, `src/index.ts`, `src/tests/automation/AutonomousContentFactory.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para transformar el motor en una fábrica 100% autónoma y desatendida de generación de clips para TikTok/Reels y videos de YouTube sin costo adicional de APIs ni intervención humana manual.
- **¿Para qué se agregó?:**
  - Implementa los 5 subsistemas de producción desatendida:
    1. `LocalWhisperTranscriptionBridge`: Transcripción fonética palabra por palabra con Whisper local ($0 costo, 100% offline).
    2. `ViralMomentDetector`: Detección algorítmica de los mejores 30s-60s evaluando Hook, Pacing/WPM y Climax con scoring predictivo de retención ($0-100$).
    3. `ActiveSpeakerReframingEngine`: Reencuadre dinámico de 16:9 a 9:16 con zonas muertas anti-jitter y Split-Screen apilado (hablante arriba, B-roll abajo).
    4. `VoiceoverTimingSynchronizer`: Sincronización de guiones locutados y corte en pausas naturales de respiración.
    5. `SocialLaunchPackager` & `HeadlessRenderOrchestrator`: Generación de 3 títulos A/B High-CTR, descripción con capítulos automáticos, hashtags para TikTok y comandos de render en segundo plano (`aerender` / FFmpeg).
- **Archivos:**
  - `[NEW]` `src/automation/transcription/LocalWhisperTranscriptionBridge.ts`
  - `[NEW]` `src/automation/clipping/ViralMomentDetector.ts`
  - `[NEW]` `src/automation/reframing/ActiveSpeakerReframingEngine.ts`
  - `[NEW]` `src/automation/voiceover/VoiceoverTimingSynchronizer.ts`
  - `[NEW]` `src/automation/packaging/SocialLaunchPackager.ts`
  - `[NEW]` `src/automation/render/HeadlessRenderOrchestrator.ts`
  - `[NEW]` `src/automation/index.ts`
  - `[NEW]` `src/tests/automation/AutonomousContentFactory.test.ts`
  - `[MODIFY]` `src/index.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **704/704 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #032: Herramientas MCP de Automatización, Pipeline CLI de 1-Clic Auto-Clip & Banco SFX WAV Procedural (`src/mcp/tools/`, `src/automation/pipeline/`, `src/audio-design/`)
- **Fecha:** 2026-08-28
- **Módulos Afectados:** `src/mcp/tools/transcribe-local-audio.ts`, `src/mcp/tools/detect-viral-clips.ts`, `src/mcp/tools/package-social-release.ts`, `src/mcp/tools/auto-reframe-video.ts`, `src/mcp/registry.ts`, `src/automation/pipeline/AutoClipPipelineOrchestrator.ts`, `bin/auto-clip.js`, `src/audio-design/SoundBankManager.ts`, `src/tests/automation/MCPAutomationTools.test.ts`, `src/tests/automation/AutoClipPipeline.test.ts`, `src/tests/automation/SoundBankManager.test.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó?:**
  - Para permitir a cualquier agente IA o usuario operar todo el ciclo de producción en 1 solo clic o llamada JSON-RPC estructurada, e incorporar efectos de sonido físicos PCM WAV reales importados a After Effects sin requerir bibliotecas externas pesadas.
- **¿Para qué se agregó?:**
  - Integra 4 herramientas formales en el servidor MCP:
    - `transcribe_local_audio`: Transcripción fonética local y síntesis determinista.
    - `detect_viral_clips`: Detección y ranking de momentos virales con scoring predictivo.
    - `package_social_release`: Generación de títulos A/B, capítulos formateados y hashtags.
    - `auto_reframe_video`: Reencuadre dinámico 16:9 a 9:16 con deadzones.
  - Implementa el pipeline CLI de 1-clic `AutoClipPipelineOrchestrator` (`node bin/auto-clip.js` o `npm run auto-clip`) que toma un video crudo y produce automáticamente 3 TikToks terminados con scripts JSX listos.
  - Implementa `SoundBankManager` con síntesis determinista de archivos WAV de 16-bit / 44.1kHz (Whoosh, Impact Boom, UI Pop, Camera Shutter, Bell Chime) y generador de fragmentos ExtendScript para importar el banco SFX a After Effects.
- **Archivos:**
  - `[NEW]` `src/mcp/tools/transcribe-local-audio.ts`
  - `[NEW]` `src/mcp/tools/detect-viral-clips.ts`
  - `[NEW]` `src/mcp/tools/package-social-release.ts`
  - `[NEW]` `src/mcp/tools/auto-reframe-video.ts`
  - `[NEW]` `src/automation/pipeline/AutoClipPipelineOrchestrator.ts`
  - `[NEW]` `bin/auto-clip.js`
  - `[NEW]` `src/audio-design/SoundBankManager.ts`
  - `[NEW]` `src/tests/automation/MCPAutomationTools.test.ts`
  - `[NEW]` `src/tests/automation/AutoClipPipeline.test.ts`
  - `[NEW]` `src/tests/automation/SoundBankManager.test.ts`
  - `[MODIFY]` `src/mcp/registry.ts`
  - `[MODIFY]` `src/automation/index.ts`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **712/712 pruebas automatizadas pasando al 100% en verde** (`npm run conformance`).

---

### 🛠️ Mejora #033: Suite de Producción Vlog / Documental Multilingüe v3.5.0 (Milestones M1 a M9)
- **Fecha:** 2026-09-01
- **Módulos Afectados:** `src/vlog/contracts/`, `src/vlog/ingestion/`, `src/vlog/classifier/`, `src/vlog/jumpcut/`, `src/vlog/voiceover/`, `src/vlog/pacing/`, `src/vlog/subtitles/`, `src/vlog/overlays/`, `src/vlog/audio/`, `src/vlog/exporter/`, `src/vlog/orchestrator/`, `src/vlog/index.ts`, `src/tests/vlog/`
- **¿Por qué se agregó?:**
  - Para dotar al motor de capacidades nativas completas para producción de vlogs, documentales y videos de viajes multilingües con cero costos mandatorios de API (offline-first), eliminando silencios mediante jump cuts, aplicando dynamic punch-ins, adaptando la línea temporal a la duración de cada locución por idioma, generando subtítulos karaoke en 7 locales, renderizando overlays cartográficos con fórmula Haversine y exportando proyectos ExtendScript JSX completos para Adobe After Effects conforme al estándar de diseño TIME Editorial.
- **¿Para qué se agregó?:**
  - Implementa la arquitectura completa de 9 milestones:
    - **M1 (Contracts):** 17 esquemas Zod e interfaces para clasificación, jump cuts, pacing, subtítulos, overlays, audio y orquestación.
    - **M2 (Media Intelligence):** Ingesta determinista con hash SHA-256, clasificador semántico A-Roll/B-Roll y matcher de metraje de apoyo.
    - **M3 (Vlog Editing):** Detección y poda de silencios con micro-crossfades de 10 ms y dynamic punch-in con preservación estricta de la precedencia `B-Roll > Punch-In`.
    - **M4 (Voiceover TTS):** Síntesis de voz offline para 7 locales (`es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`), normalizador de texto y validador canónico WAV 44.1 kHz 16-bit mono.
    - **M5 (Adaptive Pacing):** Retiming visual no destructivo, time-stretch vocal acotado $[0.95, 1.05]$ y resolución de anclas narrativas.
    - **M6 (Subtitles & Overlays):** Subtítulos karaoke sincronizados palabra por palabra, Haversine canónico con $\text{EARTH\_MEAN\_RADIUS\_KM} = 6371.0088$, Polaroid determinista con shutter SFX a $\pm 1\text{ frame}$, y SafeZoneLayoutEngine multi-aspecto protegiendo UI social en 9:16.
    - **M7 (Audio Mixing & AE JSX):** Buses jerárquicos de audio con Auto-Ducking (-10 dB, 0.12 s ataque, 0.40 s relajación, anti-pumping) y compilador ExtendScript JSX con `comp.motionBlur = true` y estilo TIME Editorial.
    - **M8 (Production Orchestrator):** FSM y DAG de 22 fases (`P00_INITIALIZE` a `P21_COMPLETE`) emitiendo `VlogManifest` con `productionHash` SHA-256 inmutable.
    - **M9 (Full Validation):** Pruebas E2E en 5 locales $\times$ 5 aspect ratios (25 composiciones), determinismo byte a byte, aislamiento lingüístico, tolerancia a fallos y PBT con `fast-check`.
- **Archivos:**
  - `[NEW]` 17 archivos de contratos en `src/vlog/contracts/`
  - `[NEW]` Módulos de ingesta y clasificación en `src/vlog/ingestion/` y `src/vlog/classifier/`
  - `[NEW]` Módulos de edición en `src/vlog/jumpcut/`
  - `[NEW]` Módulos de locución y TTS en `src/vlog/voiceover/`
  - `[NEW]` Módulos de pacing adaptativo en `src/vlog/pacing/`
  - `[NEW]` Módulos de subtítulos en `src/vlog/subtitles/`
  - `[NEW]` Módulos de overlays y geodesia en `src/vlog/overlays/`
  - `[NEW]` Módulos de mezcla de audio en `src/vlog/audio/`
  - `[NEW]` Módulos de exportación JSX en `src/vlog/exporter/`
  - `[NEW]` Módulos de orquestación en `src/vlog/orchestrator/`
  - `[NEW]` 40 archivos de suites de pruebas en `src/tests/vlog/`
  - `[MODIFY]` `src/vlog/index.ts`
  - `[MODIFY]` `src/index.ts`
- **Verificación:** **884/884 pruebas automatizadas pasando al 100% en verde** (`npm test`), build limpio con `tsc` strict.

---

### 🛠️ Mejora #034: Fase 4A — Editorial Core & Multi-Format Profiles (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/`, `src/editorial/profiles/`, `src/editorial/silence/`, `src/editorial/knowledge/`, `src/editorial/director/`, `src/editorial/index.ts`, `src/index.ts`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para transformar el motor de un ensamblador de vlogs en una plataforma editorial agnóstica al género (v4.0.0), capaz de entender qué tipo de obra audiovisual está editando (Vlog, Documental, Periodismo, Entrevistas, etc.) y aplicar las reglas de montaje correspondientes sin destruir el baseline previo.
- **¿Para qué se agregó?:**
  - Implementa el núcleo editorial de la v4.0 según `spec/MASTER-CONTENT-ENGINE-v4.md`:
    - **Contratos y Esquemas (REQ-001, REQ-002, REQ-003):** `EditorialProfileSchema`, `ProductionIntentSchema`, `ClassifiedSilenceSchema` y `EditorialDecisionGraphSchema`.
    - **Registro de 10 Perfiles Canónicos (REQ-001):** `VLOG`, `DOCUMENTARY`, `JOURNALISM`, `EDUCATIONAL`, `INTERVIEW`, `NEWS`, `CINEMATIC`, `CORPORATE`, `SHORT_FORM`, `TECHNICAL` con resolución automática e inferencia desde `AUTO`.
    - **Jerarquía Universal de Precedencia (REQ-076):** Implementación formal de `SAFETY > LEGAL_FACTUAL > EDITOR_LOCK > NARRATIVE > CONTINUITY > AUDIO > VISUAL > STYLE > OPTIMIZATION`.
    - **Inteligencia de Silencios (REQ-006, REQ-068):** `SilenceIntelligenceEngine` que categoriza pausas (`FILLER`, `BREATH`, `THINKING`, `DRAMATIC`, `ROOM_TONE`) preservando la tensión dramática en documental y podando en vlog.
    - **Grafo de Conocimiento del Proyecto (REQ-041):** `ProjectKnowledgeGraphEngine` con indexación de personas, lugares, afirmaciones, escenas y planos con checksum SHA-256 inmutable.
    - **Director Editorial y Explicabilidad (REQ-031, REQ-032):** `EditorialDirectorEngine` que calcula el `EditorialScore` multidimensional y emite el `EditorialDecisionGraph` con justificación causal auditable.
- **Archivos:**
  - `[NEW]` `src/editorial/contracts/content-profile.types.ts`
  - `[NEW]` `src/editorial/contracts/production-intent.types.ts`
  - `[NEW]` `src/editorial/contracts/silence-intelligence.types.ts`
  - `[NEW]` `src/editorial/contracts/rule-precedence.types.ts`
  - `[NEW]` `src/editorial/contracts/decision-graph.types.ts`
  - `[NEW]` `src/editorial/contracts/knowledge-graph.types.ts`
  - `[NEW]` `src/editorial/contracts/index.ts`
  - `[NEW]` `src/editorial/profiles/profile-registry.ts`
  - `[NEW]` `src/editorial/profiles/index.ts`
  - `[NEW]` `src/editorial/silence/silence-intelligence-engine.ts`
  - `[NEW]` `src/editorial/silence/index.ts`
  - `[NEW]` `src/editorial/knowledge/project-knowledge-graph.ts`
  - `[NEW]` `src/editorial/knowledge/index.ts`
  - `[NEW]` `src/editorial/director/editorial-director-engine.ts`
  - `[NEW]` `src/editorial/director/index.ts`
  - `[NEW]` `src/editorial/index.ts`
  - `[NEW]` `src/tests/editorial/EditorialProfileRegistry.test.ts`
  - `[NEW]` `src/tests/editorial/SilenceIntelligenceEngine.test.ts`
  - `[NEW]` `src/tests/editorial/ProjectKnowledgeGraph.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialDirectorEngine.test.ts`
  - `[MODIFY]` `src/index.ts`
- **Verificación:** **903/903 pruebas pasando al 100% en verde** (`npm test`), 0 fallos, 0 regresiones sobre los 884 tests del Gold Master v3.5.0.

---

### 🛠️ Mejora #035: Fase 4B — Visual & Acoustic Continuity (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/continuity/`, `src/editorial/broll/`, `src/editorial/sound/`, `src/editorial/multicam/`, `src/editorial/index.ts`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para dotar a la plataforma v4.0.0 de reglas formales de gramática cinematográfica y diseño acústico profesional, auditando saltos de eje, dirección de pantalla y temperatura de color, evitando clichés en B-roll y sincronizando J-Cuts, L-Cuts y conmutaciones multi-cámara sin desorientar al espectador.
- **¿Para qué se agregó?:**
  - Implementa las capacidades de continuidad audiovisual según `spec/MASTER-CONTENT-ENGINE-v4.md`:
    - **Visual Continuity Engine (REQ-005, REQ-017, REQ-018, REQ-056):** Detección de cruces de eje de $180^\circ$, inversiones de dirección de pantalla, colisiones de mirada (*eyeline*) y saltos de temperatura de color $>800\text{K}$.
    - **Semantic B-Roll Director 2.0 (REQ-013, REQ-014):** Motor de scoring conceptual y emocional con **penalización exponencial anti-repetición** ($P = 1 - e^{-0.7k}$) para suprimir clips cliché.
    - **Sound Design & Acoustic Continuity (REQ-020, REQ-062, REQ-063):** Planificación automática de **J-Cuts y L-Cuts** acotados ($0.2\text{--}1.5\text{s}$), parcheo de *Room Tone* en silencios para evitar cero absoluto digital, y puentes sonoros diegéticos.
    - **Multi-Camera Director (REQ-011, REQ-012):** Conmutación por seguimiento de hablante, **protección estricta de picos emocionales y testimonios clave**, supresión de *ping-pong cuts* rápidos y reseteo espacial periódico con plano general (`WIDE`).
- **Archivos:**
  - `[NEW]` `src/editorial/continuity/visual-continuity.types.ts`
  - `[NEW]` `src/editorial/continuity/visual-continuity-engine.ts`
  - `[NEW]` `src/editorial/continuity/index.ts`
  - `[NEW]` `src/editorial/broll/semantic-broll.types.ts`
  - `[NEW]` `src/editorial/broll/semantic-broll-director.ts`
  - `[NEW]` `src/editorial/broll/index.ts`
  - `[NEW]` `src/editorial/sound/sound-design.types.ts`
  - `[NEW]` `src/editorial/sound/sound-design-engine.ts`
  - `[NEW]` `src/editorial/sound/index.ts`
  - `[NEW]` `src/editorial/multicam/multicam.types.ts`
  - `[NEW]` `src/editorial/multicam/multicam-director.ts`
  - `[NEW]` `src/editorial/multicam/index.ts`
  - `[NEW]` `src/tests/editorial/VisualContinuityEngine.test.ts`
  - `[NEW]` `src/tests/editorial/SemanticBRollDirector.test.ts`
  - `[NEW]` `src/tests/editorial/SoundDesignEngine.test.ts`
  - `[NEW]` `src/tests/editorial/MultiCameraDirector.test.ts`
  - `[MODIFY]` `src/editorial/index.ts`
- **Verificación:** **924/924 pruebas pasando al 100% en verde** (`npm test`), 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #036: Fase 4C — Editorial Intermediate Representation & Universal Exporter (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/ir/`, `src/editorial/exporters/`, `src/editorial/qa/`, `src/editorial/index.ts`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para consumar el desacoplamiento total entre la planificación editorial y la renderización en el motor (v4.0.0), convirtiendo la `Editorial IR` en la única fuente de verdad inmutable y permitiendo exportar proyectos nativos sin pérdidas a OpenTimelineIO, Final Cut Pro XML v1.9 (compatible con Premiere y DaVinci Resolve) y After Effects JSX, complementado con un sistema de Quality Assurance automatizado previo a exportación.
- **¿Para qué se agregó?:**
  - Implementa la capa de compilación audiovisual universal según `spec/MASTER-CONTENT-ENGINE-v4.md`:
    - **Editorial IR Core (REQ-021, REQ-022):** Esquema canónico multi-pista (`VIDEO_PRIMARY`, `VIDEO_BROLL`, `VIDEO_GRAPHICS`, `AUDIO_DIALOGUE`, `AUDIO_MUSIC`, `AUDIO_SFX`, `AUDIO_AMBIENCE`, `SUBTITLE`), clips con rangos de tiempo fuente y destino, transiciones (`CROSS_DISSOLVE`, `J_CUT`, `L_CUT`, `DIP_TO_BLACK`, `WIPE`), marcadores y firma inmutable SHA-256 (`EditorialIRBuilder`).
    - **OpenTimelineIO Exporter (REQ-023):** Transpila la IR a esquemas nativos `Timeline.1` y `Track.1` con tiempos racionales `RationalTime` (`OtioExporter`).
    - **Final Cut Pro XML Exporter (REQ-024):** Genera XML FCPXML v1.9 con recursos, formatos, assets, spine, clips de audio y vídeo conectados y marcadores para Apple Final Cut Pro, DaVinci Resolve y Adobe Premiere Pro (`FcpxmlExporter`).
    - **After Effects ExtendScript JSX Exporter v4 (REQ-025):** Compilador multi-formato respetando perfiles y directrices visuales de `USER_DESIGN_PREFERENCES.md` (`comp.motionBlur = true`, alineación centrada de textos y niveles de audio) (`JsxExporterV4`).
    - **Editorial QA Engine 2.0 (REQ-036, REQ-037, REQ-038):** Verificador previo a exportación que intercepta fotogramas negros inadvertidos (`TRACK_GAP`), flash frames menores a 0.1s (`FLASH_FRAME`) y saturación de audio (`AUDIO_CLIPPING`).
- **Archivos:**
  - `[NEW]` `src/editorial/ir/editorial-ir.types.ts`
  - `[NEW]` `src/editorial/ir/editorial-ir-builder.ts`
  - `[NEW]` `src/editorial/ir/index.ts`
  - `[NEW]` `src/editorial/exporters/otio-exporter.ts`
  - `[NEW]` `src/editorial/exporters/fcpxml-exporter.ts`
  - `[NEW]` `src/editorial/exporters/jsx-exporter-v4.ts`
  - `[NEW]` `src/editorial/exporters/index.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa.types.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-engine.ts`
  - `[NEW]` `src/editorial/qa/index.ts`
  - `[NEW]` `src/tests/editorial/EditorialIRBuilder.test.ts`
  - `[NEW]` `src/tests/editorial/OtioExporter.test.ts`
  - `[NEW]` `src/tests/editorial/FcpxmlExporter.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialQaEngine.test.ts`
  - `[MODIFY]` `src/editorial/index.ts`
- **Verificación:** **936/936 pruebas pasando al 100% en verde** (`npm test`), 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #037: Fase 4D — Multi-Version Editorial Compiler & Platform Packaging (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/compiler/`, `src/editorial/packaging/`, `src/editorial/localization/`, `src/editorial/index.ts`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para permitir que una única obra audiovisual maestra (`EditorialIR`) se compile de manera no destructiva en múltiples formatos de duración (Full, 60s, 30s, 15s, 6s), múltiples aspect ratios (16:9, 9:16, 1:1, 4:5, 21:9) y se empaquete con los estándares técnicos y de sonoridad específicos de cada plataforma de distribución (YouTube, TikTok/Reels, Broadcast EBU R128, Cinema DCI), coordinando además la localización limpia multi-idioma.
- **¿Para qué se agregó?:**
  - Implementa el compilador multi-versión y empaquetador según `spec/MASTER-CONTENT-ENGINE-v4.md`:
    - **Multi-Version Compiler (REQ-026, REQ-027, REQ-028):** Generación de variantes derivadas respetando cotas de duración y sintaxis narrativa, re-temporizando pistas de forma continua y sellando cada plan con hash SHA-256 (`MultiVersionCompiler`).
    - **Platform Packager (REQ-029, REQ-030):** Empaquetado formal verificando aspect ratios, aplicando sonoridad LUFS de destino (-16 para YouTube, -14 para TikTok/Reels, -23 para EBU R128, -24 para DCI) y configurando Safe Zones con exclusión de UI social (`PlatformPackager`).
    - **Localization Orchestrator 2.0 (REQ-071, REQ-072, REQ-073):** Ensamblado de variantes por idioma para 7 locales (`es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`) intercambiando pistas de diálogo y subtítulos sin alterar las pistas visuales ni las músicas (`EditorialLocalizationOrchestrator`).
- **Archivos:**
  - `[NEW]` `src/editorial/compiler/multi-version.types.ts`
  - `[NEW]` `src/editorial/compiler/multi-version-compiler.ts`
  - `[NEW]` `src/editorial/compiler/index.ts`
  - `[NEW]` `src/editorial/packaging/platform-packaging.types.ts`
  - `[NEW]` `src/editorial/packaging/platform-packager.ts`
  - `[NEW]` `src/editorial/packaging/index.ts`
  - `[NEW]` `src/editorial/localization/editorial-localization.types.ts`
  - `[NEW]` `src/editorial/localization/editorial-localization-orchestrator.ts`
  - `[NEW]` `src/editorial/localization/index.ts`
  - `[NEW]` `src/tests/editorial/MultiVersionCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/PlatformPackager.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialLocalizationOrchestrator.test.ts`
  - `[MODIFY]` `src/editorial/index.ts`
- **Verificación:** **928/928 pruebas pasando al 100% en verde** (`npm test`), 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #038: Fase 4E — Documentary Narrative Arc, Fact & Evidence Layer, Archival Media & Credits Compiler (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/`, `src/editorial/narrative/`, `src/editorial/evidence/`, `src/editorial/archive/`, `src/editorial/credits/`, `src/editorial/index.ts`, `src/tests/editorial/`, `src/tests/runtime/`
- **¿Por qué se agregó?:**
  - Para completar las capacidades documentales, de verificación factual y de tratamiento de archivo de la especificación `spec/MASTER-CONTENT-ENGINE-v4.md`, dotando a la plataforma de estructuración formal en 10 beats canónicos, grafos de causalidad narrativa, auditoría rigurosa de fuentes e información, animación determinista Ken Burns para imágenes fijas de archivo, control de licencias y compilación automatizada de créditos y rótulos inferiores acordes al estilo insignia TIME Editorial.
- **¿Para qué se agregó?:**
  - Implementa los módulos de narrativa, evidencia, archivo y créditos según `spec/MASTER-CONTENT-ENGINE-v4.md`:
    - **Narrative Arc Engine (REQ-008, REQ-044, REQ-045):** Estructura en 10 beats documentales (`HOOK`, `CONTEXT`, `QUESTION`, `EVIDENCE`, `TESTIMONY`, `CONFLICT`, `ESCALATION`, `REVELATION`, `RESOLUTION`, `REFLECTION`), grafo de causalidad que detecta inversiones cronológicas no deseadas, blindaje contra revelaciones prematuras de evidencia (*spoilers*) y cálculo de la curva de energía narrativa continua `energy(t)` (`NarrativeArcEngine`).
    - **Fact & Evidence Engine (REQ-009, REQ-010):** Auditoría de afirmaciones (`claims`), verificación de fuentes de respaldo, detección de faltas de atribución (`MISSING_SOURCE`), cálculo de `evidenceIntegrityScore` (0-100) y generación sincronizada de tarjetas de citación en pantalla (`EvidenceEngine`).
    - **Archival Media Engine (REQ-016, REQ-087):** Movimiento suave Ken Burns 2D determinista para fotografías y planos fijos (pan y zoom de $1.05\text{x}$ a $1.15\text{x}$ acotado en $[0.5, 3.0]$), estampado de fechas históricas estandarizadas ("FILE FOOTAGE // YYYY") y auditoría de licencias expiradas o restringidas (`ArchivalMediaEngine`).
    - **Credits & Attribution Compiler (REQ-088, REQ-089):** Compilador automatizado de lower-thirds de oradores con tipografía `TIME_INSIGNIA` en mayúsculas, créditos de repositorios de archivo, música y reparto de voces documentales estructurado en tarjetas fijas o crawl vertical continuo (`CreditsCompiler`).
    - **Blindaje de Concurrencia en Windows:** Corrección de la ruta de almacenamiento en `AtomicWritesAndRecovery.test.ts` hacia `os.tmpdir()`, y adición de `{ maxRetries: 5, retryDelay: 100 }` en limpiezas temporales de voz para erradicar carreras con el indexador de archivos de Windows (`ENOTEMPTY`).
- **Archivos:**
  - `[NEW]` `src/editorial/contracts/narrative.types.ts`
  - `[NEW]` `src/editorial/contracts/evidence.types.ts`
  - `[NEW]` `src/editorial/contracts/archive.types.ts`
  - `[NEW]` `src/editorial/contracts/credits.types.ts`
  - `[NEW]` `src/editorial/narrative/narrative-arc-engine.ts`
  - `[NEW]` `src/editorial/narrative/index.ts`
  - `[NEW]` `src/editorial/evidence/evidence-engine.ts`
  - `[NEW]` `src/editorial/evidence/index.ts`
  - `[NEW]` `src/editorial/archive/archival-media-engine.ts`
  - `[NEW]` `src/editorial/archive/index.ts`
  - `[NEW]` `src/editorial/credits/credits-compiler.ts`
  - `[NEW]` `src/editorial/credits/index.ts`
  - `[NEW]` `src/tests/editorial/NarrativeArcEngine.test.ts`
  - `[NEW]` `src/tests/editorial/EvidenceEngine.test.ts`
  - `[NEW]` `src/tests/editorial/ArchivalMediaEngine.test.ts`
  - `[NEW]` `src/tests/editorial/CreditsCompiler.test.ts`
  - `[MODIFY]` `src/editorial/contracts/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `src/tests/runtime/AtomicWritesAndRecovery.test.ts`
  - `[MODIFY]` `src/tests/vlog/voiceover/MultilingualVoiceoverEngine.test.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **946/946 pruebas pasando al 100% en verde** (`npm test`), 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #039: Public Vlog CLI, MCP Tools & Declarative Production DSL Integration (v3.5.0 / v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `bin/`, `src/mcp/`, `src/dsl/`, `package.json`, `scripts/`, `src/tests/`
- **¿Por qué se agregó?:**
  - Para completar las interfaces públicas y de control de agente de la suite **Vlog Intelligence (v3.5.0)** según los documentos de especificación `docs/vlog-expansion/14-MCP-INTEGRATION.md`, `15-DSL-INTEGRATION.md` y `MASTER-IMPLEMENTATION-AND-ACCEPTANCE-SPECIFICATION.md` (§45 y §46), permitiendo a agentes externos y a desarrolladores invocar cortes por saltos, clasificación de metraje, emparejamiento de B-roll y producción multilingüe autónoma tanto por MCP como por CLI y bloques compactos DSL.
- **¿Para qué se agregó?:**
  - **Herramientas MCP de Vlog (`src/mcp/tools/vlog-tools.ts`, `src/mcp/registry.ts`):**
    - `vlog_generate_jump_cut_plan`: Cálculo determinista de silencios eliminados, protección fonética y punch-ins con `VlogJumpCutEngine`.
    - `vlog_classify_footage`: Clasificación probabilística con extracción automática de tags a partir del nombre de archivo y flujo óptico realista con `VlogFootageClassifier`.
    - `vlog_match_broll`: Emparejamiento semántico de B-roll multicriterio con normalización sin acentos y ranking contextual con `VlogBRollMatcher`.
    - `vlog_produce`: Orquestación autónoma de 22 fases a través del DAG multilingüe con `VlogMultilingualProductionOrchestrator`.
    - `vlog_get_status`: Consulta en memoria de estados de fases, manifiesto de entrega y artefactos con checksum SHA-256.
  - **Extensión Declarativa del Production DSL (`src/dsl/ProductionDSL.ts`):**
    - Soporte para directivas de vlog (`vlog: { enabled: true, autoJumpCut, punchInScale, travelOverlays, targetLanguages }`) manteniendo 100% de compatibilidad hacia atrás con el DSL base.
  - **CLI Autónomo de Producción (`bin/vlog-cli.js`, `package.json`):**
    - Comando ejecutable `npm run vlog:produce` con soporte para `--manifest`, `--script`, `--languages`, `--source-lang`, `--aspects`, `--output`, `--project-id` y `--dry-run`.
- **Archivos:**
  - `[NEW]` `bin/vlog-cli.js`
  - `[NEW]` `src/mcp/tools/vlog-tools.ts`
  - `[NEW]` `src/tests/mcp/MCPVlogTools.test.ts`
  - `[NEW]` `src/tests/dsl/VlogDSLIntegration.test.ts`
  - `[NEW]` `src/tests/cli/VlogCli.test.ts`
  - `[MODIFY]` `src/mcp/registry.ts`
  - `[MODIFY]` `src/dsl/ProductionDSL.ts`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **956/956 pruebas pasando al 100% en verde** (`npm test`), Gate 15 certificado, 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #040: Fase 4F — Trailer & Teaser Generator & Social Hook Intelligence (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/`, `src/editorial/trailer/`, `src/editorial/index.ts`, `scripts/`, `docs/`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para implementar los requerimientos REQ-028, REQ-029 y REQ-051 de `spec/MASTER-CONTENT-ENGINE-v4.md`, permitiendo sintetizar de forma determinista y orientada a la psicología del espectador teasers de 15s (Shorts/Stories), promos de 30s y trailers cinemáticos de 60s/90s derivados directamente del `NarrativeArcPlan` (10 beats documentales), e incorporando un evaluador cuantitativo de la retención en los primeros 3 a 6 segundos.
- **¿Para qué se agregó?:**
  - **Generador de Trailers (`src/editorial/trailer/trailer-generator.ts`):**
    - `TrailerGenerator`: Compilación de variantes promocionales respetando cotas de tiempo exactas ($\pm 0.05$s) y continuidad temporal sin huecos ni solapamientos.
    - Extracción estratégica de los beats con mayor carga dramática (`HOOK`, `ESCALATION`, `REVELATION`), sincronizando impactos de corte y cues musicales (`RISER`, `HIT`, `DROP`, `SILENCE_BREAKER`, `BED`).
    - Firma determinista inmutable mediante hash SHA-256 (`TrailerPlan`).
  - **Social Hook Scorer (`src/editorial/trailer/social-hook-scorer.ts`):**
    - `SocialHookScorer`: Algoritmo cuantitativo que evalúa la ventana de inicio ($t \in [0, 5\text{s}]$) midiendo ritmo visual (frecuencia de cortes y punch-in focal), intriga verbal (preguntas retóricas y palabras clave de alta curiosidad) e impacto acústico temprano (ausencia de silencios muertos $>0.15$s y presencia de risers/sub-hits).
    - Emite un índice de predicción de retención $[0.0, 100.0]$ y recomendaciones editoriales accionables.
- **Archivos:**
  - `[NEW]` `src/editorial/contracts/trailer.types.ts`
  - `[NEW]` `src/editorial/trailer/trailer-generator.ts`
  - `[NEW]` `src/editorial/trailer/social-hook-scorer.ts`
  - `[NEW]` `src/editorial/trailer/index.ts`
  - `[NEW]` `src/tests/editorial/TrailerGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/SocialHookScorer.test.ts`
  - `[MODIFY]` `src/editorial/contracts/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **965/965 pruebas pasando al 100% en verde** (`npm test`), Gate 16 certificado Nivel 5, 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #041: Fase 4G — Cinematic Match Cut Engine & Transition Intelligence (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/`, `src/editorial/transitions/`, `src/editorial/index.ts`, `scripts/`, `docs/`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para implementar los requerimientos REQ-060 y REQ-061 de `spec/MASTER-CONTENT-ENGINE-v4.md`, permitiendo detectar de forma algorítmica y determinista oportunidades de corte por emparejamiento formal (*match cut*) entre planos adyacentes, calculando afinidades visuales multimodales (geométrica, cromática, cinética y sonora) y compensando el encuadre espacial para transiciones fluidas de nivel cinematográfico.
- **¿Para qué se agregó?:**
  - **Motor de Match Cut (`src/editorial/transitions/match-cut-engine.ts`):**
    - `MatchCutEngine`: Análisis de afinidad formal entre pares de tomas adyacentes:
      - **Afinidad Geométrica:** Detección de figuras primitivas (`CIRCLE`, `RECTANGLE`, `LINEAR_HORIZON`, `SILHOUETTE`, `EYE`, `SPIRAL`) y proximidad entre centros focales.
      - **Afinidad Cromática:** Distancia angular mínima circular $|\Delta\theta| \le 180^\circ$ sobre la rueda de color HSL ($0\text{--}360^\circ$).
      - **Afinidad Cinética:** Coherencia direccional entre vectores de movimiento de cámara o sujeto con tolerancia angular y comparación de velocidades normalizadas.
      - **Afinidad Acústica:** Detección de motivos sonoros diegéticos compartidos para enlazar cortes visuales.
      - **Compensación Espacial:** Cálculo exacto del vector de desfase $(\Delta X, \Delta Y)$ y del factor de corrección de escala para alinear los centros de atención al instante del corte.
      - **Escaneo de Secuencia:** Función `scanSequenceForMatchCuts` con emisión de reporte estructurado e inmutable firmado por SHA-256.
- **Archivos:**
  - `[NEW]` `src/editorial/contracts/match-cut.types.ts`
  - `[NEW]` `src/editorial/transitions/match-cut-engine.ts`
  - `[NEW]` `src/editorial/transitions/index.ts`
  - `[NEW]` `src/tests/editorial/MatchCutEngine.test.ts`
  - `[MODIFY]` `src/editorial/contracts/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **972/972 pruebas pasando al 100% en verde** (`npm test`), Gate 17 certificado Nivel 5, 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #042: Fase 4H — Audience Attention, Cognitive Load & Editorial Pacing Architecture (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/`, `src/editorial/attention/`, `src/editorial/index.ts`, `scripts/`, `docs/`, `src/tests/editorial/`, `src/tests/regression/`
- **¿Por qué se agregó?:**
  - Para implementar los requerimientos REQ-046, REQ-047, REQ-048 y REQ-049 de `spec/MASTER-CONTENT-ENGINE-v4.md`, incorporando modelos deterministas heurístico-paramétricos de atención del espectador, saturación cognitiva multimodal, gramática de contrastes de tensión y cálculo formal de divergencia de ritmo editorial, certificados con hashing canónico inmutable y cero regresiones sobre los outputs previos.
- **¿Para qué se agregó?:**
  - **Utilidades Matemáticas & Hashing Canónico (`src/editorial/attention/math-utils.ts`):**
    - `MathUtils`: Implementa clamp con rechazo de `NaN`/`Infinity`, solución analítica de decaimiento con baseline explícito, operador multiplicativo simétrico de composición de estímulos y serialización canónica idempotente con exclusión de hash propio.
  - **Modelo de Atención del Espectador (`src/editorial/attention/audience-attention-model.ts`):**
    - `AudienceAttentionModel`: Simulación diferencial $A(t) = A_{\text{base}} + (A_0 - A_{\text{base}}) e^{-\lambda t}$ convergiendo asintóticamente a $A_{\text{base}} = 0.40$ (evitando colapsos espurios), impulsos conmutativos independientes del orden y detección de zonas de peligro (*attention dips*) con sugerencias de rescate.
  - **Motor de Carga Cognitiva (`src/editorial/attention/cognitive-load-engine.ts`):**
    - `CognitiveLoadEngine`: Suma ponderada multimodal $C(t) = 0.30V + 0.25D + 0.20S + 0.15M + 0.10K$ con funciones de normalización matemáticas cerradas (ej. voz aislada a $V=0.45 \implies C = 0.135$ exacto), detección de sobrecarga ($C \ge 0.85$ por $>3$s) y generación de propuestas estructuradas de mitigación (*proposal-first*).
  - **Contraste Editorial y Rachas de Tensión (`src/editorial/attention/editorial-contrast.ts`):**
    - `EditorialContrast`: Agrupación en `TensionRun` para penalización única por bloque monótono ($\ge 3$ beats contiguos en `HIGH`/`PEAK`), detección de estancamiento en `LOW` ($>35$s), ausencia de distensión tras `PEAK` y desglose transparente de penalizaciones.
  - **Compositor de Curvas de Ritmo (`src/editorial/attention/pacing-curve-composer.ts`):**
    - `PacingCurveComposer`: `PacingProfile` con ventana de $6.0$s y $5$ cortes máximos, cálculo de distancia $L_1$ continua y `AlignmentScore` matemático $[0, 100]$.
  - **Prueba de Regresión Dorada (`src/tests/regression/GoldenEditorialSnapshot.test.ts`):**
    - Certificación de que las estructuras y firmas criptográficas de proyectos previos permanecen 100% inalteradas e invariantes.
- **Archivos:**
  - `[NEW]` `src/editorial/contracts/attention.types.ts`
  - `[NEW]` `src/editorial/attention/math-utils.ts`
  - `[NEW]` `src/editorial/attention/audience-attention-model.ts`
  - `[NEW]` `src/editorial/attention/cognitive-load-engine.ts`
  - `[NEW]` `src/editorial/attention/editorial-contrast.ts`
  - `[NEW]` `src/editorial/attention/pacing-curve-composer.ts`
  - `[NEW]` `src/editorial/attention/index.ts`
  - `[NEW]` `src/tests/editorial/AttentionMathUtils.test.ts`
  - `[NEW]` `src/tests/editorial/AudienceAttentionModel.test.ts`
  - `[NEW]` `src/tests/editorial/CognitiveLoadEngine.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialContrast.test.ts`
  - `[NEW]` `src/tests/editorial/PacingCurveComposer.test.ts`
  - `[NEW]` `src/tests/regression/GoldenEditorialSnapshot.test.ts`
  - `[MODIFY]` `src/editorial/contracts/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **1,004/1,004 pruebas pasando al 100% en verde** (`npm test`), Gate 18 certificado Nivel 5, 0 fallos, 0 regresiones.

---

### 🛠️ Mejora #043: Fase 4I — Data Visualization & Editorial QA Governance (v4.0.0)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/data-visualization/`, `src/editorial/qa/`, `bin/editorial-cli.js`, `package.json`, `scripts/`, `docs/`, `src/tests/editorial/`
- **¿Por qué se agregó?:**
  - Para implementar los requerimientos REQ-025, REQ-030, REQ-081, REQ-082 y REQ-083 de `spec/MASTER-CONTENT-ENGINE-v4.md`, dotando al motor de:
    1. Un compilador de visualización de datos estructurados independiente de After Effects que transpile datasets tabulares a gráficos vectoriales animados deterministas.
    2. Un linter y auditor editorial transversal que aplique políticas de producción (BLOCKING, WARNING, SUGGESTION) sin recalcular algoritmos especializados.
    3. Una cola priorizada de revisión humana (`HumanReviewQueue`) con umbrales calibrados por regla.
    4. Un motor de diferencias editoriales semánticas (`EditorialDiffEngine`) que evalúe matemáticamente el impacto $\Delta IR$ multidimensional.
- **¿Para qué se agregó?:**
  - **Data Visualization Engine (`src/editorial/data-visualization/`):**
    - `AnimatedBarChartCompiler`: Gráficos de barras verticales u horizontales con contadores *tick-up* numéricos sin overshoot.
    - `TrendLineGraphCompiler`: Curvas dinámicas continuas con trazado progresivo (*stroke write-on*) e identificación de key points.
    - `BigStatCardGenerator`: Tarjetas de estadísticas de alto impacto con estilo TIME Editorial y divisores carmesí.
    - `ChronologyTimelineGenerator`: Ejes temporales con detección y resolución determinista de colisiones de etiquetas (`LabelCollision`).
  - **Editorial QA Linter & Audit Engine (`src/editorial/qa/`):**
    - `EditorialQALinter`: Agregador de diagnósticos y evaluador de reglas con cálculo de `overallScore` $[0, 100]$.
    - `QARuleRegistry`: Registro modular de reglas permanentes (`QA-TIME-*`, `QA-ASSET-*`, `QA-EVIDENCE-*`, `QA-COGNITIVE-*`, `QA-PACING-*`, `QA-CONTRAST-*`, `QA-DATA-*`).
    - `HumanReviewQueue`: Priorización determinista por severidad y certeza, registrando decisiones inmutables con hashes antes/después.
    - `EditorialDiffEngine`: Medición matemática del impacto $(\Delta\text{duración}, \Delta\text{pacing}, \Delta\text{atención}, \Delta\text{carga}, \Delta\text{evidencias})$ y categorización de riesgo (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
    - `ProposalEngine`: Arquitectura *Proposal-First* con validación criptográfica de precondiciones para prevenir mutaciones destructivas.
- **Archivos:**
  - `[NEW]` `src/editorial/data-visualization/types.ts`
  - `[NEW]` `src/editorial/data-visualization/schemas.ts`
  - `[NEW]` `src/editorial/data-visualization/data-normalizer.ts`
  - `[NEW]` `src/editorial/data-visualization/scales.ts`
  - `[NEW]` `src/editorial/data-visualization/visualization-layout.ts`
  - `[NEW]` `src/editorial/data-visualization/visualization-hash.ts`
  - `[NEW]` `src/editorial/data-visualization/animated-bar-chart-compiler.ts`
  - `[NEW]` `src/editorial/data-visualization/trend-line-graph-compiler.ts`
  - `[NEW]` `src/editorial/data-visualization/big-stat-card-generator.ts`
  - `[NEW]` `src/editorial/data-visualization/chronology-timeline-generator.ts`
  - `[NEW]` `src/editorial/data-visualization/index.ts`
  - `[NEW]` `src/editorial/qa/types.ts`
  - `[NEW]` `src/editorial/qa/schemas.ts`
  - `[NEW]` `src/editorial/qa/qa-rules.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-linter.ts`
  - `[NEW]` `src/editorial/qa/editorial-audit-engine.ts`
  - `[NEW]` `src/editorial/qa/human-review-queue.ts`
  - `[NEW]` `src/editorial/qa/editorial-diff-engine.ts`
  - `[NEW]` `src/editorial/qa/proposal-engine.ts`
  - `[NEW]` `src/editorial/qa/metrics-adapters.ts`
  - `[NEW]` `bin/editorial-cli.js`
  - `[NEW]` `docs/DATA_VISUALIZATION_ENGINE.md`
  - `[NEW]` `docs/EDITORIAL_QA_ENGINE.md`
  - `[NEW]` `docs/HUMAN_IN_THE_LOOP.md`
  - `[NEW]` `docs/EDITORIAL_DIFF_ENGINE.md`
  - `[NEW]` `src/tests/editorial/DataVisualization.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialQALinter.test.ts`
  - `[NEW]` `src/tests/editorial/HumanReviewQueue.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialDiffEngine.test.ts`
  - `[MODIFY]` `src/editorial/qa/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **1,024/1,024 pruebas pasando al 100% en verde** (`npm test`), Gate 19 certificado Nivel 5, 0 fallos, 0 regresiones.

---

### Mejora #044: Implementación Completa de Fase 5A — Data Visualization Engine (REQ-025)
- **Fecha y Versión:** 2026-09-02, `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/dataviz/`, `src/dsl/ProductionDSL.ts`, `bin/editorial-cli.js`, `package.json`, `fixtures/dataviz/`, `src/tests/editorial/dataviz/`, `docs/DATAVIZ_ENGINE.md`.
- **¿Por qué se agregó? (Causa raíz / Problema detectado):** Se requería materializar la especificación técnica formal de REQ-025 (§1 a §134) para generar gráficos y visualizaciones de datos editoriales animados (Barras, Líneas de Tendencia, Big Stats y Cronologías) con total determinismo byte a byte, independencia del software de composición mediante la AST canónica `DataVizIR`, y un compilador After Effects ExtendScript JSX con regla inviolable de "cero inferencia".
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Matemática e Invariantes:** Normalización numérica a 4 decimales con eliminación estricta de `-0` (`normalizeNumber`), tratamiento determinista de datasets constantes sin división por cero ($min = max \implies 0.50$ y `scaleWarning = "CONSTANT_DOMAIN"`), bloqueo explícito de escala logarítmica (`UnsupportedScaleError`), algoritmo analítico de "nice numbers" y formateo numérico determinista métrico (`K, M, B, T`) sin dependencia del locale del SO.
  - **Layout & Safe Zones:** Motor de zonas seguras adaptativo para 16:9 (EBU Title Safe), 9:16 (zonas de exclusión de UI social de 280px superior y 460px inferior) y 1:1, y motor de colisiones con bloqueo estricto (`CRITICAL_LABEL_COLLISION`) ante solapamientos de etiquetas con énfasis `PRIMARY`.
  - **Animación:** Planificador analítico de curvas cúbicas (`LINEAR`, `EASE_IN_CUBIC`, `EASE_OUT_CUBIC`, `EASE_IN_OUT_CUBIC`), cálculo analítico de longitud de trazos euclidianos y retardo progresivo determinista (`staggerSeconds`) sin jitter aleatorio.
  - **4 Generadores Editoriales:** `AnimatedBarChartCompiler` (horizontal/vertical, baseline real en 0, no overlap), `TrendLineGraphCompiler` (write-on de trazo y key points), `BigStatCardGenerator` (valor dominante, divisor vectorial carmesí `#FF1424` de 4px y etiqueta secundaria en mayúsculas), y `ChronologyTimelineGenerator` (normalización UTC, monotonía espacial y ordenamiento cronológico).
  - **Compilador AE JSX:** Transpilación determinista de la AST a ExtendScript con activación de desenfoque de movimiento (`comp.motionBlur = true`), sandbox de seguridad e inmutabilidad de decisiones editoriales.
  - **CLI & DSL:** Scripts npm `dataviz:validate`, `dataviz:compile` y `dataviz:fixture`, y directiva `dataviz()` en `ProductionDSL`.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/dataviz/constants.ts`
  - `[NEW]` `src/editorial/dataviz/errors.ts`
  - `[NEW]` `src/editorial/dataviz/types.ts`
  - `[NEW]` `src/editorial/dataviz/validators.ts`
  - `[NEW]` `src/editorial/dataviz/data-normalizer.ts`
  - `[NEW]` `src/editorial/dataviz/scale-engine.ts`
  - `[NEW]` `src/editorial/dataviz/number-formatter.ts`
  - `[NEW]` `src/editorial/dataviz/color-resolver.ts`
  - `[NEW]` `src/editorial/dataviz/safe-zone-engine.ts`
  - `[NEW]` `src/editorial/dataviz/layout-engine.ts`
  - `[NEW]` `src/editorial/dataviz/label-engine.ts`
  - `[NEW]` `src/editorial/dataviz/axis-engine.ts`
  - `[NEW]` `src/editorial/dataviz/legend-engine.ts`
  - `[NEW]` `src/editorial/dataviz/animation-planner.ts`
  - `[NEW]` `src/editorial/dataviz/dataviz-hash.ts`
  - `[NEW]` `src/editorial/dataviz/dataviz-validator.ts`
  - `[NEW]` `src/editorial/dataviz/dataviz-ir.ts`
  - `[NEW]` `src/editorial/dataviz/animated-bar-chart-compiler.ts`
  - `[NEW]` `src/editorial/dataviz/trend-line-graph-compiler.ts`
  - `[NEW]` `src/editorial/dataviz/big-stat-card-generator.ts`
  - `[NEW]` `src/editorial/dataviz/chronology-timeline-generator.ts`
  - `[NEW]` `src/editorial/dataviz/compilers/after-effects-dataviz-compiler.ts`
  - `[NEW]` `src/editorial/dataviz/index.ts`
  - `[NEW]` `fixtures/dataviz/bar-chart-basic.json`
  - `[NEW]` `fixtures/dataviz/bar-chart-negative.json`
  - `[NEW]` `fixtures/dataviz/trend-line-basic.json`
  - `[NEW]` `fixtures/dataviz/big-stat-basic.json`
  - `[NEW]` `fixtures/dataviz/chronology-basic.json`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizTypes.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataNormalizer.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/ScaleEngine.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/NumberFormatter.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/LayoutEngine.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/AnimationPlanner.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizValidator.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizDeterminism.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/AnimatedBarChartCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/TrendLineGraphCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/BigStatCardGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/ChronologyTimelineGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizPropertyBased.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizGolden.test.ts`
  - `[NEW]` `src/tests/editorial/dataviz/DataVizEditorialIntegration.test.ts`
  - `[NEW]` `docs/DATAVIZ_ENGINE.md`
  - `[MODIFY]` `src/dsl/ProductionDSL.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `docs/ROADMAP.md`
- **Verificación:** **1,134/1,134 pruebas pasando al 100% en verde** (`npm test`), con 110 pruebas nuevas en 15 suites cubriendo Unit, Integration, Golden, Property-Based (fast-check) y Determinismo Criptográfico. Certificación Nivel 5 de Producción revalidada en Gate 19 y Gate 20.

---

### 🛠️ Mejora #045: Editorial QA Linter, Audit & Human-in-the-Loop Diff Engine (REQ-030, REQ-081, REQ-082, REQ-083)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/qa/` (12 módulos), `bin/editorial-cli.js`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - La necesidad crítica de una capa formal de gobernanza editorial previa a la exportación para verificar que ninguna modificación o decisión procedimental alcance After Effects JSX, OTIO o EDL sin haber sido clasificada, auditada y trazada.
  - La ausencia de una cola determinista de revisión humana (*Human-in-the-Loop*) capaz de priorizar incertidumbres según severidad, impacto y confianza ($< 0.70$).
  - La necesidad de comparar matemáticamente estados de la IR (`EditorialDiffEngine`), aislando cambios directos de derivados (efecto dominó temporal) y detectando regresiones críticas (eliminación de afirmaciones con evidencia o alteración de revelaciones causales).
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Auditoría Transversal en 17 Categorías:** Inspección de estructura, timing, media, audio, continuidad visual, safe-zone, narrativa, evidencia, atención, carga cognitiva, contraste, pacing, estilo y exportación.
  - **Identidad Determinista de Issues:** Generación de identificadores de problemas mediante SHA-256 de estructuras canónicas sin aleatoriedad.
  - **Cola de Revisión Humana Ponderada (`HumanReviewQueue`):** Priorización formal $\text{priority} = \text{severityWeight} \times \text{impactWeight} \times (1 - \text{confidence}) \times 100$ con resolución determinista de empates e historial inmutable `HumanDecision`.
  - **Motor de Diferencias Semánticas e Impacto (`EditorialDiffEngine` & `ImpactCalculator`):** Comparación semántica de IRs (`before` vs `after`), cálculo de deltas en pacing, atención, duración y carga cognitiva, con detección automática de regresiones `BLOCKING`.
  - **CLI y Certificación Conformance:** Integración en `bin/editorial-cli.js qa` con flags `--json`, `--strict`, `--fail-on-warnings`, `--diff` y códigos de salida deterministas (0 = PASS, 1 = PASS_WITH_WARNINGS, 2 = BLOCKED, 3 = INTERNAL_ERROR).
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/qa/editorial-qa-severity.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-types.ts`
  - `[NEW]` `src/editorial/qa/editorial-diff-types.ts`
  - `[NEW]` `src/editorial/qa/qa-hash.ts`
  - `[NEW]` `src/editorial/qa/confidence-policy.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-registry.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-rules.ts`
  - `[NEW]` `src/editorial/qa/human-review-queue.ts`
  - `[NEW]` `src/editorial/qa/impact-calculator.ts`
  - `[NEW]` `src/editorial/qa/editorial-diff-engine.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-linter.ts`
  - `[MODIFY]` `src/editorial/qa/index.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[NEW]` `src/tests/editorial/qa/ConfidencePolicy.test.ts`
  - `[NEW]` `src/tests/editorial/qa/HumanReviewQueue.test.ts`
  - `[NEW]` `src/tests/editorial/qa/EditorialQARules.test.ts`
  - `[NEW]` `src/tests/editorial/qa/ImpactCalculator.test.ts`
  - `[NEW]` `src/tests/editorial/qa/EditorialDiffEngine.test.ts`
  - `[NEW]` `src/tests/editorial/qa/EditorialQALinter.test.ts`
  - `[NEW]` `src/tests/editorial/qa/EditorialQADeterminism.test.ts`
  - `[NEW]` `src/tests/regression/GoldenEditorialQASnapshot.test.ts`
- **Verificación:** **1,169/1,169 pruebas pasando al 100% en verde en 416 suites** (`npm test`), con 35 pruebas nuevas cubriendo Unit, Rules, Queue, Diff, Impact, Confidence, PBT con `fast-check` (PBT-001 a PBT-009) y Golden Snapshot. Certificación Level 5 Production Certified renovada con Gate 19 al 100%.

---

### 🛠️ Mejora #046: Intelligent Performance & Semantic Trimming Engine (RF-056)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/performance/` (7 módulos), `src/mcp/tools/performance-tools.ts`, `bin/editorial-cli.js`, `package.json`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - La necesidad de realizar poda editorial semántica sobre material audiovisual sin destruir significado, causalidad narrativa, evidencia probatoria ni la expresividad de la interpretación humana (risas, silencios dramáticos, respiraciones orgánicas).
  - La necesidad de seleccionar la mejor toma (*Best Take Selection*) de forma ponderada y con desempate determinista sin caer en selecciones aleatorias ni sesgadas exclusivamente por duración o volumen.
  - La exigencia de proteger contra la sobrepoda accidental (límite del 30%) y garantizar transiciones de audio limpias sin chasquidos (micro-crossfades).
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Detección de Redundancia Semántica (`SemanticRedundancyEngine`):** Modelo de similitud léxica y solapamiento de información ponderado ($0.40 \cdot \text{sim} + 0.30 \cdot \text{overlap} + 0.15 \cdot \text{prox} + 0.15 \cdot \text{role}$) con protección absoluta de afirmaciones con datos probatorios nuevos (`KEEP_B`).
  - **Selector Determinista de Tomas (`BestTakeSelector`):** Evaluación multidimensional en 9 ejes dominada por integridad semántica, con desempate determinista riguroso y umbral de auto-selección en $0.80$.
  - **Preservación Expresiva Humana (`NaturalPerformancePreservation`):** Protección prioritaria de risas, respiraciones y pausas reflexivas ($\text{preservationScore} \ge 0.75$) frente a errores técnicos descartables (`FALSE_START`, `STUTTER`, `TECHNICAL_ERROR`).
  - **Orquestador Proposal-First (`IntelligentTrimmingEngine`):** Generación de propuestas de poda con padding editorial ($0.08s$ pre-roll, $0.12s$ post-roll), micro-crossfades ($0.025s$), detección de dependencias narrativas y contención contra sobrepoda ($> 30\% \implies$ `REVIEW_REQUIRED`).
  - **CLI y Conformance Gate 20:** Integración en `bin/editorial-cli.js trim` con modo `--dry-run` y certificación de Gate 20.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/performance/performance-types.ts`
  - `[NEW]` `src/editorial/performance/performance-validation.ts`
  - `[NEW]` `src/editorial/performance/performance-scoring.ts`
  - `[NEW]` `src/editorial/performance/semantic-redundancy-engine.ts`
  - `[NEW]` `src/editorial/performance/best-take-selector.ts`
  - `[NEW]` `src/editorial/performance/natural-performance-preservation.ts`
  - `[NEW]` `src/editorial/performance/intelligent-trimming-engine.ts`
  - `[NEW]` `src/editorial/performance/index.ts`
  - `[NEW]` `src/editorial/performance/README.md`
  - `[NEW]` `src/mcp/tools/performance-tools.ts`
  - `[NEW]` `fixtures/performance/intelligent-trimming-production.json`
  - `[NEW]` `docs/INTELLIGENT_PERFORMANCE_ENGINE.md`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `scripts/run-conformance.mjs`
  - `[NEW]` `src/tests/editorial/SemanticRedundancyEngine.test.ts`
  - `[NEW]` `src/tests/editorial/BestTakeSelector.test.ts`
  - `[NEW]` `src/tests/editorial/NaturalPerformancePreservation.test.ts`
  - `[NEW]` `src/tests/editorial/IntelligentTrimmingEngine.test.ts`
  - `[NEW]` `src/tests/editorial/PerformancePropertyTests.test.ts`
  - `[MODIFY]` `src/tests/regression/GoldenEditorialSnapshot.test.ts`
- **Verificación:** **1,190/1,190 pruebas pasando al 100% en verde en 421 suites** (`npm test`), 21 pruebas nuevas cubriendo PBT 1 a 7 con `fast-check` y Golden Snapshot. Certificación Level 5 Production Certified con **Gate 20 aprobado**.

---

### 🛠️ Mejora #047: Formalización Modular de Editorial QA Linter, Audit & Human-in-the-Loop Diff Engine (REQ-030, REQ-081, REQ-082, REQ-083)
- **Fecha:** 2026-09-02
- **Módulos Afectados:** `src/editorial/contracts/` (3 módulos), `src/editorial/qa/` (10 módulos + 10 reglas en `src/editorial/qa/rules/`), `src/mcp/tools/qa-tools.ts`, `bin/editorial-cli.js`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Implementación definitiva del Master Requirement para QA y Diff, estableciendo contratos tipados canónicos en `src/editorial/contracts/`, catálogo desacoplado de reglas en `src/editorial/qa/rules/`, generador determinista de IDs de issues mediante SHA-256 (`qa-id.ts`) y serialización canónica inmutable (`qa-normalizer.ts`).
  - Necesidad de asegurar la simetría e idempotencia estricta del motor de diff (`diff(x, x)` = 0 cambios y nivel `NONE`), diferenciando cambios directos de derivados por efecto dominó temporal (`origin: DIRECT` vs `origin: DERIVED`).
  - Coexistencia transparente entre el motor de reglas de 17 categorías y el catálogo de 10 dominios de auditoría sin romper ninguna firma previa.
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Contratos Formales Unificados:** `editorial-qa.types.ts`, `editorial-diff.types.ts` y `human-review.types.ts` en `src/editorial/contracts/`.
  - **Catálogo Modular de Reglas por Dominio (`src/editorial/qa/rules/`):**
    - `timeline.rules.ts`: Comprobación de duraciones no positivas, inicio negativo y solapamientos ilegales.
    - `continuity.rules.ts`: Detección de cortes rápidos (< 0.8s) y discontinuidades visuales.
    - `narrative.rules.ts`: Verificación de beats obligatorios en documentales y detección de revelaciones prematuras.
    - `evidence.rules.ts`: Validación de claims contra evidencias respaldadas.
    - `cognitive.rules.ts`: Detección de sobrecarga cognitiva sostenida (> 0.85).
    - `pacing.rules.ts`: Detección de desviación de curva de ritmo respecto al perfil.
    - `visual.rules.ts`: Validación de dimensiones válidas y safe zones.
    - `audio.rules.ts`: Riesgo de clipping acústico (> 0.0 dB) y solapamiento sin ducking.
    - `export.rules.ts`: Validación de pistas y preparación para exportación.
    - `safety.rules.ts`: Detección de inyecciones de código malicioso o script tags en metadatos.
  - **Herramientas MCP de QA (`src/mcp/tools/qa-tools.ts`):** `editorial_qa_lint`, `editorial_qa_get_report`, `editorial_review_queue`, `editorial_review_decide`, `editorial_diff`, `editorial_diff_impact`.
  - **Golden Regression & PBT:** Creación de `fixtures/editorial/qa/golden-production-project.json`, `golden-production-project.qa.json`, `GoldenEditorialQARegression.test.ts` y `QAInvariant.test.ts` con `fast-check`.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/contracts/editorial-qa.types.ts`
  - `[NEW]` `src/editorial/contracts/editorial-diff.types.ts`
  - `[NEW]` `src/editorial/contracts/human-review.types.ts`
  - `[NEW]` `src/editorial/qa/qa-id.ts`
  - `[NEW]` `src/editorial/qa/qa-normalizer.ts`
  - `[NEW]` `src/editorial/qa/qa-report-builder.ts`
  - `[NEW]` `src/editorial/qa/audit-engine.ts`
  - `[NEW]` `src/editorial/qa/impact-analyzer.ts`
  - `[NEW]` `src/editorial/qa/rules/index.ts`
  - `[NEW]` `src/editorial/qa/rules/timeline.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/continuity.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/narrative.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/evidence.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/cognitive.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/pacing.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/visual.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/audio.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/export.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/safety.rules.ts`
  - `[NEW]` `src/mcp/tools/qa-tools.ts`
  - `[NEW]` `fixtures/editorial/qa/golden-production-project.json`
  - `[NEW]` `fixtures/editorial/qa/golden-production-project.qa.json`
  - `[NEW]` `src/tests/editorial/qa/EditorialAuditEngine.test.ts`
  - `[NEW]` `src/tests/editorial/qa/ImpactAnalyzer.test.ts`
  - `[NEW]` `src/tests/editorial/qa/QARules.test.ts`
  - `[NEW]` `src/tests/editorial/qa/QAInvariant.test.ts`
  - `[NEW]` `src/tests/regression/GoldenEditorialQARegression.test.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-qa-linter.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-diff-engine.ts`
  - `[MODIFY]` `src/editorial/qa/human-review-queue.ts`
  - `[MODIFY]` `src/editorial/contracts/index.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **1,202/1,202 pruebas pasando al 100% en verde en 426 suites** (`npm test`), con 12 pruebas nuevas y 8 suites del master requirement validadas. Certificación Level 5 Production Certified con **Gate 19 y Gate 20 aprobados**.

---

### 🛠️ Mejora #048: Data Visualization Engine & Procedural Infographic Compiler (REQ-025)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/data-visualization/*`, `src/mcp/tools/dataviz-tools.ts`, `bin/editorial-cli.js`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Para documentales de investigación, análisis económico, visualización histórica y periodismo de datos, el motor carecía de un compilador determinista de datos estructurados (CSV, JSON) a gráficos vectoriales animados con sellado criptográfico SHA-256 e integración directa con After Effects ExtendScript JSX.
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **4 Familias de Compilación Especializadas:**
    1. `AnimatedBarChartCompiler`: Gráficos de barras verticales y horizontales, ordenamiento (`ASCENDING`, `DESCENDING`, `SOURCE`), truncado de barras, animación de crecimiento y contadores numéricos deterministas.
    2. `TrendLineGraphCompiler`: Gráficos de líneas de tendencia para series temporales o numéricas continuas, interpolación lineal o spline Bézier cúbica suave, animación *write-on* vía `trimPath` y resaltado automático de extremos.
    3. `BigStatCardGenerator`: Tarjetas de estadísticas de alto impacto con tipografía ultra-bold condensada estilo TIME, formato numérico internacional (moneda, porcentaje, separadores de miles), línea de acento y subtítulo.
    4. `ChronologyTimelineGenerator`: Líneas de tiempo cronológicas con resolución de colisiones y asignación determinista de carriles (*lanes*), conectores vectoriales y nodos de hitos.
  - **Parsers y Validadores RFC 4180:** Soporte para comillas escapadas `""`, saltos de línea dentro de campos, stripping de BOM UTF-8 e inferencia determinista de tipos (`STRING`, `NUMBER`, `DATE`, `BOOLEAN`).
  - **Normalización Matemática Acotada:** Fórmula $n = (v - v_{\min}) / (v_{\max} - v_{\min})$ con manejo determinista de datasets constantes ($n = 0.5$) y políticas de nulos (`REJECT`, `SKIP`, `ZERO`).
  - **Transpilador After Effects JSX Seguro (`VisualizationJsxCompiler`):** Genera código ExtendScript nativo con `comp.motionBlur = true;`, respeto estricto a Safe Zones, keyframes temporales monótonos y sandbox seguro sin llamadas dinámicas `eval`.
  - **Herramientas MCP & CLI:** Comando `motion-engine data-viz` con soporte `--spec` y `--jsx`, y herramientas MCP `editorial_compile_data_visualization`, `editorial_dataviz_to_jsx`, `editorial_parse_dataset`, `editorial_validate_dataset`.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/data-visualization/constants.ts`
  - `[NEW]` `src/editorial/data-visualization/errors.ts`
  - `[NEW]` `src/editorial/data-visualization/dataset-parser.ts`
  - `[NEW]` `src/editorial/data-visualization/dataset-validator.ts`
  - `[NEW]` `src/editorial/data-visualization/dataset-normalizer.ts`
  - `[NEW]` `src/editorial/data-visualization/scale-utils.ts`
  - `[NEW]` `src/editorial/data-visualization/color-utils.ts`
  - `[NEW]` `src/editorial/data-visualization/layout-engine.ts`
  - `[NEW]` `src/editorial/data-visualization/deterministic-id.ts`
  - `[NEW]` `src/editorial/data-visualization/animation-utils.ts`
  - `[NEW]` `src/editorial/data-visualization/animated-bar-chart-compiler.ts`
  - `[NEW]` `src/editorial/data-visualization/trend-line-graph-compiler.ts`
  - `[NEW]` `src/editorial/data-visualization/big-stat-card-generator.ts`
  - `[NEW]` `src/editorial/data-visualization/chronology-timeline-generator.ts`
  - `[NEW]` `src/editorial/data-visualization/visualization-validator.ts`
  - `[NEW]` `src/editorial/data-visualization/visualization-hash.ts`
  - `[NEW]` `src/editorial/data-visualization/visualization-jsx-compiler.ts`
  - `[NEW]` `src/mcp/tools/dataviz-tools.ts`
  - `[NEW]` `fixtures/data-visualization/investigative-economy.json`
  - `[NEW]` `src/tests/editorial/DataVisualizationDataset.test.ts`
  - `[NEW]` `src/tests/editorial/AnimatedBarChartCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/TrendLineGraphCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/BigStatCardGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/ChronologyTimelineGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/DataVisualizationPropertyBased.test.ts`
  - `[NEW]` `src/tests/editorial/DataVisualizationDeterminism.test.ts`
  - `[NEW]` `src/tests/editorial/DataVisualizationRegression.test.ts`
  - `[NEW]` `docs/DATA_VISUALIZATION_ENGINE.md`
  - `[MODIFY]` `src/editorial/data-visualization/types.ts`
  - `[MODIFY]` `src/editorial/data-visualization/index.ts`
  - `[MODIFY]` `src/index.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **1,230/1,230 pruebas pasando al 100% en verde en 434 suites** (`npm test`), con 28 pruebas nuevas y 8 suites del master requirement validadas. Certificación Level 5 Production Certified con **Gate 21 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #049: Data Visualization Engine — Motor Determinista de Visualización de Datos Editoriales (REQ-025 Canónico en `src/editorial/data-viz/`)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/data-viz/*`, `src/dsl/ProductionDSL.ts`, `src/mcp/tools/dataviz-tools.ts`, `src/editorial/index.ts`, `scripts/run-conformance.mjs`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Implementación exhaustiva y cerrada del requerimiento maestro REQ-025 en el namespace canónico `src/editorial/data-viz/`, incorporando validación de esquemas Zod en tiempo de ejecución, escalas estadísticas deterministas, normalización con inmutabilidad estricta de datasets, formateadores independientes de locale, soporte para valores negativos con baseline cero explícito, y suite de 12 pruebas de 7 capas con Property-Based Testing (`fast-check`).
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **17 Módulos de Código en `src/editorial/data-viz/`:**
    - `types.ts` & `schema.ts`: Contratos e inferencias TypeScript + esquemas Zod para datasets, columnas, filas, metadata y las 4 especificaciones (`BarChartSpec`, `TrendLineSpec`, `BigStatSpec`, `ChronologyTimelineSpec`).
    - `errors.ts`: Clases de error estructuradas (`DataVisualizationError`) con códigos canónicos (`DATASET_EMPTY`, `COLUMN_NOT_FOUND`, `INVALID_NUMBER`, etc.).
    - `validation.ts`: Validación matemática y de esquema con políticas de duplicados (`REJECT`, `AGGREGATE_SUM`, `KEEP_LAST`) y rechazo estricto de `NaN` e `Infinity`.
    - `normalization.ts`: Normalización determinista sin mutación del dataset original; asignación de $n = 0.5$ para datasets constantes; dominios categóricos ordenados lexicográficamente.
    - `statistics.ts`: Resumen numérico determinista (mínimo, máximo, media, mediana, suma, conteo) y detección de índices extremos.
    - `scales.ts`: `LinearScale`, `LogarithmicScale` y `BandScale` con cálculo explícito del cruce en cero (*zero-baseline*).
    - `formatters.ts`: Formateo independiente del locale del sistema (`formatCompactNumber`, `formatPercentage`, `formatCurrency`, `formatDate`, `formatDataValue`).
    - `color-mapping.ts`: Paleta TIME Editorial (`#FF1424`, `#0A0A0A`, `#FFFFFF`) y cálculo de ratio de contraste WCAG.
    - `layout.ts`: Cálculo de áreas seguras (*Safe Zones*) y áreas de graficado (*Plot Area*) para relaciones `16:9`, `9:16` y `1:1`.
    - `animation.ts`: `AnimationPlanBuilder` determinista con animaciones sincronizadas de contadores numéricos y crecimiento de barras/líneas.
    - `dataset-hash.ts`: Serialización canónica determinista y sellado criptográfico SHA-256 (excluyendo el campo `checksumSha256`).
    - Compiladores: `AnimatedBarChartCompiler`, `TrendLineGraphCompiler`, `BigStatCardGenerator`, `ChronologyTimelineGenerator`.
    - `index.ts`: API unificada `compileDataVisualization(dataset, spec, options)`.
  - **6 Golden Fixtures en `fixtures/data-viz/`:** `revenue-bar-chart.json`, `population-trend.json`, `big-stat-revenue.json`, `historical-timeline.json`, `negative-positive-values.json`, `multilingual-dataset.json`.
  - **Integración DSL & MCP:** Directiva `dataViz` en `ProductionDSL.ts` y herramienta MCP `data_visualization_compile` en `src/mcp/tools/dataviz-tools.ts`.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/data-viz/types.ts`
  - `[NEW]` `src/editorial/data-viz/schema.ts`
  - `[NEW]` `src/editorial/data-viz/errors.ts`
  - `[NEW]` `src/editorial/data-viz/validation.ts`
  - `[NEW]` `src/editorial/data-viz/normalization.ts`
  - `[NEW]` `src/editorial/data-viz/statistics.ts`
  - `[NEW]` `src/editorial/data-viz/scales.ts`
  - `[NEW]` `src/editorial/data-viz/formatters.ts`
  - `[NEW]` `src/editorial/data-viz/color-mapping.ts`
  - `[NEW]` `src/editorial/data-viz/layout.ts`
  - `[NEW]` `src/editorial/data-viz/animation.ts`
  - `[NEW]` `src/editorial/data-viz/dataset-hash.ts`
  - `[NEW]` `src/editorial/data-viz/animated-bar-chart-compiler.ts`
  - `[NEW]` `src/editorial/data-viz/trend-line-graph-compiler.ts`
  - `[NEW]` `src/editorial/data-viz/big-stat-card-generator.ts`
  - `[NEW]` `src/editorial/data-viz/chronology-timeline-generator.ts`
  - `[NEW]` `src/editorial/data-viz/index.ts`
  - `[NEW]` `fixtures/data-viz/revenue-bar-chart.json`
  - `[NEW]` `fixtures/data-viz/population-trend.json`
  - `[NEW]` `fixtures/data-viz/big-stat-revenue.json`
  - `[NEW]` `fixtures/data-viz/historical-timeline.json`
  - `[NEW]` `fixtures/data-viz/negative-positive-values.json`
  - `[NEW]` `fixtures/data-viz/multilingual-dataset.json`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationSchema.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationValidation.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationNormalization.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationScales.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationFormatters.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/AnimatedBarChartCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/TrendLineGraphCompiler.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/BigStatCardGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/ChronologyTimelineGenerator.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationDeterminism.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationProperty.test.ts`
  - `[NEW]` `src/tests/editorial/data-viz/DataVisualizationRegression.test.ts`
  - `[MODIFY]` `src/editorial/index.ts`
  - `[MODIFY]` `src/dsl/ProductionDSL.ts`
  - `[MODIFY]` `src/mcp/tools/dataviz-tools.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **1,276/1,276 pruebas pasando al 100% en verde en 446 suites** (`npm test`), con 46 pruebas nuevas y 12 suites validadas. Certificación Level 5 Production Certified con **Gate 21 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #050: Unificación de Arquitectura Dual y Cierre de Producción REQ-025 (Data Visualization Engine en `src/editorial/data-visualization/`)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/data-visualization/*`, `src/tests/editorial/*`, `fixtures/data-visualization/*`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Existían llamadas polimórficas entre dos convenciones de API: una basada en wrappers de opciones (`compile({ dataset, config, aspectRatio })`) y otra basada en pares posicionales clásicos (`compile(dataset, spec)`). Además, las definiciones de capas requerían prefijos canónicos estandarizados (`DV::BAR::`, `DV::LABEL::`, `DV::TREND::PATH`, `DV::TIMELINE::AXIS`) e inversión vertical obligatoria en `LinearScale` para composición en After Effects.
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **16 Módulos de Código Unificados en `src/editorial/data-visualization/`:**
    - `types.ts`: Unificación de tipos (`VisualizationIR` con `layers: VisualizationLayer[]` no opcional, `BarGeometry`, `DataPoint`, etc.).
    - `constants.ts`: Constantes de marca TIME (`CRIMSON`, `WHITE`, `BLACK`), márgenes seguros y temas.
    - `validation.ts`: Validador determinista con rechazo estricto de `NaN`, `Infinity`, IDs duplicados y precisión negativa.
    - `normalization.ts`: Normalización inmutable $n \in [0, 1]$, caso constante $n = 0.5$ y `denormalizeValue`.
    - `scales.ts`: `LinearScale` con inversión vertical $y = y_{\max} - \dots$, `TimeScale` y `OrdinalScale` con constructores polimórficos.
    - `geometry.ts`: `computePlotArea` y verificación de zonas seguras con `SafeZoneViolationError`.
    - `animation.ts`: Curvas de crecimiento, write-on, fade-in y contadores de números.
    - `labels.ts`: Formateo determinista y detección de colisiones de etiquetas.
    - `accessibility.ts`: Ratio de contraste WCAG y luminancia.
    - `checksum.ts`: Sellado criptográfico SHA-256 canónico y verificación de integridad.
    - Compiladores duales: `AnimatedBarChartCompiler`, `TrendLineGraphCompiler`, `BigStatCardGenerator`, `ChronologyTimelineGenerator`.
    - `visualization-engine.ts`: Fachada `DataVisualizationEngine` con pipeline de 6 etapas.
  - **7 Golden Fixtures en `fixtures/data-visualization/`:** `bar-basic.json`, `bar-negative.json`, `trend-basic.json`, `trend-time.json`, `big-stat.json`, `chronology.json`, `edge-cases.json`.
  - **12 Suites de Testing Especializadas:** Con 49 tests aprobados al 100% (incluyendo PBT generativo con `fast-check` y suites de regresión).
- **Archivos Creados / Modificados:**
  - `[MODIFY]` `src/editorial/data-visualization/types.ts`
  - `[MODIFY]` `src/editorial/data-visualization/constants.ts`
  - `[MODIFY]` `src/editorial/data-visualization/validation.ts`
  - `[MODIFY]` `src/editorial/data-visualization/normalization.ts`
  - `[MODIFY]` `src/editorial/data-visualization/scales.ts`
  - `[MODIFY]` `src/editorial/data-visualization/geometry.ts`
  - `[MODIFY]` `src/editorial/data-visualization/animation.ts`
  - `[MODIFY]` `src/editorial/data-visualization/labels.ts`
  - `[MODIFY]` `src/editorial/data-visualization/accessibility.ts`
  - `[MODIFY]` `src/editorial/data-visualization/checksum.ts`
  - `[MODIFY]` `src/editorial/data-visualization/animated-bar-chart-compiler.ts`
  - `[MODIFY]` `src/editorial/data-visualization/trend-line-graph-compiler.ts`
  - `[MODIFY]` `src/editorial/data-visualization/big-stat-card-generator.ts`
  - `[MODIFY]` `src/editorial/data-visualization/chronology-timeline-generator.ts`
  - `[MODIFY]` `src/editorial/data-visualization/visualization-engine.ts`
  - `[MODIFY]` `src/editorial/data-visualization/index.ts`
  - `[NEW]` `fixtures/data-visualization/bar-basic.json`
  - `[NEW]` `fixtures/data-visualization/bar-negative.json`
  - `[NEW]` `fixtures/data-visualization/trend-basic.json`
  - `[NEW]` `fixtures/data-visualization/trend-time.json`
  - `[NEW]` `fixtures/data-visualization/big-stat.json`
  - `[NEW]` `fixtures/data-visualization/chronology.json`
  - `[NEW]` `fixtures/data-visualization/edge-cases.json`
  - `[NEW]` `src/tests/editorial/DataVisualizationValidation.test.ts`
  - `[NEW]` `src/tests/editorial/DataVisualizationNormalization.test.ts`
  - `[NEW]` `src/tests/editorial/DataVisualizationScales.test.ts`
  - `[NEW]` `docs/phases/phase-4i-report.md`
- **Verificación:** **1,289/1,289 pruebas pasando al 100% en 449 suites** (`npm test`). Certificación Level 5 Production Certified con **Gate 21 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #051: Implementación Canónica de Editorial QA Linter, Audit & Human-in-the-Loop Diff Engine (REQ-030 / REQ-081 / REQ-082 / REQ-083)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/qa/*`, `src/editorial/contracts/*`, `src/mcp/tools/qa-tools.ts`, `bin/editorial-cli.js`, `fixtures/editorial/qa/*`, `src/tests/editorial/*`, `src/tests/regression/*`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Se requería una capa formal y determinista de gobernanza y auditoría previa a cualquier proceso de compilación, renderizado o exportación a After Effects JSX / OpenTimelineIO / FCPXML. El sistema debía auditar de forma transversal invariantes estructurales, temporales, narrativos, de evidencia fáctica, continuidad y carga cognitiva, generando propuestas de remediación no destructivas, colas deterministas de revisión humana (*Human-in-the-Loop*) para incertidumbres $\ge 30\%$, y un comparador diferencial matemático de versiones de la IR con reevaluación selectiva de impacto.
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Contratos y Remediaciones Declarativas (`editorial-findings.ts`, `editorial-remediation.ts`):**
    - `EditorialQAFinding` con 14 categorías canónicas, severidad (`BLOCKING`, `WARNING`, `SUGGESTION`), huella digital criptográfica SHA-256 (`fingerprint`) e inmutabilidad estricta.
    - `EditorialRemediation` con 10 acciones declarativas (`SHIFT`, `TRIM`, `EXTEND`, `REMOVE`, `REPLACE`, `ADD`, `DUCK`, `SPLIT`, `REORDER`, `REVIEW`) y cálculo de impacto estimado.
  - **Catálogo de Reglas QA (`editorial-rules.ts`):**
    - `QA-STRUCT-001..004`: Validación de esquema, assets inexistentes, identificadores duplicados y nodos huérfanos.
    - `QA-TIME-001..006`: Duraciones no negativas, timecodes finitos (sin NaN/Inf), orden temporal, solapamientos ilegales, política de huecos/gaps y consistencia de duración total.
    - `QA-NARR-001..005`: Beats obligatorios (Hook, Clímax), orden causal e intercepción de spoilers prematuros.
    - `QA-EVIDENCE-001..004`: Claims sin respaldo, fuentes ausentes e inconsistencias con citaciones obligatorias.
    - Continuidad, Atención, Carga Cognitiva ($C \ge 0.85$ durante $\ge 3\text{s}$), Contraste y Exportabilidad a After Effects.
  - **Auditoría Formal Pre-Render (`editorial-audit-engine.ts`):**
    - `EditorialAuditReport` con `qualityScore` acotado estrictamente en $[0, 100]$:
      $$\text{qualityScore} = \text{clamp}(100 - (25 \times N_{\text{BLOCKING}} + 5 \times N_{\text{WARNING}} + 1 \times N_{\text{SUGGESTION}}), 0, 100)$$
    - Bloqueo inviolable de exportación ante cualquier `BLOCKING` (`canExport = false`, `status = "BLOCKED"`).
    - Sellado canónico SHA-256 determinista (`generatedAtPolicy: "DETERMINISTIC"`).
  - **Cola de Revisión Humana (*Human-in-the-Loop*, `human-review-queue.ts`):**
    - Umbral de confianza: hallazgos con $\text{confidence} < 0.70$ y `BLOCKING` ingresan automáticamente a la cola.
    - Priorización determinista $\text{priority} = \text{severityWeight} \times \text{durationWeight} \times \text{uncertaintyWeight} \times 100$.
    - Desempate estricto: Prioridad $\to$ Confianza $\to$ Timestamp $\to$ ID.
    - Transiciones de estado auditables (`PENDING`, `APPROVED`, `REJECTED`, `DEFERRED`) con creación inmutable de revisiones `IR-vN`.
  - **Motor de Diff Editorial e Impacto (`editorial-diff-engine.ts`):**
    - Comparador semántico de revisiones (`before` vs `after`) con cálculo exacto de deltas temporales (`deltaStart`, `deltaEnd`, `deltaDuration`).
    - Desglose de impacto multidimensional en duración, pacing, atención, carga cognitiva, contraste, causalidad narrativa y continuidad.
    - Identidad reflexiva: $\text{diff}(IR, IR)$ produce 0 cambios y nivel de riesgo `"NONE"`.
  - **7 Herramientas MCP Canónicas (`src/mcp/tools/qa-tools.ts`):**
    - `editorial_run_qa`, `editorial_get_audit`, `editorial_get_review_queue`, `editorial_compare_revisions`, `editorial_get_change_impact`, `editorial_approve_review`, `editorial_reject_review`.
  - **CLI y CI/CD (`bin/editorial-cli.js`):**
    - Comando `npm run editorial:qa` con flags `--strict`, `--json`, `--fail-on-warning`, `--fail-on-suggestion`.
  - **7 Golden Fixtures en `fixtures/editorial/qa/`:**
    - `golden-valid-documentary.json`, `golden-warning-pacing.json`, `golden-cognitive-overload.json`, `golden-evidence-failure.json`, `golden-continuity-failure.json`, `golden-human-review.json`, `golden-editorial-diff.json`.
  - **Nuevas Suites de Pruebas Automatizadas:**
    - `src/tests/editorial/EditorialAuditEngine.test.ts`
    - `src/tests/regression/EditorialQAGoldenSnapshot.test.ts`
  - **Documentación:**
    - `docs/EDITORIAL_QA.md`, `docs/HUMAN_REVIEW_PROTOCOL.md`, `docs/EDITORIAL_DIFF.md`.
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/qa/editorial-findings.ts`
  - `[NEW]` `src/editorial/qa/editorial-remediation.ts`
  - `[NEW]` `src/editorial/qa/editorial-rules.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-audit-engine.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-qa-linter.ts`
  - `[MODIFY]` `src/editorial/qa/human-review-queue.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-diff-engine.ts`
  - `[MODIFY]` `src/editorial/qa/index.ts`
  - `[MODIFY]` `src/editorial/contracts/editorial-diff.types.ts`
  - `[MODIFY]` `src/mcp/tools/qa-tools.ts`
  - `[MODIFY]` `bin/editorial-cli.js`
  - `[NEW]` `fixtures/editorial/qa/golden-valid-documentary.json`
  - `[NEW]` `fixtures/editorial/qa/golden-warning-pacing.json`
  - `[NEW]` `fixtures/editorial/qa/golden-cognitive-overload.json`
  - `[NEW]` `fixtures/editorial/qa/golden-evidence-failure.json`
  - `[NEW]` `fixtures/editorial/qa/golden-continuity-failure.json`
  - `[NEW]` `fixtures/editorial/qa/golden-human-review.json`
  - `[NEW]` `fixtures/editorial/qa/golden-editorial-diff.json`
  - `[NEW]` `src/tests/editorial/EditorialAuditEngine.test.ts`
  - `[NEW]` `src/tests/regression/EditorialQAGoldenSnapshot.test.ts`
  - `[NEW]` `docs/EDITORIAL_QA.md`
  - `[NEW]` `docs/HUMAN_REVIEW_PROTOCOL.md`
  - `[NEW]` `docs/EDITORIAL_DIFF.md`
- **Verificación:** **1,299/1,299 pruebas pasando al 100% en 451 suites** (`npm test`), con 10 pruebas nuevas, cero fallos y cero regresiones. Certificación Level 5 Production Certified ratificada con **Gate 19 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #052 (Ref. #043): Data Visualization Engine & Procedural Statistical Graphics (REQ-025)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/data-viz/*`, `src/editorial/contracts/*`, `src/dsl/*`, `src/mcp/tools/dataviz-tools.ts`, `src/tests/fixtures/data-viz/*`, `src/tests/property/*`, `src/tests/regression/*`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Se requería una implementación canónica y completa de compilación de datos para producción audiovisual que transformara datasets tabulares y series temporales en representaciones intermedias vectoriales (IR), totalmente desacopladas de After Effects, no destructivas, matemáticamente deterministas, auditables, con integración a EvidenceEngine y StyleProfile TIME Editorial, respaldada por las 7 capas de verificación del proyecto.
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Contratos Canónicos y Validación (§4, §5):**
    - `src/editorial/contracts/data-viz.types.ts` y `src/editorial/data-viz/contracts.ts`: Definición de `Dataset`, `DatasetValue`, `DataSourceReference`, `DatasetValidationError`, `DataVisualizationCompiler`, `ValidationResult`.
    - Validación estricta en `validation.ts`: Intercepción de `NaN`, `Infinity`, strings vacíos, identificadores vacíos, timestamps inválidos y etiquetas ausentes.
  - **Normalización y Formateo Determinista (§6, §15, §16):**
    - `normalization.ts`: Normalización $n \in [0, 1]$ con política de serie constante $n = 0.5$ (`normalizeRange`).
    - `number-formatter.ts`: `DeterministicNumberFormatter` independiente del locale del sistema para monedas (`USD`, `EUR`, `MXN`, `GBP`, `JPY`), porcentajes (`%`) y unidades físicas (`kg`, `m`, `hours`, etc.).
  - **4 Compiladores Canónicos (§8, §11, §14, §17):**
    - `animated-bar-chart.ts`: Barras verticales y horizontales, cruce en zero-baseline para positivos/negativos, contador animado $\text{displayValue}(t) = \text{finalValue} \times \text{progress}(t)$, y divulgación de eje truncado (`AxisDisclosure`).
    - `trend-line-graph.ts`: Trazado vectorial con $x = \text{normalizedTime} \times \text{chartWidth}$, $y = \text{chartHeight} - \text{normalizedValue} \times \text{chartHeight}$, orden temporal estricto y anotación de extremos (`DataPointAnnotation`).
    - `big-stat-card.ts`: Tarjetas de alto impacto TIME Editorial (`#FFFFFF`, `#000000`, `#FF1424`), animación de entrada y citación de fuente fáctica.
    - `chronology-timeline.ts`: Líneas de tiempo cronológicas con verificación de orden temporal $t_n \le t_{n+1}$ y rechazo de eventos desordenados bajo política `BLOCKING`.
  - **Provenance y Desacoplamiento (§25, §26, §27, §28):**
    - `provenance.ts`: `ProvenanceTracker` con trazabilidad inmutable y binding de evidencia.
    - `visualization-base.ts`: Nodos IR editoriales (`BarChartNode`, `TrendLineNode`, `BigStatNode`, `TimelineNode`) sin instrucciones propietarias de After Effects.
  - **DSL, CLI y MCP (§29, §30, §31):**
    - `src/dsl/ProductionDSL.ts`: Soporte de la función declarativa `visualization({...})`.
    - `package.json`: Scripts `data-viz:validate`, `data-viz:compile`, `data-viz:test-fixture`.
    - `src/mcp/tools/dataviz-tools.ts`: 5 herramientas MCP canónicas (`data_viz_validate_dataset`, `data_viz_compile_bar_chart`, `data_viz_compile_trend_line`, `data_viz_generate_stat_card`, `data_viz_generate_timeline`).
  - **11 Golden Fixtures en `src/tests/fixtures/data-viz/` (§45):**
    - `bar-basic.json`, `bar-negative.json`, `bar-zero.json`, `bar-large.json`, `trend-basic.json`, `trend-flat.json`, `trend-negative.json`, `stat-percentage.json`, `stat-currency.json`, `timeline-basic.json`, `timeline-unsorted.json`.
  - **Suites de Pruebas (§47, §48):**
    - `src/tests/property/DataVisualization.property.test.ts`: PBT con `fast-check` verificando acotamiento en $[0, 1]$, monotonicidad de barras, determinismo e invariantes de límites (6 tests).
    - `src/tests/regression/GoldenDataVisualization.test.ts`: Regresión dorada sobre los 11 fixtures con verificación determinista de hash SHA-256 (11 tests).
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/contracts/data-viz.types.ts`
  - `[NEW]` `src/editorial/data-viz/contracts.ts`
  - `[NEW]` `src/editorial/data-viz/number-formatter.ts`
  - `[NEW]` `src/editorial/data-viz/provenance.ts`
  - `[NEW]` `src/editorial/data-viz/visualization-base.ts`
  - `[NEW]` `src/editorial/data-viz/animated-bar-chart.ts`
  - `[NEW]` `src/editorial/data-viz/trend-line-graph.ts`
  - `[NEW]` `src/editorial/data-viz/big-stat-card.ts`
  - `[NEW]` `src/editorial/data-viz/chronology-timeline.ts`
  - `[MODIFY]` `src/editorial/data-viz/normalization.ts`
  - `[MODIFY]` `src/editorial/data-viz/validation.ts`
  - `[MODIFY]` `src/editorial/data-viz/index.ts`
  - `[MODIFY]` `src/dsl/ProductionDSL.ts`
  - `[NEW]` `src/dsl/index.ts`
  - `[MODIFY]` `src/mcp/tools/dataviz-tools.ts`
  - `[MODIFY]` `package.json`
  - `[NEW]` `src/tests/fixtures/data-viz/bar-basic.json`
  - `[NEW]` `src/tests/fixtures/data-viz/bar-negative.json`
  - `[NEW]` `src/tests/fixtures/data-viz/bar-zero.json`
  - `[NEW]` `src/tests/fixtures/data-viz/bar-large.json`
  - `[NEW]` `src/tests/fixtures/data-viz/trend-basic.json`
  - `[NEW]` `src/tests/fixtures/data-viz/trend-flat.json`
  - `[NEW]` `src/tests/fixtures/data-viz/trend-negative.json`
  - `[NEW]` `src/tests/fixtures/data-viz/stat-percentage.json`
  - `[NEW]` `src/tests/fixtures/data-viz/stat-currency.json`
  - `[NEW]` `src/tests/fixtures/data-viz/timeline-basic.json`
  - `[NEW]` `src/tests/fixtures/data-viz/timeline-unsorted.json`
  - `[NEW]` `src/tests/property/DataVisualization.property.test.ts`
  - `[NEW]` `src/tests/regression/GoldenDataVisualization.test.ts`
- **Verificación:** **1,316/1,316 pruebas pasando al 100% en 453 suites** (`npm test`), con 17 pruebas nuevas, cero fallos y cero regresiones. Certificación Level 5 Production Certified ratificada con **Gate 21 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #053 (Ref. #043): Editorial QA Governance, Human-in-the-Loop & Deterministic Diff Engine (REQ-030 / REQ-081 / REQ-082 / REQ-083)
- **Fecha:** 2026-09-02
- **Versión:** `v4.0.0-editorial-master`
- **Módulos Afectados:** `src/editorial/qa/*`, `src/editorial/qa/rules/*`, `src/tests/editorial/*`
- **¿Por qué se agregó? (Causa raíz / Problema detectado):**
  - Se requería una implementación canónica y desacoplada de gobernanza editorial, auditoría pre-render, colas deterministas de revisión humana y motor de diff semántico e impacto multivariante para responder de forma inmutable: *¿Este montaje puede producirse, exportarse y emitirse conforme a las reglas técnicas, narrativas y de seguridad del motor?* Cumplimiento exhaustivo de REQ-030, REQ-081, REQ-082 y REQ-083 (§1 a §52).
- **¿Para qué se agregó? (Solución / Beneficio técnico):**
  - **Estructura Modular Canónica (§37):**
    - `src/editorial/qa/editorial-qa-finding.ts`: Tipos `EditorialQAFinding` y `EditorialSeverity` (`BLOCKING`, `WARNING`, `SUGGESTION`).
    - `src/editorial/qa/editorial-qa-rule.ts`: Interfaz `EditorialQARule` y contexto `EditorialQAContext`.
    - `src/editorial/qa/editorial-qa-profile.ts`: Esquema y perfil Zod `EditorialQAProfile` (umbral de confianza $0.70$, umbrales de carga cognitiva $0.85$, pacing, atención y beats).
    - `src/editorial/qa/editorial-qa-errors.ts`: Excepción `EditorialExportBlockedError`.
    - `src/editorial/qa/editorial-qa-report.ts`: Constructor `EditorialQAReportBuilder`, scores acotados a $[0.00, 100.00]$ y estados (`BLOCKED`, `REVIEW_REQUIRED`, `PASS_WITH_WARNINGS`, `PASS`).
    - `src/editorial/qa/editorial-diff-report.ts`: Contratos `TemporalImpact` y `EditorialImpactReport`.
    - `src/editorial/qa/editorial-impact-analyzer.ts`: `EditorialImpactAnalyzer` cuantificando impacto en duración, ritmo, narrativa, continuidad y evidencia.
    - `src/editorial/qa/editorial-qa-orchestrator.ts`: Orquestador desacoplado con ordenamiento estable de hallazgos (severidad $\to$ timestamp $\to$ ruleId $\to$ entityIds $\to$ findingId).
  - **13 Dominios de Reglas en `src/editorial/qa/rules/` (§7–§16, §37, §45):**
    - `structural.rules.ts`: QA-STRUCT-001..004 (referencias rotas, duplicados, esquema Zod, rechazo de NaN/Inf).
    - `temporal.rules.ts`: QA-TIME-001..004 (timecodes negativos, inconsistencias de duración $\epsilon \le 10^{-10}$, overlaps, gaps críticos).
    - `visual.rules.ts`, `audio.rules.ts`, `narrative.rules.ts`, `evidence.rules.ts`, `continuity.rules.ts`, `attention.rules.ts`, `cognitive-load.rules.ts`, `contrast.rules.ts`, `pacing.rules.ts`, `export.rules.ts`, `security.rules.ts`.
  - **Cola de Revisión Humana y Diff Semántico (§19–§28):**
    - Enrutamiento obligatorio para decisiones con $\text{confidence} < 0.70$ o `BLOCKING`.
    - Diff estructural y temporal calculando desplazamientos acumulados (`downstreamShiftSeconds`).
  - **Suites de Pruebas (§38, §51):**
    - `EditorialQALinter.test.ts` (PASS)
    - `HumanReviewQueue.test.ts` (PASS)
    - `EditorialDiffEngine.test.ts` (PASS)
    - `EditorialImpactAnalyzer.test.ts` (PASS)
    - `EditorialQAReport.test.ts` (PASS)
    - `EditorialQAGoldenSnapshot.test.ts` (PASS)
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/editorial/qa/editorial-qa-finding.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-rule.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-profile.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-errors.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-report.ts`
  - `[NEW]` `src/editorial/qa/editorial-diff-report.ts`
  - `[NEW]` `src/editorial/qa/editorial-impact-analyzer.ts`
  - `[NEW]` `src/editorial/qa/editorial-qa-orchestrator.ts`
  - `[NEW]` `src/editorial/qa/rules/structural.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/temporal.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/attention.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/cognitive-load.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/contrast.rules.ts`
  - `[NEW]` `src/editorial/qa/rules/security.rules.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-findings.ts`
  - `[MODIFY]` `src/editorial/qa/index.ts`
  - `[NEW]` `src/tests/editorial/EditorialImpactAnalyzer.test.ts`
  - `[NEW]` `src/tests/editorial/EditorialQAReport.test.ts`
- **Verificación:** **1,322/1,322 pruebas pasando al 100% en 455 suites** (`npm test`), con cero fallos y cero regresiones. Certificación Level 5 Production Certified ratificada con **Gate 19 aprobado** en `npm run conformance`.

---

### 🛠️ Mejora #040: Master Post-v4.0 Execution Completion Program (P0 a P4 + REQ-091 Convergence)
- **Fecha:** 2026-09-02 (v4.0.0-editorial-master)
- **Módulos Afectados:**
  - `src/editorial/audio/`: Audio IR (8 buses jerárquicos), Hierarchical Mixer, J/L-Cut Engine, Room Tone Matcher/Synthesizer, Dialogue Repair Engine, Adaptive Ducking, EBU R128 / BS.1770-4 Loudness Engine, Audio Punctuation y Soundscape.
  - `src/editorial/exporters/`: OpenTimelineIO Rational Timebase, Importer con auditoría de pérdidas, MOGRT Spec Generator y Packager.
  - `src/editorial/multicam/`: Speaker Detector, MultiCamera Director con validación geométrica de la Ley del Eje de 180° y regla inviolable de Protección Emocional.
  - `src/editorial/performance/`: Augmented AVL `IntervalTree` ($O(\log N + K)$ temporal collision search) con fallback lineal y benchmarks a escala.
  - `src/editorial/qa/review-ui/`: `HumanReviewInterface` con cuantificación de impacto multivariante, firma canónica criptográfica SHA-256 vinculada a hashes de IR y reporte QA, y dashboard offline.
  - `src/editorial/perception/`: Separación formal entre `DeterministicHeuristicProvider` (fallback matemático offline) y `LocalMultimodalModelProvider` (inferencia local sin vectores fingidos), analizador de cuadros y búsqueda semántica con explicabilidad estructurada.
  - `src/editorial/director/`: `VisualMetaphorEngine` (traducción de conceptos abstractos a patrones visuales), `DirectorIntent` y `StyleBible` (auditoría de `STYLE_VIOLATION`).
  - `src/editorial/series/`: `EpisodicSeriesMemory` con continuidad inmutable de personajes, locaciones, motivos y memoria de feedback editorial.
  - `src/editorial/optimization/`: `EditorialConstraintSolver` (inviolabilidad de restricciones duras) y `ParetoEditorialOptimizer` (optimización multiobjetivo y frente de Pareto no dominado).
  - `src/editorial/rendering/`: `ChunkedRenderEngine` y verificación REQ-037 de contigüidad y ausencia de pérdidas de fotogramas.
- **¿Por qué se agregó?:**
  - Para completar íntegramente los mandatos del Execution Contract Post-v4.0, cerrando las brechas de postproducción de audio inteligente, intercambio NLE (OTIO), indexación temporal logarítmica, gobernanza humana, percepción desacoplada, metáforas visuales, memoria episódica, optimización de Pareto, generación MOGRT y convergencia end-to-end del sistema.
- **¿Para qué se agregó?:**
  - Proporciona un sistema operativo editorial completamente determinista, offline-first, auditable, no destructivo y explicable, capaz de tomar decisiones de montaje, mezcla, balance y entrega sin riesgo de regresiones.
- **Archivos Creados / Modificados:**
  - 17 módulos de código en `src/editorial/`
  - 8 suites de prueba exhaustivas con PBT (`fast-check`) y fixtures deterministas en `src/tests/editorial/`
- **Verificación:** **1,375/1,375 pruebas pasando al 100% en 466 suites** (`npm test`), con cero fallos y cero regresiones. Suite de conformidad `npm run conformance` 100% aprobada con emisión del artefacto final de certificación (`reports/production-certification.json`).

---

### 🛠️ Mejora #041: Post-v4.0 Adversarial Certification & Production Hardening
- **Fecha:** 2026-09-02 (v4.0.0-editorial-master)
- **Módulos Afectados:**
  - `src/editorial/continuity/visual-continuity-engine.ts`: Eliminación de `crypto.randomBytes(4)` y sustitución por hashes canónicos deterministas SHA-256 vinculados a IDs de planos.
  - `src/editorial/qa/editorial-qa-engine.ts`: Eliminación de `crypto.randomBytes(3)` y sustitución por hashes canónicos deterministas SHA-256 para IDs de incidencias QA.
  - `src/editorial/exporters/otio-importer.ts`: Validador adversarial de timecodes negativos con error explícito `[OTIO_INVALID_TIMECODE_ERROR]` y auditoría de fidelidad de 4 niveles (`LOSSLESS`, `LOSSY-BUT-DOCUMENTED`, `UNSUPPORTED`, `INVALID`).
  - `src/editorial/perception/embedding-provider.ts`: Blindaje defensivo de `generateVisualEmbedding` ante atributos opcionales y reafirmación de honestidad arquitectónica para `LocalMultimodalModelProvider` (`[MISSING_LOCAL_NEURAL_WEIGHTS]`).
  - `scripts/run-conformance.mjs`: Actualización del ejecutor de conformidad para validar inspección estática de red cero (cero dependencias de red/telemetría), métricas dinámicas de 1,400 tests y emisión dual de reportes canónicos.
  - `reports/final-adversarial-certification.md` & `reports/final-adversarial-certification.json`: Documentos formales de auditoría adversarial.
- **¿Por qué se agregó?:**
  - Para realizar una auditoría adversarial de cierre antes del congelamiento final de producción, identificando y eliminando cualquier residuo de no-determinismo, asegurando el blindaje estricto de invariantes matemáticas (Pareto, AVL IntervalTree, EBU R128) y formalizando el estatus de las capacidades sin pesos locales.
- **¿Para qué se agregó?:**
  - Proporciona una base demostrablemente verificable donde el 100% de las afirmaciones técnicas están respaldadas por pruebas ejecutables en entornos limpios y aislados (air-gapped).
- **Archivos Creados / Modificados:**
  - `[NEW]` `src/tests/editorial/AdversarialCertification.test.ts`
  - `[NEW]` `reports/final-adversarial-certification.md`
  - `[NEW]` `reports/final-adversarial-certification.json`
  - `[MODIFY]` `src/editorial/continuity/visual-continuity-engine.ts`
  - `[MODIFY]` `src/editorial/qa/editorial-qa-engine.ts`
  - `[MODIFY]` `src/editorial/exporters/otio-importer.ts`
  - `[MODIFY]` `src/editorial/perception/embedding-provider.ts`
  - `[MODIFY]` `scripts/run-conformance.mjs`
- **Verificación:** **1,400/1,400 pruebas pasando al 100% en 476 suites** (`npm test`), con cero fallos y cero regresiones. Suite de conformidad `npm run conformance` 100% aprobada con emisión del artefacto final de certificación (`reports/production-certification.json`).

---

### 🛠️ Mejora #042: Motor de Sincronización Rítmica por Transientes de Audio (`BeatSyncEngine`)
- **Fecha:** 2026-09-02 (v4.1.0)
- **Módulos Afectados:**
  - `src/editorial/audio/beat-sync-types.ts`: Esquemas Zod para `AudioTransient`, `BeatGridSpec`, `BeatSyncMode`, `BeatSyncCutDecision` y `BeatSyncPlan`.
  - `src/editorial/audio/beat-sync-engine.ts`: Motor `BeatSyncEngine` con detección de transientes ODF/RMS adaptativa, generador de cuadrícula BPM (4/4, 3/4), alineador de planos con drift cero ($\Delta t \le 10^{-6}\text{s}$), pulsos reactivos de escala (punch-in al bombo) y generador de marcadores ExtendScript.
  - `src/editorial/audio/index.ts` & `src/editorial/index.ts`: Re-exportaciones públicas.
  - `spec/beat-sync-engine.md`: Especificación técnica formal.
  - `scripts/build-guadalajara-beat-sync.mjs`: Script de montaje rítmico automático a 120 BPM con metraje real de Guadalajara.
  - `src/tests/editorial/BeatSyncEngine.test.ts`: Suite de pruebas con PBT (`fast-check`) de 7 capas.
- **¿Por qué se agregó?:**
  - Para permitir que el motor alinee automáticamente los cortes visuales y los efectos de punch-in con el tempo musical y los golpes de percusión (downbeats/snares) sin desfase temporal.
- **¿Para qué se agregó?:**
  - Proporciona montaje rítmico exacto, continuo (zero-gap), respetando la duración mínima de plano y generando marcadores de compás y keyframes de pulsación de escala directamente en After Effects.
- **Archivos Creados / Modificados:**
  - `[NEW]` `spec/beat-sync-engine.md`
  - `[NEW]` `src/editorial/audio/beat-sync-types.ts`
  - `[NEW]` `src/editorial/audio/beat-sync-engine.ts`
  - `[NEW]` `src/tests/editorial/BeatSyncEngine.test.ts`
  - `[NEW]` `scripts/build-guadalajara-beat-sync.mjs`
  - `[MODIFY]` `src/editorial/audio/index.ts`
  - `[MODIFY]` `package.json`
  - `[MODIFY]` `docs/POST_PHASE_IMPROVEMENTS.md`
- **Verificación:** **1,432/1,432 pruebas pasando al 100% en 482 suites** (`npm test`), 0 fallos, 0 regresiones. Demostración validada con metraje real generando `dist/guadalajara_beat_sync.jsx` y `dist/guadalajara_beat_sync.otio`.





