# Agentic OS: Future Expansion & Architectural Roadmap

El "Agentic OS" ha completado sus fundamentos (Iteraciones 1-17). El motor actual es capaz de parsear lenguaje natural a un DSL de animación (Zod), ejecutar grafos acíclicos dirigidos (DAGs) concurrentes, realizar self-healing cognitivo, recordar assets (SQLite RAG), validar resultados físicamente y visualmente (VLM, Spatial Vision), y ejecutar scripts nativos ExtendScript y macros OS de manera agnóstica. Además, cuenta con una arquitectura de Inteligencia de Enjambre (Swarm Intelligence) que orquesta sub-agentes especializados y se ha expandido fuera del ecosistema Adobe incorporando capacidades de Audio (TTS) y 3D (Blender).

Para llevar este ecosistema a una **Agencia de Animación Autónoma completa**, se proponen las siguientes expansiones estratégicas para las próximas iteraciones.

---

## 1. Expansión del Ecosistema 2D/Video (Nuevos Adapters & Integraciones Profundas)

Aunque After Effects y Premiere Pro están integrados, el motor de ejecución puede mejorar su profundidad de orquestación.

### Adobe Media Encoder (`MediaEncoderProvider`) - [X] REALIZADO
*   **Capacidad Objetivo:** `render.batch_encode`, `render.compress`.
*   **Técnica:** ExtendScript nativo / Implementación Provider.
*   **Casos de uso para la IA:** Enviar colas pesadas de After Effects y Premiere a Media Encoder en segundo plano (`background_render`) mientras el Agente sigue construyendo escenas nuevas en paralelo en el DAG.
*   *Nota: Se implementó la estructura base, pruebas unitarias y registro del Provider en la capa MCP para iniciar orquestaciones de codificación en lotes.*

### Adobe Illustrator Advanced (`IllustratorProvider` V2) - [X] REALIZADO
*   **Capacidad Objetivo:** `vector.generate_rig_layers`, `vector.style_transfer`.
*   **Técnica:** JSX Scripts complejos.
*   **Casos de uso para la IA:** Automatizar la separación lógica de un SVG plano (generado por IA) en capas estructuradas (ej. `+Head`, `+Right Arm`, `+Left Eye`), preparándolo matemáticamente para rigging en Character Animator o After Effects.
*   *Nota: Se implementaron las capacidades y tests base en IllustratorProvider, registrándolas en el parser universal y system prompt.*

### Premiere Pro Advanced (Edición Inteligente) - [X] REALIZADO
*   **Capacidad Objetivo:** `video.auto_edit`, `video.sync_audio`.
*   **Mejora:** La IA podrá utilizar Premiere para ensamblar múltiples renders de After Effects generados previamente por el Swarm, sincronizar automáticamente pistas de audio (TTS) con los cortes del video utilizando detección de silencios, y exportar la línea de tiempo final.
*   *Nota: Se han agregado las capacidades, se integraron en el IntentParser y system prompt para su uso inmediato mediante JSX.*

---

## 2. Refinamiento de la Arquitectura de Swarm y Cognición

Ya contamos con un `SwarmDirector` y agentes especializados (`DesignAgent`, `RiggingAgent`, `AudioAgent`, `BlenderAgent`). El siguiente paso es evolucionar la lógica de toma de decisiones.

### Enrutador de Swarm Basado en LLM (LLM-based Router) - [X] REALIZADO
*   **Estado Actual:** El `SwarmDirector` delega tareas basándose en reglas heurísticas simples (coincidencia de palabras clave como "3d", "audio", "rig").
*   **Mejora Objetivo:** Reemplazar el enrutamiento rígido con un clasificador basado en un modelo de lenguaje ligero o RAG semántico. Esto permitirá interpretar comandos ambiguos del usuario y dividir un prompt maestro (Ej: "Haz un comercial 3D con voz de narrador") en múltiples grafos interconectados que llamen de forma simultánea a `BlenderAgent` y `AudioAgent`.
*   *Nota: Se integró la capacidad de inyectar el `ILLMProvider` en el `SwarmDirector` para clasificar semánticamente los prompts (design, rigging, audio, 3d).*

### Generación Dinámica de Audio y Sincronización Labial
*   **Estado Actual:** `AudioAgent` expone la intención y `AudioProvider` mockea un archivo `.wav`.
*   **Mejora Objetivo:** Integrar llamadas HTTP reales a APIs de TTS (ej. ElevenLabs, OpenAI TTS). Luego, enviar la forma de onda generada al proveedor correspondiente (After Effects o Character Animator) ejecutando un proceso automatizado de Lip Sync de audio a fonemas espaciales.

---

## 3. Human-in-the-Loop (HITL) & Control UI

### Extensiones Físicas de Adobe (CEP Panels)
*   **Descripción:** Ya hemos construido el servidor `AdobeCEPAdapter` (puerto 3001). Falta construir el front-end y el archivo ZIP de extensión (HTML/JS/CSXS) que se instala nativamente.
*   **Implementación:** Un panel lateral flotante dentro de After Effects/Premiere donde el animador puede "chatear" con la IA sin salir de su ventana de trabajo. El panel muestra la barra de carga del DAG del motor Agentic OS en tiempo real.

### Checkpoints de Aprobación Cognitiva
*   **Descripción:** No todas las tareas asíncronas (como generar assets críticos) deben ejecutarse solas.
*   **Implementación:** Modificar el `WorkflowGraphEngine` para soportar estados de nodo `WAITING_FOR_HUMAN`.
*   **Caso de uso:** La IA genera 4 bocetos distintos de un personaje principal. El DAG se pausa. El humano aprueba el boceto #3 a través de la terminal o interfaz. El DAG resume (`resumeIntent`) utilizando el asset aprobado como entrada para la fase de Rigging.

---

## 4. Evolución de la Capa de 3D y Generación de Entornos

### Pipeline Blender Completo (3D Workflow)
*   **Estado Actual:** `BlenderAgent` genera intenciones y `BlenderProvider` ejecuta scripts Python (`bpy`) headless básicos.
*   **Mejora Objetivo:** Implementar un DAG 3D completo. Crear capacidades granulares como `blender.model.create`, `blender.rig`, `blender.render`, permitiendo a la IA ensamblar una cadena de procesos donde importa texturas generadas por Photoshop, modela formas paramétricas con scripts dinámicos en Python, y renderiza imágenes fotorealistas de forma autónoma.
