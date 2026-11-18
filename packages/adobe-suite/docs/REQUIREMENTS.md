# Documento de Requerimientos: Adobe Animation Engine (P0 - Character Animator)

## 1. Objetivo
Construir un motor de animación local (Operating System for Agentic Animation) que actúe como intermediario entre un Agente de IA y las aplicaciones de Adobe (iniciando con Character Animator). Su objetivo es recibir intenciones creativas de la IA en formato JSON, convertirlas en un plan de ejecución (Workflow Graph), ejecutar las operaciones en Adobe, verificar el éxito mediante una capa de percepción, e intentar recuperarse (self-healing) en caso de fallos, devolviendo finalmente los artefactos generados.

## 2. Contexto
La premisa fundamental de la arquitectura es: La IA no sabe cómo usar Adobe. La IA expresa intenciones (ej. "hacer que el personaje salude"). El motor traduce esta intención a operaciones específicas según el "Provider" disponible. Para evitar que la IA omita pasos, la orquestación de la secuencia se gestiona 100% dentro de la memoria del Engine.

## 3. Alcance
**Incluye:**
* Implementación del Motor de Animación como Servidor MCP local.
* Capa de comunicación vía stdio para ingesta de JSON (Intents) y emisión de resultados.
* Máquina de estados en memoria (RAM) para gestionar el Workflow Graph.
* Módulo de validación de estado (Desired vs Observed).
* Subsistema de recuperación (Self-healing) ante divergencias, con límite de reintentos.
* Proveedor P0: Adobe Character Animator.
* Gestión de guardado de Artifacts (archivos resultantes) en el almacenamiento local.

**No incluye:**
* Interfaz Gráfica de Usuario (UI) propia para el motor.
* Soporte para bases de datos relacionales o almacenamiento persistente del historial de estados.
* Proveedores para After Effects, Animate o Premiere (Fases posteriores).
* Ejecución o sincronización en la nube (Cloud execution).

## 4. Actores
* **IA (Cliente MCP):** Herramienta de escritorio que emite las intenciones creativas (Intents) basadas en las peticiones del usuario final.
* **Animation Engine (Servidor MCP):** El sistema core que orquesta el plan, traduce comandos y controla el estado.
* **Aplicación Destino (Provider P0):** Adobe Character Animator.

## 5. Flujo principal
1. La IA (Cliente) envía un payload JSON (Intent) al Engine mediante el protocolo MCP.
2. El Intent Model abstrae la semántica y el Planner del Engine genera un Animation Plan (pasos universales).
3. El motor crea un Workflow Graph en memoria para rastrear el progreso de la operación.
4. El motor delega las operaciones al proveedor (Character Animator Provider).
5. El Provider envía comandos específicos (vía Adobe Runtime, ExtendScript o simulación).
6. La capa de percepción (Perception Layer) lee el estado real (Observed State) de Adobe.
7. El motor compara el Desired State con el Observed State.
8. Al validar el éxito de todas las operaciones, el motor guarda los Artifacts (ej. renders o PSDs) en el disco local.
9. El motor devuelve a la IA un payload JSON de éxito con la ruta de los archivos generados.

## 6. Flujos alternativos
* **Flujo de Recuperación (Self-Healing):** Si en el paso 7 el Observed State es "DIVERGED", el sistema activa la rutina de Recovery. Genera una operación correctiva e intenta sincronizar el estado nuevamente, sumando 1 al contador de reintentos.
* **Flujo de Límite de Reintentos:** Si el flujo de recuperación falla consecutivamente y supera el límite máximo configurado (ej. 3 reintentos), la máquina de estados aborta la operación, limpia la memoria y devuelve un payload JSON de error a la IA indicando en qué nodo del Workflow Graph falló.

## 7. Entradas
* **Nombre:** ExecuteIntent
* **Tipo:** JSON Payload (vía MCP Tool Call).
* **Obligatorio:** Sí.
* **Campos mínimos esperados:**
  * `intent_id` (String): Identificador único de la petición.
  * `action` (String): Acción universal (ej. character.pose, animation.lipSync).
  * `parameters` (Object): Parámetros dinámicos según la acción (ej. ruta del audio, nombre de la pose).
  * `target_provider` (String, Opcional): Proveedor preferido (por defecto character_animator).

## 8. Salidas
El sistema debe emitir JSONs respondiendo a la llamada MCP:

**En caso de éxito (Success Payload):**
* `status`: "SUCCESS"
* `intent_id`: [ID original]
* `artifacts`: Array de objetos con el type y local_path de los archivos generados.

**En caso de error (Error Payload):**
* `status`: "FAILED"
* `intent_id`: [ID original]
* `error_code`: Código estandarizado de error.
* `failed_operation`: El nombre de la Operation que causó el fallo.
* `message`: Detalles del error para que la IA decida cómo proceder.

## 9. Reglas de negocio
* **RN-01 (Aislamiento de la IA):** La IA externa no debe tener control sobre los pasos individuales del flujo de Adobe; únicamente puede invocar intenciones completas y recibir resultados finales o de progreso.
* **RN-02 (Abstracción Universal):** Ninguna operación dentro del Animation Plan debe contener comandos nativos de Adobe. Deben usar el DSL universal; la traducción ocurre exclusivamente en la capa Provider.
* **RN-03 (Contrato de Capabilities):** Antes de iniciar la ejecución del Workflow Graph, el motor debe verificar que el Provider seleccionado soporte las capacidades requeridas por el Intent (ej. audio.lip_sync).
* **RN-04 (Inmutabilidad del Estado):** El Workflow Graph y la máquina de estados existirán únicamente en la memoria RAM (ciclo de vida del proceso). Si el proceso del servidor MCP se cierra, se pierde el estado de ejecución actual.
* **RN-05 (Límite de Self-Healing):** Toda operación que entre en estado DIVERGED tiene un máximo estricto de reintentos (configurable, valor por defecto: 3) antes de abortar.

## 10. Permisos y seguridad
* El motor heredará los permisos del usuario del Sistema Operativo local (ej. lectura/escritura en disco para almacenar Artifacts).
* No requiere autenticación de red, ya que se comunica vía M2M (stdio) con un cliente local.

## 11. Manejo de errores
* **Adobe cerrado/inaccesible:** Si el Provider no puede comunicarse con Character Animator, devuelve inmediatamente un error de tipo PROVIDER_UNAVAILABLE.
* **Fallo de Capa de Percepción:** Si la percepción no logra determinar el Observed State en un tiempo determinado (Timeout), el estado pasa a "UNKNOWN" y activa un intento de recuperación.
* **Disco lleno:** Si falla el guardado de Artifacts, el sistema intenta limpiar archivos temporales de la memoria actual; si persiste, devuelve INSUFFICIENT_STORAGE.

## 12. Casos límite
* **Interrupción forzada:** Si la IA cliente cierra abruptamente la conexión stdio durante una ejecución en Adobe, el motor debe intentar cancelar el subproceso en Adobe y limpiar la RAM.
* **Intents en paralelo:** (Pendiente de validación técnica). Por defecto, el servidor MCP debería encolar peticiones y procesar un Workflow a la vez en Adobe para evitar colisiones en la interfaz.

## 13. Integraciones
* **Protocolo MCP:** Implementación estándar del servidor MCP para exponer las Tools a la IA.
* **Adobe Character Animator Runtime:** (Método exacto a determinar en el Spike del Milestone 0) Posiblemente mediante Adobe ExtendScript, manipulación de proyectos o automatización a nivel OS.
* **File System Local:** Para lectura de assets iniciales y escritura de Artifacts finales.

## 14. Persistencia
* **Estado:** En memoria RAM exclusivamente.
* **Artefactos:** Se almacenan en una carpeta designada (ej. `~/Documents/AnimationEngine/Artifacts/`). Se crearán referencias (paths absolutos) para enviar en el JSON de salida.

## 15. UI/UX
No aplica. Es una herramienta 100% headless / CLI (M2M).

## 16. Restricciones técnicas
* Debe ejecutarse en una máquina con sistema operativo compatible con Adobe Creative Cloud (Windows o macOS).
* Requiere que la aplicación de Adobe objetivo (Character Animator) esté instalada y con licencia válida en el equipo local.
* La comunicación M2M (IA - Engine) debe ser exclusivamente local, sin latencias de red externas.

## 17. Criterios de aceptación
* **AC-01**
  * Dado: Un servidor MCP corriendo localmente y Adobe Character Animator disponible.
  * Cuando: La IA envía un Intent válido (ej. character.pose) vía stdio.
  * Entonces: El motor genera el Workflow Graph, lo completa exitosamente y responde a la IA con un JSON con el status SUCCESS y la ruta del archivo generado.
* **AC-02**
  * Dado: El motor ejecutando una operación en Character Animator.
  * Cuando: La capa de percepción detecta que el estado Observed no coincide con el Desired (Estado: DIVERGED).
  * Entonces: El motor ejecuta automáticamente una acción de Recovery sin devolver el control a la IA.
* **AC-03**
  * Dado: El motor intentando recuperar un estado DIVERGED.
  * Cuando: Se supera el límite máximo de reintentos preconfigurado (ej. 3 fallos).
  * Entonces: El motor detiene el flujo y responde a la IA con un JSON con status FAILED, incluyendo el nodo donde falló y el historial de intentos en el campo de detalles.

## 18. Casos de prueba sugeridos
* **Happy Path:** Enviar un Intent simple y verificar la creación del archivo final en el disco.
* **Recuperación exitosa:** Simular un fallo en el paso 1 que se resuelva en el intento de recuperación 2, y verificar que la operación finalice en SUCCESS.
* **Timeout / Aborto:** Enviar un comando a Adobe y simular que Adobe no responde; verificar que el límite de reintentos se cumple y retorna FAILED correctamente formateado a la IA.
* **Validación de Capas:** Confirmar mediante pruebas unitarias que la IA cliente no puede inyectar código ExtendScript directamente, sino únicamente el DSL del Intent.

## 19. Entregables
* **Investigación Técnica (Spike - Fase 0):** Documento definiendo el mecanismo exacto de la Perception Layer para Character Animator.
* **Código fuente:** Implementación del servidor MCP (Engine core, State Machine, Artifact manager).
* **Módulo Provider P0:** Integración específica de comandos para Character Animator.
* **Tests unitarios:** Cobertura para la máquina de estados y el flujo de Self-healing.
