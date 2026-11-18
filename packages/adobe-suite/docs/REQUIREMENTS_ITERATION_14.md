# Iteration 14: After Effects Native Bridge (ExtendScript & Dynamic Link)

## Objetivo
Posicionar a After Effects como el motor central de composición "headless" (sin UI) para el Agentic OS. En lugar de simular clics, el agente inyectará scripts ExtendScript (.jsx) nativos dentro de AE para importar proyectos de Character Animator o Photoshop (usando Dynamic Link), manipular el timeline, crear animaciones algorítmicas y renderizar sin intervención humana.

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-45: ExtendScript Execution Capability:**
    *   `AfterEffectsProvider` debe exponer una nueva capacidad `ae.execute_jsx`.
    *   La capacidad debe aceptar una ruta a un archivo `.jsx` local o un payload de script en string.
*   **AC-46: Provider Integration:**
    *   Modificar `AfterEffectsProvider.executeCapability()` para enrutar `ae.execute_jsx` a través de la comunicación subyacente. En este caso, usaremos el `Client` de `@modelcontextprotocol/sdk/client` para inyectar comandos de After Effects.
*   **AC-47: Dynamic Link Prototype (importAndRig.jsx):**
    *   Crear al menos un script funcional `importAndRig.jsx` dentro del código del motor (`src/providers/after-effects/jsx/`) que demuestre la API de ExtendScript de After Effects: importar un asset y agregarlo a una nueva composición.
*   **AC-48: LLM Awareness:**
    *   Actualizar `system_prompt.ts` para informar a la IA que puede utilizar `ae.execute_jsx` enviando instrucciones a este motor semántico para componer escenas sin pedir ayuda.
