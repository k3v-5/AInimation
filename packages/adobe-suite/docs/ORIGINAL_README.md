# Adobe Animation MCP (Model Context Protocol Server)

Servidor **MCP (Model Context Protocol)** nativo de alto rendimiento especializado en **animación 2D, rigging profundo de marionetas para Adobe Character Animator, producción vectorial en Illustrator, voces neuronales HD & Lip-Sync, composición en After Effects y escenografías 3D / Grease Pencil en Blender**.

Diseñado para permitir que modelos de lenguaje (Claude, Cursor, Antigravity, etc.) operen como directores de animación con control granular, cero simulaciones/mocks y máxima fidelidad técnica.

---

## 🌟 Capacidades y Catálogo de Herramientas (38 Tools)

### 1. Adobe Character Animator & Rigging 2D Profundo (12 Tools)
- **`ch_scaffold_puppet`**: Genera de forma headless (sin necesidad de Photoshop o Illustrator) un archivo binario `.psd` con rigging anatómico completo:
  - Estructura `+Head` independiente y parallax facial 2.5D.
  - Conjuntos de bocas con los **14 visemas gráficos estilizados** (`Neutral`, `Ah`, `Ee`, `Oh`, `Uh`, `W-Oo`, `F`, `L`, `M`, `D`, `S`, `R`, `Smile`, `Surprised`).
  - Tags físicos reglamentarios de Adobe: **Dangle** (inercia elástica en cabello y accesorios), **Draggable** (control manual con cursor) y **Fixed** (anclaje de pies al suelo).
  - Hand swap triggers con atajos numéricos (`Open (1)`, `Fist (2)`, `Point (3)`, `ThumbsUp (4)`).
- **`ch_scaffold_multi_angle_puppet`**: Genera marionetas multi-ángulo para el comportamiento **Head Turner** de Character Animator (3 vistas: `Frontal`, `Left Quarter`, `Right Quarter` o 5 vistas: añadiendo `Left Profile` y `Right Profile`). Cada ángulo cuenta con su propia boca con los 14 visemas completos, ojos y pupilas con desfase de perspectiva 2.5D.
- **`ch_scaffold_walk_puppet`**: Rigging integral para el motor de caminata (**Walk Behavior**), con vistas frontales y laterales de perfil completas y las 12 articulaciones reglamentarias etiquetadas (`Left Hip`, `Left Knee`, `Left Ankle`, `Left Heel`, `Left Toe`, `Right Hip`... `Waist`, `Neck`).
- **`ch_slice_artwork_to_puppet`**: Convierte cualquier ilustración plana o dimensiones de personaje en un puppet `.psd` anatómico multicapa con ojos, pupilas, cejas, torso, extremidades y los 14 visemas sintetizados.
- **`ch_add_puppet_triggers_and_physics`**: Inyecta en cualquier marioneta PSD existente sets de expresiones emocionales (`Blush (b)`, `Sweatdrop (w)`, `AnimeVein (v)`), ciclo de lágrimas de fotograma por fotograma (`Tears Cycle [1..3] (t)`), swap set de 6 gestos de manos (`Open (1)`, `Fist (2)`, `Point (3)`, `Peace (4)`, `ThumbsUp (5)`, `Wave (6)`), respiración automática (`+Chest Breather`) y física elástica Dangle.
- **`ch_audit_puppet_deep`**: Herramienta de Puppet Doctor que realiza un examen médico exhaustivo de cualquier PSD de Character Animator, evaluando 6 categorías (independencia, visemas, ojos, articulaciones de caminata, físicas y triggers) y emitiendo un score de salud de 0 a 100 con plan de remedición paso a paso.
- **`ch_auto_repair_puppet`**: Herramienta de auto-reparación del Puppet Doctor que toma un archivo PSD desorganizado, roto o incompleto y automáticamente agrega coronas de independencia (`+`), sintetiza los visemas faltantes, repara nombres de ojos/pupilas y reestructura la jerarquía sin tocar el arte original.
- **`ch_prepare_recording_take`**: Conductor de sesión de grabación: sintetiza audio neuronal 48kHz, genera la línea de tiempo de visemas (`.json`), cue sheet de hotkeys de triggers (`.txt`) y un script ExtendScript (`.jsx`) para After Effects Dynamic Link.
- **`ch_validate_puppet`**: Audita cualquier marioneta `.psd` en disco y emite un diagnóstico riguroso de rigging, capas independientes, jerarquía y físicas.
- **`ch_launch_character_animator`**: Lanza Adobe Character Animator en Windows abriendo directamente la marioneta o proyecto.
- **`ch_inspect_environment`**: Escanea el sistema e identifica automáticamente las rutas de Character Animator 2026, Illustrator 2026, After Effects 2026 y Blender 5.2.
- **`ch_get_roadmap_status`**: Hook persistente que reporta el avance secuencial de las fases del roadmap de desarrollo.

### 2. Adobe Illustrator Vector Studio (6 Tools)
- **`ai_create_document`**: Crea lienzos vectoriales con resolución, orientación y perfil de color RGB.
- **`ai_execute_jsx`**: Ejecución directa de scripts ExtendScript (`.jsx`) en Illustrator mediante automatización VBScript/COM sin bloqueos de interfaz.
- **`ai_trace_and_clean_sketch`**: Vectoriza bocetos o ilustraciones rasterizadas con presets optimizados de calco interactivo (Image Trace), limpiando nodos y trazados huérfanos.
- **`ai_auto_rig_slice`**: Analiza ilustraciones vectoriales y descompone su geometría en capas anatómicas reglamentarias (`+Head`, `Torso`, `+Left Arm`, `+Right Arm`, `+Left Leg`, `+Right Leg`).
- **`ai_apply_color_palette`**: Armoniza la paleta cromática del personaje con presets profesionales (`cyberpunk`, `pastel`, `anime`, `retro`, `monochrome`).
- **`ai_export_character_package`**: Exporta simultáneamente a formato `.ai` (PDF compatible para Character Animator) y `.svg` optimizado para web.

### 3. Motor de Voz Neuronal & Lip-Sync Preciso (5 Tools)
- **`audio_generate_expressive_speech`**: Síntesis neuronal cinematográfica mediante Microsoft Edge-TTS con 320+ voces HD:
  - **Español Regional:** Voces regionales auténticas (México, España, Argentina, Colombia).
  - **Inglés & Otros:** Voces nativas (US, UK, Australia, Canadá, Japón, etc.).
  - **Presets Emocionales:** Modulación dinámica de entonación y velocidad (`neutral`, `cheerful`, `whispering`, `angry`, `sad`, `excited`, `dramatic`).
  - **Formato Broadcast:** Resampleo automático a **48,000 Hz**, **16-bit PCM Mono WAV** con normalización de picos a **-1.0 dBFS** (estándar EBU R128 para Character Animator y postproducción).
- **`audio_export_lip_sync_markers`**: Exportación sincronizada de marcadores de línea de tiempo correspondientes a los 14 visemas:
  - **After Effects ExtendScript (`.jsx`)**: Crea marcadores automáticos con nombre de visema en la composición o capa activa.
  - **JSON Cue Sheet**: Datos estructurados con fotogramas exactos (`fps`), marcas de tiempo y visemas para motores de juego o web.
  - **Premiere Pro / Audition (`.csv`)**: Marcadores tabulados compatibles con software de edición no lineal.
- **`audio_list_available_voices`**: Catálogo completo de voces neuronales disponibles filtrables por código de idioma (`es`, `en`, `ja`, etc.).
- **`audio_generate_speech`**: Generador rápido de audio PCM 48kHz compatible con SAPI de Windows.
- **`audio_calculate_viseme_cues`**: Estimador analítico de cadencia fonética a partir de texto o guion.

### 4. Adobe After Effects & Interoperabilidad 2.5D (7 Tools)
- **`ae_generate_scene_manifest`**: Crea un archivo estándar Scene Manifest JSON y su constructor ExtendScript (`.jsx`). Define planos de profundidad (fondo, props, personaje, primer plano), cámara 3D, profundidad de campo, audio y lip-sync para interoperabilidad fluida con el motor de After Effects del usuario.
- **`ae_setup_25d_stage`**: Ensambla un escenario 2.5D tridimensional en After Effects con cámara 3D, controlador nulo (`Camera_Controller`), capas distribuidas en el eje Z y cálculo de compensación de escala para preservar el encuadre exacto.
- **`ae_apply_animation_expressions`**: Inyecta expresiones matemáticas ExtendScript profesionales para animación secundaria reactiva:
  - `squash_and_stretch`: Deformación elástica al hablar, impactar o rebotar.
  - `camera_shake`: Movimiento orgánico o dramático de cámara (`wiggle`).
  - `audio_reactive_bounce`: Escala o posición modulada por la amplitud del diálogo.
  - `blink_cycle`: Ciclo procedural de parpadeo para ojos.
  - `floating_idle`: Movimiento suave de respiración / flotación en reposo.
- **`ae_batch_render_queue`**: Encola y procesa lotes de renderizado desatendido con `aerender.exe` soportando plantillas y módulos de salida (ProRes con canal Alfa, H.264, etc.).
- **`ae_import_puppet_scene`**: Importa marionetas `.psd`/`.ai` en composiciones de After Effects ajustando dimensiones y encuadre.
- **`ae_execute_jsx`**: Ejecuta scripts ExtendScript en After Effects mediante el puente CLI `AfterFX.exe -r`.
- **`ae_render_comp`**: Renderizado desatendido en segundo plano con `aerender.exe`.

### 5. Blender 3D & Grease Pencil Híbrido (5 Tools)
- **`blender_scaffold_3d_room`**: Genera escenarios arquitectónicos tridimensionales procedurales en Blender 5.2 (habitación interior, dormitorio anime, calle cyberpunk, escenario ciclorama de estudio, galería minimalista) con iluminación cinematográfica de 3 puntos (Key, Fill, Rim), geometría de piso/paredes, atrezzo/props y cámara configurada.
- **`blender_render_parallax_passes`**: Renderiza pases multicapa de composición en canal alfa para After Effects:
  - **Beauty Pass**: Renderizado a todo color RGBA con transparencia de película activa.
  - **Shadow Catcher Pass**: Suelo configurado como capturador de sombras con canal alfa (permite que los personajes 2D proyecten sombras realistas sobre el fondo 3D).
  - **Z-Depth / Mist Pass**: Mapa de profundidad en escala de grises para niebla atmosférica y desenfoque de lente óptico en After Effects.
- **`blender_grease_pencil_sketch`**: Crea trazados y dibujos vectoriales estilizados 2D en el espacio 3D de Blender utilizando Grease Pencil v3 (siluetas de personajes, líneas de velocidad estilo anime, nubes cel-shaded y contornos neón).
- **`blender_execute_script`**: Ejecución desatendida de scripts Python (`bpy`) en Blender 5.2 con arranque ultra-rápido `--factory-startup -b`.
- **`blender_render_frame`**: Renderizado headless de fotogramas a resolución completa en PNG.

### 6. Visión Multimodal & Pipelines de 1 Clic (3 Tools)
- **`render_preview_frame_to_base64`**: Extrae y codifica fotogramas o imágenes en Base64 (`image/png` o `image/jpeg`) dentro de bloques de contenido nativo MCP, dotando a modelos con visión (Claude 3.5 Sonnet, Gemini 2.0 Flash/Pro, GPT-4o) de "ojos" para evaluar estética, poses de marionetas y armonía visual.
- **`pipeline_create_talking_character`**: Macro integral de dirección en un solo clic: genera simultáneamente la marioneta anatómica PSD, sintetiza el audio neuronal 48kHz con inflexión emocional, exporta los marcadores de visemas alineados y opcionalmente abre Character Animator.
- **`pipeline_render_social_clip`**: Macro para redes sociales: construye composiciones verticales (9:16 para TikTok/Shorts/Reels) u horizontales (16:9) combinando personaje 2D, fondo 2.5D/3D, diálogo sincronizado y rebote secundario.

---

## 🚀 Configuración en Clientes MCP

### En Claude Desktop (`claude_desktop_config.json`) o Cursor:

```json
{
  "mcpServers": {
    "adobe-animation": {
      "command": "node",
      "args": ["F:/Dev/AdobeEngineSuit/dist/index.js"]
    }
  }
}
```

---

## 🛠️ Comandos de Desarrollo

```bash
# Compilar TypeScript y copiar scripts auxiliares
npm run build

# Ejecutar suite de pruebas unitarias reales (39 tests pasando)
npm test

# Iniciar servidor MCP en modo manual por stdio
npm start
```

---

## 📁 Estructura del Proyecto

```
AdobeEngineSuit/
├── src/
│   ├── index.ts                 # Servidor MCP y registro central (38 herramientas activas)
│   ├── core/
│   │   ├── AdobeDetector.ts     # Detección de software local 2026
│   │   ├── CharacterAnimatorDeepEngine.ts # Rigging profundo multi-ángulo, caminata, triggers y doctor
│   │   ├── PuppetBuilder.ts     # Rigging base y PSD binario real (ag-psd)
│   │   ├── VisemeDrawer.ts      # Geometría de los 14 visemas reglamentarios
│   │   ├── NeuralSpeechEngine.ts# Motor de voz Edge-TTS, modulación emocional y marcadores
│   │   ├── WavGenerator.ts      # Generador WAV 48kHz PCM y fonemas
│   │   ├── SceneManifestBuilder.ts # Manifiestos de escena 2.5D para After Effects
│   │   ├── BlenderEngine.ts     # Motor procedural 3D y Grease Pencil v3
│   │   ├── PipelineManager.ts   # Pipelines macro y encoder base64
│   │   ├── VbsRunner.ts         # Automatización COM de Illustrator
│   │   └── scripts/
│   │       └── edge_synth.py    # Helper Python para síntesis, resampleo 48k y normalización
│   └── tools/
│       ├── characterTools.ts    # 12 herramientas profundas de Character Animator
│       ├── illustratorTools.ts  # 6 herramientas de Illustrator Vector Studio
│       ├── audioTools.ts        # 5 herramientas de Audio y Voz Neuronal
│       ├── afterEffectsTools.ts # 7 herramientas de After Effects 2.5D
│       ├── blenderTools.ts      # 5 herramientas de Blender 3D & Grease Pencil
│       └── pipelineTools.ts     # 3 herramientas de visión multimodal y pipelines de 1 clic
├── tests/                       # 8 suites de pruebas unitarias reales (39 de 39 pasando, 100%)
└── .animation_roadmap_state.json# Estado persistente del roadmap
```
