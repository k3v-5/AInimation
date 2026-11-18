# Documento de Requerimientos: Iteración 6 - Agent Planner & System Prompting

## 1. Objetivo de la Iteración

Desarrollar la capa cognitiva (Cliente MCP) que interactúa con el usuario final. Este Agente tomará peticiones en lenguaje natural (ej. "Anima a Juan saludando y ponle un fondo en After Effects"), razonará sobre las capacidades del sistema, construirá el `Intent` en formato JSON cumpliendo estrictamente con el esquema Zod, y manejará los errores devueltos por el motor mediante autorreflexión.

## 2. Alcance

**Incluye:**

1. **Ingeniería de Prompts (System Instructions):** Diseño del contexto maestro que le enseña al LLM (ej. Claude) qué es el *Animation Engine*, cuáles son sus *Providers* (Character Animator, After Effects) y cómo estructurar el DSL.
2. **Ciclo de Reflexión y Corrección (LLM Self-Correction):** Lógica para que el Agente interprete los errores de validación (Zod) o de ejecución (ej. archivo no encontrado) devueltos por el servidor MCP, y regenere el JSON corregido sin pedir ayuda al usuario.
3. **Matriz de Pruebas de Intención:** Creación de un *test suite* automatizado para validar que distintos *prompts* en lenguaje natural siempre converjan en grafos válidos.

**No incluye:**

* Nuevos *Providers* para aplicaciones de Adobe (Photoshop, Illustrator, Premiere).
* Desarrollo de una Interfaz Gráfica (UI) compleja; la interacción puede ser vía CLI o un chat básico de cliente MCP.

---

## 3. Requerimientos Técnicos Detallados

### Req 1: Diseño del "System Prompt" del Director de Animación

* **Descripción:** El LLM debe entender las reglas de negocio y las restricciones topológicas del DAG.
* **Especificaciones:**
* Definir explícitamente en el prompt la lista de `Capabilities` disponibles (ej. `puppet.pose`, `render.export`, `ae.comp.create`).
* Instruir al modelo sobre cómo usar la sintaxis de interpolación (`${nodo_id.output}`) desarrollada en la Iteración 5 para pasar contexto de CH a AE.
* Imponer la regla estricta de no alucinar parámetros u operaciones que no estén en la especificación del esquema.

### Req 2: Bucle de Ejecución y Reflexión (Self-Healing Cognitivo)

* **Descripción:** El Agente no debe rendirse al primer error de sintaxis. Debe comportarse como un sistema resiliente en la capa lógica.
* **Especificaciones:**
* Si el servidor MCP responde con un error de validación (ej. *ZodError: missing required field 'audio_path'*), el Agente debe capturar este payload, analizar qué campo omitió, corregir el JSON interno y volver a invocar la herramienta (`Tool Call`) automáticamente.
* Establecer un límite de reflexiones (ej. máximo 3 intentos de corregir el JSON) antes de informar al usuario humano que la petición es irresoluble.

### Req 3: Suite de Pruebas de Comportamiento del Agente

* **Descripción:** Garantizar que el modelo genere estructuras de datos consistentes y predecibles.
* **Especificaciones:**
* Diseñar una matriz de pruebas que inyecte *prompts* semilla estandarizados.
* Validar que la salida del LLM (antes de enviarse al MCP) pase el validador Zod localmente en el entorno de pruebas.
* Casos a probar: Intenciones simples (solo CH), Intenciones Multi-App (CH + AE), e Intenciones con información faltante (el Agente debe preguntar al usuario en lugar de inventar rutas de archivos).

---

## 4. Criterios de Aceptación (AC)

* **AC-16 (Traducción Natural a DSL):**
* **Dado:** El Agente LLM inicializado con el System Prompt.
* **Cuando:** El usuario ingresa: *"Renderiza una animación de 5s y pásala por After Effects"*.
* **Entonces:** El Agente invoca la herramienta del servidor MCP enviando un JSON válido que contiene al menos dos nodos orquestados, con el nodo de AE dependiendo del *output* del nodo de CH.

* **AC-17 (Autorreflexión ante Errores Zod):**
* **Dado:** El Agente generando un JSON con un error semántico (ej. usa `ch.render` en lugar de `ch.export_video`).
* **Cuando:** El motor MCP rechaza el *payload* y devuelve un `FAILED` con el detalle del error.
* **Entonces:** El Agente lee el error, corrige silenciosamente el nombre del comando, y vuelve a enviar la petición exitosamente sin alertar al usuario humano del fallo intermedio.

* **AC-18 (Solicitud de Clarificación):**
* **Dado:** El usuario solicitando una acción que requiere un recurso externo obligatorio (ej. *"Haz que el personaje hable"*).
* **Cuando:** El usuario no proporciona la ruta del archivo de audio.
* **Entonces:** El Agente, conociendo las restricciones del DSL, detiene la creación del JSON y responde al usuario solicitando explícitamente la ruta del archivo de audio necesario.
