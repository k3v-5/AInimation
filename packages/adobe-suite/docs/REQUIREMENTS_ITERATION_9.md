# Documento de Requerimientos: Iteración 9 - Memoria de Proyecto y Contexto Persistente

## 1. Objetivo de la Iteración

Dotar al sistema de persistencia a largo plazo mediante una base de datos local que actúe como un registro histórico y relacional de proyectos, *assets* y estados de ejecución. El Agente de IA debe ser capaz de consultar este repositorio para reutilizar archivos (como personajes o fondos generados en sesiones anteriores) y modificar proyectos existentes mediante actualizaciones parciales del DAG, sin regenerar todo desde cero.

## 2. Alcance

**Incluye:**
1. **Capa de Persistencia de Datos:** Integración de un motor de base de datos local (ej. SQLite) para almacenar el esquema relacional de los proyectos.
2. **Sistema de Indexación de Assets:** Un gestor (ProjectManager) que guarde metadatos críticos de cada archivo generado (ID, ruta absoluta, tipo de *provider*, *checksum* o fecha de modificación).
3. **Recuperación de Contexto Cognitivo:** Expansión del bucle REPL para que la IA pueda hacer consultas (queries) a la base de datos antes de armar su DAG, descubriendo qué *assets* ya existen.
4. **Ejecución Parcial (Cache-Aware DAG):** Modificación del motor de grafos para saltar nodos si el *asset* de salida ya existe y el usuario no ha solicitado su modificación.

**No incluye:**
* Plantillas automáticas o flujos pre-armados (Opción C).
* Desarrollo de animaciones complejas o físicas exageradas (Opción A).

## 3. Requerimientos Técnicos Detallados

### Req 1: Diseño del Esquema de Datos Relacional
* **Descripción:** Definir la estructura base para el gestor de proyectos local.
* **Especificaciones:**
  * Crear e inicializar el esquema en el arranque del sistema (`npm start`).
  * **Entidades Principales:**
    * **Project**: El contenedor lógico de una petición del usuario. `id`, `name`, `created_at`, `last_modified`
    * **Asset**: Archivos físicos generados (.psd, .chproj, .mp4). `id`, `project_id`, `type`, `local_path`, `hash`
    * **Execution**: Registro de una corrida del DAG. `id`, `project_id`, `status`, `intent_json`

### Req 2: Herramientas de Recuperación para la IA (RAG Local)
* **Descripción:** El Agente LLM no puede adivinar qué existe en el disco duro. Necesita herramientas MCP para investigar.
* **Especificaciones:**
  * Exponer nuevas `Tools` al servidor MCP específicas para memoria:
    * `memory.list_projects()`: Devuelve los proyectos recientes.
    * `memory.get_assets(project_id)`: Lista los archivos asociados a un proyecto, incluyendo sus rutas.
  * Actualizar el *System Prompt* para que, cuando el usuario pida "cambiar algo de ayer", el Agente sepa que su primera acción debe ser consultar la memoria antes de armar el *Intent* de animación.

### Req 3: Optimización del DAG (Ejecución Parcial)
* **Descripción:** Eficiencia en la iteración. Si el fondo no cambia, no abras Photoshop.
* **Especificaciones:**
  * Modificar el `WorkflowGraphEngine` para evaluar el estado previo.
  * Si el JSON de intención usa una ruta referenciada desde la base de datos (ej. un *puppet* ya exportado), el motor debe marcar el nodo generador como `SKIPPED (Cached)` y usar el archivo existente directamente en las operaciones dependientes (Character Animator / After Effects).

## 4. Criterios de Aceptación (AC)

* **AC-25 (Persistencia Estructurada):**
  * **Dado:** El usuario pide generar una animación desde cero.
  * **Cuando:** El flujo End-to-End finaliza exitosamente.
  * **Entonces:** La base de datos local registra un nuevo `Project`, y asocia como mínimo tres `Assets` (el `.psd` de PS, el `.chproj` de CH, y el `.mp4` de AE) con sus rutas absolutas correctas.

* **AC-26 (Recuperación y Modificación):**
  * **Dado:** Un proyecto guardado en la sesión de ayer (ej. "Video Juan").
  * **Cuando:** El usuario reinicia el sistema hoy y pide: *"Abre el Video Juan y cámbiale la voz"*.
  * **Entonces:** El Agente consulta la herramienta de memoria, localiza el `.chproj` de Juan, arma un DAG que omite la fase de Photoshop (porque el *puppet* ya existe), y solo ejecuta Character Animator para el nuevo *lip-sync* y After Effects para el *render*.

* **AC-27 (Integridad Física vs Lógica):**
  * **Dado:** Un registro en la base de datos que apunta a un archivo `.psd`.
  * **Cuando:** El usuario borra accidentalmente el `.psd` manualmente del explorador de Windows/Mac.
  * **Entonces:** Cuando el motor intenta usarlo en una ejecución parcial, la *Perception Layer* detecta la ausencia física, invalida la caché de ese nodo, y desencadena el *Self-Healing* para regenerar el archivo en Photoshop de forma transparente.
