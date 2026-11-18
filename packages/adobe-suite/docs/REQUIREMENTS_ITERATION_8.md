# Documento de Requerimientos: Iteración 8 - CLI de Producción y Observabilidad

## 1. Objetivo de la Iteración

Desarrollar una Interfaz de Usuario de Terminal (TUI) interactiva y un subsistema de registro (*logging*) global. El objetivo es proporcionar al usuario un entorno de chat continuo con el Agente de IA y, al mismo tiempo, exponer la telemetría del motor (estado de los nodos del DAG, progreso de Adobe, captura de errores) mediante salidas de consola ricas y archivos de registro persistentes.

## 2. Alcance

**Incluye:**

1. **CLI Interactivo (REPL):** Un bucle de lectura-evaluación que permita al usuario enviar *prompts* en lenguaje natural, recibir respuestas del Agente y mantener el hilo de la conversación.
2. **Visualización del DAG (TUI):** Implementación de barras de progreso, *spinners* y actualización de estados en tiempo real (ej. `[Ejecutando] ch.import_puppet...`) en la terminal.
3. **Subsistema de Logging Global:** Captura estructurada de todo el flujo de eventos, salidas estándar (`stdout`/`stderr`) de los procesos de Python/JSX, y rotación de archivos de log.

**No incluye:**

* Almacenamiento persistente del contexto entre diferentes sesiones (Memoria de Proyecto - Opción C).
* Librería semántica de animación (Opción A).

---

## 3. Requerimientos Técnicos Detallados

### Req 1: Bucle de Interacción del Agente (CLI App)
* **Descripción:** Crear el punto de entrada principal para el usuario final (ej. `npm run agent`).
* **Especificaciones:**
  * Implementar un *prompt* interactivo que capture la entrada del usuario y la envíe al *Agent Planner*.
  * El CLI debe renderizar la respuesta reflexiva del Agente (ej. *"Entendido, generando los assets en Photoshop..."*) antes de ceder el control al motor MCP.
  * Debe soportar comandos de control integrados (ej. `/clear`, `/exit`, `/status`).

### Req 2: Motor de Observabilidad y TUI
* **Descripción:** Romper la "caja negra" visualizando el procesamiento concurrente.
* **Especificaciones:**
  * Utilizar librerías de terminal (como `ora` para *spinners* o `ink`/`cli-progress`) para renderizar el estado del `WorkflowGraphEngine`.
  * La interfaz debe mostrar qué nodos están en cola, cuáles se están ejecutando en paralelo y cuáles fallaron y entraron en modo *Self-Healing*.
  * La TUI debe interceptar la salida de los *Providers* (ej. el porcentaje de render de After Effects) y mapearla a la interfaz sin romper el formato visual.

### Req 3: Logging Estructurado y Gestión de Procesos
* **Descripción:** Rastreabilidad total para auditoría y *debugging*.
* **Especificaciones:**
  * Implementar un *logger* (ej. Winston o Pino) que escriba eventos en formato JSON en archivos de registro locales (ej. `logs/engine-YYYY-MM-DD.log`).
  * Diseñar la arquitectura de salida de logs para que sea fácilmente consumible y monitoreable por gestores de procesos (como PM2) en entornos Linux o servidores *headless*, aislando los *logs* de error de los *logs* de información.
  * Implementar rotación automática de archivos para evitar el desbordamiento de disco.

---

## 4. Criterios de Aceptación (AC)

* **AC-22 (Sesión Interactiva):**
  * **Dado:** El usuario inicia el sistema desde la terminal.
  * **Cuando:** Escribe una instrucción y presiona *Enter*.
  * **Entonces:** El sistema no se cierra tras la ejecución; procesa el flujo en Adobe, muestra el resultado final (ruta del video) y vuelve a presentar el *prompt* esperando una nueva instrucción, manteniendo limpia la terminal.

* **AC-23 (Feedback Visual del DAG):**
  * **Dado:** El Agente envía un JSON con 4 nodos paralelos/secuenciales al servidor MCP.
  * **Cuando:** El motor comienza a procesarlos.
  * **Entonces:** La terminal muestra un árbol o lista dinámica que cambia de color/estado (Pendiente -> Ejecutando -> Éxito/Fallo) en tiempo real, reflejando el progreso físico de las aplicaciones de Adobe.

* **AC-24 (Trazabilidad y PM2 Readiness):**
  * **Dado:** Ocurre un fallo catastrófico en un script de ExtendScript.
  * **Cuando:** El sistema aborta y limpia los subprocesos.
  * **Entonces:** El usuario puede inspeccionar el archivo `logs/error.log` (o usar herramientas como `pm2 logs` si se despliega como servicio) y encontrar un *stack trace* completo, en formato JSON, que indique exactamente en qué nodo, *provider* y línea de código falló la ejecución.
