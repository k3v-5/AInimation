# Iteration 16: Active Spatial Vision & Swarm Intelligence

## Objetivo
Transformar el Agentic OS de un sistema de agente único (AgentPlanner) con validación pasiva a un enjambre de inteligencias especializadas (Swarm Intelligence) capaz de realizar auto-correcciones milimétricas utilizando modelos de visión con conciencia espacial (Spatial VLM).

Esto está diseñado asumiendo que un Agente LLM maestro externo (como Claude Code o Antigravity) consumirá el MCP de este motor para solicitar tareas complejas.

## Acceptance Criteria (Criterios de Aceptación)

### 1. Swarm Intelligence (Multi-Agent Architecture)
*   **AC-53: Swarm Director:** Crear `SwarmDirector` que actúe como router. Cuando el LLM externo envíe una petición abstracta, el Director decidirá si delega al `DesignAgent` o al `RiggingAgent`.
*   **AC-54: Specialized Sub-agents:**
    *   `DesignAgent`: Experto en generar prompts de Photoshop y comandos de dibujado.
    *   `RiggingAgent`: Experto en generar scripts ExtendScript (`.jsx`) para alinear anclas y componer en After Effects/Character Animator.

### 2. Visión Espacial Dinámica (Active Spatial VLM)
*   **AC-55: Spatial Queries:** Actualizar el `VisionModelProvider` con un método `inspectImageSpatial(filePath, query)` que no solo devuelva "aprobado/fallido", sino coordenadas `(x, y)` o cajas delimitadoras (Bounding Boxes).
*   **AC-56: Dynamic JSX Correction:**
    *   Si el Motor (PerceptionLayer) detecta que una capa o ancla está desalineada según las coordenadas del VLM, el `RiggingAgent` debe ser invocado dinámicamente durante la fase de *Self-Healing*.
    *   El `RiggingAgent` generará un snippet `.jsx` on-the-fly (ej. `layer.property("Position").setValue([newX, newY])`) para corregir el desfase espacial matemáticamente.
    *   El motor ejecutará esta corrección automáticamente usando el `AfterEffectsProvider` antes de volver a validar.
