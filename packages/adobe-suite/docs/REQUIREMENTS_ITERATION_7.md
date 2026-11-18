# Documento de Requerimientos: Iteración 7 - La Fábrica de Assets (End-to-End Pipeline)

## 1. Objetivo de la Iteración

Cerrar el ciclo horizontal de generación de contenido integrando las aplicaciones de diseño estático (Adobe Photoshop y Adobe Illustrator). El sistema debe ser capaz de recibir instrucciones conceptuales, generar o estructurar los *assets* visuales mediante secuencias de comandos nativas (ExtendScript/COM), y pasar dinámicamente estos archivos generados a Character Animator como *puppets* válidos, culminando con la post-producción en After Effects.

## 2. Alcance

**Incluye:**
1. **Activación de Providers Estáticos:** Implementación real de `PhotoshopProvider` e `IllustratorProvider` utilizando el puente oficial de `adobe-mcp`.
2. **Generación y Estructuración de Capas:** Capacidad del motor para crear documentos nuevos, generar capas (nombradas específicamente para coincidir con la jerarquía de *rigging* de Character Animator, ej. `+Mouth`, `Left Eye`) y exportar archivos `.psd` o `.ai`.
3. **Expansión Cognitiva del Agente:** Actualización del *System Prompt* para que el LLM comprenda que ya no necesita solicitar rutas de archivos base; ahora tiene herramientas para crearlos desde cero.
4. **Orquestación de Asset a Puppet (Pipeline A -> B):** Modificación del DAG para inyectar dinámicamente el `.psd` recién creado como entrada (input) del nodo de importación de Character Animator.

**No incluye:**
* Librería de comportamientos avanzados de animación (Opción B - desplazada a Iteración 8).
* CLI interactiva y sistema de logging global (Opción C - desplazada a Iteración 9).

## 3. Requerimientos Técnicos Detallados

### Req 1: Integración Nativa de PS y AI (Static Providers)
* **Descripción:** Sustituir los *mocks* actuales por llamadas de ejecución reales.
* **Especificaciones:**
  * Conectar el `PhotoshopProvider` y el `IllustratorProvider` con los comandos JSX/ExtendScript soportados por `adobe-mcp`.
  * **Capacidades mínimas a implementar:**
    * `ps.document_create` / `ai.document_create`: Crear un lienzo con dimensiones específicas (ej. 1920x1080).
    * `ps.layer_create` / `ps.layer_rename`: Fundamental para construir la estructura de carpetas y capas que Character Animator exige para el *auto-rigging*.
    * `ps.export_document`: Guardar el estado actual en el sistema de archivos local (`Artifacts`).

### Req 2: Expansión del System Prompt (Cognitive Independence)
* **Descripción:** El Agente debe orquestar la creación de los *assets* antes de intentar animarlos.
* **Especificaciones:**
  * Incorporar las nuevas herramientas (`ps.*`, `ai.*`) en el esquema de validación Zod.
  * Instruir al LLM sobre la convención de nombres de Character Animator (ej. el uso del símbolo `+` para capas independientes).
  * El LLM debe ser capaz de dividir un *prompt* general ("Haz un personaje que hable") en un DAG donde el nodo 1 es `ps.document_create` y el nodo 2 es `ch.import_puppet`, pasándose la variable del archivo por contexto.

### Req 3: Validación de Integridad de Assets (Perception Layer Upgrade)
* **Descripción:** La capa de percepción debe validar que el archivo gráfico sea estructuralmente correcto antes de pasarlo a la fase de animación.
* **Especificaciones:**
  * La *Perception Layer* debe verificar no solo que el archivo `.psd` exista en el disco (mediante el `FileSystemObserver`), sino que las capas críticas (definidas en el *Intent*) se hayan creado con los nombres correctos antes de marcar el nodo como `SUCCESS`.

## 4. Criterios de Aceptación (AC)

* **AC-19 (Generación Estructural de PSD):**
  * **Dado:** El `PhotoshopProvider` conectado y activo.
  * **Cuando:** El motor ejecuta una operación para crear un personaje básico.
  * **Entonces:** Photoshop se abre (o ejecuta en *background*), crea un nuevo archivo `.psd`, genera grupos de capas nombrados según los estándares de Character Animator (ej. `Head`, `Body`, `+Right Arm`) y guarda el archivo en la ruta de *Artifacts*, reportando un `SUCCESS` unificado.

* **AC-20 (Orquestación Extremo a Extremo - El Santo Grial):**
  * **Dado:** Un JSON de intención orquestado por el Agente.
  * **Cuando:** El sistema procesa un flujo que requiere Photoshop, Character Animator y After Effects.
  * **Entonces:** El `WorkflowGraphEngine` ejecuta el nodo de Photoshop, pasa la ruta del `.psd` generado a Character Animator (que lo importa y le aplica *Lip Sync*), y finalmente pasa el `.mp4` resultante a After Effects para la composición final, todo sin interrupción de la interfaz ni errores de dependencias perdidas.

* **AC-21 (Autonomía del Agente):**
  * **Dado:** Un usuario que solicita: *"Anima una pelota rebotando con fondo azul"*.
  * **Cuando:** El usuario **no** proporciona ningún archivo gráfico base.
  * **Entonces:** El Agente planifica la creación de la pelota y el fondo en Illustrator/Photoshop, los inyecta en el DAG, y no detiene la ejecución pidiendo recursos faltantes al humano.
