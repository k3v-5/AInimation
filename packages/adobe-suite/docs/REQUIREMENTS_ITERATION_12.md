# Iteration 12: Visual Computer Vision Perception (VLM Integration)

## Objetivo
Mejorar la capa de percepción (`PerceptionAndRecoveryLayer`) para que, además de verificar la existencia de archivos físicos, su tamaño (FileSystemObserver) y su integridad estructural (JSON/metadatos), el motor pueda inspeccionar **visualmente** el artefacto resultante usando un Vision Language Model (VLM). Esto garantiza que no solo haya un archivo ".psd" o ".mp4", sino que su contenido cumpla la expectativa creativa (e.g. "El personaje tiene los ojos abiertos", "El video no tiene glitches").

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-38: VLM Provider Interface:**
    *   Implementar una interfaz y clase base `VisionModelProvider` que reciba una ruta de archivo (imagen o frame de video) y un prompt de validación.
*   **AC-39: Visual Perception Layer Hook:**
    *   Agregar `validateVisualArtifact(filePath: string, criteria: string): Promise<ValidationResult>` a `PerceptionAndRecoveryLayer`.
    *   El método debe extraer el resultado del VLM. Si el VLM indica que no cumple el criterio, devolver `isValid: false` y los `divergences` (el feedback del VLM).
*   **AC-40: DAG Engine Injection:**
    *   Modificar `AnimationEngine.ts` para que, si un nodo del plan especifica un parámetro `visual_validation` (p.ej. en `ps.document.export` o `render.export`), el motor ejecute la validación visual *después* de la validación física.
    *   Si falla la validación visual, disparar el ciclo de `Recovery` estándar (Self-healing).
*   **AC-41: Prompt Engineering:**
    *   Modificar `system_prompt.ts` para instruir al Agente de IA a que inyecte el campo `visual_validation` con descripciones explícitas para assets clave.
