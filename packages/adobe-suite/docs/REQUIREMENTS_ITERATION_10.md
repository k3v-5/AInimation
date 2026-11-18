# Iteration 10: Gestión de Contexto Interrumpible y Continuación de Memoria

## Objetivo
Permitir que los flujos de trabajo (DAGs) de animación de larga duración puedan ser pausados, interrumpidos (por ejemplo, por un fallo del sistema, una interrupción manual SIGINT, o un cierre inesperado) y reanudados exactamente desde el punto donde se quedaron, sin regenerar o re-ejecutar nodos que ya se completaron con éxito.

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-30: Persistencia de Operaciones (Node State Tracking):**
    *   El `ProjectManager` y la base de datos (SQLite) deben registrar el estado granular de cada `Operation` (nodo del DAG) asociado a una ejecución (`executions`).
    *   Estados permitidos a persistir: PLANNED, EXECUTING, SUCCESS, FAILED, SKIPPED, PAUSED.
*   **AC-31: Serialización de Contexto (Context Hydration):**
    *   El `executionContext` (los mapeos de variables y salidas de dependencias, ej. `${op1.output} = /ruta/al/archivo.psd`) debe serializarse y guardarse en la base de datos conforme avanza el DAG.
    *   Al reanudar, este contexto debe ser rehidratado para que los nodos posteriores reciban correctamente las rutas de los nodos ya completados en sesiones anteriores.
*   **AC-32: Lógica de Reanudación (Resume Intent):**
    *   Implementar un método `resumeIntent(intent_id)` en `AnimationEngine.ts`.
    *   Este método debe cargar el intent original, reconstruir el Grafo de Flujo de Trabajo (DAG), leer el estado histórico, y planificar únicamente los nodos cuyo estado *no* sea `SUCCESS` ni `SKIPPED`.
*   **AC-33: Transiciones Seguras ante AbortController:**
    *   Si se recibe una señal de cancelación (ej. el usuario pulsa Ctrl+C o llama al abortController), el sistema debe capturar esto y guardar el estado actual de los nodos en progreso como `FAILED` o `PAUSED` de manera limpia en SQLite antes de morir.
*   **AC-34: Exposición a la IA (MCP Tools):**
    *   Agregar una herramienta `memory.resume_intent` al servidor MCP para que la IA pueda proponer la reanudación si el usuario menciona un trabajo fallido o pausado.

## Diseño de la Solución

1. **Schema DB Upgrade (`Database.ts`):**
   - Modificar la tabla `executions` para incluir `context_json` (para guardar el executionContext).
   - Crear una tabla `operations` (o `execution_nodes`) referenciando a `execution_id`, que guarde: `id`, `capability`, `status`, `result_json`, `error_text`.
2. **Eventos y Persistencia en Tiempo Real:**
   - Escuchar los eventos `operation_status` del `AnimationEngine` para hacer UPDATEs inmediatos a la tabla `operations` usando el `ProjectManager`.
3. **Re-hidratación del Contexto:**
   - En `AnimationEngine.processIntent`, añadir una validación inicial: Si existe una ejecución previa para ese intent, cargar su `executionContext`.
   - Modificar el procesado por lotes (`for (const batch of executionBatches)`) para que evalúe si todos los nodos del batch ya están en `SUCCESS` en DB. Si es así, saltarlos y popular el `executionContext` a partir de sus resultados pasados.
