# Documento de Requerimientos: Iteración 2 - Conexión Real, DAG y Resiliencia

## 1. Objetivo de la Iteración
Evolucionar el motor de animación desde su estado actual de "esqueleto funcional" (operando con mocks secuenciales) hacia un sistema capaz de ejecutar comandos reales y profundos en Adobe Character Animator, orquestando operaciones complejas mediante grafos (DAG) y garantizando la limpieza de procesos del sistema operativo ante desconexiones abruptas.

## 2. Contexto y Estado Actual
La arquitectura base como Servidor MCP local ya está completada. El flujo de intenciones, validación (Desired vs. Observed), almacenamiento lógico de artefactos y la rutina de self-healing operan correctamente en memoria. Sin embargo, para alcanzar el Milestone 2 completo, es necesario sustituir la iteración secuencial básica (for...of) por un motor de grafos (DAG), conectar los comandos lógicos a APIs reales de Adobe (expandiendo adobe-mcp) y blindar la gestión de subprocesos.

## 3. Alcance de la Iteración
**Incluye:**
* **Investigación e Implementación (Spike):** Expansión del script puente en Python (adobe-mcp) o creación de automatizaciones nativas del OS para inyectar comandos reales en Character Animator.
* **Motor DAG (Workflow Graph):** Implementación de la máquina de inferencia para procesar nodos en un Grafo Acíclico Dirigido (DAG), permitiendo ejecución en paralelo de operaciones independientes.
* **Gestión Asíncrona de Cancelaciones (Graceful Shutdown):** Intercepción de señales de desconexión del cliente MCP y limpieza estricta de subprocesos (matar procesos huérfanos de Python/ExtendScript).

**No incluye:**
* Soporte para nuevos proveedores (After Effects, Animate). Esta iteración sigue enfocada estrictamente en consolidar Character Animator (P0).

## 4. Requerimientos Técnicos Detallados

### Req 1: Conexión Real con Character Animator (Deep Integration)
**Descripción:** El Provider actual se comunica con adobe-mcp pero utiliza mocks. Se requiere implementar los métodos reales de manipulación.
**Especificaciones:**
* Realizar el Spike Técnico para determinar el mejor método de control profundo en Character Animator (ExtendScript, manipulación de archivos .chproj, o automatización de UI).
* Expandir la herramienta puente en Python (adobe-mcp) para recibir y ejecutar los comandos específicos enviados por el CharacterAnimatorProvider.
* Implementar la Capa de Percepción Real: El puente debe ser capaz de leer el estado actual de la aplicación (ej. verificar si un Puppet fue importado correctamente) para alimentar el flujo de validación.

### Req 2: Motor de Inferencia DAG (Grafo de Workflow)
**Descripción:** Sustituir el bucle iterativo for...of del orquestador por un procesador de Grafos Acíclicos Dirigidos.
**Especificaciones:**
* El IntentParser debe generar un WorkflowGraph donde cada nodo es una operación y las aristas (edges) representan dependencias de datos o estado.
* El motor debe recorrer el DAG resolviendo dependencias y ejecutando nodos independientes de forma concurrente (en paralelo).
* El sistema de self-healing debe ser capaz de retroceder o re-evaluar ramas específicas del grafo si un nodo dependiente entra en estado DIVERGED y supera sus reintentos.

### Req 3: Manejo Avanzado de Cancelación (Disconnect & Cleanup)
**Descripción:** Prevenir fugas de memoria y subprocesos "zombies" si el cliente IA pierde la conexión o el usuario final interrumpe el proceso.
**Especificaciones:**
* Escuchar eventos de cierre o interrupción (SIGTERM, SIGINT, pérdida de pipe stdio en el servidor MCP).
* Implementar un AbortController transversal inyectado en cada operación.
* Al detectar desconexión, el motor debe enviar una señal de matar (kill -9 o equivalente en Windows) al subproceso de adobe-mcp (Python/ExtendScript) asociado a la sesión.
* Limpiar el mapa de memoria y archivos temporales residuales.

## 5. Criterios de Aceptación (AC)
* **AC-04 (Conexión Real):**
  * Dado: Adobe Character Animator abierto en la máquina local.
  * Cuando: El servidor MCP recibe el intent character.pose o puppet.import.
  * Entonces: Character Animator refleja físicamente el cambio en su interfaz o proyecto sin devolver un mock, y el motor reporta SUCCESS basándose en la lectura del estado real de la aplicación.
* **AC-05 (Ejecución DAG Paralela):**
  * Dado: Un plan de animación con operaciones independientes (ej. "Generar audio de voz" y "Preparar el rig del personaje").
  * Cuando: El motor procesa el Workflow Graph.
  * Entonces: Ambas operaciones se inicializan concurrentemente, y la operación dependiente posterior (ej. "Lip Sync") solo comienza cuando ambas dependencias previas han emitido artefactos válidos.
* **AC-06 (Limpieza de Subprocesos):**
  * Dado: El motor ejecutando una operación pesada mediante adobe-mcp.
  * Cuando: La conexión stdio de la IA cliente se cierra abruptamente.
  * Entonces: El motor intercepta la desconexión, cancela el Workflow, destruye el subproceso de Python/Adobe en el OS y libera la memoria en menos de 3 segundos, evitando procesos zombies en el administrador de tareas del sistema operativo.

## 6. Entregables de la Iteración 2
* **Documento Técnico de Capa de Percepción:** Conclusión del Spike, explicando cómo el sistema lee el estado de Character Animator (ExtendScript vs OS Automation).
* **Pull Request (Core):** Implementación del procesador DAG sustituyendo el orquestador lineal actual.
* **Pull Request (Provider/Python):** Extensión del puente adobe-mcp con capacidades reales para Character Animator.
* **Pruebas Unitarias Actualizadas:** Tests en Vitest que simulen desconexiones (AbortSignal) y demuestren la ejecución en paralelo (DAG) mediante timers.
