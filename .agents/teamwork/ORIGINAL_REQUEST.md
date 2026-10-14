# Original User Request

## 2026-10-14T00:27:10Z

Construir una aplicación de escritorio nativa ("Orquestador de Animación 3D e IA") que automatiza la creación de objetos 3D desde imágenes, rigging, captura de movimiento y renderizado cinemático audiovisual mediante un servidor FastMCP que controla Unreal Engine 5 e integra pipelines de IA generativa en modo copiloto asistido paso a paso.

Working directory: e:\Disco F\Dev\IANIMATION
Integrity mode: demo

## Requirements

### R1. Orquestación y Control de Unreal Engine 5 (Headless / Remote Control)
Desarrollar el cliente/adaptador de comunicación bidireccional (HTTP / WebSocket) con Unreal Engine 5 Remote Control API. Debe permitir:
- Importación dinámica en runtime de mallas 3D (`.glb` / `.fbx`) y esqueletos animados.
- Asignación programática de materiales PBR, texturas y configuración de iluminación Lumen.
- Generación y control de cámaras cinemáticas sincronizadas por frames/marcas de tiempo.
- Disparo de colas de renderizado de alta fidelidad vía Movie Render Queue (MRQ) o exportador cinemático.

### R2. Pipeline Híbrido de IA (Cloud API + Local Fallback)
Implementar una arquitectura modular y desacoplada de pipelines de IA con soporte primario para APIs Cloud (Fal.ai, Tripo AI, Replicate) y compatibilidad para backends locales (TRELLIS, ComfyUI, GVHMR/4DHumans):
- **Audio:** Análisis de BPM, beats y separación de stems (batería, bajo, voz) con Librosa/Demucs.
- **Image-to-3D:** Conversión de imágenes 2D a mallas 3D estructuradas con texturas PBR.
- **Auto-Rigging:** Detección de anatomía bípeda y asignación de esqueleto estándar deformable.
- **Mocap & Rotoscopia:** Extracción de movimiento 3D desde video de referencia y limpieza de fondos.
- **Neural Enhancer:** Integración con ComfyUI (ControlNet / AnimateDiff / Wan 2.1) para pase estético final.

### R3. Interfaz de Escritorio Nativa en Tauri (Rust + React/TypeScript)
Construir una interfaz de usuario fluida, moderna y reactiva:
- Zona interactiva Drag-and-Drop para importar imágenes de referencia, pistas de audio (`.mp3`/`.wav`) y videos de baile (`.mp4`).
- Timeline audiovisual multipista con visualización de formas de onda de audio y keyframes de escena.
- Visor de previsualización 3D (soporte para Pixel Streaming WebRTC embebido o ventana esclava sincronizada).
- Consola de diálogo con el Agente Copiloto con visualización de las herramientas ejecutadas y previsualizaciones intermedias.

### R4. Servidor FastMCP y Modo Copiloto Asistido (Human-in-the-Loop)
Construir un servidor MCP en Python (FastMCP) que expone las herramientas atómicas del pipeline (`analyze_audio`, `image_to_3d`, `auto_rig`, `extract_mocap`, `build_ue5_scene`, `render_video`):
- Flujo guiado paso a paso donde el agente propone el plan de producción desglosado y solicita confirmación del usuario antes de ejecutar operaciones pesadas.
- Sistema de telemetría, logs en tiempo real y reporte de progreso porcentual transmitido al frontend vía WebSocket/SSE.

## Acceptance Criteria

### Control y Comunicación con UE5
- [ ] La capa de control de UE5 cuenta con un cliente WebSocket/REST que serializa y envía comandos conformes a la especificación de Unreal Engine Remote Control API.
- [ ] Existe un emulador/mock server de UE5 Remote Control API para validar todas las llamadas RPC sin requerir una instancia de Unreal abierta.
- [ ] La carga de assets GLB/FBX y asignación de transformadas espaciales produce respuestas estructuradas verificables con código de éxito.

### Pipelines de IA y Audio
- [ ] El módulo de análisis de audio procesa un archivo `.wav`/`.mp3` y extrae BPM, onsets y timestamps en un formato JSON estandarizado.
- [ ] Los adaptadores de Image-to-3D y Auto-rigging procesan la entrada y entregan rutas a archivos `.glb`/`.fbx` válidos, con manejo de reintentos y fallback ante errores.
- [ ] El pipeline soporta ejecución asíncrona no bloqueante con emisión de eventos de progreso.

### Servidor FastMCP y Copiloto
- [ ] El servidor FastMCP expone las herramientas con esquemas JSON Schema rigurosos y documentación de parámetros.
- [ ] La interacción copilot emite planes estructurados con puntos de confirmación explícitos antes de invocar herramientas de renderizado o generación.
- [ ] Todas las herramientas MCP pueden invocarse tanto vía cliente MCP estándar como directamente desde el backend de la app.

### Frontend Desktop y Suite de Verificación
- [ ] El proyecto Tauri compila correctamente y renderiza los componentes principales (timeline, dropzone, chat copiloto y panel de configuración).
- [ ] Existe una suite de pruebas automatizadas (`pytest` para el backend/MCP y tests unitarios para el frontend) con cobertura de casos nominales y de fallo.
- [ ] Un script CLI de verificación end-to-end (`verify_pipeline.py`) ejecuta el flujo simulado completo desde el audio hasta el render mockeado, verificando que todos los artefactos intermedios se generen con éxito.

### Estándares de Ingeniería, Continuidad y Calidad (SOLID, Tipado y Verificación Visual)
- [ ] **Tipado Estricto 100%**: Código TypeScript con `strict: true` (sin uso de `any`) y código Python con tipado estricto (`mypy` / modelos Pydantic v2).
- [ ] **Diseño SOLID y Modular**: Interfaces desacopladas para motores 3D y backends de IA que permitan extensión sin modificar el núcleo.
- [ ] **Documentación e Indexación**: Toda función, módulo y herramienta MCP documentada e indexada en un `README.md` y catálogo de herramientas.
- [ ] **Continuidad entre LLMs (`PROJECT_STATUS.md`)**: Creación y mantenimiento continuo de un archivo de estado con avances completados, decisiones clave y lista priorizada de pendientes detallada.
- [ ] **Verificación Visual Exhaustiva**: Comprobación visual minuciosa en las pruebas de UI para constatar que cada botón, timeline, forma de onda y panel esté correctamente posicionado y formateado.
