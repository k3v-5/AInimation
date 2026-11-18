# Iteration 15: Adobe Premiere Pro Integration (Auto-Editing Bridge)

## Objetivo
Expandir el Agentic OS integrando Adobe Premiere Pro como el motor de edición final. Después de que After Effects o Character Animator hayan renderizado múltiples tomas (shots), el Agente de IA usará Premiere Pro mediante scripts nativos (ExtendScript JSX) para ensamblar el corte final automáticamente.

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-49: ExtendScript Execution Capability (Premiere):**
    *   Implementar `PremiereProProvider.ts` que exporte las capacidades `video.edit` y `pr.execute_jsx`.
    *   La ejecución debe basarse en el CLI nativo (e.g. pasar el script al proceso de Premiere o usar la abstracción OS fallback) de forma similar a `AfterEffectsProvider`.
*   **AC-50: Sequencing JSX Prototype:**
    *   Crear `importAndSequence.jsx` que lea una serie de rutas de archivos de video, cree una secuencia en Premiere, y los agregue consecutivamente a la línea de tiempo.
*   **AC-51: Engine Registration:**
    *   Instanciar y registrar el `PremiereProProvider` en el punto de entrada de la aplicación (`src/index.ts` y `src/cli.ts`).
*   **AC-52: Agent Awareness:**
    *   Actualizar `system_prompt.ts` para que el Agente conozca la capacidad de unir videos exportados usando Premiere Pro en su Workflow DAG.
