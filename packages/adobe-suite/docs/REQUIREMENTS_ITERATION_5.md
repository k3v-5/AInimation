# Documento de Requerimientos: Iteración 5 - Orquestación Multi-App y Post-Producción

## 1. Objetivo de la Iteración
Evolucionar el WorkflowGraphEngine de un sistema mono-aplicación a un verdadero orquestador de suite (Multi-App). El motor debe ser capaz de transferir el estado y los artefactos físicos (rutas de archivos) resultantes de una aplicación (Character Animator) como entradas directas para una segunda aplicación (After Effects), logrando un pipeline ininterrumpido.

## 2. Alcance

**Incluye:**
*   **Paso de Contexto (Context & Artifact Passing):** Modificación del DAG para inyectar dinámicamente las salidas de un nodo (ej. el `.mp4` de CH) en los parámetros de entrada del nodo dependiente.
*   **Enrutamiento de Proveedores (Provider Routing):** Capacidad del motor para inicializar y alternar entre distintos Providers dentro del mismo flujo de trabajo, basándose en la declaración del Intent.
*   **Fundación After Effects (AE Provider):** Implementación de los comandos base en el `AfterEffectsProvider` utilizando llamadas reales a ExtendScript vía `adobe-mcp` (Importar archivo, Añadir a composición, Renderizar).

**No incluye (Desplazado a iteraciones futuras):**
*   Generación de assets estáticos (Photoshop/Illustrator).
*   Lógica de prompting para LLMs (Agent Planner).

## 3. Requerimientos Técnicos Detallados

### Req 1: Inyección Dinámica de Dependencias en el DAG
*   **Descripción:** Los nodos del grafo necesitan compartir memoria. Lo que genera el Nodo A debe ser consumible por el Nodo B.
*   **Especificaciones:**
    *   Implementar un almacén de contexto (`ExecutionContext` o `ArtifactRegistry`) a nivel del grafo.
    *   Cuando un nodo finaliza en `SUCCESS`, debe registrar sus rutas de salida absolutas en este contexto usando una clave única (ej. `node_1.output.video`).
    *   El `IntentParser` y Zod deben permitir sintaxis de referencia en los parámetros de los nodos dependientes (ej. `{"input_file": "${node_1.output.video}"}`).
    *   El motor debe resolver estas referencias (templating) justo antes de iniciar la ejecución del nodo dependiente.

### Req 2: Multi-Provider Routing
*   **Descripción:** El servidor MCP debe saber a qué aplicación de Adobe enviarle el comando en cada paso.
*   **Especificaciones:**
    *   El esquema DSL debe hacer obligatorio el campo `provider` (o inferirlo mediante un prefijo en la acción, ej. `ae.import_footage` vs `ch.export_video`) en cada nodo.
    *   El `AnimationEngine` debe instanciar y mantener activas múltiples sesiones/puentes si el DAG las requiere.
    *   El sistema de Graceful Shutdown debe actualizarse para limpiar múltiples subprocesos (ej. cerrar tanto el proceso de Python de CH como el de AE) en caso de cancelación abrupta.

### Req 3: Integración Nativa con After Effects (AE Provider)
*   **Descripción:** A diferencia de CH, AE se controlará de forma limpia y oficial.
*   **Especificaciones:**
    *   Conectar el `AfterEffectsProvider` con los comandos de ExtendScript (.jsx) soportados por `adobe-mcp`.
    *   Capacidades mínimas a implementar:
        *   Crear composición nueva.
        *   Importar footage (el video generado por CH).
        *   Añadir footage a la composición.
        *   Lanzar render de la composición usando la Render Queue nativa.
    *   La Perception Layer de AE puede ser directa (leyendo los callbacks o retornos JSON del script JSX) en lugar de depender exclusivamente del `FileSystemObserver`.

## 4. Criterios de Aceptación (AC)

*   **AC-13 (Inyección de Artefactos):**
    *   Dado: Un DAG donde el Nodo 2 depende del Nodo 1.
    *   Cuando: El Nodo 1 termina y genera el archivo `C:/temp/anim.mp4`.
    *   Entonces: El motor inyecta esa ruta exacta en los parámetros del Nodo 2 antes de ejecutarlo, sin intervención del cliente IA.

*   **AC-14 (Orquestación CH a AE):**
    *   Dado: Un JSON de intención que ordena generar una animación en CH y luego procesarla en AE.
    *   Cuando: Se envía el Intent al servidor MCP.
    *   Entonces: El motor controla robóticamente Character Animator para generar el video base, luego abre After Effects, importa el video recién creado mediante ExtendScript, lo coloca en una composición y lo renderiza de nuevo, reportando un SUCCESS unificado con la ruta del render final de AE.

*   **AC-15 (Percepción Nativa AE):**
    *   Dado: Una operación enviada al `AfterEffectsProvider`.
    *   Cuando: Se ejecuta un script JSX fallido (ej. archivo no encontrado).
    *   Entonces: La Perception Layer captura la excepción nativa de ExtendScript (en lugar de esperar un timeout en el disco) y activa el Self-healing inmediatamente.
